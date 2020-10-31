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

"""This module contains the strategy class."""

import random  # nosec
from typing import Dict, List, Optional, Tuple, Union

import yaml

from aea.configurations.constants import DEFAULT_LEDGER
from aea.exceptions import enforce
from aea.helpers.search.generic import (
    AGENT_LOCATION_MODEL,
    AGENT_REMOVE_SERVICE_MODEL,
    AGENT_SET_SERVICE_MODEL,
    SIMPLE_SERVICE_MODEL,
)
from aea.helpers.search.models import Description
from aea.helpers.transaction.base import Terms
from aea.skills.base import Model


DEFAULT_LEDGER_ID = DEFAULT_LEDGER


class Strategy(Model):
    """This class defines a strategy for the agent."""

    def __init__(self, **kwargs) -> None:
        """Initialize the strategy of the agent."""
        self._ledger_id = kwargs.pop("ledger_id", DEFAULT_LEDGER_ID)
        self._deployment_status: Dict[
            str, Union[Tuple[Optional[str], Optional[str]], str]
        ] = {}
        not_deployed = 0
        for contract in [
            "wbtc",
            "hegic",
            "priceprovider",
            "btcpriceprovider",
            "ethoptions",
            "btcoptions",
            "exchange",
            "stakingwbtc",
            "stakingeth",
            "liquidity",
            "ethpool",
            "btcpool",
            "ethoptions_estimate",
            "ethoptions_create_option",
            "ethoptions_exercise",
            "btcoptions_estimate",
            "btcoptions_create_option",
            "btcoptions_exercise",
        ]:  # post test remove
            param = kwargs.pop(contract, None)
            if param == "" or param is None:
                not_deployed += 1
                self._deployment_status[contract] = (None, None)
            else:
                self._deployment_status[contract] = ("deployed", param)

        if not_deployed >= 0:
            self._deployment_status["status"] = "pending"
        self.eth_balance = None
        super().__init__(**kwargs)
        self.context.logger.info(f"Deployment paramets {self.deployment_status}")
        self.generate_configs = True
        self._contract_address: Optional[str] = None
        self._is_contract_deployed: bool = False
        self._is_tokens_created: bool = False
        self._is_tokens_minted: bool = False
        if self.generate_configs:
            self.clear_contracts()  # clean contracts for a fresh start

    @property
    def deployment_status(self) -> dict:
        """Return the deployment status."""
        return self._deployment_status

    @property
    def ledger_id(self) -> str:
        """Get the ledger id."""
        return self._ledger_id

    @property
    def mint_quantities(self) -> List[int]:
        """Get the list of mint quantities."""
        return self._mint_quantities

    @property
    def token_ids(self) -> List[int]:
        """Get the token ids."""
        if self._token_ids is None:
            raise ValueError("Token ids not set.")
        return self._token_ids

    @property
    def contract_address(self) -> str:
        """Get the contract address."""
        if self._contract_address is None:
            raise ValueError("Contract address not set!")
        return self._contract_address

    @contract_address.setter
    def contract_address(self, contract_address: str) -> None:
        """Set the contract address."""
        enforce(self._contract_address is None, "Contract address already set!")
        self._contract_address = contract_address

    @property
    def is_contract_deployed(self) -> bool:
        """Get contract deploy status."""
        return self._is_contract_deployed

    @is_contract_deployed.setter
    def is_contract_deployed(self, is_contract_deployed: bool) -> None:
        """Set contract deploy status."""
        enforce(
            not self._is_contract_deployed and is_contract_deployed,
            "Only allowed to switch to true.",
        )
        self._is_contract_deployed = is_contract_deployed

    @property
    def is_tokens_created(self) -> bool:
        """Get token created status."""
        return self._is_tokens_created

    @is_tokens_created.setter
    def is_tokens_created(self, is_tokens_created: bool) -> None:
        """Set token created status."""
        enforce(
            not self._is_tokens_created and is_tokens_created,
            "Only allowed to switch to true.",
        )
        self._is_tokens_created = is_tokens_created

    @property
    def is_tokens_minted(self) -> bool:
        """Get token minted status."""
        return self._is_tokens_minted

    @is_tokens_minted.setter
    def is_tokens_minted(self, is_tokens_minted: bool) -> None:
        """Set token minted status."""
        enforce(
            not self._is_tokens_minted and is_tokens_minted,
            "Only allowed to switch to true.",
        )
        self._is_tokens_minted = is_tokens_minted

    def create_config_yaml(self, dev_mode: bool = True) -> None:
        """Output the contract config into a skill file."""
        if self.generate_configs is False:
            return
        agent_skill_path = "./skills/hegic_deployer/skill.yaml"
        with open(agent_skill_path) as file:
            yaml_file = yaml.safe_load(file)
        required = yaml_file["models"]["strategy"]["args"]
        output = {
            k: v[1] for k, v in self.deployment_status.items() if k in required.keys()
        }
        with open("contract_config.yaml", "w") as f:
            yaml.dump(output, f)

        # update the AH with the new contract files
        with open("../autonomous_hegician/contract_config.yaml", "w") as f:
            yaml.dump(yaml_file, f)

    def get_location_description(self) -> Description:
        """
        Get the location description.

        :return: a description of the agent's location
        """
        description = Description(
            self._agent_location, data_model=AGENT_LOCATION_MODEL,
        )
        return description

    def get_register_service_description(self) -> Description:
        """
        Get the register service description.

        :return: a description of the offered services
        """
        description = Description(
            self._set_service_data, data_model=AGENT_SET_SERVICE_MODEL,
        )
        return description

    def get_service_description(self) -> Description:
        """
        Get the simple service description.

        :return: a description of the offered services
        """
        description = Description(
            self._simple_service_data, data_model=SIMPLE_SERVICE_MODEL,
        )
        return description

    def get_unregister_service_description(self) -> Description:
        """
        Get the unregister service description.

        :return: a description of the to be removed service
        """
        description = Description(
            self._remove_service_data, data_model=AGENT_REMOVE_SERVICE_MODEL,
        )
        return description

    def get_deploy_terms(self) -> Terms:
        """
        Get deploy terms of deployment.

        :return: terms
        """
        terms = Terms(
            ledger_id=self.ledger_id,
            sender_address=self.context.agent_address,
            counterparty_address=self.context.agent_address,
            amount_by_currency_id={},
            quantities_by_good_id={},
            nonce="",
        )
        return terms

    def get_create_token_terms(self) -> Terms:
        """
        Get create token terms of deployment.

        :return: terms
        """
        terms = Terms(
            ledger_id=self.ledger_id,
            sender_address=self.context.agent_address,
            counterparty_address=self.context.agent_address,
            amount_by_currency_id={},
            quantities_by_good_id={},
            nonce="",
        )
        return terms

    def get_mint_token_terms(self) -> Terms:
        """
        Get mint token terms of deployment.

        :return: terms
        """
        terms = Terms(
            ledger_id=self.ledger_id,
            sender_address=self.context.agent_address,
            counterparty_address=self.context.agent_address,
            amount_by_currency_id={},
            quantities_by_good_id={},
            nonce="",
        )
        return terms

    def get_proposal(self) -> Description:
        """Get the proposal."""
        trade_nonce = random.randrange(  # nosec
            0, 10000000
        )  # quickfix, to avoid contract call
        token_id = self.token_ids[0]
        proposal = Description(
            {
                "contract_address": self.contract_address,
                "token_id": str(token_id),
                "trade_nonce": str(trade_nonce),
                "from_supply": str(self.from_supply),
                "to_supply": str(self.to_supply),
                "value": str(self.value),
            }
        )
        return proposal

    def get_single_swap_terms(
        self, proposal: Description, counterparty_address
    ) -> Terms:
        """Get the proposal."""
        terms = Terms(
            ledger_id=self.ledger_id,
            sender_address=self.context.agent_address,
            counterparty_address=counterparty_address,
            amount_by_currency_id={
                str(proposal.values["token_id"]): int(proposal.values["from_supply"])
                - int(proposal.values["to_supply"])
            },
            quantities_by_good_id={},
            is_sender_payable_tx_fee=True,
            nonce=str(proposal.values["trade_nonce"]),
            fee_by_currency_id={},
        )
        return terms

    def clear_contracts(self):
        path = "./skills/hegic_deployer/skill.yaml"
        with open(path) as f:
            i = yaml.safe_load(f.read())

        to_clear = [
            "btcoptions",
            "btcpool",
            "btcpriceprovider",
            "ethoptions",
            "ethpool",
            "exchange",
            "hegic",
            # 'ledger_id',
            "priceprovider",
            "stakingeth",
            "stakingwbtc",
            "wbtc",
        ]
        new_params = {
            k: "" for k, v in i["models"]["strategy"]["args"].items() if k in to_clear
        }

        path = "contract_config.yaml"
        with open(path, "w") as f:
            yaml.dump(new_params, f)
