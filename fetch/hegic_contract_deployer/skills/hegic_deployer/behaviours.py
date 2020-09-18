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

from typing import cast, Dict, Any

from aea.skills.behaviours import TickerBehaviour

from packages.fetchai.protocols.contract_api.message import ContractApiMessage
from packages.fetchai.protocols.ledger_api.message import LedgerApiMessage
from packages.fetchai.protocols.oef_search.message import OefSearchMessage
from packages.eight_baller.skills.hegic_deployer.dialogues import (
    ContractApiDialogue,
    ContractApiDialogues,
    LedgerApiDialogues,
    OefSearchDialogues,
)
from packages.eight_baller.skills.hegic_deployer.strategy import Strategy

DEFAULT_SERVICES_INTERVAL = 30.0
LEDGER_API_ADDRESS = "fetchai/ledger:0.4.0"



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
        # self.context.logger.info(
        #    f"Contract Deployment status : {{k: v[0] for k, v in self.context.strategy.deployment_status.items()}}"
        # )
        return None
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
            self.context.strategy.deployment_status["status"] = "deploying"

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

        elif strategy.deployment_status["options_estimate"][0] is None and \
                strategy.deployment_status["liquidity"][0] == "deployed":
            params = {
                "period": 24 * 3600,
                "strike_price": 200,
                "amount": Web3.toWei(0.1, "ether"),
                "option_type": "call",
            }
            params = self.context.strategy.create_new_option(params)
            self._option_interaction(option_type="call",
                                     deployment_name="options_estimate",
                                     act="options_estimate",
                                     params=params)
        else:
            self.context.logger.info("Deployment complete!")

    def _option_interaction(self, option_type: str, act: str,
                            params: Dict[str,
                                         Any], deployment_name: str) -> bool:
        assert option_type in ["call", "put"]
        assert act in [
            "create_call_option", "options_estimate", "exercise_option"
        ]
        self.context.strategy.deployment_status["status"] = "deploying"
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(ContractApiDialogues,
                                      self.context.contract_api_dialogues)
        deploy_ref = contract_api_dialogues.new_self_initiated_dialogue_reference(
        )
        params.update({"deployer_address": self.context.agent_address})
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
            dialogue_reference=deploy_ref,
            ledger_id=strategy.ledger_id,
            contract_id=f"tomrae/{option_type}options:0.1.0",
            contract_address=strategy.deployment_status[f"{option_type}options"][1],
            callable=act,
            kwargs=ContractApiMessage.Kwargs(params),
        )
        contract_api_msg.counterparty = LEDGER_API_ADDRESS
        contract_api_dialogue = cast(
            Optional[ContractApiDialogue],
            contract_api_dialogues.update(contract_api_msg),
        )
        self.context.strategy.deployment_status[act] = (
            "pending", deploy_ref[0])
        assert contract_api_dialogue is not None, "ContractApiDialogue not generated"
        contract_api_dialogue.terms = strategy.get_create_token_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        self.context.logger.info(
            f"contract deployer requesting {act} {option_type} transaction...")

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
                "price": 200
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

        deploy_ref = contract_api_dialogues.new_self_initiated_dialogue_reference(
        )
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
            dialogue_reference=deploy_ref,
            ledger_id=strategy.ledger_id,
            contract_id="tomrae/ethpool:0.1.0",
            contract_address=strategy.deployment_status["ethpool"][1],
            callable="provide_liquidity",
            kwargs=ContractApiMessage.Kwargs({
                "deployer_address": self.context.agent_address,
                "amount": 0,
            }),
        )
        contract_api_msg.counterparty = LEDGER_API_ADDRESS
        contract_api_dialogue = cast(
            Optional[ContractApiDialogue],
            contract_api_dialogues.update(contract_api_msg),
        )
        self.context.strategy.deployment_status["liquidity"] = ("pending",
                                                                deploy_ref[0])
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


class ServiceRegistrationBehaviour(TickerBehaviour):
    """This class implements a behaviour."""

    def __init__(self, **kwargs):
        """Initialise the behaviour."""
        services_interval = kwargs.pop(
            "services_interval", DEFAULT_SERVICES_INTERVAL
        )  # type: int
        super().__init__(tick_interval=services_interval, **kwargs)
        self.is_service_registered = False

    def setup(self) -> None:
        """
        Implement the setup.

        :return: None
        """
        self._request_balance()
        strategy = cast(Strategy, self.context.strategy)
        if not strategy.is_contract_deployed:
            self._request_contract_deploy_transaction()

    def act(self) -> None:
        """
        Implement the act.

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        if not strategy.is_behaviour_active:
            return

        if strategy.is_contract_deployed and not strategy.is_tokens_created:
            self._request_token_create_transaction()
        elif (
            strategy.is_contract_deployed
            and strategy.is_tokens_created
            and not strategy.is_tokens_minted
        ):
            self._request_token_mint_transaction()
        elif (
            strategy.is_contract_deployed
            and strategy.is_tokens_created
            and strategy.is_tokens_minted
            and not self.is_service_registered
        ):
            self._register_agent()
            self._register_service()
            self.is_service_registered = True

    def teardown(self) -> None:
        """
        Implement the task teardown.

        :return: None
        """
        self._unregister_service()
        self._unregister_agent()

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

    def _request_contract_deploy_transaction(self) -> None:
        """
        Request contract deploy transaction

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(
            ContractApiDialogues, self.context.contract_api_dialogues
        )
        contract_api_msg, contract_api_dialogue = contract_api_dialogues.create(
            counterparty=LEDGER_API_ADDRESS,
            performative=ContractApiMessage.Performative.GET_DEPLOY_TRANSACTION,
            ledger_id=strategy.ledger_id,
            contract_id="fetchai/erc1155:0.9.0",
            callable="get_deploy_transaction",
            kwargs=ContractApiMessage.Kwargs(
                {"deployer_address": self.context.agent_address}
            ),
        )
        contract_api_dialogue = cast(ContractApiDialogue, contract_api_dialogue,)
        contract_api_dialogue.terms = strategy.get_deploy_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        self.context.logger.info("requesting contract deployment transaction...")

    def _request_token_create_transaction(self) -> None:
        """
        Request token create transaction

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(
            ContractApiDialogues, self.context.contract_api_dialogues
        )
        contract_api_msg, contract_api_dialogue = contract_api_dialogues.create(
            counterparty=LEDGER_API_ADDRESS,
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
            ledger_id=strategy.ledger_id,
            contract_id="fetchai/erc1155:0.9.0",
            contract_address=strategy.contract_address,
            callable="get_create_batch_transaction",
            kwargs=ContractApiMessage.Kwargs(
                {
                    "deployer_address": self.context.agent_address,
                    "token_ids": strategy.token_ids,
                }
            ),
        )
        contract_api_dialogue = cast(ContractApiDialogue, contract_api_dialogue)
        contract_api_dialogue.terms = strategy.get_create_token_terms()
        self.context.outbox.put_message(message=contract_api_msg)
        self.context.logger.info("requesting create batch transaction...")

    def _request_token_mint_transaction(self) -> None:
        """
        Request token mint transaction

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        strategy.is_behaviour_active = False
        contract_api_dialogues = cast(
            ContractApiDialogues, self.context.contract_api_dialogues
        )
        contract_api_msg, contract_api_dialogue = contract_api_dialogues.create(
            counterparty=LEDGER_API_ADDRESS,
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
            ledger_id=strategy.ledger_id,
            contract_id="fetchai/erc1155:0.9.0",
            contract_address=strategy.contract_address,
            callable="get_mint_batch_transaction",
            kwargs=ContractApiMessage.Kwargs(
                {
                    "deployer_address": self.context.agent_address,
                    "recipient_address": self.context.agent_address,
                    "token_ids": strategy.token_ids,
                    "mint_quantities": strategy.mint_quantities,
                }
            ),
        )
        contract_api_dialogue = cast(ContractApiDialogue, contract_api_dialogue)
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
        oef_search_dialogues = cast(
            OefSearchDialogues, self.context.oef_search_dialogues
        )
        oef_search_msg, _ = oef_search_dialogues.create(
            counterparty=self.context.search_service_address,
            performative=OefSearchMessage.Performative.REGISTER_SERVICE,
            service_description=description,
        )
        self.context.outbox.put_message(message=oef_search_msg)
        self.context.logger.info("registering agent on SOEF.")

    def _register_service(self) -> None:
        """
        Register the agent's service.

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        description = strategy.get_register_service_description()
        oef_search_dialogues = cast(
            OefSearchDialogues, self.context.oef_search_dialogues
        )
        oef_search_msg, _ = oef_search_dialogues.create(
            counterparty=self.context.search_service_address,
            performative=OefSearchMessage.Performative.REGISTER_SERVICE,
            service_description=description,
        )
        self.context.outbox.put_message(message=oef_search_msg)
        self.context.logger.info("registering service on SOEF.")

    def _unregister_service(self) -> None:
        """
        Unregister service from the SOEF.

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        description = strategy.get_unregister_service_description()
        oef_search_dialogues = cast(
            OefSearchDialogues, self.context.oef_search_dialogues
        )
        oef_search_msg, _ = oef_search_dialogues.create(
            counterparty=self.context.search_service_address,
            performative=OefSearchMessage.Performative.UNREGISTER_SERVICE,
            service_description=description,
        )
        self.context.outbox.put_message(message=oef_search_msg)
        self.context.logger.info("unregistering service from SOEF.")

    def _unregister_agent(self) -> None:
        """
        Unregister agent from the SOEF.

        :return: None
        """
        strategy = cast(Strategy, self.context.strategy)
        description = strategy.get_location_description()
        oef_search_dialogues = cast(
            OefSearchDialogues, self.context.oef_search_dialogues
        )
        oef_search_msg, _ = oef_search_dialogues.create(
            counterparty=self.context.search_service_address,
            performative=OefSearchMessage.Performative.UNREGISTER_SERVICE,
            service_description=description,
        )
        self.context.outbox.put_message(message=oef_search_msg)
        self.context.logger.info("unregistering agent from SOEF.")
