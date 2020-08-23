#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Tom Rae
Authorised use only
"""
import logging
from datetime import datetime, timedelta

import os

from packages.tomrae.skills.auto_itm_closure.dex_wrapper import DexWrapper
from packages.tomrae.skills.auto_itm_closure.db_communication import DBCommunication


from aea.configurations.constants import DEFAULT_LEDGER
from aea.skills.base import Model


logger = logging.getLogger(
    "aea.packages.fetchai.skills.auto_itm_closure.behaviour")

logger.setLevel(logging.INFO)

DEFAULT_TIME_BEFORE_EXECUTION = 300  # seconds 5 mins to give txs a chance to be processed


class Strategy(Model):
    """Main strategy class for the AutoExecution."""
    @property
    def ledger_id(self) -> str:
        """Get the ledger id."""
        return self._ledger_id


    def __init__(self, *args, **kwargs) -> None:
        """Initialise the Strategy."""
        self.database = DBCommunication()
        self.dex = DexWrapper()
        self.current_rate = self.dex.get_ticker("DAI", "ETH")
        self._ledger_id = kwargs.pop("ledger_id", DEFAULT_LEDGER)
        logger.info("Strategy Initialised")
        super().__init__(**kwargs)

    def gather_pending_orders(self) -> list:
        """Here we retrieve all non-executed contracts."""
        return self.database.get_orders()

    def set_current_price(self) -> None:
        """Retrieve the current Eth dai price from the Dex."""
        self.current_rate = self.dex.get_ticker("DAI", "ETH")
        logger.info(f"Current Rate : {round(self.current_rate, 2)}")

    def get_contracts_to_execute(self) -> list:
        orders = self.gather_pending_orders()
        results = []
        logger.info(f"Monitoring {len(orders)} orders for execution.")
        for order in orders:
            if self.check_contract_should_execute(order):
                results.append(order)
        return results

    def check_contract_should_execute(self, contract: dict) -> bool:
        """Check if the contract is in the money, 
           and that the expiration date is near
        """
        deadline = datetime.fromisoformat(
            contract["expiration_date"]) - timedelta(
                seconds=DEFAULT_TIME_BEFORE_EXECUTION)
        if contract["status"] == "pending" and datetime.now() > deadline:
            if any([(contract["type_of_option"] == "put"
                     and contract["strike_price"] > self.current_rate),
                    (contract["type_of_option"] == "call"
                     and contract["strike_price"] < self.current_rate)]):
                logger.info(f"Order is ready to execute!")
                return True
        return False

    def retrieve_actions(self) -> list:
        self.set_current_price()
        self.get_contracts_to_execute()
        return []


def main():
    """Run the main method."""
    pass


if __name__ == "__main__":
    main()
