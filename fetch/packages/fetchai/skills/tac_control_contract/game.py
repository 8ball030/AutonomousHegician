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

"""This package contains a class representing the game."""

import copy
import datetime
import pprint
from enum import Enum
from typing import Dict, List, Optional, cast

from aea.common import Address
from aea.exceptions import AEAEnforceError, enforce
from aea.helpers.preference_representations.base import (
    linear_utility,
    logarithmic_utility,
)
from aea.helpers.transaction.base import Terms
from aea.skills.base import Model

from packages.fetchai.protocols.tac.message import TacMessage
from packages.fetchai.skills.tac_control_contract.helpers import (
    determine_scaling_factor,
    generate_currency_endowments,
    generate_equilibrium_prices_and_holdings,
    generate_exchange_params,
    generate_good_endowments,
    generate_utility_params,
)
from packages.fetchai.skills.tac_control_contract.parameters import Parameters

GoodId = str
CurrencyId = str
Quantity = int
EquilibriumQuantity = float
Parameter = float
TransactionId = str
CurrencyEndowment = Dict[CurrencyId, Quantity]
ExchangeParams = Dict[CurrencyId, Parameter]
GoodEndowment = Dict[GoodId, Quantity]
UtilityParams = Dict[GoodId, Parameter]
EquilibriumCurrencyHoldings = Dict[CurrencyId, EquilibriumQuantity]
EquilibriumGoodHoldings = Dict[GoodId, EquilibriumQuantity]


class Phase(Enum):
    """This class defines the phases of the game."""

    PRE_GAME = "pre_game"
    CONTRACT_DEPLOYMENT_PROPOSAL = "contract_deployment_proposal"
    CONTRACT_DEPLOYING = "contract_deploying"
    CONTRACT_DEPLOYED = "contract_deployed"
    GAME_REGISTRATION = "game_registration"
    GAME_SETUP = "game_setup"
    TOKENS_CREATION_PROPOSAL = "token_creation_proposal"  # nosec
    TOKENS_CREATING = "tokens_creating"
    TOKENS_CREATED = "tokens_created"  # nosec
    TOKENS_MINTING_PROPOSAL = "token_minting_proposal"
    TOKENS_MINTING = "token_minting"  # nosec
    TOKENS_MINTED = "tokens_minted"  # nosec
    GAME = "game"
    POST_GAME = "post_game"
    CANCELLED_GAME = "cancelled_game"


class Configuration:
    """Class containing the configuration of the game."""

    def __init__(self, version_id: str, tx_fee: int):
        """
        Instantiate a game configuration.

        :param version_id: the version of the game.
        :param tx_fee: the fee for a transaction.
        """
        self._version_id = version_id
        self._tx_fee = tx_fee
        self._contract_address = None  # type: Optional[str]
        self._agent_addr_to_name = None  # type: Optional[Dict[str, str]]
        self._good_id_to_name = None  # type: Optional[Dict[str, str]]
        self._currency_id_to_name = None  # type: Optional[Dict[str, str]]

    @property
    def version_id(self) -> str:
        """Agent number of a TAC instance."""
        return self._version_id

    @property
    def tx_fee(self) -> int:
        """Transaction fee for the TAC instance."""
        return self._tx_fee

    @property
    def contract_address(self) -> str:
        """Get the contract address for the game."""
        if self._contract_address is None:
            raise AEAEnforceError("Contract_address not set yet!")
        return self._contract_address

    @contract_address.setter
    def contract_address(self, contract_address: str) -> None:
        """Set the contract address for the game."""
        enforce(self._contract_address is None, "Contract_address already set!")
        self._contract_address = contract_address

    @property
    def agent_addr_to_name(self) -> Dict[Address, str]:
        """Return the map agent addresses to names."""
        if self._agent_addr_to_name is None:
            raise AEAEnforceError("Agent_addr_to_name not set yet!")
        return self._agent_addr_to_name

    @agent_addr_to_name.setter
    def agent_addr_to_name(self, agent_addr_to_name: Dict[Address, str]) -> None:
        """Set map of agent addresses to names"""
        enforce(self._agent_addr_to_name is None, "Agent_addr_to_name already set!")
        self._agent_addr_to_name = agent_addr_to_name

    @property
    def good_id_to_name(self) -> Dict[str, str]:
        """Map good ids to names."""
        if self._good_id_to_name is None:
            raise AEAEnforceError("Good_id_to_name not set yet!")
        return self._good_id_to_name

    @good_id_to_name.setter
    def good_id_to_name(self, good_id_to_name: Dict[str, str]) -> None:
        """Set map of goods ids to names."""
        enforce(self._good_id_to_name is None, "Good_id_to_name already set!")
        self._good_id_to_name = good_id_to_name

    @property
    def currency_id_to_name(self) -> Dict[str, str]:
        """Map currency id to name."""
        if self._currency_id_to_name is None:
            raise AEAEnforceError("Currency_id_to_name not set yet!")
        return self._currency_id_to_name

    @currency_id_to_name.setter
    def currency_id_to_name(self, currency_id_to_name: Dict[str, str]) -> None:
        """Set map of currency id to name."""
        enforce(self._currency_id_to_name is None, "Currency_id_to_name already set!")
        self._currency_id_to_name = currency_id_to_name

    def check_consistency(self):
        """
        Check the consistency of the game configuration.

        :return: None
        :raises: AEAEnforceError: if some constraint is not satisfied.
        """
        enforce(self.version_id is not None, "A version id must be set.")
        enforce(self.tx_fee >= 0, "Tx fee must be non-negative.")
        enforce(len(self.agent_addr_to_name) >= 2, "Must have at least two agents.")
        enforce(len(self.good_id_to_name) >= 2, "Must have at least two goods.")
        enforce(len(self.currency_id_to_name) == 1, "Must have exactly one currency.")


class Initialization:
    """Class containing the initialization of the game."""

    def __init__(
        self,
        agent_addr_to_currency_endowments: Dict[Address, CurrencyEndowment],
        agent_addr_to_exchange_params: Dict[Address, ExchangeParams],
        agent_addr_to_good_endowments: Dict[Address, GoodEndowment],
        agent_addr_to_utility_params: Dict[Address, UtilityParams],
        good_id_to_eq_prices: Dict[GoodId, float],
        agent_addr_to_eq_good_holdings: Dict[Address, EquilibriumGoodHoldings],
        agent_addr_to_eq_currency_holdings: Dict[Address, EquilibriumCurrencyHoldings],
    ):
        """
        Instantiate a game initialization.

        :param agent_addr_to_currency_endowments: the currency endowments of the agents. A nested dict where the outer key is the agent id
                            and the inner key is the currency id.
        :param agent_addr_to_exchange_params: the exchange params representing the exchange rate the agetns use between currencies.
        :param agent_addr_to_good_endowments: the good endowments of the agents. A nested dict where the outer key is the agent id
                            and the inner key is the good id.
        :param agent_addr_to_utility_params: the utility params representing the preferences of the agents.
        :param good_id_to_eq_prices: the competitive equilibrium prices of the goods. A list.
        :param agent_addr_to_eq_good_holdings: the competitive equilibrium good holdings of the agents.
        :param agent_addr_to_eq_currency_holdings: the competitive equilibrium money holdings of the agents.
        """
        self._agent_addr_to_currency_endowments = agent_addr_to_currency_endowments
        self._agent_addr_to_exchange_params = agent_addr_to_exchange_params
        self._agent_addr_to_good_endowments = agent_addr_to_good_endowments
        self._agent_addr_to_utility_params = agent_addr_to_utility_params
        self._good_id_to_eq_prices = good_id_to_eq_prices
        self._agent_addr_to_eq_good_holdings = agent_addr_to_eq_good_holdings
        self._agent_addr_to_eq_currency_holdings = agent_addr_to_eq_currency_holdings
        self._check_consistency()

    @property
    def agent_addr_to_currency_endowments(self) -> Dict[Address, CurrencyEndowment]:
        """Get currency endowments of agents."""
        return self._agent_addr_to_currency_endowments

    @property
    def agent_addr_to_exchange_params(self) -> Dict[Address, ExchangeParams]:
        """Get exchange params of agents."""
        return self._agent_addr_to_exchange_params

    @property
    def agent_addr_to_good_endowments(self) -> Dict[Address, GoodEndowment]:
        """Get good endowments of the agents."""
        return self._agent_addr_to_good_endowments

    @property
    def agent_addr_to_utility_params(self) -> Dict[Address, UtilityParams]:
        """Get utility parameters of agents."""
        return self._agent_addr_to_utility_params

    @property
    def good_id_to_eq_prices(self) -> Dict[GoodId, float]:
        """Get theoretical equilibrium prices (a benchmark)."""
        return self._good_id_to_eq_prices

    @property
    def agent_addr_to_eq_good_holdings(self) -> Dict[Address, EquilibriumGoodHoldings]:
        """Get theoretical equilibrium good holdings (a benchmark)."""
        return self._agent_addr_to_eq_good_holdings

    @property
    def agent_addr_to_eq_currency_holdings(
        self,
    ) -> Dict[Address, EquilibriumCurrencyHoldings]:
        """Get theoretical equilibrium currency holdings (a benchmark)."""
        return self._agent_addr_to_eq_currency_holdings

    def _check_consistency(self):
        """
        Check the consistency of the game configuration.

        :return: None
        :raises: AEAEnforceError: if some constraint is not satisfied.
        """
        enforce(
            all(
                c_e >= 0
                for currency_endowments in self.agent_addr_to_currency_endowments.values()
                for c_e in currency_endowments.values()
            ),
            "Currency endowments must be non-negative.",
        )
        enforce(
            all(
                p > 0
                for params in self.agent_addr_to_exchange_params.values()
                for p in params.values()
            ),
            "ExchangeParams must be strictly positive.",
        )
        enforce(
            all(
                g_e > 0
                for good_endowments in self.agent_addr_to_good_endowments.values()
                for g_e in good_endowments.values()
            ),
            "Good endowments must be strictly positive.",
        )
        enforce(
            all(
                p > 0
                for params in self.agent_addr_to_utility_params.values()
                for p in params.values()
            ),
            "UtilityParams must be strictly positive.",
        )
        enforce(
            len(self.agent_addr_to_good_endowments.keys())
            == len(self.agent_addr_to_currency_endowments.keys()),
            "Length of endowments must be the same.",
        )
        enforce(
            len(self.agent_addr_to_exchange_params.keys())
            == len(self.agent_addr_to_utility_params.keys()),
            "Length of params must be the same.",
        )
        enforce(
            all(
                len(self.good_id_to_eq_prices.values()) == len(eq_good_holdings)
                for eq_good_holdings in self.agent_addr_to_eq_good_holdings.values()
            ),
            "Length of eq_prices and an element of eq_good_holdings must be the same.",
        )
        enforce(
            len(self.agent_addr_to_eq_good_holdings.values())
            == len(self.agent_addr_to_eq_currency_holdings.values()),
            "Length of eq_good_holdings and eq_currency_holdings must be the same.",
        )
        enforce(
            all(
                len(self.agent_addr_to_exchange_params[agent_addr]) == len(endowments)
                for agent_addr, endowments in self.agent_addr_to_currency_endowments.items()
            ),
            "Dimensions for exchange_params and currency_endowments rows must be the same.",
        )
        enforce(
            all(
                len(self.agent_addr_to_utility_params[agent_addr]) == len(endowments)
                for agent_addr, endowments in self.agent_addr_to_good_endowments.items()
            ),
            "Dimensions for utility_params and good_endowments rows must be the same.",
        )


class Transaction(Terms):
    """Convenience representation of a transaction."""

    def __init__(
        self,
        ledger_id: str,
        sender_address: Address,
        counterparty_address: Address,
        amount_by_currency_id: Dict[str, int],
        quantities_by_good_id: Dict[str, int],
        is_sender_payable_tx_fee: bool,
        nonce: str,
        fee_by_currency_id: Optional[Dict[str, int]],
        sender_signature: str,
        counterparty_signature: str,
    ) -> None:
        """
        Instantiate transaction.

        This extends a terms object to be used as a transaction.

        :param ledger_id: the ledger on which the terms are to be settled.
        :param sender_address: the sender address of the transaction.
        :param counterparty_address: the counterparty address of the transaction.
        :param amount_by_currency_id: the amount by the currency of the transaction.
        :param quantities_by_good_id: a map from good id to the quantity of that good involved in the transaction.
        :param is_sender_payable_tx_fee: whether the sender or counterparty pays the tx fee.
        :param nonce: nonce to be included in transaction to discriminate otherwise identical transactions.
        :param fee_by_currency_id: the fee associated with the transaction.
        :param sender_signature: the signature of the terms by the sender.
        :param counterparty_signature: the signature of the terms by the counterparty.
        """
        super().__init__(
            ledger_id=ledger_id,
            sender_address=sender_address,
            counterparty_address=counterparty_address,
            amount_by_currency_id=amount_by_currency_id,
            quantities_by_good_id=quantities_by_good_id,
            is_sender_payable_tx_fee=is_sender_payable_tx_fee,
            nonce=nonce,
            fee_by_currency_id=fee_by_currency_id,
        )
        self._sender_signature = sender_signature
        self._counterparty_signature = counterparty_signature

    @property
    def sender_signature(self) -> str:
        """Get the sender signature."""
        return self._sender_signature

    @property
    def counterparty_signature(self) -> str:
        """Get the counterparty signature."""
        return self._counterparty_signature

    @classmethod
    def from_message(cls, message: TacMessage) -> "Transaction":
        """
        Create a transaction from a proposal.

        :param message: the message
        :return: Transaction
        """
        enforce(
            message.performative == TacMessage.Performative.TRANSACTION,
            "Wrong performative",
        )
        transaction = Transaction(
            ledger_id=message.ledger_id,
            sender_address=message.sender_address,
            counterparty_address=message.counterparty_address,
            amount_by_currency_id=message.amount_by_currency_id,
            fee_by_currency_id=message.fee_by_currency_id,
            quantities_by_good_id=message.quantities_by_good_id,
            is_sender_payable_tx_fee=True,
            nonce=str(message.nonce),
            sender_signature=message.sender_signature,
            counterparty_signature=message.counterparty_signature,
        )
        enforce(
            transaction.id == message.transaction_id,
            "Transaction content does not match hash.",
        )
        return transaction

    def __eq__(self, other):
        """Compare to another object."""
        return (
            isinstance(other, Transaction)
            and super.__eq__()
            and self.sender_signature == other.sender_signature
            and self.counterparty_signature == other.counterparty_signature
        )


class AgentState:
    """Represent the state of an agent during the game."""

    def __init__(
        self,
        agent_address: Address,
        amount_by_currency_id: Dict[CurrencyId, Quantity],
        exchange_params_by_currency_id: Dict[CurrencyId, Parameter],
        quantities_by_good_id: Dict[GoodId, Quantity],
        utility_params_by_good_id: Dict[GoodId, Parameter],
    ):
        """
        Instantiate an agent state object.

        :param agent_address: the agent address
        :param amount_by_currency_id: the amount for each currency
        :param exchange_params_by_currency_id: the exchange parameters of the different currencies
        :param quantities_by_good_id: the quantities for each good.
        :param utility_params_by_good_id: the utility params for every good.
        """
        enforce(
            len(amount_by_currency_id.keys())
            == len(exchange_params_by_currency_id.keys()),
            "Different number of elements in amount_by_currency_id and exchange_params_by_currency_id.",
        )
        enforce(
            len(quantities_by_good_id.keys()) == len(utility_params_by_good_id.keys()),
            "Different number of elements in quantities_by_good_id and utility_params_by_good_id.",
        )
        self._agent_address = agent_address
        self._amount_by_currency_id = copy.copy(amount_by_currency_id)
        self._exchange_params_by_currency_id = copy.copy(exchange_params_by_currency_id)
        self._quantities_by_good_id = quantities_by_good_id
        self._utility_params_by_good_id = copy.copy(utility_params_by_good_id)

    @property
    def agent_address(self) -> str:
        """Get address of the agent which state that is."""
        return self._agent_address

    @property
    def amount_by_currency_id(self) -> Dict[CurrencyId, Quantity]:
        """Get the amount for each currency."""
        return copy.copy(self._amount_by_currency_id)

    @property
    def exchange_params_by_currency_id(self) -> Dict[CurrencyId, Parameter]:
        """Get the exchange parameters for each currency."""
        return copy.copy(self._exchange_params_by_currency_id)

    @property
    def quantities_by_good_id(self) -> Dict[GoodId, Quantity]:
        """Get holding of each good."""
        return copy.copy(self._quantities_by_good_id)

    @property
    def utility_params_by_good_id(self) -> Dict[GoodId, Parameter]:
        """Get utility parameter for each good."""
        return copy.copy(self._utility_params_by_good_id)

    def get_score(self) -> float:
        """
        Compute the score of the current state.

        The score is computed as the sum of all the utilities for the good holdings
        with positive quantity plus the money left.
        :return: the score.
        """
        goods_score = logarithmic_utility(
            self.utility_params_by_good_id, self.quantities_by_good_id
        )
        money_score = linear_utility(
            self.exchange_params_by_currency_id, self.amount_by_currency_id
        )
        score = goods_score + money_score
        return score

    def is_consistent_transaction(self, tx: Transaction) -> bool:
        """
        Check if the transaction is consistent.

        E.g. check that the agent state has enough money if it is a buyer
        or enough holdings if it is a seller.
        :return: True if the transaction is legal wrt the current state, False otherwise.
        """
        result = self.agent_address in [tx.sender_address, tx.counterparty_address]
        result = result and tx.is_single_currency
        if not result:
            return result
        if all(amount == 0 for amount in tx.amount_by_currency_id.values()) and all(
            quantity == 0 for quantity in tx.quantities_by_good_id.values()
        ):
            # reject the transaction when there is no wealth exchange
            result = False
        elif all(amount <= 0 for amount in tx.amount_by_currency_id.values()) and all(
            quantity >= 0 for quantity in tx.quantities_by_good_id.values()
        ):
            # sender is buyer, counterparty is seller
            if self.agent_address == tx.sender_address:
                # check this sender state has enough money
                result = result and (
                    self.amount_by_currency_id[tx.currency_id]
                    >= tx.sender_payable_amount
                )
            elif self.agent_address == tx.counterparty_address:
                # check this counterparty state has enough goods
                result = result and all(
                    self.quantities_by_good_id[good_id] >= quantity
                    for good_id, quantity in tx.quantities_by_good_id.items()
                )
        elif all(amount >= 0 for amount in tx.amount_by_currency_id.values()) and all(
            quantity <= 0 for quantity in tx.quantities_by_good_id.values()
        ):
            # sender is seller, counterparty is buyer
            # Note, on a ledger, this atomic swap would only be possible for amount == 0!
            if self.agent_address == tx.sender_address:
                # check this sender state has enough goods
                result = result and all(
                    self.quantities_by_good_id[good_id] >= -quantity
                    for good_id, quantity in tx.quantities_by_good_id.items()
                )
            elif self.agent_address == tx.counterparty_address:
                # check this counterparty state has enough money
                result = result and (
                    self.amount_by_currency_id[tx.currency_id]
                    >= tx.counterparty_payable_amount
                )
        else:
            result = False
        return result

    def apply(self, transactions: List[Transaction]) -> "AgentState":
        """
        Apply a list of transactions to the current state.

        :param transactions: the sequence of transaction.
        :return: the final state.
        """
        new_state = copy.copy(self)
        for tx in transactions:
            new_state.update(tx)

        return new_state

    def update(self, tx: Transaction) -> None:
        """
        Update the agent state from a transaction.

        :param tx: the transaction.
        :return: None
        """
        enforce(self.is_consistent_transaction(tx), "Inconsistent transaction.")

        new_amount_by_currency_id = self.amount_by_currency_id
        if self.agent_address == tx.sender_address:
            # settling the transaction for the sender
            for currency_id, amount in tx.amount_by_currency_id.items():
                new_amount_by_currency_id[currency_id] += amount
        elif self.agent_address == tx.counterparty_address:
            # settling the transaction for the counterparty
            for currency_id, amount in tx.amount_by_currency_id.items():
                new_amount_by_currency_id[currency_id] += amount

        self._amount_by_currency_id = new_amount_by_currency_id

        new_quantities_by_good_id = self.quantities_by_good_id
        for good_id, quantity in tx.quantities_by_good_id.items():
            if self.agent_address == tx.sender_address:
                new_quantities_by_good_id[good_id] += quantity
            elif self.agent_address == tx.counterparty_address:
                new_quantities_by_good_id[good_id] -= quantity
        self._quantities_by_good_id = new_quantities_by_good_id

    def __copy__(self):
        """Copy the object."""
        return AgentState(
            self.agent_address,
            self.amount_by_currency_id,
            self.exchange_params_by_currency_id,
            self.quantities_by_good_id,
            self.utility_params_by_good_id,
        )

    def __str__(self):
        """From object to string."""
        return "AgentState{}".format(
            pprint.pformat(
                {
                    "agent_address": self.agent_address,
                    "amount_by_currency_id": self.amount_by_currency_id,
                    "exchange_params_by_currency_id": self.exchange_params_by_currency_id,
                    "quantities_by_good_id": self.quantities_by_good_id,
                    "utility_params_by_good_id": self.utility_params_by_good_id,
                }
            )
        )

    def __eq__(self, other) -> bool:
        """Compare equality of two instances of the class."""
        return (
            isinstance(other, AgentState)
            and self.agent_address == other.agent_address
            and self.amount_by_currency_id == other.amount_by_currency_id
            and self.exchange_params_by_currency_id
            == other.exchange_params_by_currency_id
            and self.quantities_by_good_id == other.quantities_by_good_id
            and self.utility_params_by_good_id == other.utility_params_by_good_id
        )


class Transactions:
    """Class managing the transactions."""

    def __init__(self):
        """Instantiate the transaction class."""
        self._confirmed = {}  # type: Dict[datetime.datetime, Transaction]
        self._confirmed_per_agent = (
            {}
        )  # type: Dict[Address, Dict[datetime.datetime, Transaction]]

    @property
    def confirmed(self) -> Dict[datetime.datetime, Transaction]:
        """Get the confirmed transactions."""
        return self._confirmed

    @property
    def confirmed_per_agent(
        self,
    ) -> Dict[Address, Dict[datetime.datetime, Transaction]]:
        """Get the confirmed transactions by agent."""
        return self._confirmed_per_agent

    def add(self, transaction: Transaction) -> None:
        """
        Add a confirmed transaction.

        :param transaction: the transaction
        :return: None
        """
        now = datetime.datetime.now()
        self._confirmed[now] = transaction
        if self._confirmed_per_agent.get(transaction.sender_address) is None:
            self._confirmed_per_agent[transaction.sender_address] = {}
        self._confirmed_per_agent[transaction.sender_address][now] = transaction
        if self._confirmed_per_agent.get(transaction.counterparty_address) is None:
            self._confirmed_per_agent[transaction.counterparty_address] = {}
        self._confirmed_per_agent[transaction.counterparty_address][now] = transaction


class Registration:
    """Class managing the registration of the game."""

    def __init__(self):
        """Instantiate the registration class."""
        self._agent_addr_to_name = {}  # type: Dict[str, str]

    @property
    def agent_addr_to_name(self) -> Dict[str, str]:
        """Get the registered agent addresses and their names."""
        return self._agent_addr_to_name

    @property
    def nb_agents(self) -> int:
        """Get the number of registered agents."""
        return len(self._agent_addr_to_name)

    def register_agent(self, agent_addr: Address, agent_name: str) -> None:
        """
        Register an agent.

        :param agent_addr: the Address of the agent
        :param agent_name: the name of the agent
        :return: None
        """
        self._agent_addr_to_name[agent_addr] = agent_name

    def unregister_agent(self, agent_addr: Address) -> None:
        """
        Register an agent.

        :param agent_addr: the Address of the agent
        :return: None
        """
        self._agent_addr_to_name.pop(agent_addr)


class ContractManager:
    """Class managing the contract."""

    def __init__(self):
        """Instantiate the contract manager class."""
        self._deploy_tx_digest = None  # type: Optional[str]
        self._create_tokens_tx_digest = None  # type: Optional[str]
        self._mint_tokens_tx_digests = {}  # type: Dict[str, str]
        self._confirmed_mint_tokens_agents = []  # type: List[str, str]

    @property
    def deploy_tx_digest(self) -> str:
        """Get the contract deployment tx digest."""
        if self._deploy_tx_digest is None:
            raise AEAEnforceError("Deploy_tx_digest is not set yet!")
        return self._deploy_tx_digest

    @deploy_tx_digest.setter
    def deploy_tx_digest(self, deploy_tx_digest: str) -> None:
        """Set the contract deployment tx digest."""
        enforce(self._deploy_tx_digest is None, "Deploy_tx_digest already set!")
        self._deploy_tx_digest = deploy_tx_digest

    @property
    def create_tokens_tx_digest(self) -> str:
        """Get the contract deployment tx digest."""
        if self._create_tokens_tx_digest is None:
            raise AEAEnforceError("Create_tokens_tx_digest is not set yet!")
        return self._create_tokens_tx_digest

    @create_tokens_tx_digest.setter
    def create_tokens_tx_digest(self, create_tokens_tx_digest: str) -> None:
        """Set the contract deployment tx digest."""
        enforce(
            self._create_tokens_tx_digest is None,
            "Create_tokens_tx_digest already set!",
        )
        self._create_tokens_tx_digest = create_tokens_tx_digest

    @property
    def mint_tokens_tx_digests(self) -> Dict[str, str]:
        """Get the mint tokens tx digests."""
        return self._mint_tokens_tx_digests

    def set_mint_tokens_tx_digest(self, agent_addr: str, tx_digest: str) -> None:
        """
        Set a mint token tx digest for an agent.

        :param agent_addr: the agent addresss
        :param tx_digest: the transaction digest
        """
        enforce(
            agent_addr not in self._mint_tokens_tx_digests, "Tx digest already set."
        )
        self._mint_tokens_tx_digests[agent_addr] = tx_digest

    @property
    def confirmed_mint_tokens_agents(self) -> List[str]:
        """Get the agents which are confirmed to have minted tokens on chain."""
        return self._confirmed_mint_tokens_agents

    def add_confirmed_mint_tokens_agents(self, agent_addr: str) -> None:
        """
        Set agent addresses whose tokens have been minted.

        :param agent_addr: the agent address
        """
        enforce(
            agent_addr not in self.confirmed_mint_tokens_agents,
            "Agent already in list.",
        )
        self._confirmed_mint_tokens_agents.append(agent_addr)


class Game(Model):
    """A class to manage a TAC instance."""

    def __init__(self, **kwargs):
        """Instantiate the search class."""
        super().__init__(**kwargs)
        self._phase = Phase.PRE_GAME
        self._registration = Registration()
        self._contract_manager = ContractManager()
        self._conf = None  # type: Optional[Configuration]
        self._initialization = None  # type: Optional[Initialization]
        self._initial_agent_states = None  # type: Optional[Dict[str, AgentState]]
        self._current_agent_states = None  # type: Optional[Dict[str, AgentState]]
        self._transactions = Transactions()

    @property
    def phase(self) -> Phase:
        """Get the game phase."""
        return self._phase

    @phase.setter
    def phase(self, phase: Phase) -> None:
        """Set the game phase."""
        self.context.logger.debug("Game phase set to: {}".format(phase))
        self._phase = phase

    @property
    def registration(self) -> Registration:
        """Get the registration."""
        return self._registration

    @property
    def contract_manager(self) -> ContractManager:
        """Get the contract manager."""
        return self._contract_manager

    @property
    def conf(self) -> Configuration:
        """Get game configuration."""
        if self._conf is None:
            raise AEAEnforceError("Call create before calling configuration.")
        return self._conf

    @conf.setter
    def conf(self, configuration: Configuration):
        """Set the configuration."""
        enforce(self._conf is None, "Configuration already set!.")
        self._conf = configuration

    @property
    def initialization(self) -> Initialization:
        """Get game initialization."""
        if self._initialization is None:
            raise AEAEnforceError("Call create before calling initialization.")
        return self._initialization

    @property
    def initial_agent_states(self) -> Dict[str, AgentState]:
        """Get initial state of each agent."""
        if self._initial_agent_states is None:
            raise AEAEnforceError("Call create before calling initial_agent_states.")
        return self._initial_agent_states

    @property
    def current_agent_states(self) -> Dict[str, AgentState]:
        """Get current state of each agent."""
        if self._current_agent_states is None:
            raise AEAEnforceError("Call create before calling current_agent_states.")
        return self._current_agent_states

    @property
    def transactions(self) -> Transactions:
        """Get the transactions."""
        return self._transactions

    def create(self):
        """Create a game."""
        enforce(self.phase.value == Phase.GAME_SETUP.value, "Wrong game phase.")
        self.context.logger.info("setting Up the TAC game.")
        self._generate()

    def _generate(self):
        """Generate a TAC game."""
        parameters = cast(Parameters, self.context.parameters)
        self.conf.agent_addr_to_name = self.registration.agent_addr_to_name
        self.conf.check_consistency()

        scaling_factor = determine_scaling_factor(parameters.money_endowment)

        agent_addr_to_currency_endowments = generate_currency_endowments(
            list(self.conf.agent_addr_to_name.keys()),
            list(self.conf.currency_id_to_name.keys()),
            parameters.money_endowment,
        )

        agent_addr_to_exchange_params = generate_exchange_params(
            list(self.conf.agent_addr_to_name.keys()),
            list(self.conf.currency_id_to_name.keys()),
        )

        agent_addr_to_good_endowments = generate_good_endowments(
            list(self.conf.agent_addr_to_name.keys()),
            list(self.conf.good_id_to_name.keys()),
            parameters.base_good_endowment,
            parameters.lower_bound_factor,
            parameters.upper_bound_factor,
        )

        agent_addr_to_utility_params = generate_utility_params(
            list(self.conf.agent_addr_to_name.keys()),
            list(self.conf.good_id_to_name.keys()),
            scaling_factor,
        )

        (
            good_id_to_eq_prices,
            agent_addr_to_eq_good_holdings,
            agent_addr_to_eq_currency_holdings,
        ) = generate_equilibrium_prices_and_holdings(
            agent_addr_to_good_endowments,
            agent_addr_to_utility_params,
            agent_addr_to_currency_endowments,
            agent_addr_to_exchange_params,
            scaling_factor,
        )

        self._initialization = Initialization(
            agent_addr_to_currency_endowments,
            agent_addr_to_exchange_params,
            agent_addr_to_good_endowments,
            agent_addr_to_utility_params,
            good_id_to_eq_prices,
            agent_addr_to_eq_good_holdings,
            agent_addr_to_eq_currency_holdings,
        )

        self._initial_agent_states = dict(
            (
                agent_addr,
                AgentState(
                    agent_addr,
                    self.initialization.agent_addr_to_currency_endowments[agent_addr],
                    self.initialization.agent_addr_to_exchange_params[agent_addr],
                    self.initialization.agent_addr_to_good_endowments[agent_addr],
                    self.initialization.agent_addr_to_utility_params[agent_addr],
                ),
            )
            for agent_addr in self.conf.agent_addr_to_name.keys()
        )

        self._current_agent_states = dict(
            (
                agent_addr,
                AgentState(
                    agent_addr,
                    self.initialization.agent_addr_to_currency_endowments[agent_addr],
                    self.initialization.agent_addr_to_exchange_params[agent_addr],
                    self.initialization.agent_addr_to_good_endowments[agent_addr],
                    self.initialization.agent_addr_to_utility_params[agent_addr],
                ),
            )
            for agent_addr in self.conf.agent_addr_to_name.keys()
        )

    @property
    def holdings_summary(self) -> str:
        """Get holdings summary (a string representing the holdings for every agent)."""
        result = "\n" + "Current good & money allocation & score: \n"
        for agent_addr, agent_state in self.current_agent_states.items():
            result = (
                result + "- " + self.conf.agent_addr_to_name[agent_addr] + ":" + "\n"
            )
            for good_id, quantity in agent_state.quantities_by_good_id.items():
                result += (
                    "    "
                    + self.conf.good_id_to_name[good_id]
                    + ": "
                    + str(quantity)
                    + "\n"
                )
            for currency_id, amount in agent_state.amount_by_currency_id.items():
                result += (
                    "    "
                    + self.conf.currency_id_to_name[currency_id]
                    + ": "
                    + str(amount)
                    + "\n"
                )
            result += "    score: " + str(round(agent_state.get_score(), 2)) + "\n"
        result = result + "\n"
        return result

    @property
    def equilibrium_summary(self) -> str:
        """Get equilibrium summary."""
        result = "\n" + "Equilibrium prices: \n"
        for good_id, eq_price in self.initialization.good_id_to_eq_prices.items():
            result = (
                result + self.conf.good_id_to_name[good_id] + " " + str(eq_price) + "\n"
            )
        result = result + "\n"
        result = result + "Equilibrium good allocation: \n"
        for (
            agent_addr,
            eq_allocations,
        ) in self.initialization.agent_addr_to_eq_good_holdings.items():
            result = result + "- " + self.conf.agent_addr_to_name[agent_addr] + ":\n"
            for good_id, quantity in eq_allocations.items():
                result = (
                    result
                    + "    "
                    + self.conf.good_id_to_name[good_id]
                    + ": "
                    + str(quantity)
                    + "\n"
                )
        result = result + "\n"
        result = result + "Equilibrium money allocation: \n"
        for (
            agent_addr,
            eq_allocation,
        ) in self.initialization.agent_addr_to_eq_currency_holdings.items():
            result = (
                result
                + self.conf.agent_addr_to_name[agent_addr]
                + " "
                + str(eq_allocation)
                + "\n"
            )
        result = result + "\n"
        return result
