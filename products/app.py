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
        return  f'id:{self.id} \n' \
                f'name:{self.name} '

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
        return  f'id:{self.id} \n' \
                f'name:{self.name} '


def db_init():
    c = sqlite3.connect("products.db").cursor()
    c.execute("CREATE TABLE IF NOT EXISTS PRODUCTS("
              "id TEXT, name TEXT, releaseDate TEXT, quantity TEXT, price TEXT, photos TEXT, manufacturer TEXT)"
              )
    c.execute("CREATE TABLE IF NOT EXISTS MANUFACTURERS("
              "id TEXT, name TEXT, homePage TEXT, phone TEXT)"
              )
    c.connection.close()

@app.route('/v1')
def homepage():
    db_init()
    return '<p>This is PRODUCTS API</p>'

@app.route('/v1/products', methods=['GET'])
def get_products():
    c = sqlite3.connect("products.db").cursor()
    c.execute("SELECT * FROM PRODUCTS")
    data = c.fetchall()
    return jsonify(data)

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
    

    c.execute("INSERT INTO PRODUCTS VALUES(?,?,?,?,?,?,?)",
              (product.id, product.name, product.releaseDate, product.quantity, product.price, product.photos, product.manufacturer))
    db.commit()
    data = c.lastrowid
    return json.dumps(data)

@app.route('/v1/product/<id>', methods=['GET'])
def getProductsById(id):    
    c = sqlite3.connect("products.db").cursor()
    c.execute("SELECT * FROM PRODUCTS WHERE id=?", (id,))
    data = c.fetchone()
    return json.dumps(data)

@app.route('/v1/product/<id>', methods=['PUT'])
def approveProduct(id):
    db = sqlite3.connect("products.db")
    c = db.cursor()
    qnt = request.json["quantity"]
    c.execute("UPDATE PRODUCTS SET quantity = ? WHERE id=?", (qnt, id))
    db.commit()
    return json.dumps("Product was successfully updated")


@app.route('/v1/product/<id>', methods=['DELETE'])
def removeProduct(id):
    db = sqlite3.connect("products.db")
    c = db.cursor()
    c.execute("DELETE FROM PRODUCTS WHERE id=?", (id,))
    db.commit()
    return json.dumps("Product was successfully removed")

if __name__ == '__main__':
    app.run(port=8888)