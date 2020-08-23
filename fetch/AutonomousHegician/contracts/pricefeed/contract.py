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


class MyScaffoldContract(Contract):
    """
    The scaffold contract class for an ethereum based smart contract.

    For non-ethereum based contracts import `from aea.contracts.base import Contract` and extend accordingly.
    """
    @classmethod
    def  get_custom_deploy_transaction(
            cls,
            ledger_api: LedgerApi,
            deployer_address: str,
            price: float,
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
        raise
        # create the transaction dict

        nonce = ledger_api.api.eth.getTransactionCount(deployer_address)
        instance = ledger_api.api.eth.get_instance(ledger_api, contract_address)
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