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

import sys
from typing import Any, Dict, Union, cast

import web3

from aea.skills.behaviours import TickerBehaviour

from packages.eightballer.skills.hegic_deployer.dialogues import (
    ContractApiDialogue,
    ContractApiDialogues,
    LedgerApiDialogues,
)
from packages.eightballer.skills.hegic_deployer.strategy import Strategy
from packages.fetchai.connections.ledger.base import (
    CONNECTION_ID as LEDGER_CONNECTION_PUBLIC_ID,
)
from packages.fetchai.protocols.contract_api.message import ContractApiMessage
from packages.fetchai.protocols.ledger_api.message import LedgerApiMessage


DEFAULT_SERVICES_INTERVAL = 0.1
LEDGER_API_ADDRESS = str(LEDGER_CONNECTION_PUBLIC_ID)


def toBTC(x):
    return int(web3.Web3.toWei(x, "ether") / 1e10)


class ServiceRegistrationBehaviour(TickerBehaviour):
    """This class implements a behaviour."""

    params: Dict[str, Union[int, Dict[str, int]]] = {
        "ETHPrice": 200,
        "BTCPrice": 200,
        "ETHtoBTC": 200,
        "OptionType": {"Put": 1, "Call": 2},
    }
    test_option_btc_params = {
        "period": 86400,
        "amount": toBTC(0.1),
        "strike": 200,
        "type": 1,
    }
    provided_eth = False
    tested_eth = False
    tested_btc = False
    provided_btc = False
    btc_minted = False
    btc_approved = False
    run_contract_tests = False
    monitoring = False

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
        self._request_balance()

    def act(self) -> None:
        """
        Implement the act.

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        if strategy.deployment_status["status"] in [
            "complete",
            "deploying",
        ]:
            return
        #         self.context.logger.info(f"strategy.deployment_status['status']")

        if strategy.deployment_status["wbtc"][0] is None:
            self._request_contract_deploy_transaction("wbtc", {})

        elif (
            strategy.deployment_status["wbtc"][0] == "deployed"
            and strategy.deployment_status["hegic"][0] is None
        ):
            self._request_contract_deploy_transaction("hegic", {})

        elif (
            strategy.deployment_status["wbtc"][0] == "deployed"
            and strategy.deployment_status["priceprovider"][0] is None
        ):
            self._request_contract_deploy_transaction(
                "priceprovider", {"args": [self.params["ETHPrice"]]}
            )

        elif (
            strategy.deployment_status["priceprovider"][0] == "deployed"
            and strategy.deployment_status["btcpriceprovider"][0] is None
        ):
            self._request_contract_deploy_transaction(
                "btcpriceprovider", {"args": [self.params["BTCPrice"]]}
            )
        elif (
            strategy.deployment_status["btcpriceprovider"][0] == "deployed"
            and strategy.deployment_status["exchange"][0] is None
        ):
            self._request_contract_deploy_transaction(
                "exchange",
                {
                    "args": [
                        strategy.deployment_status["wbtc"][1],
                        self.params["ETHtoBTC"],
                    ]
                },
            )

        # we additionally need to deploy the staking contracts
        elif (
            strategy.deployment_status["exchange"][0] == "deployed"
            and strategy.deployment_status["stakingwbtc"][0] is None
        ):
            self._request_contract_deploy_transaction(
                "stakingwbtc",
                {
                    "args": [
                        strategy.deployment_status["hegic"][1],
                        strategy.deployment_status["wbtc"][1],
                    ]
                },
            )

        elif (
            strategy.deployment_status["stakingwbtc"][0] == "deployed"
            and strategy.deployment_status["stakingeth"][0] is None
        ):
            self._request_contract_deploy_transaction(
                "stakingeth", {"args": [strategy.deployment_status["hegic"][1]]}
            )

        elif (
            strategy.deployment_status["exchange"][0] == "deployed"
            and strategy.deployment_status["ethoptions"][0] is None
        ):
            self._request_contract_deploy_transaction(
                "ethoptions",
                {
                    "args": [
                        strategy.deployment_status["priceprovider"][1],
                        strategy.deployment_status["stakingeth"][1],
                    ]
                },
            )

        elif (
            strategy.deployment_status["ethoptions"][0] == "deployed"
            and strategy.deployment_status["btcoptions"][0] is None
        ):
            self._request_contract_deploy_transaction(
                "btcoptions",
                {
                    "args": [
                        strategy.deployment_status["btcpriceprovider"][1],
                        strategy.deployment_status["exchange"][1],
                        strategy.deployment_status["wbtc"][1],
                        strategy.deployment_status["stakingwbtc"][1],
                    ]
                },
            )

        else:
            # self.context.logger.info(
            #            f"Deployment complete! {strategy.deployment_status}")

            # we now know that our base contracts are deployed, so we can retrieve state to the params to continue

            if strategy.deployment_status.get("ethoptions_get_pool", None) is None:
                self._request_contract_state("ethoptions", "get_pool", {})
            elif (
                strategy.deployment_status.get("ethpool")[0] is None
                and strategy.deployment_status["ethoptions_get_pool"][0] == "results"
            ):
                strategy.deployment_status["ethpool"] = [
                    "deployed",
                    strategy.deployment_status["ethoptions_get_pool"][1],
                ]

            elif (
                strategy.deployment_status.get("btcoptions_get_pool", None) is None
                and strategy.deployment_status.get("ethpool",)[0] is not None
            ):
                self._request_contract_state("btcoptions", "get_pool", {})
            elif (
                strategy.deployment_status.get("btcpool")[0] is None
                and strategy.deployment_status["btcoptions_get_pool"][0] == "results"
            ):
                strategy.deployment_status["btcpool"] = [
                    "deployed",
                    strategy.deployment_status["btcoptions_get_pool"][1],
                ]

            elif self.run_contract_tests is False and self.monitoring is False:
                # now we provide liquidity to the pool
                if self.provided_eth is False:
                    self._request_contract_interaction(
                        "ethpool",
                        "provide_liquidity",
                        {"args": [web3.Web3.toWei(1, "ether")]},
                    )
                    self.provided_eth = True

                elif (
                    self.provided_eth is True
                    and self.btc_minted is False
                    and self.provided_btc is False
                ):
                    self._request_contract_interaction(
                        "wbtc",
                        "mint",
                        {"args": [int(self.test_option_btc_params["amount"] * 1e10)]},
                    )
                    self.btc_minted = True

                elif self.btc_minted is True and self.btc_approved is False:
                    self._request_contract_interaction(
                        "wbtc",
                        "approve",
                        {
                            "args": [
                                strategy.deployment_status["btcpool"][1],
                                int(self.test_option_btc_params["amount"] * 1e10),
                            ]
                        },
                    )
                    self.btc_approved = True

                elif (
                    self.provided_eth is True
                    and self.btc_minted is True
                    and self.provided_btc is False
                ):
                    self._request_contract_interaction(
                        "btcpool",
                        "provide_liquidity",
                        {
                            "args": [
                                int(self.test_option_btc_params["amount"] * 1e10),
                                0,
                            ]
                        },
                    )
                    self.provided_btc = True

                elif self.provided_btc is True:
                    self.run_contract_tests = True
                    # here we should call the function to generate the new skill for the AH
                    self.context.logger.info(
                        f"Deployment complete! {strategy.deployment_status}"
                    )
                    strategy.create_config_yaml()

            elif self.run_contract_tests is True and self.monitoring is False:
                if strategy.deployment_status.get("ethoptions_estimate")[0] is None:
                    self.context.logger.info(
                        "**** Running Test of eth contract estimate."
                    )
                    self._request_contract_state(
                        "ethoptions",
                        "estimate",
                        {
                            "period": 24 * 3600 * 1,
                            "amount": web3.Web3.toWei(0.1, "ether"),
                            "strike": self.params["ETHPrice"],
                            "type": self.params["OptionType"]["Call"]
                            if isinstance(self.params["OptionType"], dict)
                            else "",
                        },
                    )

                elif (
                    strategy.deployment_status.get("ethoptions_create_option")[0]
                    is None
                ):
                    self.context.logger.info("**** Running Test of contract create.")
                    self._request_contract_interaction(
                        "ethoptions",
                        "create_option",
                        {
                            "period": 24 * 3600 * 1,
                            "amount": web3.Web3.toWei(0.1, "ether"),
                            "strike": self.params["ETHPrice"],
                            "type": self.params["OptionType"]["Call"]
                            if isinstance(self.params["OptionType"], dict)
                            else "",
                        },
                    )
                elif (
                    strategy.deployment_status.get("ethoptions_create_option")[0]
                    == "deployed"
                    and strategy.deployment_status.get("ethoptions_estimate")[0]
                    == "results"
                    and strategy.deployment_status.get("ethoptions_exercise")[0] is None
                ):
                    self.context.logger.info("**** Running Test of contract excercise.")
                    option_id = strategy.deployment_status.get("ethoptions_estimate")[
                        1
                    ]["option_id"]
                    self._request_contract_interaction(
                        "ethoptions", "exercise", {"option_id": option_id}
                    )

                elif (
                    strategy.deployment_status.get("ethoptions_exercise") is not None
                    and not self.tested_eth
                ):
                    self.context.logger.info(
                        "****Functionality Test of eth contracts complete!"
                    )
                    self.tested_eth = True

                # now we test the btc contract.

                elif strategy.deployment_status.get("btcoptions_estimate")[0] is None:
                    self.context.logger.info(
                        "**** Running Test of btc contract estimate."
                    )
                    self._request_contract_state(
                        "btcoptions", "estimate", self.test_option_btc_params
                    )

                elif (
                    strategy.deployment_status.get("btcoptions_create_option")[0]
                    is None
                ):
                    self.context.logger.info("**** Running Test of contract create.")
                    self._request_contract_interaction(
                        "btcoptions",
                        "create_option",
                        self.test_option_btc_params,
                        # {
                        #     "period": 24 * 3600 * 1,
                        #     "amount": toBTC((0.1)),
                        #     "strike": self.params["BTCPrice"],
                        #     "type": self.params["OptionType"]["Call"]
                        #     if isinstance(self.params["OptionType"], dict)
                        #     else "",
                        # },
                    )
                elif (
                    strategy.deployment_status.get("btcoptions_create_option")[0]
                    == "deployed"
                    and strategy.deployment_status.get("btcoptions_estimate")[0]
                    == "results"
                    and strategy.deployment_status.get("btcoptions_exercise")[0] is None
                ):
                    self.context.logger.info("**** Running Test of contract excercise.")
                    option_id = strategy.deployment_status.get("btcoptions_estimate")[
                        1
                    ]["option_id"]
                    self._request_contract_interaction(
                        "btcoptions", "exercise", {"option_id": option_id}
                    )

                elif strategy.deployment_status.get("btcoptions_exercise") is not None:
                    self.context.logger.info(
                        "****Functionality Test of btc contracts complete!"
                    )
                    strategy.deployment_status["status"] = "complete"

                    sys.exit()

    def _option_interaction(
        self, option_type: str, act: str, params: Dict[str, Any]
    ) -> None:
        if option_type not in ["btc", "eth"]:
            raise ValueError("Missing option types!")
        if act not in ["create_option", "exercise", "estimate"]:
            raise ValueError("Missing act types!")
        strategy = cast(Strategy, self.context.strategy)
        strategy.deployment_status["status"] = "deploying"
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(
            ContractApiDialogues, self.context.contract_api_dialogues
        )
        params.update({"deployer_address": self.context.agent_address})
        contract_api_msg, contract_api_dialogue = contract_api_dialogues.create(
            counterparty=LEDGER_API_ADDRESS,
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
            ledger_id=strategy.ledger_id,
            contract_id=f"eightballer/{option_type}options:0.1.0",
            contract_address=strategy.deployment_status[f"{option_type}options"][1],
            callable=f"{act}",
            kwargs=ContractApiMessage.Kwargs(params),
        )
        strategy.deployment_status[f"{option_type}options_{act}"] = (
            "pending",
            contract_api_dialogue.dialogue_label.dialogue_reference[0],
        )
        contract_api_dialogue = cast(ContractApiDialogue, contract_api_dialogue,)
        contract_api_dialogue.terms = strategy.get_deploy_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        self.context.logger.info(
            f"contract deployer requesting {act} {option_type} transaction..."
        )

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
        strategy.deployment_status["status"] = "deploying"
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
        strategy.deployment_status["status"] = "deploying"
        self.context.logger.info(
            f"requesting contract {contract_name} state transaction..."
        )

    def teardown(self) -> None:
        """
        Implement the task teardown.

        :return: None
        """
        pass

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
        self.context.logger.info(f"Balance Requested {ledger_api_msg}")

    def _request_contract_deploy_transaction(
        self, contract_name: str, parameters: dict
    ) -> None:
        """
        Request contract deploy transaction

        :return: None
        """
        params = {"deployer_address": self.context.agent_address}
        params.update(parameters)
        if params.get("args", None) is None:
            params["args"] = []
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(
            ContractApiDialogues, self.context.contract_api_dialogues
        )
        contract_api_msg, contract_api_dialogue = contract_api_dialogues.create(
            counterparty=LEDGER_API_ADDRESS,
            performative=ContractApiMessage.Performative.GET_DEPLOY_TRANSACTION,
            ledger_id=strategy.ledger_id,
            contract_id=f"eightballer/{contract_name}:0.1.0",
            callable="get_deploy_transaction",
            kwargs=ContractApiMessage.Kwargs(params),
        )
        contract_api_dialogue = cast(ContractApiDialogue, contract_api_dialogue,)
        contract_api_dialogue.terms = strategy.get_deploy_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        strategy.deployment_status[contract_name] = (
            "pending",
            contract_api_dialogue.dialogue_label.dialogue_reference[0],
        )
        strategy.deployment_status["status"] = "deploying"
        self.context.logger.info(
            f"requesting contract {contract_name} deployment transaction..."
        )
