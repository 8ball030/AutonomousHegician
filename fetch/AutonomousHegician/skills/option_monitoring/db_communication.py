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

    def get_orders(self):
        with flask_app.app_context():
            db.create_all()
            results = db.session.query(Option).all()
            db.session.close()
        return results

    def create_new_snapshot(self, params):
        with flask_app.app_context():
            snap = Snapshot(**params)
            db.session.add(snap)
            db.session.commit()
            db.session.close()
        return snap

        
    def create_new_option(self, amount, strike_price, period, option_type) -> Dict:
        with flask_app.app_context():
            execution_strategy = db.session.query(ExecutionStrategy).one()
            status_code = db.session.query(StatusCode).filter(StatusCode.id==1).one()
            option = Option(
                            amount=amount,
                            strike_price=strike_price,
                            period=period,
                            date_modified=datetime.now(),
                            date_created=datetime.now(),
                            option_type=option_type,
                            expiration_date=datetime.now() + timedelta(seconds=period),
                            execution_strategy_id=execution_strategy.id,
                            status_code_id=status_code.id,
                            )
            db.session.add(option)
            db.session.commit()
            _id = option.id
            db.session.close()
        return {"option_id":_id, "amount": amount, "strike_price": strike_price,"period": period, "option_type": option_type}

    def update_option(self, option_db_id, params) -> Option:
        with flask_app.app_context():
            option = db.session.query(Option).filter(Option.id == option_db_id).one()
            for key, value in params.items():
                setattr(option, key, value)
            db.session.merge(option)
            db.session.commit()
            db.session.close()
        return option

    @staticmethod
    def get_option(cls, option_id) -> Option:
        with flask_app.app_context():
            option = db.session.query(option_id).fetchone()
            db.session.close()
        return option
