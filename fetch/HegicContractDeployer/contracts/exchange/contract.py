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

from typing import Any, Dict

from aea.contracts.base import Contract
from aea.crypto.base import LedgerApi



class FakeExchange(Contract):
    """The scaffold contract class for a smart contract."""

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

        contract_interface = cls.contract_interface.get(
            ledger_api.identifier, {})
        nonce = ledger_api.api.eth.getTransactionCount(deployer_address)
        instance = ledger_api.get_contract_instance(contract_interface)
        constructed = instance.constructor(*args)
        data = constructed.buildTransaction()['data']
        tx = {
            "from":
            deployer_address,  # only 'from' address, don't insert 'to' address!
            "value": 0,  # transfer as part of deployment
            "gas": gas,
            "gasPrice": gas,  # TODO: refine
            "nonce": nonce,
            "data": data,
        }
        tx = cls._try_estimate_gas(ledger_api, tx)
        return tx

    @classmethod
    def get_raw_transaction(
        cls, ledger_api: LedgerApi, contract_address: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Handler method for the 'GET_RAW_TRANSACTION' requests.

        Implement this method in the sub class if you want
        to handle the contract requests manually.

        :param ledger_api: the ledger apis.
        :param contract_address: the contract address.
        :return: the tx
        """
        raise NotImplementedError

    @classmethod
    def get_raw_message(
        cls, ledger_api: LedgerApi, contract_address: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Handler method for the 'GET_RAW_MESSAGE' requests.

        Implement this method in the sub class if you want
        to handle the contract requests manually.

        :param ledger_api: the ledger apis.
        :param contract_address: the contract address.
        :return: the tx
        """
        raise NotImplementedError

    @classmethod
    def get_state(
        cls, ledger_api: LedgerApi, contract_address: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Handler method for the 'GET_STATE' requests.

        Implement this method in the sub class if you want
        to handle the contract requests manually.

        :param ledger_api: the ledger apis.
        :param contract_address: the contract address.
        :return: the tx
        """
        raise NotImplementedError

    @staticmethod
    def _try_estimate_gas(ledger_api: LedgerApi,
                          tx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempts to update the transaction with a gas estimate.
        :param ledger_api: the ledger API
        :param tx: the transaction
        :return: the transaction (potentially updated)
        """
        try:
            # try estimate the gas and update the transaction dict
            gas_estimate = ledger_api.api.eth.estimateGas(transaction=tx)
            tx["gas"] = gas_estimate
        except Exception as e:  # pylint: disable=broad-except
            raise 
        return tx

