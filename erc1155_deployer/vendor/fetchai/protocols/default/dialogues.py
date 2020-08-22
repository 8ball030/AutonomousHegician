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
This module contains the classes required for default dialogue management.

- DefaultDialogue: The dialogue class maintains state of a dialogue and manages it.
- DefaultDialogues: The dialogues class keeps track of all dialogues.
"""

from abc import ABC
from typing import Dict, FrozenSet, Optional, cast

from aea.helpers.dialogue.base import Dialogue, DialogueLabel, Dialogues
from aea.mail.base import Address
from aea.protocols.base import Message
from aea.protocols.default.message import DefaultMessage


class DefaultDialogue(Dialogue):
    """The default dialogue class maintains state of a dialogue and manages it."""

    INITIAL_PERFORMATIVES = frozenset(
        {DefaultMessage.Performative.BYTES, DefaultMessage.Performative.ERROR}
    )
    TERMINAL_PERFORMATIVES = frozenset(
        {DefaultMessage.Performative.BYTES, DefaultMessage.Performative.ERROR}
    )
    VALID_REPLIES = {
        DefaultMessage.Performative.BYTES: frozenset(
            {DefaultMessage.Performative.BYTES, DefaultMessage.Performative.ERROR}
        ),
        DefaultMessage.Performative.ERROR: frozenset(),
    }

    class Role(Dialogue.Role):
        """This class defines the agent's role in a default dialogue."""

        AGENT = "agent"

    class EndState(Dialogue.EndState):
        """This class defines the end states of a default dialogue."""

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


class DefaultDialogues(Dialogues, ABC):
    """This class keeps track of all default dialogues."""

    END_STATES = frozenset(
        {DefaultDialogue.EndState.SUCCESSFUL, DefaultDialogue.EndState.FAILED}
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
    ) -> DefaultDialogue:
        """
        Create an instance of default dialogue.

        :param dialogue_label: the identifier of the dialogue
        :param role: the role of the agent this dialogue is maintained for

        :return: the created dialogue
        """
        dialogue = DefaultDialogue(
            dialogue_label=dialogue_label, agent_address=self.agent_address, role=role
        )
        return dialogue
