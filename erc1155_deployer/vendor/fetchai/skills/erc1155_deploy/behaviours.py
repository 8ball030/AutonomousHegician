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

from aea.skills.behaviours import TickerBehaviour

from packages.fetchai.protocols.contract_api.message import ContractApiMessage
from packages.fetchai.protocols.ledger_api.message import LedgerApiMessage
from packages.fetchai.protocols.oef_search.message import OefSearchMessage
from packages.fetchai.skills.erc1155_deploy.dialogues import (
    ContractApiDialogue,
    ContractApiDialogues,
    LedgerApiDialogues,
    OefSearchDialogues,
)
from packages.fetchai.skills.erc1155_deploy.strategy import Strategy

DEFAULT_SERVICES_INTERVAL = 30.0
LEDGER_API_ADDRESS = "fetchai/ledger:0.3.0"


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
        ledger_api_msg = LedgerApiMessage(
            performative=LedgerApiMessage.Performative.GET_BALANCE,
            dialogue_reference=ledger_api_dialogues.new_self_initiated_dialogue_reference(),
            ledger_id=strategy.ledger_id,
            address=cast(str, self.context.agent_addresses.get(strategy.ledger_id)),
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
        contract_api_dialogues = cast(
            ContractApiDialogues, self.context.contract_api_dialogues
        )
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.GET_DEPLOY_TRANSACTION,
            dialogue_reference=contract_api_dialogues.new_self_initiated_dialogue_reference(),
            ledger_id=strategy.ledger_id,
            contract_id="fetchai/erc1155:0.8.0",
            callable="get_deploy_transaction",
            kwargs=ContractApiMessage.Kwargs(
                {"deployer_address": self.context.agent_address}
            ),
        )
        contract_api_msg.counterparty = LEDGER_API_ADDRESS
        contract_api_dialogue = cast(
            Optional[ContractApiDialogue],
            contract_api_dialogues.update(contract_api_msg),
        )
        assert contract_api_dialogue is not None, "ContractApiDialogue not generated"
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
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
            dialogue_reference=contract_api_dialogues.new_self_initiated_dialogue_reference(),
            ledger_id=strategy.ledger_id,
            contract_id="fetchai/erc1155:0.8.0",
            contract_address=strategy.contract_address,
            callable="get_create_batch_transaction",
            kwargs=ContractApiMessage.Kwargs(
                {
                    "deployer_address": self.context.agent_address,
                    "token_ids": strategy.token_ids,
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
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
            dialogue_reference=contract_api_dialogues.new_self_initiated_dialogue_reference(),
            ledger_id=strategy.ledger_id,
            contract_id="fetchai/erc1155:0.8.0",
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
        oef_search_dialogues = cast(
            OefSearchDialogues, self.context.oef_search_dialogues
        )
        oef_search_msg = OefSearchMessage(
            performative=OefSearchMessage.Performative.REGISTER_SERVICE,
            dialogue_reference=oef_search_dialogues.new_self_initiated_dialogue_reference(),
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
        oef_search_dialogues = cast(
            OefSearchDialogues, self.context.oef_search_dialogues
        )
        oef_search_msg = OefSearchMessage(
            performative=OefSearchMessage.Performative.REGISTER_SERVICE,
            dialogue_reference=oef_search_dialogues.new_self_initiated_dialogue_reference(),
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
        oef_search_dialogues = cast(
            OefSearchDialogues, self.context.oef_search_dialogues
        )
        oef_search_msg = OefSearchMessage(
            performative=OefSearchMessage.Performative.UNREGISTER_SERVICE,
            dialogue_reference=oef_search_dialogues.new_self_initiated_dialogue_reference(),
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
        oef_search_dialogues = cast(
            OefSearchDialogues, self.context.oef_search_dialogues
        )
        oef_search_msg = OefSearchMessage(
            performative=OefSearchMessage.Performative.UNREGISTER_SERVICE,
            dialogue_reference=oef_search_dialogues.new_self_initiated_dialogue_reference(),
            service_description=description,
        )
        oef_search_msg.counterparty = self.context.search_service_address
        oef_search_dialogues.update(oef_search_msg)
        self.context.outbox.put_message(message=oef_search_msg)
        self.context.logger.info("unregistering agent from SOEF.")
