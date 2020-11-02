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

"""This module defines the webserver."""

import json
import logging
from datetime import datetime, timedelta

from flask import Flask, request
from flask_cors import CORS
from flask_restplus import Api, Resource
from flask_restplus_sqlalchemy import ApiModelFactory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import subqueryload


logger = logging.getLogger(__name__)

flask_app = Flask(__name__)  # Flask Application
flask_app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://admin:WKLpwoDJd03DJ423DJwlDJlaDJsdDJsdDJlDJsa@postgresdb:5432/cortex"
flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# Create RestPlus API
api = Api(
    flask_app,
    version="0.1.2",
    title="AutonomousHegician",
    default="default",
    default_label="default",
    description="Api for interacting with the Agent",
)

db = SQLAlchemy()
cors = CORS(flask_app)


# note we need to import from this specific db instance for the api to generate the swagger documents
class ExecutionStrategy(db.Model):  # type: ignore

    __tablename__ = "ExecutionStrategies"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))


class Option(db.Model):  # type: ignore
    is_submitted_for_estimate = False
    is_estimated = False
    is_submitted_for_deployment = False
    is_deployed = False
    is_execerised = False

    __tablename__ = "Options"

    id = db.Column(db.BigInteger(), primary_key=True)
    ledger_id = db.Column(db.BigInteger())
    tx_hash = db.Column(db.String)
    market = db.Column(db.String(255))
    period = db.Column(db.BigInteger())
    amount = db.Column(db.BigInteger())
    strike_price = db.Column(db.BigInteger())
    fees = db.Column(db.String(255))
    option_type = db.Column(db.Integer)
    breakeven = db.Column(db.Integer)
    status_code_id = db.Column(db.ForeignKey("StatusCodes.id"))
    execution_strategy_id = db.Column(db.ForeignKey("ExecutionStrategies.id"))
    date_created = db.Column(db.DateTime(timezone=True))
    date_modified = db.Column(db.DateTime(timezone=True))
    expiration_date = db.Column(db.DateTime(timezone=True))

    execution_strategy = db.relationship(
        "ExecutionStrategy",
        primaryjoin="Option.execution_strategy_id == ExecutionStrategy.id",
        backref="options",
        lazy="subquery",
    )
    status_code = db.relationship(
        "StatusCode",
        primaryjoin="Option.status_code_id == StatusCode.id",
        backref="options",
        lazy="subquery",
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Snapshot(db.Model):  # type: ignore
    __tablename__ = "Snapshot"

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime)
    date_updated = db.Column(db.DateTime)
    usd_val = db.Column(db.Float)
    eth_val = db.Column(db.Float)
    address = db.Column(db.String(255))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class StatusCode(db.Model):  # type: ignore
    __tablename__ = "StatusCodes"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))


db.Index("ix_date_created", func.lower(Snapshot.date_created))
# Bind the SQLAlchemy to the Flask Application
db.init_app(flask_app)
api_model_factory = ApiModelFactory(api=api, db=db)
option_model = api_model_factory.get_entity(Option.__tablename__)
snapshot_model = api_model_factory.get_entity(Snapshot.__tablename__)


@api.route("/get_all_options")
class HegicOptions(Resource):
    def get(self):
        db.create_all()
        ret = []

        def aggregate(row, ret):
            ret = row.as_dict()
            ret["status_code_id"] = row.status_code.description
            ret["option_type"] = "Put" if row.option_type == 1 else "Call"
            return ret

        results = [
            aggregate(f, ret)
            for f in db.session.query(Option)
            .options(subqueryload(Option.status_code))
            .limit(2000)
            .all()
        ]
        for res in results:
            for k, v in res.items():
                if k.find("date") >= 0:
                    res[k] = str(v)
        return results


@api.route("/get_all_agents")
class HegicAgents(Resource):
    def get(self):
        db.create_all()
        results = [
            f.as_dict()
            for f in [
                db.session.query(Snapshot)
                .order_by(Snapshot.date_created.desc())
                .limit(1)
                .one()
            ]
        ]
        for res in results:
            if res["date_updated"] + timedelta(seconds=30) > datetime.utcnow():
                res["status"] = "running"
            else:
                res["status"] = "paused"
            for k, v in res.items():
                if k.find("date") >= 0:
                    res[k] = str(v)
        return results


@api.route("/get_snapshots")
class SnapShots(Resource):
    def get(self):
        db.create_all()
        results = [f.as_dict() for f in db.session.query(Snapshot).limit(2000).all()]
        for res in results:
            for k, v in res.items():
                if k.find("date") >= 0:
                    res[k] = str(v)
        return results


@api.route("/create_new_option")
class HegicOption(Resource):
    @api.expect(option_model, validate=False)
    def post(self):
        db.create_all()
        res = json.loads(request.data)["data"]
        option = Option(
            period=res["period"] * 3600 * 24,
            status_code_id=0,
            market=res["market"],
            execution_strategy_id=res["execution_strategy_id"],
            option_type=res["option_type"],
            amount=res["amount"],
            strike_price=res["strike_price"],
            date_created=datetime.utcnow(),
            date_modified=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=res["period"]),
        )
        db.session.add(option)
        db.session.commit()
        return 200


def run_server(**kwargs):
    flask_app.run(debug=False, host="0.0.0.0", port=8080, **kwargs)


if __name__ == "__main__":
    flask_app.run(debug=False, host="0.0.0.0", port=8080)
