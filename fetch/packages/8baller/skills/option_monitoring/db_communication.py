import datetime
import os.path
import sqlite3
from typing import Dict, cast

from packages.tomrae.skills.option_monitoring.web_server import (
    Option,
    Snapshot,
    StatusCode,
    ExecutionStrategy,
    db,
    flask_app
)
from datetime import datetime, timedelta

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



    def get_orders(self):
        with flask_app.app_context():
            results = db.session.query(Option).all()
            db.session.close()
        return results

    def create_new_option(self, amount, strike_price, period, option_type) -> Option:
        option = Option(id="1", 
                        amount=amount,
                        strike_price=strike_price,
                        period=period,
                        date_modified=datetime.now(),
                        date_created=datetime.now(),
                        option_type=option_type,
                        expiration_date=datetime.now() + timedelta(seconds=period),
                        execution_strategy_id=1,
                        status_code=0, 
        )
        with flask_app.app_context():
            db.session.add(option)
            db.session.close()
        return option
    
    @staticmethod
    def update_option(cls, option) -> Option:
        with flask_app.app_context():
            db.session.merge(option)
            db.session.close()
        return option
        
        
    @staticmethod
    def get_option(cls, option_id) -> Option:
        with flask_app.app_context():
            option = db.session.query(option_id).fetchone()
            db.session.close()
        return option

        