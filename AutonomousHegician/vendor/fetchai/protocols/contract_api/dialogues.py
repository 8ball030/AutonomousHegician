# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2020 fetchai
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

"""
This module contains the classes required for contract_api dialogue management.

- ContractApiDialogue: The dialogue class maintains state of a dialogue and manages it.
- ContractApiDialogues: The dialogues class keeps track of all dialogues.
"""

from abc import ABC
from typing import Dict, FrozenSet, Optional, cast

from aea.helpers.dialogue.base import Dialogue, DialogueLabel, Dialogues
from aea.mail.base import Address
from aea.protocols.base import Message

from packages.fetchai.protocols.contract_api.message import ContractApiMessage


class ContractApiDialogue(Dialogue):
    """The contract_api dialogue class maintains state of a dialogue and manages it."""

    INITIAL_PERFORMATIVES = frozenset(
        {
            ContractApiMessage.Performative.GET_DEPLOY_TRANSACTION,
            ContractApiMessage.Performative.GET_RAW_TRANSACTION,
            ContractApiMessage.Performative.GET_RAW_MESSAGE,
            ContractApiMessage.Performative.GET_STATE,
        }
    )
    TERMINAL_PERFORMATIVES = frozenset(
        {
            ContractApiMessage.Performative.STATE,
            ContractApiMessage.Performative.RAW_TRANSACTION,
            ContractApiMessage.Performative.RAW_MESSAGE,
        }
    )
    VALID_REPLIES = {
        ContractApiMessage.Performative.ERROR: frozenset(),
        ContractApiMessage.Performative.GET_DEPLOY_TRANSACTION: frozenset(
            {
                ContractApiMessage.Performative.RAW_TRANSACTION,
                ContractApiMessage.Performative.ERROR,
            }
        ),
        ContractApiMessage.Performative.GET_RAW_MESSAGE: frozenset(
            {
                ContractApiMessage.Performative.RAW_MESSAGE,
                ContractApiMessage.Performative.ERROR,
            }
        ),
        ContractApiMessage.Performative.GET_RAW_TRANSACTION: frozenset(
            {
                ContractApiMessage.Performative.RAW_TRANSACTION,
                ContractApiMessage.Performative.ERROR,
            }
        ),
        ContractApiMessage.Performative.GET_STATE: frozenset(
            {
                ContractApiMessage.Performative.STATE,
                ContractApiMessage.Performative.ERROR,
            }
        ),
        ContractApiMessage.Performative.RAW_MESSAGE: frozenset(),
        ContractApiMessage.Performative.RAW_TRANSACTION: frozenset(),
        ContractApiMessage.Performative.STATE: frozenset(),
    }

    class Role(Dialogue.Role):
        """This class defines the agent's role in a contract_api dialogue."""

        AGENT = "agent"
        LEDGER = "ledger"

    class EndState(Dialogue.EndState):
        """This class defines the end states of a contract_api dialogue."""

        SUCCESSFUL = 0
        FAILED = 1

    def __init__(
        self,
        dialogue_label: DialogueLabel,
        agent_address: Optional[Address] = None,
        role: Optional[Dialogue.Role] = None,
    ) -> None:
        """
        Initialize a dialogue.

        :param dialogue_label: the identifier of the dialogue
        :param agent_address: the address of the agent for whom this dialogue is maintained
        :param role: the role of the agent this dialogue is maintained for
        :return: None
        """
        Dialogue.__init__(
            self,
            dialogue_label=dialogue_label,
            agent_address=agent_address,
            role=role,
            rules=Dialogue.Rules(
                cast(FrozenSet[Message.Performative], self.INITIAL_PERFORMATIVES),
                cast(FrozenSet[Message.Performative], self.TERMINAL_PERFORMATIVES),
                cast(
                    Dict[Message.Performative, FrozenSet[Message.Performative]],
                    self.VALID_REPLIES,
                ),
            ),
        )

    def is_valid(self, message: Message) -> bool:
        """
        Check whether 'message' is a valid next message in the dialogue.

        These rules capture specific constraints designed for dialogues which are instances of a concrete sub-class of this class.
        Override this method with your additional dialogue rules.

        :param message: the message to be validated
        :return: True if valid, False otherwise
        """
        return True


class ContractApiDialogues(Dialogues, ABC):
    """This class keeps track of all contract_api dialogues."""

    END_STATES = frozenset(
        {ContractApiDialogue.EndState.SUCCESSFUL, ContractApiDialogue.EndState.FAILED}
    )

    def __init__(self, agent_address: Address) -> None:
        """
        Initialize dialogues.

        :param agent_address: the address of the agent for whom dialogues are maintained
        :return: None
        """
        Dialogues.__init__(
            self,
            agent_address=agent_address,
            end_states=cast(FrozenSet[Dialogue.EndState], self.END_STATES),
        )

    def create_dialogue(
        self, dialogue_label: DialogueLabel, role: Dialogue.Role,
    ) -> ContractApiDialogue:
        """
        Create an instance of contract_api dialogue.

        :param dialogue_label: the identifier of the dialogue
        :param role: the role of the agent this dialogue is maintained for

        :return: the created dialogue
        """
        dialogue = ContractApiDialogue(
            dialogue_label=dialogue_label, agent_address=self.agent_address, role=role
        )
        return dialogue
