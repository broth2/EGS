import uuid
from flask import *
import json
import sqlite3
from pymongo import MongoClient
# ver sql alchemy
app = Flask(__name__)

client = MongoClient('localhost', 27017)

mdb = client.m_entities
todos = mdb.todos

class Entity:

    def __init__(self, approved, isPartner, name, address, description, homePage, phoneNo, nif, sku_list):
        self.id = uuid.uuid4().hex
        self.approved = approved
        self.isPartner = isPartner
        self.name = name
        self.address = address
        self.description = description
        self.homePage = homePage
        self.phoneNo = phoneNo
        self.nif = nif
        self.sku_list = sku_list

    def __str__(self):
        return  f'id:{self.id} \n' \
                f'name:{self.name} '

def db_init():
    c = sqlite3.connect("entities.db").cursor()
    c.execute("CREATE TABLE IF NOT EXISTS ENTITIES("
              "id TEXT, approved TEXT, isPartner TEXT, name TEXT, address TEXT, description TEXT, homePage TEXT, phoneNo TEXT, nif TEXT, sku_list TEXT)"
              )
    c.connection.close()

@app.route('/v1')
def homepage():
    db_init()
    return '<p>This is entities API</p>'

@app.route('/v1/entities', methods=['GET'])
def get_entities():
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)
    offset = (page - 1) * page_size
    in_offset = request.args.get('offset', default=offset, type=int)


    c = sqlite3.connect("entities.db").cursor()
    c.execute(f'SELECT * FROM ENTITIES LIMIT {page_size} OFFSET {in_offset}')
    data = c.fetchall()
    return jsonify(data)

@app.route('/v1/entity', methods=['POST'])
def add_entity():
    db = sqlite3.connect("entities.db")
    c = db.cursor()
    entity = Entity(0, request.json["isPartner"],
                      request.json["name"],
                      request.json["address"],
                      request.json["description"],
                      request.json["homePage"],
                      request.json["phoneNo"],
                      request.json["nif"],
                      request.json["sku_list"])
    

    c.execute("INSERT INTO ENTITIES VALUES(?,?,?,?,?,?,?,?,?,?)",
              (entity.id, 0, entity.isPartner, entity.name, entity.address, entity.description, entity.homePage, entity.phoneNo, entity.nif, entity.sku_list))
    db.commit()
    data = c.lastrowid
    return json.dumps(data)

@app.route('/v1/entity/<id>', methods=['GET'])
def getEntitiesById(id):    
    c = sqlite3.connect("entities.db").cursor()
    c.execute("SELECT * FROM ENTITIES WHERE id=?", (id,))
    data = c.fetchone()
    return json.dumps(data)

@app.route('/v1/entity/<id>', methods=['PUT'])
def approveEntity(id):
    db = sqlite3.connect("entities.db")
    c = db.cursor()
    if request.form["approved"] == 1 :
        c.execute("UPDATE ENTITIES SET approved = ? WHERE id=?", (1, id))
        db.commit()
        return json.dumps("Entity was successfully approved")
    return json.dumps("Couldn't approve entity")

@app.route('/v1/entity/<id>', methods=['DELETE'])
def removeEntity(id):
    db = sqlite3.connect("entities.db")
    c = db.cursor()
    c.execute("DELETE FROM ENTITIES WHERE id=?", (id))
    db.commit()
    return json.dumps("Entity was successfully removed")

@app.route('/v1/entity/<id>/sku/<skuid>', methods=['PUT'])
def addSKU(id, skuid):
    db = sqlite3.connect("entities.db")
    c = db.cursor()
    c.execute("SELECT * FROM ENTITIES WHERE id=?", (id))
    skus = c.fetchone().sku_list
    if skuid not in skus:
        skus.append(skuid)
        c.execute("UPDATE ENTITIES SET sku_list = ? WHERE id=?", (skus, id))
        db.commit()
        return json.dumps("SKU successfully added   ")
    return json.dumps("SKU already associated to partner")

@app.route('/v1/entity/<id>/sku/<skuid>', methods=['DELETE'])
def removeSKU(id, skuid):
    db = sqlite3.connect("entities.db")
    c = db.cursor()
    c.execute("SELECT * FROM ENTITIES WHERE id=?", (id))
    skus = c.fetchone().sku_list
    if skuid in skus:
        skus.remove(skuid)
        c.execute("UPDATE ENTITIES SET sku_list = ? WHERE id=?", (skus, id))
        db.commit()
        return json.dumps("SKU successfully removed")
    return json.dumps("SKU not associated to partner")

if __name__ == '__main__':
    app.run(port=8888)