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

"""This package contains the behaviour of a erc1155 deploy skill AEA."""

import time
from datetime import datetime
from typing import Dict, cast

import web3

from aea.skills.behaviours import TickerBehaviour

from packages.eightballer.skills.option_management.dex_wrapper import DexWrapper
from packages.eightballer.skills.option_management.dialogues import (
    ContractApiDialogue,
    ContractApiDialogues,
    LedgerApiDialogues,
)
from packages.eightballer.skills.option_management.strategy import Strategy
from packages.fetchai.protocols.contract_api.message import ContractApiMessage
from packages.fetchai.protocols.ledger_api.message import LedgerApiMessage


DEFAULT_SERVICES_INTERVAL = 30.0
LEDGER_API_ADDRESS = "fetchai/ledger:0.8.0"


def toBTC(x):
    return int(web3.Web3.toWei(x, "ether") / 1e10)


class SnapShot(TickerBehaviour):
    """This class monitors the balance of agent and takes snapshots to the db."""

    def act(self) -> None:
        strategy = cast(Strategy, self.context.strategy)
        if strategy.eth_balance is None:
            return
        self._request_balance()
        eth_val = web3.Web3.fromWei(strategy.eth_balance, "ether")
        snapshot_params = dict(
            eth_val=eth_val,
            usd_val=float(eth_val)
            * float(self.context.behaviours.price_ticker.current_price["ETH"]),
            date_created=datetime.now(),
            date_updated=datetime.now(),
            address=self.context.agent_address,
        )
        strategy.create_new_snapshot(snapshot_params)

    def __init__(self, **kwargs):
        """Initialise the behaviour."""
        services_interval = kwargs.pop(
            "services_interval", DEFAULT_SERVICES_INTERVAL
        )  # type: int
        super().__init__(tick_interval=services_interval, **kwargs)

    def setup(self) -> None:
        """Setup the agent."""
        self._request_balance()

    def _request_balance(self) -> None:
        """
        Request ledger balance.

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        ledger_api_dialogues = cast(
            LedgerApiDialogues, self.context.ledger_api_dialogues
        )
        ledger_api_msg, _ = ledger_api_dialogues.create(
            counterparty=LEDGER_API_ADDRESS,
            performative=LedgerApiMessage.Performative.GET_BALANCE,
            ledger_id=strategy.ledger_id,
            address=cast(str, self.context.agent_addresses.get(strategy.ledger_id)),
        )
        self.context.outbox.put_message(message=ledger_api_msg)


class PriceTicker(TickerBehaviour):
    """This class monitors the price"""

    @property
    def current_price(self) -> Dict:
        """Get the last recorded price from Uniswap."""
        return self._current_price

    def __init__(self, **kwargs):
        """Initialise the behaviour."""
        services_interval = kwargs.pop(
            "services_interval", DEFAULT_SERVICES_INTERVAL
        )  # type: int
        super().__init__(tick_interval=services_interval, **kwargs)

    def setup(self) -> None:
        """
        Implement the setup.
        :return: None
        """
        self.dex = DexWrapper()
        self._set_current_price()

    def _set_current_price(self) -> None:
        """Retrieve the current Eth dai price from the Dex."""
        try:
            prices = {k: 100 for k in ["ETH", "WBTC"]}  # self.dex.get_ticker("DAI", k)
            self._current_price = prices
        except Exception as e:
            self.context.logger.info(f"Error getting price!\n{e}")
            time.sleep(15)

    def act(self) -> None:
        """
        Implement the act.

        :return: None
        """
        self._set_current_price()


class OptionMonitor(TickerBehaviour):
    """This class scaffolds a behaviour."""

    def __init__(self, **kwargs):
        """Initialise the behaviour."""
        services_interval = kwargs.pop(
            "services_interval", DEFAULT_SERVICES_INTERVAL
        )  # type: int
        super().__init__(tick_interval=services_interval, **kwargs)
        self.is_service_registered = False

    def setup(self) -> None:
        """Setup the agent."""
        pass

    def act(self) -> None:
        """
        Implement the act.

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        if strategy.deployment_status["status"][0] == "deploying":
            return

        orders_to_estimate = strategy.retrieve_orders(status_code=0)
        orders_to_create = strategy.retrieve_orders(status_code=1)
        orders_to_execise = strategy.retrieve_orders(status_code=3)

        for order_batch in [orders_to_create, orders_to_estimate, orders_to_execise]:
            if len(order_batch) == 0:
                continue
            self.context.logger.info(f"Orders to action! : {len(order_batch)}")

        for order in orders_to_execise:
            self._request_contract_interaction(
                order.market.lower() + "options",
                "exercise",
                {"option_id": order.ledger_id},
            )
            strategy.current_order = order
            return
        for order in orders_to_create:
            self._request_contract_interaction(
                order.market.lower() + "options",
                "create_option",
                {
                    "period": order.period,
                    "amount": order.amount,
                    "strike": order.strike_price,
                    "type": order.option_type,
                },
            )
            # now we mark as pending placement while we submit
            strategy.current_order = order
            strategy.update_current_order(order, {"status_code_id": 2})
            return

        for order in orders_to_estimate:
            self._request_contract_state(
                contract_name=f"{order.market.lower()}options",
                callable="estimate",
                parameters={
                    "amount": order.amount,
                    "period": order.period,
                    "strike": order.strike_price,
                    "type": order.option_type,
                },
            )
            strategy.current_order = order
            return

    def _request_contract_interaction(
        self, contract_name: str, callable: str, parameters: dict
    ) -> None:
        """
        Request contract interaction

        :return: None
        """
        params = {"deployer_address": self.context.agent_address}
        params.update(parameters)
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(
            ContractApiDialogues, self.context.contract_api_dialogues
        )
        contract_api_msg, contract_api_dialogue = contract_api_dialogues.create(
            counterparty=LEDGER_API_ADDRESS,
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
            ledger_id=strategy.ledger_id,
            contract_id=f"eightballer/{contract_name}:0.1.0",
            contract_address=strategy.deployment_status[contract_name][1],
            callable=callable,
            kwargs=ContractApiMessage.Kwargs(params),
        )
        contract_api_dialogue = cast(ContractApiDialogue, contract_api_dialogue,)
        contract_api_dialogue.terms = strategy.get_deploy_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        strategy.deployment_status[f"{contract_name}_{callable}"] = (
            "pending",
            contract_api_dialogue.dialogue_label.dialogue_reference[0],
        )
        strategy.deployment_status["status"] = ["deploying", contract_name]
        self.context.logger.info(
            f"**** requesting contract {contract_name} {callable} state transaction..."
        )

    def _request_contract_state(
        self, contract_name: str, callable: str, parameters: dict
    ) -> None:
        """
        Request contract deploy transaction

        :return: None
        """
        params = {"deployer_address": self.context.agent_address}
        params.update(parameters)
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(
            ContractApiDialogues, self.context.contract_api_dialogues
        )
        contract_api_msg, contract_api_dialogue = contract_api_dialogues.create(
            counterparty=LEDGER_API_ADDRESS,
            performative=ContractApiMessage.Performative.GET_STATE,
            ledger_id=strategy.ledger_id,
            contract_id=f"eightballer/{contract_name}:0.1.0",
            contract_address=strategy.deployment_status[contract_name][1],
            callable=callable,
            kwargs=ContractApiMessage.Kwargs(params),
        )
        contract_api_dialogue = cast(ContractApiDialogue, contract_api_dialogue,)
        contract_api_dialogue.terms = strategy.get_deploy_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        strategy.deployment_status[f"{contract_name}_{callable}"] = (
            "pending",
            contract_api_dialogue.dialogue_label.dialogue_reference[0],
        )
        strategy.deployment_status["status"] = ["deploying", contract_name]
        self.context.logger.info(
            f"requesting contract {contract_name} state transaction..."
        )
