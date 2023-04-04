import uuid
from flask import *
import json
import sqlite3
import os


app = Flask(__name__)

class Entity:

    def __init__(self, approved, isPartner, name, address, description, homePage, phoneNo, nif, sku_list, externalID):
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
        self.externalID = externalID

    def __str__(self):
        return  f'{{id:{self.id} \n' \
                f'name:{self.name}}}'

def db_init():
    c = sqlite3.connect("entities.db").cursor()
    c.execute("CREATE TABLE IF NOT EXISTS entities("
              "id TEXT PRIMARY KEY, approved TEXT, isPartner TEXT, name TEXT, address TEXT, description TEXT, homePage TEXT, phoneNo TEXT, nif TEXT, sku_list TEXT, externalID TEXT)"
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
    srch = request.args.get('searchName', default="", type=str)


    c = sqlite3.connect("entities.db").cursor()
    query = f"SELECT * FROM entities WHERE name LIKE ? LIMIT ? OFFSET ?"
    c.execute(query, ('%' + srch + '%', page_size, in_offset))
    data = c.fetchall()

    entities = entitiesToJson(data)
    metadata = {
        'searchName': srch,
        'page': page,
        'offset': in_offset,
        'count': len(entities)
    }

    response = {
        'pagination': metadata,
        'entities': entities
    }

    return jsonify(response)

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
                      request.json["sku_list"],
                      request.json["externalID"])
    

    c.execute("INSERT INTO entities VALUES(?,?,?,?,?,?,?,?,?,?,?)",
              (entity.id, 0, entity.isPartner, entity.name, entity.address, entity.description, entity.homePage, entity.phoneNo, entity.nif, entity.sku_list, entity.externalID))
    db.commit()
    data = c.lastrowid
    return json.dumps(data)

@app.route('/v1/entity/<id>', methods=['GET'])
def getEntitiesById(id):    
    c = sqlite3.connect("entities.db").cursor()
    c.execute("SELECT * FROM entities WHERE id=?", (id,))
    data = c.fetchone()

    entt = entityToJson(data)
    return entt

@app.route('/v1/entity/<id>', methods=['PUT'])
def approveEntity(id):
    db = sqlite3.connect("entities.db")
    c = db.cursor()
    if request.form["approved"] == "1" :
        c.execute("UPDATE entities SET approved = ? WHERE id=?", (1, id))
        db.commit()
        return json.dumps("Entity was successfully approved")
    return json.dumps("Couldn't approve entity")

@app.route('/v1/entity/<id>', methods=['DELETE'])
def removeEntity(id):
    db = sqlite3.connect("entities.db")
    c = db.cursor()
    c.execute("DELETE FROM entities WHERE id=?", (id))
    db.commit()
    return json.dumps("Entity was successfully removed")

@app.route('/v1/entity/<id>/sku/<skuid>', methods=['PUT'])
def addSKU(id, skuid):
    db = sqlite3.connect("entities.db")
    c = db.cursor()
    c.execute("SELECT * FROM entities WHERE id=?", (id))
    skus = c.fetchone().sku_list
    if skuid not in skus:
        skus.append(skuid)
        c.execute("UPDATE entities SET sku_list = ? WHERE id=?", (skus, id))
        db.commit()
        return json.dumps("SKU successfully added   ")
    return json.dumps("SKU already associated to partner")

@app.route('/v1/entity/<id>/sku/<skuid>', methods=['DELETE'])
def removeSKU(id, skuid):
    db = sqlite3.connect("entities.db")
    c = db.cursor()
    c.execute("SELECT * FROM entities WHERE id=?", (id))
    skus = c.fetchone().sku_list
    if skuid in skus:
        skus.remove(skuid)
        c.execute("UPDATE entities SET sku_list = ? WHERE id=?", (skus, id))
        db.commit()
        return json.dumps("SKU successfully removed")
    return json.dumps("SKU not associated to partner")

def entitiesToJson(data):
    prdtcs = [{'id': row[0], 'approved': row[1], 'isPartner': row[2], 'name': row[3], 'address': row[4], 'description': row[5], 'homePage': row[6], 'phoneNo': row[7], 'nif': row[8], 'sku_list': row[9], 'externalID': row[10] } for row in data]
    return prdtcs

def entityToJson(row):
    entty = {'id': row[0], 'approved': row[1], 'isPartner': row[2], 'name': row[3], 'address': row[4], 'description': row[5], 'homePage': row[6], 'phoneNo': row[7], 'nif': row[8], 'sku_list': row[9], 'externalID': row[10]}
    return jsonify(entty)

if __name__ == '__main__':
    app.run(port=8888)

