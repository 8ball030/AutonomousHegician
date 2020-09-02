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
from aea.mail.base import Address
import os
import json
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import text

engine = create_engine("postgresql://admin:WKLpwoDJd03DJ423DJwlDJlaDJsdDJsdDJlDJsa@postgresdb:5432/cortex")

logger = logging.getLogger("aea.packages.fetchai.contracts.ethpool")
logger.setLevel(logging.INFO)


class MyScaffoldContract(Contract):
    """
    The scaffold contract class for an ethereum based smart contract.

    For non-ethereum based contracts import `from aea.contracts.base import Contract` and extend accordingly.
    """

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
        contract_interface = cls.contract_interface.get(ledger_api.identifier, {})
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
    def options_exercise(
        cls,
        ledger_api: LedgerApi,
        contract_address: Address,
        deployer_address: Address,
        option_db_id: int,
        option_ledger_id: int,
        data: Optional[bytes] = b"",
        gas: int = 300000,
    ) -> Dict[str, Any]:
        """
        Get the transaction to create a single token.
        :param ledger_api: the ledger API
        :param contract_address: the address of the contract
        :param deployer_address: the address of the deployer
        :param token_id: the token id for creation
        :param data: the data to include in the transaction
        :param gas: the gas to be used
        :return: the transaction object
        """
        # create the transaction dict
        logger.info(f"Requesting to Exercise {option_ledger_id}**")
        nonce = ledger_api.api.eth.getTransactionCount(deployer_address)
        instance = cls.get_instance(ledger_api, contract_address)
        tx = instance.functions.exercise(
            option_ledger_id
        ).buildTransaction(
            {
                "from": deployer_address,
                "gas": gas,
                "gasPrice": ledger_api.api.toWei("50", "gwei"),
                "nonce": nonce,
                "value": 0
            }
        )
        cls._update_option_contract(option_db_id, params={"ledger_id": option_ledger_id,
                                                          "status_code_id": 4})
        tx = cls._try_estimate_gas(ledger_api, tx)
        return tx

    @classmethod
    def options_create_call_option(
        cls,
        ledger_api: LedgerApi,
        contract_address: Address,
        deployer_address: Address,
        option_db_id: int,
        amount: int,
        period: int,
        strike_price: int,
        fees: List[int],
        data: Optional[bytes] = b"",
        gas: int = 300000,
    ) -> Dict[str, Any]:
        """
        Get the transaction to create a single token.
        :param ledger_api: the ledger API
        :param contract_address: the address of the contract
        :param deployer_address: the address of the deployer
        :param token_id: the token id for creation
        :param data: the data to include in the transaction
        :param gas: the gas to be used
        :return: the transaction object
        """
        # create the transaction dict
        nonce = ledger_api.api.eth.getTransactionCount(deployer_address)
        instance = cls.get_instance(ledger_api, contract_address)
        fee_estimate = instance.functions.fees(
            int(period), int(amount), int(strike_price)
        ).call()
        tx = instance.functions.create(
            period, amount, strike_price
        ).buildTransaction(
            {
                "from": deployer_address,
                "gas": gas,
                "gasPrice": ledger_api.api.toWei("50", "gwei"),
                "nonce": nonce,
                "value": fee_estimate[0]
            }
        )
        ledger_id = instance.functions.create(
            period, amount, strike_price
        ).call(
            {
                "from": deployer_address,
                "gas": gas,
                "gasPrice": ledger_api.api.toWei("50", "gwei"),
                "nonce": nonce,
                "value": fee_estimate[0]
            }
        )
        cls._update_option_contract(option_db_id, params={"ledger_id": ledger_id,
                                                          "status_code_id": 2})
        tx = cls._try_estimate_gas(ledger_api, tx)
        return tx

    @classmethod
    def options_estimate(
        cls,
        ledger_api: LedgerApi,
        contract_address: Address,
        deployer_address: Address,
        option_db_id: int,
        amount: int,
        period: int,
        strike_price: int,
        data: Optional[bytes] = b"",
        gas: int = 300000,
    ) -> Dict[str, Any]:
        """
        Get the transaction to create a single token.
        :param ledger_api: the ledger API
        :param contract_address: the address of the contract
        :param deployer_address: the address of the deployer
        :param token_id: the token id for creation
        :param data: the data to include in the transaction
        :param gas: the gas to be used
        :return: the transaction object
        """
        # create the transaction dict
        nonce = ledger_api.api.eth.getTransactionCount(deployer_address)
        instance = cls.get_instance(ledger_api, contract_address)
        tx = instance.functions.fees(
            period, amount, strike_price
        ).buildTransaction(
            {
                "from": deployer_address,
                "gas": gas,
                "gasPrice": ledger_api.api.toWei("50", "gwei"),
                "nonce": nonce,
            }
        )
        fee_estimate = instance.functions.fees(
            int(period), int(amount), int(strike_price)
        ).call()

        cls._update_option_contract(option_db_id, params={"fees": fee_estimate,
                                                          "status_code_id": 1})
        tx = cls._try_estimate_gas(ledger_api, tx)
        return tx

    @classmethod
    def _update_option_contract(cls, option_id, params):
        #option = DBCommunications.get_option(option_id)
        #option.update(params)
        #DBCommunication.update_option(option)
        with engine.connect() as con:
            
            inner_sql = []
            for k, v in params.items():
                inner_sql.append(f"{k}='{v}'")
        
            sql= f"""
            UPDATE public."Options"
	        SET {','.join(inner_sql)}
	        WHERE id={option_id};
            """
        
            statement = text(sql)
            con.execute(statement)


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
            logger.info(
                "[ethpool_contract]: gas estimate: {}".format(gas_estimate))
            tx["gas"] = gas_estimate
        except Exception as e:  # pylint: disable=broad-except
            logger.info(
                "[ethpool_contract]: Error when trying to estimate gas: {}".
                format(e))
        return tx
