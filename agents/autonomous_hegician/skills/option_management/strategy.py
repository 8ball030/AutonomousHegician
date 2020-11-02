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

"""This module contains the strategy class."""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Union

from aea.configurations.constants import DEFAULT_LEDGER
from aea.helpers.transaction.base import Terms
from aea.skills.base import Model

from packages.eightballer.skills.option_management.db_communication import (
    DBCommunication,
)
from packages.eightballer.skills.option_management.web_server import Option


DEFAULT_LEDGER_ID = "ethereum" 
DEFAULT_TIME_BEFORE_EXECUTION = 600


class Strategy(Model):
    """This class defines a strategy for the agent."""

    def __init__(self, **kwargs) -> None:
        """Initialize the strategy of the agent."""
        self._ledger_id = kwargs.pop("ledger_id", DEFAULT_LEDGER_ID)
        self._deployment_status: Dict[
            str, Union[Tuple[Optional[str], Optional[str]], str]
        ] = {}
        not_deployed = 0
        for contract in [
            "wbtc",
            "hegic",
            "priceprovider",
            "btcpriceprovider",
            "ethoptions",
            "btcoptions",
            "exchange",
            "stakingwbtc",
            "stakingeth",
            "liquidity",
            "ethpool",
            "btcpool",
            "ethoptions_estimate",
            "ethoptions_create_option",
            "ethoptions_exercise",
            "btcoptions_estimate",
            "btcoptions_create_option",
            "btcoptions_exercise",
        ]:  # post test remove
            param = kwargs.pop(contract, None)
            if param == "" or param is None:
                not_deployed += 1
                self._deployment_status[contract] = (None, None)
            else:
                self._deployment_status[contract] = ("deployed", param)
            self._database = DBCommunication()

        if not_deployed >= 0:
            self._deployment_status["status"] = "pending"
        self._current_order = None
        self.eth_balance = None
        super().__init__(**kwargs)
        self.context.logger.info(f"Deployment paramets {self.deployment_status}")

    @property
    def current_order(self) -> None:
        """Get current order being interacted with"""
        return self._current_order

    @current_order.setter
    def current_order(self, order) -> None:
        """Set current order being interacted with"""
        self._current_order = order

    def gather_pending_orders(self) -> List[Option]:
        """Here we retrieve all non-executed contracts."""
        return self._database.get_options()

    def get_contracts_to_execute(self) -> list:
        orders = [f for f in self.gather_pending_orders() if f.status_code_id == 3]
        results = []
        #  self.context.logger.info(
        #      f"Monitoring {len(orders)} orders for execution.")
        for order in orders:
            if self.check_contract_should_execute(order):
                results.append(order)
        return results

    def check_contract_should_execute(self, contract: Option) -> bool:
        """Check if the contract is in the money, and that the expiration date is near"""
        deadline = contract.expiration_date - timedelta(
            seconds=DEFAULT_TIME_BEFORE_EXECUTION
        )

        if contract.status_code_id == 3 and datetime.now(deadline.tzinfo) > deadline:
            price = self.context.behaviours.price_ticker.current_price[contract.market]
            if any(
                [
                    (
                        contract.option_type == 1  # put option
                        and contract.strike_price > price
                    ),
                    (
                        contract.option_type == 2  # call option
                        and contract.strike_price < price
                    ),
                ]
            ):
                self.context.logger.info(f"Order is ready to execute!")
                return True
        return False

    def create_new_option(self, params):
        return self._database.create_new_option(**params)

    def create_new_snapshot(self, params):
        return self._database.create_new_snapshot(params)

    def get_order(self, option_id):
        return self._database.get_option(option_id)

    def update_current_order(self, option, params):
        self.context.logger.info(f"Updating order {option.id} with {params}")
        return self._database.update_option(option.id, params)

    def retrieve_orders(self, status_code) -> list:
        if status_code == 3:
            return self.get_contracts_to_execute()
        elif status_code == 1 or status_code == 0:
            return [
                f
                for f in self.gather_pending_orders()
                if f.status_code_id == status_code
            ]
        else:
            raise ValueError(f"Invalid status code {status_code}")

    @property
    def deployment_status(self) -> dict:
        """Return the deployment status."""
        return self._deployment_status

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
