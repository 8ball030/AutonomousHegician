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
"""This module contains the scaffold contract definition."""
import logging
from aea.contracts.base import Contract
from aea.crypto.base import LedgerApi
from typing import List, Dict, Optional, Any

from aea.configurations.base import ContractConfig
import os
import json

logger = logging.getLogger("aea.packages.fetchai.contracts.ethpool")


class MyScaffoldContract(Contract):
    """
    The scaffold contract class for an ethereum based smart contract.

    For non-ethereum based contracts import `from aea.contracts.base import Contract` and extend accordingly.
    """

    @classmethod
    def _get_abi(cls, configuration):
        with open(os.getcwd() + "/contracts/ethpool/" + configuration["contract_interface_paths"]["ethereum"], "r") as f:
            return json.loads(f.read())

    @classmethod
    def get_deploy_transaction(
            cls,
            ledger_api: LedgerApi,
            deployer_address: str,
            args: list,
            gas: int = 60000000,
    ) -> Dict[str, Any]:
        """
        Get the transaction to create a batch of tokens.

        :param ledger_api: the ledger API
        :param deployer_address: the address of the deployer
        :param args: the price
        :param gas: the gas to be used
        :return: the transaction object
        """
        conf = dict(name="ethpool",
                    author="tomrae",
                    version="0.1.0",
                    license_="Apache-2.0",
                    aea_version='>=0.5.0, <0.6.0',
                    contract_interface_paths={
                        'ethereum': 'build/contracts/FakeExchange.json'}
                    )

        # ContractConfig(**conf).contract_interfaces
        contract_specs = cls._get_abi(conf)
        nonce = ledger_api.api.eth.getTransactionCount(deployer_address)
        instance = ledger_api.api.eth.contract(
            abi=contract_specs["abi"], bytecode=contract_specs["bytecode"],
        )
        constructed = instance.constructor(*args)
        data = constructed.buildTransaction()['data']

        tx = {
            "from": deployer_address,  # only 'from' address, don't insert 'to' address!
            "value":  0,  # transfer as part of deployment
            "gas": gas,
            "gasPrice": gas,  # TODO: refine
            "nonce": nonce,
            "data": data,
        }
        tx = cls._try_estimate_gas(ledger_api, tx)
        return tx

    @classmethod
    def provide_liquidity(
            cls,
            ledger_api: LedgerApi,
            deployer_address: str,
            args: list,
            gas: int = 60000000,
    ) -> Dict[str, Any]:
        """
        Get the transaction to create a batch of tokens.

        :param ledger_api: the ledger API
        :param deployer_address: the address of the deployer
        :param args: the price
        :param gas: the gas to be used
        :return: the transaction object
        """
        conf = dict(name="ethpool",
                    author="tomrae",
                    version="0.1.0",
                    license_="Apache-2.0",
                    aea_version='>=0.5.0, <0.6.0',
                    contract_interface_paths={
                        'ethereum': 'build/contracts/FakeExchange.json'}
                    )

        # ContractConfig(**conf).contract_interfaces
        contract_specs = cls._get_abi(conf)
        nonce = ledger_api.api.eth.getTransactionCount(deployer_address)
        instance = ledger_api.api.eth.contract(
            abi=contract_specs["abi"], bytecode=contract_specs["bytecode"],
        )
        constructed = instance.functions.provide(*args)
        data = constructed.buildTransaction()['data']

        tx = {
            "from": deployer_address,  # only 'from' address, don't insert 'to' address!
            "value":  0,  # transfer as part of deployment
            "gas": gas,
            "gasPrice": gas,  # TODO: refine
            "nonce": nonce,
            "data": data,
        }
        tx = cls._try_estimate_gas(ledger_api, tx)
        return tx

    @staticmethod
    def _try_estimate_gas(ledger_api: LedgerApi, tx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempts to update the transaction with a gas estimate.
        :param ledger_api: the ledger API
        :param tx: the transaction
        :return: the transaction (potentially updated)
        """
        try:
            # try estimate the gas and update the transaction dict
            gas_estimate = ledger_api.api.eth.estimateGas(transaction=tx)
            logger.info(
                "[ethpool_contract]: gas estimate: {}".format(gas_estimate))
            tx["gas"] = gas_estimate
        except Exception as e:  # pylint: disable=broad-except
            logger.info(
                "[ethpool_contract]: Error when trying to estimate gas: {}".format(
                    e)
            )
        return tx
