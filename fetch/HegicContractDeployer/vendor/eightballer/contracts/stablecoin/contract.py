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

from aea.contracts.base import Contract
from aea.crypto.base import LedgerApi
from typing import List, Dict, Optional, Any
import os
import json
import logging

logger = logging.getLogger(__name__)


class MyScaffoldContract(Contract):
    """
    The scaffold contract class for an ethereum based smart contract.

    For non-ethereum based contracts import `from aea.contracts.base import Contract` and extend accordingly.
    """
    @classmethod
    def get_create_batch_transaction(
            cls,
            ledger_api: LedgerApi,
            contract_address: str,
            deployer_address: str,
            token_ids: List[int],
            data: Optional[bytes] = b"",
            gas: int = 300000,
    ) -> Dict[str, Any]:
        """
        Get the transaction to create a batch of tokens.

        :param ledger_api: the ledger API
        :param contract_address: the address of the contract
        :param deployer_address: the address of the deployer
        :param token_ids: the list of token ids for creation
        :param data: the data to include in the transaction
        :param gas: the gas to be used
        :return: the transaction object
        """
        # create the transaction dict
        nonce = ledger_api.api.eth.getTransactionCount(deployer_address)
        instance = cls.get_instance(ledger_api, contract_address)
        tx = instance.functions.createBatch(deployer_address,
                                            token_ids).buildTransaction({
                                                "gas":
                                                gas,
                                                "gasPrice":
                                                ledger_api.api.toWei(
                                                    "50", "gwei"),
                                                "nonce":
                                                nonce,
                                            })
        tx = cls._try_estimate_gas(ledger_api, tx)
        return tx

    @classmethod
    def excercise_option(
            cls,
            ledger_api: LedgerApi,
            contract_address: str,
            deployer_address: str,
            token_ids: List[int],
            data: Optional[bytes] = b"",
            gas: int = 300000,
    ) -> Dict[str, Any]:
        """
        Get the transaction to create a batch of tokens.

        :param ledger_api: the ledger API
        :param contract_address: the address of the contract
        :param deployer_address: the address of the deployer
        :param token_ids: the list of token ids for creation
        :param data: the data to include in the transaction
        :param gas: the gas to be used
        :return: the transaction object
        """
        # create the transaction dict
        nonce = ledger_api.api.eth.getTransactionCount(deployer_address)
        instance = cls.get_instance(ledger_api, contract_address)
        tx = instance.functions.createBatch(deployer_address,
                                            token_ids).buildTransaction({
                                                "gas":
                                                gas,
                                                "gasPrice":
                                                ledger_api.api.toWei(
                                                    "50", "gwei"),
                                                "nonce":
                                                nonce,
                                            })
        logger.info(
            "[STABLECOIN]: gas estimate:")
        tx = cls._try_estimate_gas(ledger_api, tx)
        return tx

    @staticmethod
    def _try_estimate_gas_(ledger_api: LedgerApi, tx: Dict[str, Any]) -> Dict[str, Any]:
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
                "[ERC1155Contract]: gas estimate: {}".format(gas_estimate))
            tx["gas"] = gas_estimate
        except Exception as e:  # pylint: disable=broad-except
            logger.info(
                "[ERC1155Contract]: Error when trying to estimate gas: {}".format(
                    e)
            )
        return tx

    @classmethod
    def _get_abi(cls, configuration):
        with open(os.getcwd() + "/contracts/stablecoin/build/contracts/FakeUSD.json", "r") as f:
            return json.loads(f.read())

    @classmethod
    def get_deploy_transaction(
            cls,
            ledger_api: LedgerApi,
            deployer_address: str,
            gas: int = 600000000000,
    ) -> Dict[str, Any]:
        """
        Get the transaction to create a batch of tokens.

        :param ledger_api: the ledger API
        :param deployer_address: the address of the deployer
        :param price: the price
        :param data: the data to include in the transaction
        :param gas: the gas to be used
        :return: the transaction object
        """
        conf = dict(name="pricefeed",
                    author="tomrae",
                    version="0.1.0",
                    license_="Apache-2.0",
                    aea_version='>=0.5.0, <0.6.0',
                    contract_interface_paths={
                        'ethereum': 'build/contracts/FakeUSD.json'}
                    )

        # ContractConfig(**conf).contract_interfaces
        contract_specs = cls._get_abi(conf)
        nonce = ledger_api.api.eth.getTransactionCount(deployer_address)
        instance = ledger_api.api.eth.contract(
            abi=contract_specs["abi"], bytecode=contract_specs["bytecode"],
        )
        constructed = instance.constructor()
        data = constructed.buildTransaction()['data']

        tx = {
            "from": deployer_address,  # only 'from' address, don't insert 'to' address!
            "value":  0,  # transfer as part of deployment
            "gas": gas,
            "gasPrice": gas,  # TODO: refine
            "nonce": nonce,
            "data": data,
        }
        tx = cls._try_estimate_gas_(ledger_api, tx)
        return tx
