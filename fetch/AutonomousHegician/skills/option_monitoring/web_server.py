from datetime import datetime, timedelta
from sqlalchemy import BigInteger, Column, Integer, String, DateTime, Date
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request
from flask_cors import CORS
from flask_restplus import Api, Resource
import os
import json
from flask_restplus_sqlalchemy import ApiModelFactory
import logging
logger = logging.getLogger(__name__)
from web3 import Web3


flask_app = Flask(__name__)  # Flask Application
flask_app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://admin:WKLpwoDJd03DJ423DJwlDJlaDJsdDJsdDJlDJsa@postgresdb:5432/cortex"
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# Create RestPlus API
api = Api(flask_app,
          version='0.1.2',
          title='AutonomousHegician',
          default='default',
          default_label='default',
          description='Api for interacting with the Agent')

db = SQLAlchemy()
cors = CORS(flask_app)


# note we need to import from this specific db instance for the api to generate the swagger documents
class ExecutionStrategy(db.Model):

    __tablename__ = 'ExecutionStrategies'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))


class Option(db.Model):
    is_submitted_for_estimate = False
    is_estimated = False
    is_submitted_for_deployment = False
    is_deployed = False
    is_execerised = False

    __tablename__ = 'Options'

    id = db.Column(db.BigInteger(), primary_key=True)
    ledger_id = db.Column(db.BigInteger())
    period = db.Column(db.BigInteger())
    amount = db.Column(db.BigInteger())
    strike_price = db.Column(db.BigInteger())
    fees = db.Column(db.String(255))
    option_type = db.Column(db.Integer())
    status_code_id = db.Column(db.ForeignKey('StatusCodes.id'))
    execution_strategy_id = db.Column(db.ForeignKey('ExecutionStrategies.id'))
    date_created = db.Column(db.DateTime)
    date_modified = db.Column(db.DateTime)
    expiration_date = db.Column(db.DateTime)
    market = db.Column(db.String(255))

    execution_strategy = db.relationship(
        'ExecutionStrategy', primaryjoin='Option.execution_strategy_id == ExecutionStrategy.id', backref='options', lazy='joined')
    status_code = db.relationship(
        'StatusCode', primaryjoin='Option.status_code_id == StatusCode.id', backref='options', lazy='joined')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Snapshot(db.Model):
    __tablename__ = 'Snapshot'

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime)
    usd_val = db.Column(db.Float)
    eth_val = db.Column(db.Float)
    address = db.Column(db.String(255))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class StatusCode(db.Model):
    __tablename__ = 'StatusCodes'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))


# Bind the SQLAlchemy to the Flask Application
db.init_app(flask_app)
api_model_factory = ApiModelFactory(api=api, db=db)
option_model = api_model_factory.get_entity(Option.__tablename__)
snapshot_model = api_model_factory.get_entity(Option.__tablename__)


@api.route('/get_all_options')
class HegicOptions(Resource):
    def get(self):
        db.create_all()
        results = [f.as_dict() for f in db.session.query(Option).all()]
        for res in results:
            for k, v in res.items():
                if k.find('date') >= 0:
                    res[k] = str(v)
        return results

@api.route('/get_snapshots')
class SnapShots(Resource):
    def get(self):
        db.create_all()
        results = [f.as_dict() for f in db.session.query(Snapshot).all()]
        for res in results:
            for k, v in res.items():
                if k.find('date') >= 0:
                    res[k] = str(v)
        return results

@api.route('/create_new_option')
class HegicOption(Resource):
    @api.expect(option_model, validate=False)
    def post(self):
        db.create_all()
        res = json.loads(request.data)['data']
        option = Option(period=res['period'] * 3600 * 24,
               status_code_id=0,
               execution_strategy_id=0,
               option_type=res['type_of_option'],
               amount=Web3.toWei(res['amount'], "ether"),
               strike_price=res['strike_price'],
               date_created=datetime.now(),
               date_modified=datetime.now(),
               expiration_date=datetime.now() + timedelta(days=res['period']),
               )
        db.session.add(option)
        db.session.commit()
        return 200


def run_server(**kwargs):
    flask_app.run(debug=False, host="0.0.0.0", port=8080, **kwargs)


if __name__ == '__main__':
    flask_app.run(debug=True, host="0.0.0.0", port=8080)
