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

"""This package contains the behaviour of a erc1155 deploy skill AEA."""

import time
from datetime import datetime
from typing import Any, Dict, Optional, cast

import web3

from aea.skills.behaviours import TickerBehaviour

from packages.eightballer.skills.option_management.dex_wrapper import DexWrapper
from packages.eightballer.skills.option_management.dialogues import (
    ContractApiDialogue,
    ContractApiDialogues,
    LedgerApiDialogues,
    OefSearchDialogues,
)
from packages.eightballer.skills.option_management.strategy import Strategy
from packages.fetchai.protocols.contract_api.message import ContractApiMessage
from packages.fetchai.protocols.ledger_api.message import LedgerApiMessage
from packages.fetchai.protocols.oef_search.message import OefSearchMessage


DEFAULT_SERVICES_INTERVAL = 30.0
LEDGER_API_ADDRESS = "fetchai/ledger:0.8.0"


def toBTC(x):
    return int(web3.Web3.toWei(x, "ether") / 1e10)


class SnapShot(TickerBehaviour):
    """This class monitors the balance of agent and takes snapshots to the db."""

    def act(self) -> None:
        if self.context.strategy.eth_balance is None:
            return
        self._request_balance()
        eth_val = web3.Web3.fromWei(self.context.strategy.eth_balance, "ether")
        snapshot_params = dict(
            eth_val=eth_val,
            usd_val=float(eth_val)
            * float(self.context.behaviours.price_ticker.current_price["ETH"]),
            date_created=datetime.now(),
            date_updated=datetime.now(),
            address=self.context.agent_address,
        )
        self.context.strategy.create_new_snapshot(snapshot_params)

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


#        self.context.logger.info(f"Rate : {round(self.current_price, 2)}")


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
                {"option_id": order.ledger_id,},
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


# class ServiceRegistrationBehaviour(TickerBehaviour):
#     """This class implements a behaviour."""
#     params = {
#         "ETHPrice": 380*10**8,
#         "BTCPrice": 1161000000000,
#         "ETHtoBTC": 200,
#         "OptionType": {"Put": 1, "Call": 2}
#     }
#     provided_eth = False
#     tested_eth = False
#     tested_btc = False
#     provided_btc = False
#     btc_minted = False
#     btc_approved = False
#     run_contract_tests = False
#     monitoring = False
#
#     def __init__(self, **kwargs):
#         """Initialise the behaviour."""
#         services_interval = kwargs.pop(
#             "services_interval", DEFAULT_SERVICES_INTERVAL
#         )  # type: int
#         super().__init__(tick_interval=services_interval, **kwargs)
#         self.is_service_registered = False
#
#     def setup(self) -> None:
#         """
#         Implement the setup.
#
#         :return: None
#         """
#         self._request_balance()
#         strategy = cast(Strategy, self.context.strategy)
#
#     def act(self) -> None:
#         """
#         Implement the act.
#
#         :return: None
#         """
#         strategy = cast(Strategy, self.context.strategy)
#         if self.context.strategy.deployment_status["status"] in [
#                 "complete", "deploying"
#         ]:
#             return
# #         self.context.logger.info(f"strategy.deployment_status['status']")
#         strategy = cast(Strategy, self.context.strategy)
#
#         if strategy.deployment_status["wbtc"][0] is None:
#             self._request_contract_deploy_transaction("wbtc", {})
#
#         elif strategy.deployment_status["wbtc"][0] == "deployed" and \
#                 strategy.deployment_status["hegic"][0] is None:
#             self._request_contract_deploy_transaction("hegic", {})
#
#         elif strategy.deployment_status["wbtc"][0] == "deployed" and \
#                 strategy.deployment_status["priceprovider"][0] is None:
#             self._request_contract_deploy_transaction(
#                 "priceprovider", {"args": [self.params["ETHPrice"]]}
#             )
#
#         elif strategy.deployment_status["priceprovider"][0] == "deployed" and \
#                 strategy.deployment_status["btcpriceprovider"][0] is None:
#             self._request_contract_deploy_transaction(
#                 "btcpriceprovider", {"args": [self.params["BTCPrice"]]}
#             )
#         elif strategy.deployment_status["btcpriceprovider"][0] == "deployed" and \
#                 strategy.deployment_status["exchange"][0] is None:
#             self._request_contract_deploy_transaction("exchange", {"args": [
#                 strategy.deployment_status["wbtc"][1],
#                 self.params["ETHtoBTC"],
#             ]})
#
#         # we additionally need to deploy the staking contracts
#         elif strategy.deployment_status["exchange"][0] == "deployed" and \
#                 strategy.deployment_status["stakingwbtc"][0] is None:
#             self._request_contract_deploy_transaction("stakingwbtc", {"args": [
#                 strategy.deployment_status["hegic"][1],
#                 strategy.deployment_status["wbtc"][1],
#             ]})
#
#         elif strategy.deployment_status["stakingwbtc"][0] == "deployed" and \
#                 strategy.deployment_status["stakingeth"][0] is None:
#             self._request_contract_deploy_transaction("stakingeth", {"args": [
#                 strategy.deployment_status["hegic"][1],
#             ]})
#
#         elif strategy.deployment_status["exchange"][0] == "deployed" and \
#                 strategy.deployment_status["ethoptions"][0] is None:
#             self._request_contract_deploy_transaction("ethoptions", {"args": [
#                 strategy.deployment_status["priceprovider"][1],
#                 strategy.deployment_status["stakingeth"][1],
#             ]})
#
#         elif strategy.deployment_status["ethoptions"][0] == "deployed" and \
#                 strategy.deployment_status["btcoptions"][0] is None:
#             self._request_contract_deploy_transaction("btcoptions", {"args": [
#                 strategy.deployment_status["btcpriceprovider"][1],
#                 strategy.deployment_status["exchange"][1],
#                 strategy.deployment_status["wbtc"][1],
#                 strategy.deployment_status["stakingwbtc"][1],
#             ]})
#
#         else:
#
#             # we now know that our base contracts are deployed, so we can retrieve state to the params to continue
#
#             if strategy.deployment_status.get("ethoptions_get_pool", None) is None:
#                 self._request_contract_state("ethoptions", "get_pool", {})
#             elif strategy.deployment_status.get("ethpool")[0] is None \
#                     and strategy.deployment_status["ethoptions_get_pool"][0] == "results":
#                 strategy.deployment_status["ethpool"] = [
#                     "deployed", strategy.deployment_status["ethoptions_get_pool"][1]]
#
#             elif strategy.deployment_status.get("btcoptions_get_pool", None) is None and \
#                     strategy.deployment_status.get("ethpool",)[0] is not None:
#                 self._request_contract_state("btcoptions", "get_pool", {})
#             elif strategy.deployment_status.get("btcpool")[0] is None \
#                     and strategy.deployment_status["btcoptions_get_pool"][0] == "results":
#                 strategy.deployment_status["btcpool"] = [
#                     "deployed", strategy.deployment_status["btcoptions_get_pool"][1]]
#
#             elif self.run_contract_tests is False and self.monitoring is False:
#                 # now we provide liquidity to the pool
#                 if self.provided_eth is False:
#                     self._request_contract_interaction("ethpool", "provide_liquidity", {
#                                                        "args": [web3.Web3.toWei(1, "ether")]})
#                     self.provided_eth = True
#
#                 elif self.provided_eth is True and self.btc_minted is False and self.provided_btc is False:
#                     self._request_contract_interaction(
#                         "wbtc", "mint", {"args": [100000000000]})
#                     self.btc_minted = True
#
#                 elif self.btc_minted is True and self.btc_approved is False:
#                     self._request_contract_interaction("wbtc", "approve",
#                                                        {"args": [strategy.deployment_status["btcpool"][1],
#                                                                  100000000000]
#                                                         }
#                                                        )
#                     self.btc_approved = True
#
#                 elif self.provided_eth is True and self.btc_minted is True and self.provided_btc is False:
#                     self._request_contract_interaction("btcpool", "provide_liquidity",
#                                                        {"args": [100000000000, 0]
#                                                         })
#                     self.provided_btc = True
#
#                 elif self.provided_btc is True:
#                     self.run_contract_tests = True
#                     # here we should call the function to generate the new skill for the AH
#                     self.context.logger.info(
#                         f"Deployment complete! {self.context.strategy.deployment_status}")
#                     strategy.create_config_yaml()
#
#             elif self.run_contract_tests is True and self.monitoring is False:
#                 if strategy.deployment_status.get("ethoptions_estimate")[0] is None:
#                     self.context.logger.info(
#                         f"**** Running Test of contract estimate.")
#                     self._request_contract_state("ethoptions", "estimate", {"period": 24 * 3600 * 1,
#                                                                             "amount": web3.Web3.toWei(0.1, "ether"),
#                                                                             "strike": self.params["ETHPrice"],
#                                                                             "type": self.params["OptionType"]["Call"]
#                                                                             },
#                                                  )
#
#                 elif strategy.deployment_status.get("ethoptions_create_option")[0] is None:
#                     self.context.logger.info(
#                         f"**** Running Test of contract create.")
#                     self._request_contract_interaction("ethoptions", "create_option", {"period": 24 * 3600 * 1,
#                                                                                        "amount": web3.Web3.toWei(0.1, "ether"),
#                                                                                        "strike": self.params["ETHPrice"],
#                                                                                        "type": self.params["OptionType"]["Call"]
#                                                                                        },
#                                                        )
#                 elif strategy.deployment_status.get("ethoptions_create_option")[0] == "deployed"\
#                         and strategy.deployment_status.get("ethoptions_estimate")[0] == "results" \
#                         and strategy.deployment_status.get("ethoptions_exercise")[0] is None:
#                     self.context.logger.info(
#                         f"**** Running Test of contract excercise.")
#                     option_id = strategy.deployment_status.get("ethoptions_estimate")[1]['option_id']
#                     self._request_contract_interaction("ethoptions", "exercise", {"option_id": option_id})
#
#                 elif strategy.deployment_status.get("ethoptions_exercise") is not None and not self.tested_eth:
#                     self.context.logger.info(
#                         f"****Functionality Test of eth contracts complete!")
#                     self.tested_eth = True
#
#
#                 # now we test the btc contract.
#
#                 elif strategy.deployment_status.get("btcoptions_estimate")[0] is None:
#                     self.context.logger.info(
#                         f"**** Running Test of contract estimate.")
#                     self._request_contract_state("btcoptions", "estimate", {"period": 24 * 3600 * 1,
#                                                                             "amount": toBTC(0.1),
#                                                                             "strike": self.params["BTCPrice"],
#                                                                             "type": self.params["OptionType"]["Call"]
#                                                                             },
#                                                  )
#
#                 elif strategy.deployment_status.get("btcoptions_create_option")[0] is None:
#                     self.context.logger.info(
#                         f"**** Running Test of contract create.")
#                     self._request_contract_interaction("btcoptions", "create_option", {"period": 24 * 3600 * 1,
#                                                                                        "amount": toBTC((0.1)),
#                                                                                        "strike": self.params["BTCPrice"],
#                                                                                        "type": self.params["OptionType"]["Call"]
#                                                                                        },
#                                                        )
#                 elif strategy.deployment_status.get("btcoptions_create_option")[0] == "deployed"\
#                         and strategy.deployment_status.get("btcoptions_estimate")[0] == "results" \
#                         and strategy.deployment_status.get("btcoptions_exercise")[0] is None:
#                     self.context.logger.info(
#                         f"**** Running Test of contract excercise.")
#                     option_id = strategy.deployment_status.get("btcoptions_estimate")[1]['option_id']
#                     self._request_contract_interaction("btcoptions", "exercise", {"option_id": option_id})
#
#                 elif strategy.deployment_status.get("btcoptions_exercise") is not None:
#                     self.context.logger.info(
#                         f"****Functionality Test of btc contracts complete!")
#
#     def _option_interaction(self, option_type: str, act: str,
#                             params: Dict[str,
#                                          Any]) -> bool:
#         assert option_type in ["btc", "eth"]
#         assert act in [
#             "create_option", "exercise", "estimate"
#         ]
#         strategy = cast(Strategy, self.context.strategy)
#         strategy.deployment_status["status"] = "deploying"
#         strategy.is_behaviour_active = False
#         contract_api_dialogues = cast(ContractApiDialogues,
#                                       self.context.contract_api_dialogues)
#         params.update({"deployer_address": self.context.agent_address})
#         contract_api_msg, contract_api_dialogue = contract_api_dialogues.create(
#             counterparty=LEDGER_API_ADDRESS,
#             performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
#             ledger_id=strategy.ledger_id,
#             contract_id=f"eightballer/{option_type}options:0.1.0",
#             contract_address=strategy.deployment_status[f"{option_type}options"][1],
#             callable=f"{act}",
#             kwargs=ContractApiMessage.Kwargs(params),
#         )
#         self.context.strategy.deployment_status[f"{option_type}options_{act}"] = (
#             "pending", contract_api_dialogue.dialogue_label.dialogue_reference[0])
#         contract_api_dialogue = cast(
#             ContractApiDialogue, contract_api_dialogue,)
#         contract_api_dialogue.terms = strategy.get_deploy_terms()
#         self.context.outbox.put_message(message=contract_api_msg)
#         self.context.logger.info(
#             f"contract deployer requesting {act} {option_type} transaction...")
#
#
#     def _request_contract_interaction(self, contract_name: str, callable: str, parameters: dict) -> None:
#         """
#         Request contract interaction
#
#         :return: None
#         """
#         params = {"deployer_address": self.context.agent_address}
#         params.update(parameters)
#         strategy = cast(Strategy, self.context.strategy)
#         strategy.is_behaviour_active = False
#         contract_api_dialogues = cast(
#             ContractApiDialogues, self.context.contract_api_dialogues
#         )
#         contract_api_msg, contract_api_dialogue = contract_api_dialogues.create(
#             counterparty=LEDGER_API_ADDRESS,
#             performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
#             ledger_id=strategy.ledger_id,
#             contract_id=f"eightballer/{contract_name}:0.1.0",
#             contract_address=strategy.deployment_status[contract_name][1],
#             callable=callable,
#             kwargs=ContractApiMessage.Kwargs(params),
#         )
#         contract_api_dialogue = cast(
#             ContractApiDialogue, contract_api_dialogue,)
#         contract_api_dialogue.terms = strategy.get_deploy_terms()
#         self.context.outbox.put_message(message=contract_api_msg)
#         strategy.deployment_status[f"{contract_name}_{callable}"] = (
#             "pending", contract_api_dialogue.dialogue_label.dialogue_reference[0])
#         strategy.deployment_status["status"] = "deploying"
#         self.context.logger.info(
#             f"**** requesting contract {contract_name} {callable} state transaction...")
#
#     def _request_contract_state(self, contract_name: str, callable: str, parameters: dict) -> None:
#         """
#         Request contract deploy transaction
#
#         :return: None
#         """
#         params = {"deployer_address": self.context.agent_address}
#         params.update(parameters)
#         strategy = cast(Strategy, self.context.strategy)
#         strategy.is_behaviour_active = False
#         contract_api_dialogues = cast(
#             ContractApiDialogues, self.context.contract_api_dialogues
#         )
#         contract_api_msg, contract_api_dialogue = contract_api_dialogues.create(
#             counterparty=LEDGER_API_ADDRESS,
#             performative=ContractApiMessage.Performative.GET_STATE,
#             ledger_id=strategy.ledger_id,
#             contract_id=f"eightballer/{contract_name}:0.1.0",
#             contract_address=strategy.deployment_status[contract_name][1],
#             callable=callable,
#             kwargs=ContractApiMessage.Kwargs(params),
#         )
#         contract_api_dialogue = cast(
#             ContractApiDialogue, contract_api_dialogue,)
#         contract_api_dialogue.terms = strategy.get_deploy_terms()
#         self.context.outbox.put_message(message=contract_api_msg)
#         strategy.deployment_status[f"{contract_name}_{callable}"] = (
#             "pending", contract_api_dialogue.dialogue_label.dialogue_reference[0])
#         strategy.deployment_status["status"] = "deploying"
#         self.context.logger.info(
#             f"requesting contract {contract_name} state transaction...")
#
#     def teardown(self) -> None:
#         """
#         Implement the task teardown.
#
#         :return: None
#         """
#         self._unregister_service()
#         self._unregister_agent()
#
#     def _request_balance(self) -> None:
#         """
#         Request ledger balance.
#
#         :return: None
#         """
#         strategy = cast(Strategy, self.context.strategy)
#         ledger_api_dialogues = cast(
#             LedgerApiDialogues, self.context.ledger_api_dialogues
#         )
#         ledger_api_msg, _ = ledger_api_dialogues.create(
#             counterparty=LEDGER_API_ADDRESS,
#             performative=LedgerApiMessage.Performative.GET_BALANCE,
#             ledger_id=strategy.ledger_id,
#             address=cast(str, self.context.agent_addresses.get(
#                 strategy.ledger_id)),
#         )
#         self.context.outbox.put_message(message=ledger_api_msg)
#         self.context.logger.info(f"Balance Requested {ledger_api_msg}")
#
#     def _request_contract_deploy_transaction(self, contract_name: str, parameters: dict) -> None:
#         """
#         Request contract deploy transaction
#
#         :return: None
#         """
#         params = {"deployer_address": self.context.agent_address}
#         params.update(parameters)
#         if params.get("args", None) is None:
#             params["args"] = []
#         strategy = cast(Strategy, self.context.strategy)
#         strategy.is_behaviour_active = False
#         contract_api_dialogues = cast(
#             ContractApiDialogues, self.context.contract_api_dialogues
#         )
#         contract_api_msg, contract_api_dialogue = contract_api_dialogues.create(
#             counterparty=LEDGER_API_ADDRESS,
#             performative=ContractApiMessage.Performative.GET_DEPLOY_TRANSACTION,
#             ledger_id=strategy.ledger_id,
#             contract_id=f"eightballer/{contract_name}:0.1.0",
#             callable="get_deploy_transaction",
#             kwargs=ContractApiMessage.Kwargs(params),
#         )
#         contract_api_dialogue = cast(
#             ContractApiDialogue, contract_api_dialogue,)
#         contract_api_dialogue.terms = strategy.get_deploy_terms()
#         self.context.outbox.put_message(message=contract_api_msg)
#         strategy.deployment_status[contract_name] = (
#             "pending", contract_api_dialogue.dialogue_label.dialogue_reference[0])
#         strategy.deployment_status["status"] = "deploying"
#         self.context.logger.info(
#             f"requesting contract {contract_name} deployment transaction...")
#
#     def _request_token_create_transaction(self) -> None:
#         """
#         Request token create transaction
#
#         :return: None
#         """
#         strategy = cast(Strategy, self.context.strategy)
#         strategy.is_behaviour_active = False
#         contract_api_dialogues = cast(
#             ContractApiDialogues, self.context.contract_api_dialogues
#         )
#         contract_api_msg, contract_api_dialogue = contract_api_dialogues.create(
#             counterparty=LEDGER_API_ADDRESS,
#             performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
#             ledger_id=strategy.ledger_id,
#             contract_id="fetchai/erc1155:0.9.0",
#             contract_address=strategy.contract_address,
#             callable="get_create_batch_transaction",
#             kwargs=ContractApiMessage.Kwargs(
#                 {
#                     "deployer_address": self.context.agent_address,
#                     "token_ids": strategy.token_ids,
#                 }
#             ),
#         )
#         contract_api_dialogue = cast(
#             ContractApiDialogue, contract_api_dialogue)
#         contract_api_dialogue.terms = strategy.get_create_token_terms()
#         self.context.outbox.put_message(message=contract_api_msg)
#         self.context.logger.info("requesting create batch transaction...")
#
#     def _request_token_mint_transaction(self) -> None:
#         """
#         Request token mint transaction
#
#         :return: None
#         """
#         strategy = cast(Strategy, self.context.strategy)
#         strategy.is_behaviour_active = False
#         contract_api_dialogues = cast(
#             ContractApiDialogues, self.context.contract_api_dialogues
#         )
#         contract_api_msg, contract_api_dialogue = contract_api_dialogues.create(
#             counterparty=LEDGER_API_ADDRESS,
#             performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
#             ledger_id=strategy.ledger_id,
#             contract_id="fetchai/erc1155:0.9.0",
#             contract_address=strategy.contract_address,
#             callable="get_mint_batch_transaction",
#             kwargs=ContractApiMessage.Kwargs(
#                 {
#                     "deployer_address": self.context.agent_address,
#                     "recipient_address": self.context.agent_address,
#                     "token_ids": strategy.token_ids,
#                     "mint_quantities": strategy.mint_quantities,
#                 }
#             ),
#         )
#         contract_api_dialogue = cast(
#             ContractApiDialogue, contract_api_dialogue)
#         contract_api_dialogue.terms = strategy.get_mint_token_terms()
#         self.context.outbox.put_message(message=contract_api_msg)
#         self.context.logger.info("requesting mint batch transaction...")
#
#     def _register_agent(self) -> None:
#         """
#         Register the agent's location.
#
#         :return: None
#         """
#         strategy = cast(Strategy, self.context.strategy)
#         description = strategy.get_location_description()
#         oef_search_dialogues = cast(
#             OefSearchDialogues, self.context.oef_search_dialogues
#         )
#         oef_search_msg, _ = oef_search_dialogues.create(
#             counterparty=self.context.search_service_address,
#             performative=OefSearchMessage.Performative.REGISTER_SERVICE,
#             service_description=description,
#         )
#         self.context.outbox.put_message(message=oef_search_msg)
#         self.context.logger.info("registering agent on SOEF.")
#
#     def _register_service(self) -> None:
#         """
#         Register the agent's service.
#
#         :return: None
#         """
#         strategy = cast(Strategy, self.context.strategy)
#         description = strategy.get_register_service_description()
#         oef_search_dialogues = cast(
#             OefSearchDialogues, self.context.oef_search_dialogues
#         )
#         oef_search_msg, _ = oef_search_dialogues.create(
#             counterparty=self.context.search_service_address,
#             performative=OefSearchMessage.Performative.REGISTER_SERVICE,
#             service_description=description,
#         )
#         self.context.outbox.put_message(message=oef_search_msg)
#         self.context.logger.info("registering service on SOEF.")
#
#     def _unregister_service(self) -> None:
#         """
#         Unregister service from the SOEF.
#
#         :return: None
#         """
#         strategy = cast(Strategy, self.context.strategy)
#         description = strategy.get_unregister_service_description()
#         oef_search_dialogues = cast(
#             OefSearchDialogues, self.context.oef_search_dialogues
#         )
#         oef_search_msg, _ = oef_search_dialogues.create(
#             counterparty=self.context.search_service_address,
#             performative=OefSearchMessage.Performative.UNREGISTER_SERVICE,
#             service_description=description,
#         )
#         self.context.outbox.put_message(message=oef_search_msg)
#         self.context.logger.info("unregistering service from SOEF.")
#
#     def _unregister_agent(self) -> None:
#         """
#         Unregister agent from the SOEF.
#
#         :return: None
#         """
#         strategy = cast(Strategy, self.context.strategy)
#         description = strategy.get_location_description()
#         oef_search_dialogues = cast(
#             OefSearchDialogues, self.context.oef_search_dialogues
#         )
#         oef_search_msg, _ = oef_search_dialogues.create(
#             counterparty=self.context.search_service_address,
#             performative=OefSearchMessage.Performative.UNREGISTER_SERVICE,
#             service_description=description,
#         )
#         self.context.outbox.put_message(message=oef_search_msg)
#         self.context.logger.info("unregistering agent from SOEF.")
#
