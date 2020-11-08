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

from typing import Dict, Optional, Tuple, Union

import yaml

from aea.configurations.constants import DEFAULT_LEDGER
from aea.helpers.transaction.base import Terms
from aea.skills.base import Model


DEFAULT_LEDGER_ID = DEFAULT_LEDGER


class Strategy(Model):
    """This class defines a strategy for the agent."""

    def __init__(self, **kwargs) -> None:
        """Initialize the strategy of the agent."""
        self._ledger_id = kwargs.pop("ledger_id", DEFAULT_LEDGER_ID)
        self.generate_configs = kwargs.pop("generate_configs", True)
        self.clear_configs = kwargs.pop("clear_configs", False)
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
        if self.clear_configs:
            self.clear_contracts()  # clean contracts for a fresh start

    @property
    def deployment_status(
        self,
    ) -> Dict[str, Union[Tuple[Optional[str], Optional[str]], str]]:
        """Return the deployment status."""
        return self._deployment_status

    @property
    def ledger_id(self) -> str:
        """Get the ledger id."""
        return self._ledger_id

    def create_config_yaml(self) -> None:
        """Output the contract config into a skill file."""
        if self.generate_configs is False:
            return
        self.context.logger.info("Writing the newly deployed contracts to file configs")
        agent_skill_path = "./skills/hegic_deployer/skill.yaml"
        with open(agent_skill_path) as file:
            yaml_file = yaml.safe_load(file)
        required = yaml_file["models"]["strategy"]["args"]
        output = {
            k: v[1] for k, v in self.deployment_status.items() if k in required.keys()
        }
        with open("contract_config.yaml", "w") as f:
            yaml.dump(output, f)

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
        with open(path, "w+") as f:
            yaml.dump(new_params, f)
