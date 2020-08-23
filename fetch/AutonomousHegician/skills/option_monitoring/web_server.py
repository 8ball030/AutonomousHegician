#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Tom Rae
Authorised use only
"""
from flask import Flask
from flask_restplus import Resource, Api
import sqlite3
from flask import g
from flask import Flask, request
from flask_restplus import Resource, Api
from typing import Dict, Union
from datetime import datetime
import json
from flask_restplus import fields
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
cors = CORS(app)

DATABASE = '/home/tom/Desktop/Medium/fetch_playground/fetch/AutonomousHegician/skills/option_monitoring/hegic_option_data.db'

option_fields = api.model(
    'Resource', {
        'optionID': fields.Integer,
        'strike_price': fields.Float,
        'expiration_date': fields.String,
        'amount': fields.Float,
        'type_of_option': fields.String,
        'type_of_order': fields.String,
        'status': fields.String,
        'params': fields.String
    })

def add_data(tagged_data: Dict[str, Union[int, datetime]]) -> None:
    """
    Add data to the orders.

    :param tagged_data: the data dictionary
    :return: None
    """
    con = get_db()
    cur = con.cursor()
    sql = f"""INSERT INTO data(strike_price,
                            expiration_date,
                            amount,
                            type_of_option,
                            type_of_order,
                            status,
                            optionID,
                            params) 
        VALUES({tagged_data["strike_price"]},
               '{tagged_data["expiration_date"]}',
               {tagged_data["amount"]},
               '{tagged_data["type_of_option"]}',
               '{tagged_data["type_of_order"]}',
               '{tagged_data["status"]}',
               '{tagged_data["optionID"]}',
               '{tagged_data["params"]}')
               """
    cur.execute(sql)
    cur.close()
    con.commit()
    con.close()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@api.route('/get_all_options')
class HegicOptions(Resource):
    def get(self):
        db = get_db()
        return [dict(i) for i in db.execute("SELECT * FROM data").fetchall()]

@api.route('/create_new_option')
class HegicOption(Resource):
    @api.expect(option_fields)
    def post(self):
        print(request.data)
        add_data(json.loads(request.data))
        return 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
