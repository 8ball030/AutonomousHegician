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

from typing import Optional, cast

from aea.skills.behaviours import TickerBehaviour, Behaviour

from packages.fetchai.protocols.contract_api.message import ContractApiMessage
from packages.fetchai.protocols.ledger_api.message import LedgerApiMessage
from packages.tomrae.skills.option_monitoring.dialogues import (
    ContractApiDialogue,
    ContractApiDialogues,
    LedgerApiDialogues,
)
from packages.tomrae.skills.option_monitoring.strategy import Strategy
from packages.tomrae.skills.option_monitoring.dex_wrapper import DexWrapper

DEFAULT_SERVICES_INTERVAL = 30.0
LEDGER_API_ADDRESS = "fetchai/ledger:0.3.0"


class PriceTicker(TickerBehaviour):
    """This class monitors the price"""
    @property
    def current_price(self) -> str:
        """Get the last recorded price from Uniswap."""
        return self._current_price

    def __init__(self, **kwargs):
        """Initialise the behaviour."""
        services_interval = kwargs.pop("services_interval",
                                       DEFAULT_SERVICES_INTERVAL)  # type: int
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
        self._current_price = self.dex.get_ticker("DAI", "ETH")

    def act(self) -> None:
        """
        Implement the act.

        :return: None
        """
        self._set_current_price()
        self.context.logger.info(
            f"Current Rate : {round(self.current_price, 2)}")


class OptionMonitoring(TickerBehaviour):
    """This class scaffolds a behaviour."""
    def __init__(self, **kwargs):
        """Initialise the behaviour."""
        services_interval = kwargs.pop("services_interval",
                                       DEFAULT_SERVICES_INTERVAL)  # type: int
        super().__init__(tick_interval=services_interval, **kwargs)

    def setup(self) -> None:
        """
        Implement the setup.

        :return: None
        """
        self._request_balance()

    def _request_balance(self) -> None:
        """
        Request ledger balance.
        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        ledger_api_dialogues = cast(LedgerApiDialogues,
                                    self.context.ledger_api_dialogues)
        ledger_api_msg = LedgerApiMessage(
            performative=LedgerApiMessage.Performative.GET_BALANCE,
            dialogue_reference=ledger_api_dialogues.
            new_self_initiated_dialogue_reference(),
            ledger_id=strategy.ledger_id,
            address=cast(str,
                         self.context.agent_addresses.get(strategy.ledger_id)),
        )
        ledger_api_msg.counterparty = LEDGER_API_ADDRESS
        ledger_api_dialogues.update(ledger_api_msg)
        self.context.logger.info(f"Balance Requested {ledger_api_msg}")
        self.context.outbox.put_message(message=ledger_api_msg)

    def act(self) -> None:
        """
        Implement the act.

        :return: None
        """
        # self._request_balance()

        strategy = cast(Strategy, self.context.strategy)
        orders_to_execute = strategy.retrieve_actions()

        for order in orders_to_execute:
            self.logger.info(f"Order to Execute -> {order}")
            self.exercise_option(order)

    def exercise_option(self, order) -> None:
        """
        Exercise the option.

        :return: None

        """
        if order["type_of_option"] is "put":
            contract_id = "tomrae/putoption:0.1.0"
            contract_address = self.putoption
        elif order["type_of_option"] is "call":
            contract_id = "tomrae/calloption:0.1.0"
            contract_address = self.calloption

        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
            dialogue_reference=contract_api_dialogues.
            new_self_initiated_dialogue_reference(),
            ledger_id=strategy.ledger_id,
            contract_id=contract_id,
            contract_address=contract_address,
            callable="exercise",
            kwargs=ContractApiMessage.Kwargs({"option_id": order["optionID"]}),
        )

    def teardown(self) -> None:
        """
        Implement the task teardown.

        :return: None
        """
        pass


class ContractDeployer(TickerBehaviour):
    """This class implements a behaviour."""
    def __init__(self, **kwargs):
        """Initialise the behaviour."""
        self.__dict__.update(kwargs)
        super().__init__(tick_interval=DEFAULT_SERVICES_INTERVAL, **kwargs)

    def setup(self) -> None:
        """
        Implement the setup.

        :return: None
        """
        self.deployed = False  # self.calloptions is None
        self._request_balance()

    def act(self) -> None:
        """
        Implement the act.

        :return: None
        """
        self.context.logger.info(
            f"Contract Deployment status : {self.context.strategy.deployment_status}"
        )
        if self.context.strategy.deployment_status["status"] in [
                "complete", "deploying"
        ]:
            return
        strategy = cast(Strategy, self.context.strategy)

        if strategy.deployment_status["stablecoin"][0] is None:
            self._request_deploy_stablecoin()
            # self._request_deploy_pricefeed()
            self.context.strategy.deploying = True

        elif strategy.deployment_status["stablecoin"][0] == "deployed" and \
                strategy.deployment_status["pricefeed"][0] is None:
            self._request_deploy_pricefeed()
            self.context.strategy.deployment_status["status"] = "deploying"

        elif strategy.deployment_status["pricefeed"][0] == "deployed" and \
                strategy.deployment_status["exchange"][0] is None:
            self.pricefeed = strategy.deployment_status["pricefeed"][1]
            self._request_deploy_exchange()
            self.context.strategy.deployment_status["status"] = "deploying"

        elif strategy.deployment_status["exchange"][0] == "deployed" and \
                strategy.deployment_status["ethpool"][0] is None:
            self._request_deploy_ethpool()

        elif strategy.deployment_status["ethpool"][0] == "deployed" and \
                strategy.deployment_status["ercpool"][0] is None:
            self.ethpool = strategy.deployment_status["ethpool"][1]
            self._request_deploy_ercpool()
            self.context.strategy.deployment_status["status"] = "deploying"

        elif strategy.deployment_status["ercpool"][0] == "deployed" and \
                strategy.deployment_status["calloptions"][0] is None:
            self.ercpool = strategy.deployment_status["ercpool"][1]
            self._request_deploy_calloptions()
            self.context.strategy.deployment_status["status"] = "deploying"

        elif strategy.deployment_status["calloptions"][0] == "deployed" and \
                strategy.deployment_status["putoptions"][0] is None:
            self.calloptions = strategy.deployment_status["calloptions"][1]
            self._request_deploy_putoptions()
            self.context.strategy.deployment_status["status"] = "deploying"

        elif strategy.deployment_status["putoptions"][0] == "deployed" and \
                strategy.deployment_status["liquidity"][0] is None:
            self.putoptions = strategy.deployment_status["putoptions"][1]
            self._request_deploy_liquidity()
            self.context.strategy.deployment_status["status"] = "deploying"

        elif strategy.deployment_status["liquidity"][0] == "deployed" and \
                strategy.deployment_status["options"][0] is None:
            self._request_purchase_options()
            self.context.strategy.deployment_status["status"] = "deploying"

        elif strategy.deployment_status["options"][0] == "deployed" and \
                self.context.strategy.deployment_status["status"][0] == "deployed":
            self.context.strategy.deployment_status["status"] = "complete"
        else:
            self.context.logger.info("Deployment complete!")

    def _request_deploy_options(self) -> None:
        """
        Request contract deploy transaction

        :return: None
        """
        self.context.logger.info("options Contract Deployment!")
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(ContractApiDialogues,
                                      self.context.contract_api_dialogues)
        deployment_ref = contract_api_dialogues.new_self_initiated_dialogue_reference(
        )
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
            dialogue_reference=contract_api_dialogues.
            new_self_initiated_dialogue_reference(),
            ledger_id=strategy.ledger_id,
            contract_id="tomrae/ethpool:0.8.0",
            contract_address=self.ethpool,
            callable="provide_liquidity",
            kwargs=ContractApiMessage.Kwargs({
                "deployer_address": self.context.agent_address,
                "args": [200000]
            }))
        contract_api_msg.counterparty = LEDGER_API_ADDRESS
        contract_api_dialogue = cast(
            Optional[ContractApiDialogue],
            contract_api_dialogues.update(contract_api_msg),
        )
        self.context.strategy.deployment_status["options"] = (
            "pending", deployment_ref[0])
        assert contract_api_dialogue is not None, "ContractApiDialogue not generated"
        contract_api_dialogue.terms = strategy.get_deploy_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        self.context.logger.info(
            "requesting options contract deployment transaction...")

 #  def _request_deploy_ethpool(self) -> None:
 #      """
 #      Request contract deploy transaction

 #      :return: None
 #      """
 #      self.context.logger.info("ethpool Contract Deployment!")
 #      strategy = cast(Strategy, self.context.strategy)
 #      strategy.is_behaviour_active = False
 #      contract_api_dialogues = cast(ContractApiDialogues,
 #                                    self.context.contract_api_dialogues)
 #      deployment_ref = contract_api_dialogues.new_self_initiated_dialogue_reference(
 #      )
 #      contract_api_msg = ContractApiMessage(
 #          performative=ContractApiMessage.Performative.
 #          GET_DEPLOY_TRANSACTION,
 #          dialogue_reference=deployment_ref,
 #          ledger_id=strategy.ledger_id,
 #          contract_id="tomrae/ethpool:0.1.0",
 #          callable="get_deploy_transaction",
 #          kwargs=ContractApiMessage.Kwargs({
 #              "deployer_address": self.context.agent_address,
 #              "args": [self.stablecoin]
 #          }),
 #      )
 #      contract_api_msg.counterparty = LEDGER_API_ADDRESS
 #      contract_api_dialogue = cast(
 #          Optional[ContractApiDialogue],
 #          contract_api_dialogues.update(contract_api_msg),
 #      )
 #      self.context.strategy.deployment_status["ethpool"] = (
 #          "pending", deployment_ref[0])
 #      assert contract_api_dialogue is not None, "ContractApiDialogue not generated"
 #      contract_api_dialogue.terms = strategy.get_deploy_terms()
 #      self.context.outbox.put_message(message=contract_api_msg)
 #      self.context.logger.info(
 #          "requesting ethpool contract deployment transaction...")


    def _request_deploy_putoptions(self) -> None:
        """
        Request contract deploy transaction

        :return: None
        """
        self.context.logger.info("putoptions Contract Deployment!")
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(ContractApiDialogues,
                                      self.context.contract_api_dialogues)
        deployment_ref = contract_api_dialogues.new_self_initiated_dialogue_reference(
        )
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.
            GET_DEPLOY_TRANSACTION,
            dialogue_reference=deployment_ref,
            ledger_id=strategy.ledger_id,
            contract_id="tomrae/putoptions:0.1.0",
            callable="get_deploy_transaction",
            kwargs=ContractApiMessage.Kwargs({
                "deployer_address":
                self.context.agent_address,
                "args": [
                    self.context.strategy.deployment_status["stablecoin"][1],
                    self.context.strategy.deployment_status["pricefeed"][1],
                    self.context.strategy.deployment_status["exchange"][1]
                ]
            }),
        )
        contract_api_msg.counterparty = LEDGER_API_ADDRESS
        contract_api_dialogue = cast(
            Optional[ContractApiDialogue],
            contract_api_dialogues.update(contract_api_msg),
        )
        self.context.strategy.deployment_status["putoptions"] = (
            "pending", deployment_ref[0])
        assert contract_api_dialogue is not None, "ContractApiDialogue not generated"
        contract_api_dialogue.terms = strategy.get_deploy_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        self.context.logger.info(
            "requesting putoptions contract deployment transaction...")

    def _request_deploy_calloptions(self) -> None:
        """
        Request contract deploy transaction

        :return: None
        """
        self.context.logger.info("calloptions Contract Deployment!")
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(ContractApiDialogues,
                                      self.context.contract_api_dialogues)
        deployment_ref = contract_api_dialogues.new_self_initiated_dialogue_reference(
        )
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.
            GET_DEPLOY_TRANSACTION,
            dialogue_reference=deployment_ref,
            ledger_id=strategy.ledger_id,
            contract_id="tomrae/calloptions:0.1.0",
            callable="get_deploy_transaction",
            kwargs=ContractApiMessage.Kwargs({
                "deployer_address":
                self.context.agent_address,
                "args":
                [self.context.strategy.deployment_status["pricefeed"][1]]
            }),
        )
        contract_api_msg.counterparty = LEDGER_API_ADDRESS
        contract_api_dialogue = cast(
            Optional[ContractApiDialogue],
            contract_api_dialogues.update(contract_api_msg),
        )
        self.context.strategy.deployment_status["calloptions"] = (
            "pending", deployment_ref[0])
        assert contract_api_dialogue is not None, "ContractApiDialogue not generated"
        contract_api_dialogue.terms = strategy.get_deploy_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        self.context.logger.info(
            "requesting calloptions contract deployment transaction...")

    def _request_deploy_ercpool(self) -> None:
        """
        Request contract deploy transaction

        :return: None
        """
        self.context.logger.info("ercpool Contract Deployment!")
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(ContractApiDialogues,
                                      self.context.contract_api_dialogues)
        deployment_ref = contract_api_dialogues.new_self_initiated_dialogue_reference(
        )
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.
            GET_DEPLOY_TRANSACTION,
            dialogue_reference=deployment_ref,
            ledger_id=strategy.ledger_id,
            contract_id="tomrae/ercpool:0.1.0",
            callable="get_deploy_transaction",
            kwargs=ContractApiMessage.Kwargs({
                "deployer_address":
                self.context.agent_address,
                "args":
                [self.context.strategy.deployment_status["stablecoin"][1]]
            }),
        )
        self.context.logger.info({
            "deployer_address":
            self.context.agent_address,
            "args": [self.context.strategy.deployment_status["stablecoin"][1]]
        })

        contract_api_msg.counterparty = LEDGER_API_ADDRESS
        contract_api_dialogue = cast(
            Optional[ContractApiDialogue],
            contract_api_dialogues.update(contract_api_msg),
        )
        self.context.strategy.deployment_status["ercpool"] = (
            "pending", deployment_ref[0])
        assert contract_api_dialogue is not None, "ContractApiDialogue not generated"
        contract_api_dialogue.terms = strategy.get_deploy_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        self.context.logger.info(
            "requesting ercpool contract deployment transaction...")

    def _request_deploy_ethpool(self) -> None:
        """
        Request contract deploy transaction

        :return: None
        """
        self.context.logger.info("ethpool Contract Deployment!")
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(ContractApiDialogues,
                                      self.context.contract_api_dialogues)
        deployment_ref = contract_api_dialogues.new_self_initiated_dialogue_reference(
        )
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.
            GET_DEPLOY_TRANSACTION,
            dialogue_reference=deployment_ref,
            ledger_id=strategy.ledger_id,
            contract_id="tomrae/ethpool:0.1.0",
            callable="get_deploy_transaction",
            kwargs=ContractApiMessage.Kwargs({
                "deployer_address":
                self.context.agent_address,
                "args":
                [self.context.strategy.deployment_status["stablecoin"]]
            }),
        )
        contract_api_msg.counterparty = LEDGER_API_ADDRESS
        contract_api_dialogue = cast(
            Optional[ContractApiDialogue],
            contract_api_dialogues.update(contract_api_msg),
        )
        self.context.strategy.deployment_status["ethpool"] = (
            "pending", deployment_ref[0])
        assert contract_api_dialogue is not None, "ContractApiDialogue not generated"
        contract_api_dialogue.terms = strategy.get_deploy_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        self.context.logger.info(
            "requesting ethpool contract deployment transaction...")

    def _request_deploy_exchange(self) -> None:
        """
        Request contract deploy transaction

        :return: None
        """
        self.context.logger.info("exchange Contract Deployment!")
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(ContractApiDialogues,
                                      self.context.contract_api_dialogues)
        deployment_ref = contract_api_dialogues.new_self_initiated_dialogue_reference(
        )
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.
            GET_DEPLOY_TRANSACTION,
            dialogue_reference=deployment_ref,
            ledger_id=strategy.ledger_id,
            contract_id="tomrae/exchange:0.1.0",
            callable="get_deploy_transaction",
            kwargs=ContractApiMessage.Kwargs({
                "deployer_address":
                self.context.agent_address,
                "args": [
                    self.context.strategy.deployment_status["pricefeed"][1],
                    self.context.strategy.deployment_status["stablecoin"][1]
                ]
            }),
        )
        contract_api_msg.counterparty = LEDGER_API_ADDRESS
        contract_api_dialogue = cast(
            Optional[ContractApiDialogue],
            contract_api_dialogues.update(contract_api_msg),
        )
        self.context.strategy.deployment_status["exchange"] = (
            "pending", deployment_ref[0])
        assert contract_api_dialogue is not None, "ContractApiDialogue not generated"
        contract_api_dialogue.terms = strategy.get_deploy_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        self.context.logger.info(
            "requesting exchange contract deployment transaction...")

    def _request_deploy_pricefeed(self) -> None:
        """
        Request contract deploy transaction

        :return: None
        """
        self.context.logger.info("Pricefeed Contract Deployment!")
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(ContractApiDialogues,
                                      self.context.contract_api_dialogues)
        deployment_ref = contract_api_dialogues.new_self_initiated_dialogue_reference(
        )
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.
            GET_DEPLOY_TRANSACTION,
            dialogue_reference=deployment_ref,
            ledger_id=strategy.ledger_id,
            contract_id="tomrae/pricefeed:0.1.0",
            callable="get_deploy_transaction",
            kwargs=ContractApiMessage.Kwargs({
                "deployer_address": self.context.agent_address,
                "price": 10000
            }),
        )
        contract_api_msg.counterparty = LEDGER_API_ADDRESS
        contract_api_dialogue = cast(
            Optional[ContractApiDialogue],
            contract_api_dialogues.update(contract_api_msg),
        )
        self.context.strategy.deployment_status["pricefeed"] = (
            "pending", deployment_ref[0])
        assert contract_api_dialogue is not None, "ContractApiDialogue not generated"
        contract_api_dialogue.terms = strategy.get_deploy_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        self.context.logger.info(
            "requesting pricefeed contract deployment transaction...")

    def _request_deploy_stablecoin(self) -> None:
        """
        Request contract deploy transaction

        :return: None
        """
        self.context.logger.info("Stablecoin Contract Deployment!")
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(ContractApiDialogues,
                                      self.context.contract_api_dialogues)
        deployment_ref = contract_api_dialogues.new_self_initiated_dialogue_reference(
        )
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.
            GET_DEPLOY_TRANSACTION,
            dialogue_reference=deployment_ref,
            ledger_id=strategy.ledger_id,
            contract_id="tomrae/stablecoin:0.1.0",
            callable="get_deploy_transaction",
            kwargs=ContractApiMessage.Kwargs(
                {"deployer_address": self.context.agent_address}),
        )
        contract_api_msg.counterparty = LEDGER_API_ADDRESS
        contract_api_dialogue = cast(
            Optional[ContractApiDialogue],
            contract_api_dialogues.update(contract_api_msg),
        )
        self.context.strategy.deployment_status["stablecoin"] = (
            "pending", deployment_ref[0])
        assert contract_api_dialogue is not None, "ContractApiDialogue not generated"
        contract_api_dialogue.terms = strategy.get_deploy_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        self.context.logger.info(
            "requesting stablecoin contract deployment transaction...")

    def teardown(self) -> None:
        """
        Implement the task teardown.

        :return: None
        """
        pass
#        self._unregister_service()
#        self._unregister_agent()

    def _request_balance(self) -> None:
        """
        Request ledger balance.

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        ledger_api_dialogues = cast(LedgerApiDialogues,
                                    self.context.ledger_api_dialogues)
        ledger_api_msg = LedgerApiMessage(
            performative=LedgerApiMessage.Performative.GET_BALANCE,
            dialogue_reference=ledger_api_dialogues.
            new_self_initiated_dialogue_reference(),
            ledger_id=strategy.ledger_id,
            address=cast(str,
                         self.context.agent_addresses.get(strategy.ledger_id)),
        )
        ledger_api_msg.counterparty = LEDGER_API_ADDRESS
        ledger_api_dialogues.update(ledger_api_msg)
        self.context.outbox.put_message(message=ledger_api_msg)

    def _request_contract_deploy_transaction(self) -> None:
        """
        Request contract deploy transaction

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(ContractApiDialogues,
                                      self.context.contract_api_dialogues)
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.
            GET_DEPLOY_TRANSACTION,
            dialogue_reference=contract_api_dialogues.
            new_self_initiated_dialogue_reference(),
            ledger_id=strategy.ledger_id,
            #            contract_id="fetchai/erc1155:0.8.0",
            contract_id="tomrae/stablecoin:0.1.0",
            callable="get_deploy_transaction",
            kwargs=ContractApiMessage.Kwargs(
                {"deployer_address": self.context.agent_address}),
        )
        contract_api_msg.counterparty = LEDGER_API_ADDRESS
        contract_api_dialogue = cast(
            Optional[ContractApiDialogue],
            contract_api_dialogues.update(contract_api_msg),
        )
        assert contract_api_dialogue is not None, "ContractApiDialogue not generated"
        contract_api_dialogue.terms = strategy.get_deploy_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        self.context.logger.info(
            "requesting contract deployment transaction...")

    def _request_deploy_liquidity(self) -> None:
        """
        Request token create transaction

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(ContractApiDialogues,
                                      self.context.contract_api_dialogues)
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
            dialogue_reference=contract_api_dialogues.
            new_self_initiated_dialogue_reference(),
            ledger_id=strategy.ledger_id,
            contract_id="tomrae/ethpool:0.1.0",
            callable="provide_liquidity",
            kwargs=ContractApiMessage.Kwargs({
                "deployer_address":
                self.context.agent_address,
                "args": [
                    1000000,
                    self.context.strategy.deployment_status["ethpool"][1],
                    self.context.agent_address
                ],
            }),
        )
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
            dialogue_reference=contract_api_dialogues.new_self_initiated_dialogue_reference(),
            ledger_id=strategy.ledger_id,
            contract_id="tomrae/ethpool:0.1.0",
            contract_address=strategy.deployment_status["ethpool"][1],
            callable="provide_liquidity",
            kwargs=ContractApiMessage.Kwargs(
                {
                    "deployer_address": self.context.agent_address,
                    "amount": 100,
                }
            ),
        )
        contract_api_msg.counterparty = LEDGER_API_ADDRESS
        contract_api_dialogue = cast(
            Optional[ContractApiDialogue],
            contract_api_dialogues.update(contract_api_msg),
        )
        assert contract_api_dialogue is not None, "ContractApiDialogue not generated"
        contract_api_dialogue.terms = strategy.get_create_token_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        self.context.logger.info("requesting provide liquidity transaction...")

    def _request_token_mint_transaction(self) -> None:
        """
        Request token mint transaction

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(ContractApiDialogues,
                                      self.context.contract_api_dialogues)
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
            dialogue_reference=contract_api_dialogues.
            new_self_initiated_dialogue_reference(),
            ledger_id=strategy.ledger_id,
            contract_id="fetchai/erc1155:0.8.0",
            contract_address=strategy.contract_address,
            callable="get_mint_batch_transaction",
            kwargs=ContractApiMessage.Kwargs({
                "deployer_address":
                self.context.agent_address,
                "recipient_address":
                self.context.agent_address,
                "token_ids":
                strategy.token_ids,
                "mint_quantities":
                strategy.mint_quantities,
            }),
        )
        contract_api_msg.counterparty = LEDGER_API_ADDRESS
        contract_api_dialogue = cast(
            Optional[ContractApiDialogue],
            contract_api_dialogues.update(contract_api_msg),
        )
        assert contract_api_dialogue is not None, "ContractApiDialogue not generated"
        contract_api_dialogue.terms = strategy.get_mint_token_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        self.context.logger.info("requesting mint batch transaction...")

    def _register_agent(self) -> None:
        """
        Register the agent's location.

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        description = strategy.get_location_description()
        oef_search_dialogues = cast(OefSearchDialogues,
                                    self.context.oef_search_dialogues)
        oef_search_msg = OefSearchMessage(
            performative=OefSearchMessage.Performative.REGISTER_SERVICE,
            dialogue_reference=oef_search_dialogues.
            new_self_initiated_dialogue_reference(),
            service_description=description,
        )
        oef_search_msg.counterparty = self.context.search_service_address
        oef_search_dialogues.update(oef_search_msg)
        self.context.outbox.put_message(message=oef_search_msg)
        self.context.logger.info("registering agent on SOEF.")

    def _register_service(self) -> None:
        """
        Register the agent's service.

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        description = strategy.get_register_service_description()
        oef_search_dialogues = cast(OefSearchDialogues,
                                    self.context.oef_search_dialogues)
        oef_search_msg = OefSearchMessage(
            performative=OefSearchMessage.Performative.REGISTER_SERVICE,
            dialogue_reference=oef_search_dialogues.
            new_self_initiated_dialogue_reference(),
            service_description=description,
        )
        oef_search_msg.counterparty = self.context.search_service_address
        oef_search_dialogues.update(oef_search_msg)
        self.context.outbox.put_message(message=oef_search_msg)
        self.context.logger.info("registering service on SOEF.")

    def _unregister_service(self) -> None:
        """
        Unregister service from the SOEF.

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        description = strategy.get_unregister_service_description()
        oef_search_dialogues = cast(OefSearchDialogues,
                                    self.context.oef_search_dialogues)
        oef_search_msg = OefSearchMessage(
            performative=OefSearchMessage.Performative.UNREGISTER_SERVICE,
            dialogue_reference=oef_search_dialogues.
            new_self_initiated_dialogue_reference(),
            service_description=description,
        )
        oef_search_msg.counterparty = self.context.search_service_address
        oef_search_dialogues.update(oef_search_msg)
        self.context.outbox.put_message(message=oef_search_msg)
        self.context.logger.info("unregistering service from SOEF.")

    def _unregister_agent(self) -> None:
        """
        Unregister agent from the SOEF.

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        description = strategy.get_location_description()
        oef_search_dialogues = cast(OefSearchDialogues,
                                    self.context.oef_search_dialogues)
        oef_search_msg = OefSearchMessage(
            performative=OefSearchMessage.Performative.UNREGISTER_SERVICE,
            dialogue_reference=oef_search_dialogues.
            new_self_initiated_dialogue_reference(),
            service_description=description,
        )
        oef_search_msg.counterparty = self.context.search_service_address
        oef_search_dialogues.update(oef_search_msg)
        self.context.outbox.put_message(message=oef_search_msg)
        self.context.logger.info("unregistering agent from SOEF.")

