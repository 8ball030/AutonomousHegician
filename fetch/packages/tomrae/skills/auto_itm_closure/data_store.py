#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Tom Rae
Authorised use only
"""
from datetime import datetime, timedelta
import logging
import os.path
import json
import sqlite3
import time
from typing import Dict, Union

logging.basicConfig()

logger = logging.getLogger(
    "aea.packages.fetchai.skills.hegic_helper.dummy_hegic_option_data")

logger.setLevel(logging.INFO)
my_path = os.path.dirname(__file__)
DB_SOURCE = os.path.join(my_path, "dummy_hegic_option_data.db")


# Checking if the database exists
def setup_datastore():
    con = sqlite3.connect(DB_SOURCE)
    cur = con.cursor()
    return cur, con


def create_datastore(cur, con):
    # Create a table if it doesn't exist'
    command = """ CREATE TABLE IF NOT EXISTS data (
                                     strike_price REAL,
                                     expiration_date DATETIME,
                                     amount REAL,
                                     type_of_option VARCHAR,
                                     type_of_order VARCHAR,
                                     status VARCHAR,
                                     tx_id VARCHAR,
                                     params VARCHAR
                                     )"""
    cur.execute(command)
    cur.close()
    con.commit()
    if con is not None:
        logger.debug(
            "HegicHelper: I closed the db after checking it is populated!")
        con.close()


class OptionData:
    """Represents a collection of options contracts."""
    @staticmethod
    def add_data(tagged_data: Dict[str, Union[int, datetime]]) -> None:
        """
        Add data to the orders.

        :param tagged_data: the data dictionary
        :return: None
        """
        con = sqlite3.connect(DB_SOURCE)
        cur = con.cursor()
        sql = f"""INSERT INTO data(strike_price,
                                expiration_date,
                                amount,
                                type_of_option,
                                type_of_order,
                                status,
                                tx_id,
                                params) 
            VALUES({tagged_data["strike_price"]},
                   '{tagged_data["expiration_date"]}',
                   {tagged_data["amount"]},
                   '{tagged_data["type_of_option"]}',
                   '{tagged_data["type_of_order"]}',
                   '{tagged_data["status"]}',
                   '{tagged_data["tx_id"]}',
                   '{tagged_data["params"]}')
                   """
        cur.execute(sql)
        logger.info("DB_Data_orders: I added data in the db!")
        cur.close()
        con.commit()
        con.close()

    def generate(self):
        """Generate option data."""
        # In the money put
        dict_of_data = {
            "strike_price": 5000,
            "expiration_date": datetime.now() + timedelta(days=14),
            "amount": 1,
            "type_of_option": "put",
            "type_of_order": "auto_execute",
            "status": "pending",
            "tx_id": "asdkjaslkdjerjasdmasdkj",
            "params": json.dumps({})
        }  # type: Dict[str, Union[int, datetime.datetime]]
        self.add_data(dict_of_data)
        # out of the money put
        dict_of_data = {
            "strike_price": 100,
            "expiration_date": datetime.now() + timedelta(days=14),
            "amount": 1,
            "type_of_option": "put",
            "type_of_order": "auto_execute",
            "status": "pending",
            "tx_id": "asdkjaslkdjerjasdmasdkj",
            "params": json.dumps({})
        }  # type: Dict[str, Union[int, datetime.datetime]]
        self.add_data(dict_of_data)
        # in the money call
        dict_of_data = {
            "strike_price": 100,
            "expiration_date": datetime.now() + timedelta(days=14),
            "amount": 1,
            "type_of_option": "call",
            "type_of_order": "auto_execute",
            "status": "pending",
            "tx_id": "asdkjaslkdjerjasdmasdkj",
            "params": json.dumps({})
        }  # type: Dict[str, Union[int, datetime.datetime]]
        self.add_data(dict_of_data)
        # out of the money call
        dict_of_data = {
            "strike_price": 1000,
            "expiration_date": datetime.now() + timedelta(days=14),
            "amount": 1,
            "type_of_option": "call",
            "type_of_order": "auto_execute",
            "status": "pending",
            "tx_id": "asdkjaslkdjerjasdmasdkj",
            "params": json.dumps({})
        }  # type: Dict[str, Union[int, datetime.datetime]]
        self.add_data(dict_of_data)


if __name__ == "__main__":
    cur, con = setup_datastore()
    create_datastore(cur, con)
    a = OptionData()
    a.generate()
