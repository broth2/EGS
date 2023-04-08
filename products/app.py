import uuid
from flask import *
import json
import sqlite3


app = Flask(__name__)

class Manufacturer:
    def __init__(self, name, homePage, phone):
        self.id = uuid.uuid4().hex
        self.name = name
        self.homePage = homePage
        self.phone = phone

    def __str__(self):
        return  f'{{id:{self.id} \n' \
                f'name:{self.name}}}'

class Product:
    def __init__(self, name, releaseDate, quantity, price, photos, manufacturer):
        self.id = uuid.uuid4().hex
        self.name = name
        self.releaseDate = releaseDate
        self.quantity = quantity
        self.price = price
        self.photos = photos
        self.manufacturer = manufacturer

    def __str__(self):
        return  f'{{id:{self.id} \n' \
                f'name:{self.name}}}'


def db_init():
    c = sqlite3.connect("products.db").cursor()
    c.execute("CREATE TABLE IF NOT EXISTS manufacturers("
              "id TEXT PRIMARY KEY, name TEXT, homePage TEXT, phone TEXT)"
              )
    c.execute("CREATE TABLE IF NOT EXISTS products("
              "id TEXT PRIMARY KEY, name TEXT, releaseDate TEXT, quantity TEXT, price TEXT, photos TEXT, manufacturer_id TEXT)" #, FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id))"
              )
    c.connection.close()

@app.route('/v1')
def homepage():
    db_init()
    return '<p>This is PRODUCTS API</p>'

@app.route('/v1/products', methods=['GET'])
def get_products():
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)
    offset = (page - 1) * page_size
    in_offset = request.args.get('offset', default=offset, type=int)
    srch = request.args.get('searchName', default="", type=str)

    c = sqlite3.connect("products.db").cursor()
    query = f"SELECT * FROM products WHERE name LIKE ? LIMIT ? OFFSET ?"
    c.execute(query, ('%' + srch + '%', page_size, in_offset))
    data = c.fetchall()
    products = productsToJson(data)

    metadata = {
        "searchName": srch,
        'page': page,
        'offset': in_offset,
        'count': len(products)
    }

    response = {
        'pagination': metadata,
        'products': products
    }

    return jsonify(response)

@app.route('/v1/product', methods=['POST'])
def add_product():
    db = sqlite3.connect("products.db")
    c = db.cursor()
    product = Product(request.json["name"],
                      request.json["releaseDate"],
                      request.json["quantity"],
                      request.json["price"],
                      request.json["photos"],
                      request.json["manufacturer"])
    

    c.execute("INSERT INTO products VALUES(?,?,?,?,?,?,?)",
              (product.id, product.name, product.releaseDate, product.quantity, product.price, product.photos, product.manufacturer))
    db.commit()
    data = c.lastrowid
    return json.dumps(data)

@app.route('/v1/products', methods=['POST'])
def add_products():
    data = 0
    db = sqlite3.connect("products.db")
    c = db.cursor()
    for entry in request.json:
        product = Product(entry["name"],
                        entry["releaseDate"],
                        entry["quantity"],
                        entry["price"],
                        entry["photos"],
                        entry["manufacturer"])

        c.execute("INSERT INTO products VALUES(?,?,?,?,?,?,?)",
                (product.id, product.name, product.releaseDate, product.quantity, product.price, product.photos, product.manufacturer))
        data += 1
    db.commit()
    data = f"inserted {data} elements"
    return json.dumps(data)

@app.route('/v1/product/<id>', methods=['GET'])
def getProductsById(id):    
    c = sqlite3.connect("products.db").cursor()
    c.execute("SELECT * FROM products WHERE id=?", (id,))
    data = c.fetchone()
    prod = productToJson(data)
    return prod

@app.route('/v1/product/<id>', methods=['PUT'])
def approveProduct(id):
    rtrn_str = ""
    db = sqlite3.connect("products.db")
    c = db.cursor()
    if "quantity" in request.json:
        qnt = request.json["quantity"]
        c.execute("UPDATE products SET quantity = ? WHERE id=?", (qnt, id))
        rtrn_str += f"quantity={qnt} "
    if "price" in request.json:
        prc = request.json["price"]
        c.execute("UPDATE products SET price = ? WHERE id=?", (prc, id))
        rtrn_str += f"price={prc} "
    if "photos" in request.json:
        pht_cntr = 0
        c.execute("SELECT photos FROM products WHERE id=?", (id,))
        old_photos = json.loads(c.fetchone()[0])
        new_photos = request.json["photos"]
        for photo in new_photos:
            if photo not in old_photos:
                old_photos.append(photo)
                pht_cntr += 1
        old_photos = parseToString(old_photos)
        # photo list format example: '["www.pcdiga.com", "www.website.com", "www.images.pt", "www.wikipedi.org/objecto"]'
        c.execute("UPDATE products SET photos = ? WHERE id=?", (old_photos, id))
        rtrn_str += f"photos+={pht_cntr}"

    db.commit()
    return json.dumps(f"Product was successfully updated to {rtrn_str}")

@app.route('/v1/product/<id>', methods=['DELETE'])
def removeProduct(id):
    db = sqlite3.connect("products.db")
    c = db.cursor()
    c.execute("DELETE FROM products WHERE id=?", (id,))
    db.commit()
    return json.dumps("Product was successfully removed")


def productsToJson(data):
    prdtcs = [{'id': row[0], 'name': row[1], 'releaseDate': row[2], 'quantity': row[3], 'price': row[4], 'photos': row[5], 'manufacturer': row[6] } for row in data]
    return prdtcs

def productToJson(row):
    prdtc = {'id': row[0], 'name': row[1], 'releaseDate': row[2], 'quantity': row[3], 'price': row[4], 'photos': row[5], 'manufacturer': row[6] }
    return jsonify(prdtc)

def parseToString(mylist):
    new_string = "["
    for a in mylist:
        new_string += '"'
        new_string += a
        new_string += '", '
    new_string = new_string[:-2]
    new_string += "]"
    print(new_string)
    return new_string

if __name__ == '__main__':
    app.run(port=8888)
