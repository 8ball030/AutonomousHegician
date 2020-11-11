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
import os
from datetime import datetime, timedelta

import yaml
from flask import Flask, request
from flask_cors import CORS
from flask_restplus import Api, Resource
from flask_restplus_sqlalchemy import ApiModelFactory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import subqueryload
from web3 import HTTPProvider, Web3


logger = logging.getLogger(__name__)


def _create_url():

    for required in ["DB_URL", "DB_PORT", "DB_USER", "DB_PASS"]:
        if os.environ.get(required, None) is None:
            raise ValueError("DB_URL is required check environ vars")
    un = os.environ.get("DB_USER")
    pw = os.environ.get("DB_PASS")
    url = os.environ.get("DB_URL")
    port = os.environ.get("DB_PORT")
    uri_string = f"postgresql://{un}:{pw}@{url}:{port}/cortex"
    return uri_string


flask_app = Flask(__name__)  # Flask Application
flask_app.config["SQLALCHEMY_DATABASE_URI"] = _create_url()
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
    amount = db.Column(db.Numeric())
    strike_price = db.Column(db.BigInteger())
    fees = db.Column(db.String(255))
    option_type = db.Column(db.Integer)
    status_code_id = db.Column(db.ForeignKey("StatusCodes.id"))
    execution_strategy_id = db.Column(db.ForeignKey("ExecutionStrategies.id"))
    date_created = db.Column(db.DateTime(timezone=True))
    date_modified = db.Column(db.DateTime(timezone=True))
    expiration_date = db.Column(db.DateTime(timezone=True))
    breakeven = db.Column(db.BigInteger(), default=0)
    current_pnl = db.Column(db.BigInteger(), default=0)
    agent_id = db.Column(db.ForeignKey("Agents.id"))

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

    def update_with_fees(self, current_price):
        pnl = 0
        cost = int(self.fees.strip("}{").split(",")[0])
        cost_per_unit = int(int(cost) / self.amount)
        if self.option_type == 1:
            self.breakeven = self.strike_price - cost_per_unit
        else:
            self.breakeven = self.strike_price + cost_per_unit
        dif = current_price - self.breakeven
        if self.option_type == 1 and dif < 0:
            pnl = -dif * self.amount
        elif self.option_type == 2 and dif > 1:
            pnl = dif * self.amount
        self.current_pnl = pnl / cost * 100


class Snapshot(db.Model):  # type: ignore
    __tablename__ = "Snapshot"

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime)
    date_updated = db.Column(db.DateTime)
    usd_val = db.Column(db.Float)
    eth_val = db.Column(db.Float)
    agent_id = db.Column(db.ForeignKey("Agents.id"))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Agent(db.Model):  # type: ignore
    __tablename__ = "Agents"

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime)
    date_updated = db.Column(db.DateTime)
    address = db.Column(db.String(255))
    status = db.Column(db.String(255))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class StatusCode(db.Model):  # type: ignore
    __tablename__ = "StatusCodes"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))


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
            ret["amount"] = int(Web3.fromWei(row.amount, "ether"))
            ret["breakeven"] = (
                int(Web3.fromWei(row.breakeven, "ether")) if row.breakeven != 0 else 0
            )
            ret["current_pnl"] = (
                int(Web3.fromWei(row.current_pnl, "ether"))
                if row.current_pnl != 0
                else 0
            )
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
        results = []
        for res in [i.as_dict() for i in db.session.query(Agent).all()]:
            for k, v in res.items():
                if k.find("date") >= 0:
                    res[k] = str(v)
            results.append(res)
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
            period=res["period"],
            status_code_id=0,
            market=res["market"],
            execution_strategy_id=res["execution_strategy_id"],
            option_type=res["option_type"],
            amount=res["amount"],  # TODO BTC is wrong!
            strike_price=res["strike_price"],
            date_created=datetime.utcnow(),
            date_modified=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=res["period"]),
        )
        db.session.add(option)
        db.session.commit()
        return option.id


@api.route("/get_web3_config")
class web3_config(Resource):
    def _load_contracts(self):
        """Read in the contracts from the agent."""
        w3 = Web3(HTTPProvider(os.environ.get("LEDGER")))
        if not w3.isConnected():
            raise ValueError("Not successfully conencted to the chain!")

        addresses = self._read_addresses()
        mapping = {
            "priceprovider": "FakePriceProvider.json",
            "ethoptions": "HegicETHOptions.json",
            "ethpool": "HegicETHPool.json",
            "ethpriceprovider": "FakeETHPriceProvider.json",
            "btcoptions": "HegicWBTCOptions.json",
            "btcpool": "HegicERCPool.json",
            "btcpriceprovider": "FakeBTCPriceProvider.json",
            "exchange": "FakeExchange.json",
            "hegic": "FakeHEGIC.json",
            "wbtc": "FakeWBTC.json",
            "stakingeth": "HegicStakingETH.json",
            "stakingwbtc": "HegicStakingWBTC.json",
        }
        contracts = {}
        for contract, _address in addresses.items():
            with open(
                f"./hegic_deployer/contracts/{contract}/build/contracts/{mapping[contract]}",
                "r",
            ) as f:
                c = json.loads(f.read())
                contracts[contract] = c
        return contracts

    def _read_addresses(self):
        with open(
            "./autonomous_hegician/skills/option_management/skill.yaml", "r"
        ) as f:
            return {
                k: v
                for k, v in yaml.safe_load(f)["models"]["strategy"]["args"].items()
                if k != "ledger_id"
            }

    def get(self):
        object = {
            "ledger_string": os.environ["LEDGER"],
            "contract_addresses": self._read_addresses(),
            "contract_abis": self._load_contracts(),
        }

        return object


if __name__ == "__main__":
    flask_app.run(debug=False, host="0.0.0.0", port=8080)
