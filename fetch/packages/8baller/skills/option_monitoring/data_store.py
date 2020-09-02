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
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from web_server import (
    Option,
    Snapshot,
    StatusCode,
    ExecutionStrategy,
    db,
    flask_app
)
logging.basicConfig()

logger = logging.getLogger(
    "aea.packages.fetchai.skills.hegic_helper.hegic_option_data")


class DataStore():
    """An object allowing wrapping of persistent memory"""
    def add_data(self,):
        """Create the initial state for the agent"""
        with flask_app.app_context():
            db.create_all()
            db.session.merge(ExecutionStrategy(id=1, description="auto_itm_execution"))
            db.session.merge(StatusCode(id=0, description="options_estimate"))
            db.session.merge(StatusCode(id=1, description="pending_placement"))
            db.session.merge(StatusCode(id=2, description="placing"))
            db.session.merge(StatusCode(id=3, description="open"))
            db.session.merge(StatusCode(id=4, description="closed"))
            db.session.merge(StatusCode(id=5, description="failed"))
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
