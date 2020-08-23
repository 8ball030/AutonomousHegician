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
    def create(
            cls,
            ledger_api: LedgerApi,
            contract_address: str,
            deployer_address: str,
            period: float,
            amount: float, 
            strike: float,
            data: Optional[bytes] = b"",
            gas: int = 300000,
    ) -> Dict[str, Any]:
        """
        * @nonce A provider supplies ETH to the pool and receives writeETH tokens
        * @param minMint Minimum amount of tokens that should be received by a provider.
                         Calling the provide function will require the minimum amount of tokens to be minted.
                         The actual amount that will be minted could vary but can only be higher (not lower) than the minimum value.
        * @return mint Amount of tokens to be received
        """
        # create the transaction dict
        nonce = ledger_api.api.eth.getTransactionCount(deployer_address)
        instance = cls.get_instance(ledger_api, contract_address)
        tx = instance.functions.create(deployer_address, period, amount, strike).buildTransaction({
                                                "gas": gas,
                                                "gasPrice": ledger_api.api.toWei(
                                                    "50", "gwei"
                                                    ),
                                                "nonce": nonce,
                                            })
        tx = cls._try_estimate_gas(ledger_api, tx)
        return tx

    def excercise_option(
            cls,
            ledger_api: LedgerApi,
            contract_address: str,
            deployer_address: str,
            option_id: float,
            data: Optional[bytes] = b"",
            gas: int = 300000,
    ) -> Dict[str, Any]:
        """
        * @nonce A provider supplies ETH to the pool and receives writeETH tokens
        * @param minMint Minimum amount of tokens that should be received by a provider.
                         Calling the provide function will require the minimum amount of tokens to be minted.
                         The actual amount that will be minted could vary but can only be higher (not lower) than the minimum value.
        * @return mint Amount of tokens to be received
        """
        # create the transaction dict
        nonce = ledger_api.api.eth.getTransactionCount(deployer_address)
        instance = cls.get_instance(ledger_api, contract_address)
        tx = instance.functions.excercise(deployer_address, option_id).buildTransaction({
                                                "gas": gas,
                                                "gasPrice": ledger_api.api.toWei(
                                                    "50", "gwei"
                                                    ),
                                                "nonce": nonce,
                                            })
        tx = cls._try_estimate_gas(ledger_api, tx)
        return tx

