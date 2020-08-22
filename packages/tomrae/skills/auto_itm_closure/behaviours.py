# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2019 Fetch.AI Limited
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
"""This package contains a scaffold of a behaviour."""
import logging
from typing import cast

from aea.skills.base import Behaviour
from aea.protocols.default.message import DefaultMessage

from packages.fetchai.protocols.oef_search.message import OefSearchMessage
from packages.fetchai.protocols.ledger_api.message import LedgerApiMessage
from packages.fetchai.protocols.contract_api.message import ContractApiMessage


from packages.tomrae.skills.auto_itm_closure.strategy import Strategy
from packages.tomrae.skills.auto_itm_closure.dialogues import (
    LedgerApiDialogues,
    DefaultDialogues,
    ContractApiDialogues
)


logger = logging.getLogger(
    "aea.packages.fetchai.skills.auto_itm_closure.behaviour")

logger.setLevel(logging.INFO)
LEDGER_API_ADDRESS = "fetchai/ledger:0.4.0"


class OptionMonitor(Behaviour):
    """This class scaffolds a behaviour."""

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
        logger.info(f"Balance Requested {ledger_api_msg}")
        self.context.outbox.put_message(message=ledger_api_msg)

    def act(self) -> None:
        """
        Implement the act.

        :return: None
        """
        self._request_balance()

        msg = DefaultMessage(
           performative=DefaultMessage.Performative.ERROR,
           error_code=DefaultMessage.ErrorCode.UNSUPPORTED_PROTOCOL,
           error_msg="This protocol is not supported by this AEA.",
           error_data={"unsupported_msg": b"serialized unsupported protocol message"},
        )


        msg_dialogues = cast(
            DefaultDialogues, self.context.default_dialogues
        )
#         msg.counterparty = LEDGER_API_ADDRESS
#         msg_dialogues.update(msg)
        # logger.info(f"Message {msg}")

#         self.context.outbox.put_message(message=msg)


        strategy = cast(Strategy, self.context.strategy)
        orders_to_execute = strategy.retrieve_actions()


        contract_api_dialogues = cast(
            ContractApiDialogues, self.context.contract_api_dialogues
        )
        contract_api_msg = ContractApiMessage(
            performative=ContractApiMessage.Performative.GET_STATE,
            dialogue_reference=contract_api_dialogues.new_self_initiated_dialogue_reference(),
            ledger_id="ethereum",
            contract_id="tomrae/HegicCallOption:0.1.0",
            contract_address="0x2990C030dcf370920Ed0cCa80bF32Af9503F4bB5",#strategy.contract_address,
            callable="",
            kwargs=ContractApiMessage.Kwargs(
                {
                    "deployer_address": self.context.agent_address, 
                    "token_id": "TESTE"
                }
            ),
        )
        # logger.info("Sending Tx To out_box")
#         contract_api_msg.counterparty = LEDGER_API_ADDRESS
 #        contract_api_dialogues.update(contract_api_msg)
        # self.context.outbox.put_message(message=contract_api_msg)

        for order in orders_to_execute:
            self.logger.info(f"Order to Execute -> {order}")

    def teardown(self) -> None:
        """
        Implement the task teardown.

        :return: None
        """
        pass
