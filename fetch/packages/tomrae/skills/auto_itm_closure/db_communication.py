import datetime
import os.path
import sqlite3
from typing import Dict, cast

my_path = os.path.dirname(__file__)

DB_SOURCE = os.path.join(my_path, "dummy_hegic_option_data.db")


class DBCommunication:
    """A class to communicate with a database."""
    def __init__(self):
        """
        Initialize the database communication.

        :param source: the source
        """
        self.source = DB_SOURCE

    def db_connection(self) -> sqlite3.Connection:
        """
        Get db connection.

        :return: the db connection
        """
        con = sqlite3.connect(self.source)
        con.row_factory = sqlite3.Row
        return con

    def get_orders(self) -> Dict[str, int]:
        """
        Get data for all upcoming contracts.

        :param start_date: the start date
        :param end_date: the end date
        :return: the data
        """
        con = self.db_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM data where status = 'pending'")
        data = cur.fetchall()
        cur.close()
        con.close()
        return data
