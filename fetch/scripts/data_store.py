#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Tom Rae
Authorised use only
"""
import web3
from datetime import datetime, timedelta
import logging
import os.path
import json
import sqlite3
import time
from typing import Dict, Union
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sys, os

sys.path += [os.path.sep.join(os.getcwd().split(os.path.sep)[:-1])]

from AutonomousHegician.skills.option_management.web_server import (
    Option,
    Snapshot,
    StatusCode,
    ExecutionStrategy,
    db,
    flask_app
)

import os

logging.basicConfig()
logger = logging.getLogger(
    "hegic_option_datastore")


class DataStore():
    """An object allowing wrapping of persistent memory"""

    def add_data(self,):
        """Create the initial state for the agent"""
        with flask_app.app_context():
            db.create_all()
            db.session.merge(ExecutionStrategy(
                id=0, description="auto_itm_execution"))
            db.session.merge(StatusCode(id=0, description="options_estimate"))
            db.session.merge(StatusCode(id=1, description="pending_placement"))
            db.session.merge(StatusCode(id=2, description="placing"))
            db.session.merge(StatusCode(id=3, description="open"))
            db.session.merge(StatusCode(id=4, description="closed"))
            db.session.merge(StatusCode(id=5, description="failed"))
            db.session.query(Option).delete()
            db.session.commit()
            db.session.close()
        logger.info("Added start up data to the database")

    def get_orders(self):
        with flask_app.app_context():
            #            db = self._get_session()
            db.create_all()
            results = db.session.query(Option).all()
            db.session.close()
        return results


if __name__ == '__main__':
    ds = DataStore()
    ds.add_data()
