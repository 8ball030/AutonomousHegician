# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2020 eightballer
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This module defines the db communication models."""

from typing import Dict


try:
    from packages.eightballer.skills.option_management.web_server import (
        ExecutionStrategy,
        Option,
        Snapshot,
        StatusCode,
        db,
        flask_app,
    )
except Exception:
    from .web_server import (
        Option,
        Snapshot,
        StatusCode,
        ExecutionStrategy,
        db,
        flask_app,
    )

from datetime import datetime, timedelta


class DBCommunication:
    """A class to communicate with a database."""

    def __init__(self):
        """
        Initialize the database communication.

        :param source: the source
        """

    @staticmethod
    def get_orders():
        with flask_app.app_context():
            db.create_all()
            results = db.session.query(Option).all()
            db.session.close()
        return results

    @staticmethod
    def create_new_snapshot(params):
        with flask_app.app_context():
            snap = Snapshot(**params)
            db.session.add(snap)
            db.session.commit()
            db.session.close()
        return snap

    @staticmethod
    def create_new_option(amount, strike_price, period, option_type, market) -> Dict:
        with flask_app.app_context():
            execution_strategy = db.session.query(ExecutionStrategy).one()
            status_code = db.session.query(StatusCode).filter(StatusCode.id == 1).one()
            option = Option(
                amount=amount,
                strike_price=strike_price,
                period=period,
                market=market,
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
        return {
            "option_id": _id,
            "amount": amount,
            "strike_price": strike_price,
            "period": period,
            "option_type": option_type,
            "market": market,
            "status_code": 1,
        }

    @staticmethod
    def update_option(option_db_id, params) -> Option:
        with flask_app.app_context():
            option = db.session.query(Option).filter(Option.id == option_db_id).one()
            for key, value in params.items():
                setattr(option, key, value)
            db.session.merge(option)
            db.session.commit()
            db.session.close()
        return option

    @staticmethod
    def delete_options() -> bool:
        with flask_app.app_context():
            _ = db.session.query(Option).delete()
            db.session.commit()
            db.session.close()
        return True

    @staticmethod
    def get_option(option_id) -> Option:
        with flask_app.app_context():
            option = db.session.query(Option).filter(Option.id == option_id).one()
            db.session.close()
        return option
