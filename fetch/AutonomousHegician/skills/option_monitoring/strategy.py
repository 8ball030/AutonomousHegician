# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2020 Fetch.AI Limited
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

"""This module contains the strategy class."""

import random  # nosec
from typing import List
from datetime import datetime, timedelta

from aea.configurations.constants import DEFAULT_LEDGER
from aea.helpers.search.generic import (
    AGENT_LOCATION_MODEL,
    AGENT_REMOVE_SERVICE_MODEL,
    AGENT_SET_SERVICE_MODEL,
    SIMPLE_SERVICE_MODEL,
)
from aea.helpers.search.models import Description, Location
from aea.helpers.transaction.base import Terms
from aea.skills.base import Model

from packages.fetchai.contracts.erc1155.contract import ERC1155Contract

from packages.tomrae.skills.option_monitoring.db_communication import DBCommunication

DEFAULT_LEDGER_ID = DEFAULT_LEDGER
DEFAULT_TIME_BEFORE_EXECUTION = 300



class OptionContract:
    is_submitted_for_estimate = False
    is_estimated = False
    is_submitted_for_deployment = False
    is_deployed = False
    is_execerised = False
    
    
    
class OptionContractManager:
    """Class to help manage the deployment of options contracts."""
    contracts = []
    
    
    
    
    

    

class Strategy(Model):
    """This class defines a strategy for the agent."""

    def gather_pending_orders(self) -> list:
        """Here we retrieve all non-executed contracts."""
        return self._database.get_orders()

    def get_contracts_to_execute(self) -> list:
        orders = self.gather_pending_orders()
        results = []
        self.context.logger.info(
            f"Monitoring {len(orders)} orders for execution.")
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

        price = self.context.behaviours.price_ticker.current_price

        if contract["status"] == "pending" and datetime.now() > deadline:
            if any([(contract["type_of_option"] == "put"
                     and contract["strike_price"] > price),
                    (contract["type_of_option"] == "call"
                     and contract["strike_price"] < price)]):
                self.context.logger.info(f"Order is ready to execute!")
                return True
        return False

    def retrieve_actions(self) -> list:
        self.get_contracts_to_execute()
        return []

    def __init__(self, **kwargs) -> None:
        """Initialize the strategy of the agent."""
        self._option_contract_manager = OptionContractManager()
        self._database = DBCommunication()
        self._ledger_id = kwargs.pop("ledger_id", DEFAULT_LEDGER_ID)

        self.deployment_status = {
        }
        not_deployed = 0
        for contract in ["stablecoin", "pricefeed",
                         "exchange",
                         "calloptions",
                         "putoptions",
                         "ercpool",
                         "ethpool",
                         "liquidity",
                         "options_estimate",
                         "options_create",
                         "options_excercise"]: # post test remove
            param = kwargs.pop(contract, None)
            if param is "" or param is None:
                not_deployed += 1
                self.deployment_status[contract] = (None, None)
            else:
                self.deployment_status[contract] = ("deployed", param)

        if not_deployed >= 0:
            self.deployment_status["status"] = "pending"
        super().__init__(**kwargs)


    @property
    def ledger_id(self) -> str:
        """Get the ledger id."""
        return self._ledger_id


    def get_deploy_terms(self) -> Terms:
        """
        Get deploy terms of deployment.

        :return: terms
        """
        terms = Terms(
            ledger_id=self.ledger_id,
            sender_address=self.context.agent_address,
            counterparty_address=self.context.agent_address,
            amount_by_currency_id={},
            quantities_by_good_id={},
            nonce="",
        )
        return terms

    def get_create_token_terms(self) -> Terms:
         """
         Get create token terms of deployment.

         :return: terms
         """
         terms = Terms(
             ledger_id=self.ledger_id,
             sender_address=self.context.agent_address,
             counterparty_address=self.context.agent_address,
             amount_by_currency_id={},
             quantities_by_good_id={},
             nonce="",
         )
         return terms
