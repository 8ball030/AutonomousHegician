"""Tests of the AH."""

import json
import os
import subprocess
import sys
import time
import unittest
from copy import deepcopy
from datetime import datetime, timedelta
from multiprocessing import Process

import web3
import yaml


# we need access to the database, so we will piggy back off the option monitoring skill

try:
    sys.path += [os.path.sep.join(os.getcwd().split(os.path.sep)[:-1])]
    from agents.autonomous_hegician.skills.option_management.db_communication import (
        CLOSED,
        DBCommunication,
        EXPIRED,
        OPEN,
    )

except ImportError as e:
    raise e


def setup_db():
    ds = DBCommunication()
    ds.add_data()
    return ds


# the ah must be run in demo mode after the hegicContractDeployer has deployed the contracts to a local ganache cli

w3 = web3.Web3(web3.HTTPProvider("http://127.0.0.1:7545"))
w3.isConnected()
deployer_address = w3.eth.coinbase


def launch_autonomous_hegician():
    """Emulate the AH launch."""
    command = "cd autonomous_hegician/; aea -s run"
    p = Process(target=subprocess.run, args=[command], kwargs={"shell": True})
    p.start()
    time.sleep(10)  # give it time to start up
    return p


def get_current_addresses():
    with open("./autonomous_hegician/skills/option_management/skill.yaml", "r") as f:
        return {
            k: v
            for k, v in yaml.safe_load(f)["models"]["strategy"]["args"].items()
            if k != "ledger_id"
        }


def load_contracts(addresses):
    """Read in the contracts from the agent."""
    mapping = {
        "priceprovider": "FakePriceProvider.json",
        "ethoptions": "HegicETHOptions.json",
        "ethpool": "HegicETHPool.json",
        "ethpriceprovider": "FakeETHPriceProvider.json",
        "btcoptions": "HegicWBTCOptions.json",
        "btcpool": "HegicERCPool.json",
        "btcpriceprovider": "FakeBTCPriceProvider.json",
        "exchange": "FakeExchange.json",
        "hegic": "FakeHEGIC.json",
        "wbtc": "FakeWBTC.json",
        "stakingeth": "HegicStakingETH.json",
        "stakingwbtc": "HegicStakingWBTC.json",
    }
    contracts = {}
    for contract, address in addresses.items():
        with open(
            f"./hegic_deployer/contracts/{contract}/build/contracts/{mapping[contract]}",
            "r",
        ) as f:
            c = json.loads(f.read())
            contracts[contract] = w3.eth.contract(address=address, abi=c["abi"])
    return contracts


class TestOptionExecutionTester(unittest.TestCase):
    def set_btc_price(price):
        pass

    def set_price(self, new_price, provider):
        price_provider = self.contracts[provider]
        price_provider.functions.setPrice(new_price).transact(
            {"from": deployer_address}
        )

    def tearDown(self):
        DBCommunication.delete_options()

    order_params = {
        "amount": 10000000,
        "strike_price": 200,
        "period": 60 * 60 * 24 * 2,
        "option_type": 1,
        "market": "ETH",
    }

    @classmethod
    def setUpClass(cls):
        setup_db()
        cls.addresses = get_current_addresses()
        cls.contracts = load_contracts(cls.addresses)

    def test_does_ah_create_eth_put_option(self):
        # now the ah will retrieve this order from the db an execute it.
        self.set_price(self.order_params["strike_price"], "priceprovider")
        new_order = DBCommunication.create_new_option(**self.order_params)
        orders = DBCommunication.get_options()
        self.assertEqual(len(orders), 1, "Only 1 order expected as in testing!")
        self.assertTrue(self.await_order_status_code(OPEN, new_order))

    def test_does_ah_create_btc_put_option(self):
        order_params = deepcopy(self.order_params)
        order_params["market"] = "BTC"
        new_order = DBCommunication.create_new_option(**order_params)
        orders = DBCommunication.get_options()
        self.assertEqual(len(orders), 1, "Only 1 order expected as in testing!")
        self.assertTrue(self.await_order_status_code(OPEN, new_order))

    def test_does_ah_create_eth_call_option(self):
        self.set_price(self.order_params["strike_price"], "priceprovider")
        option_params = deepcopy(self.order_params)
        option_params["option_type"] = 2
        new_order = DBCommunication.create_new_option(**self.order_params)
        orders = DBCommunication.get_options()
        self.assertEqual(len(orders), 1, "Only 1 order expected as in testing!")
        self.assertTrue(self.await_order_status_code(OPEN, new_order))

    def test_does_ah_create_btc_call_option(self):
        order_params = deepcopy(self.order_params)
        order_params["market"] = "BTC"
        order_params["option_type"] = 2
        new_order = DBCommunication.create_new_option(**order_params)
        orders = DBCommunication.get_options()
        self.assertEqual(len(orders), 1, "Only 1 order expected as in testing!")
        self.assertTrue(self.await_order_status_code(OPEN, new_order))

    def test_does_ah_excercise_eth_atm_put_option(self):
        # now the ah will retrieve this order from the db an execute it.
        order_params = deepcopy(self.order_params)
        self.set_price(order_params["strike_price"], "priceprovider")
        new_order = DBCommunication.create_new_option(**order_params)
        orders = DBCommunication.get_options()
        self.assertEqual(len(orders), 1, "Only 1 order expected as in testing!")
        self.assertTrue(self.await_order_status_code(OPEN, new_order))

        expiration_date = datetime.utcnow() + timedelta(seconds=10)
        DBCommunication.update_option(
            new_order["option_id"], {"expiration_date": expiration_date}
        )
        self.assertTrue(self.await_order_status_code(4, new_order))

    def test_does_ah_excercise_itm_eth_put_option(self):
        # now the ah will retrieve this order from the db an execute it.
        order_params = deepcopy(self.order_params)
        self.set_price(int(order_params["strike_price"] * 0.95), "priceprovider")
        new_order = DBCommunication.create_new_option(**order_params)
        orders = DBCommunication.get_options()
        self.assertEqual(len(orders), 1, "Only 1 order expected as in testing!")
        self.assertTrue(self.await_order_status_code(OPEN, new_order))

        expiration_date = datetime.utcnow() + timedelta(seconds=10)
        DBCommunication.update_option(
            new_order["option_id"], {"expiration_date": expiration_date}
        )
        self.assertTrue(self.await_order_status_code(CLOSED, new_order))

    def test_does_ah_expire_otm_eth_put_option(self):
        # now the ah will retrieve this order from the db an execute it.
        order_params = deepcopy(self.order_params)
        new_order = DBCommunication.create_new_option(**order_params)
        self.set_price(int(order_params["strike_price"] * 1.05), "priceprovider")
        orders = DBCommunication.get_options()
        self.assertEqual(len(orders), 1, "Only 1 order expected as in testing!")
        self.assertTrue(self.await_order_status_code(OPEN, new_order))

        expiration_date = datetime.utcnow() + timedelta(seconds=10)
        DBCommunication.update_option(
            new_order["option_id"], {"expiration_date": expiration_date}
        )
        self.assertTrue(self.await_order_status_code(EXPIRED, new_order))

    def test_does_ah_expire_otm_eth_call_option(self):
        # now the ah will retrieve this order from the db an execute it.
        order_params = deepcopy(self.order_params)
        order_params["option_type"] = 2
        new_order = DBCommunication.create_new_option(**order_params)
        self.set_price(int(order_params["strike_price"] * 0.95), "priceprovider")
        orders = DBCommunication.get_options()
        self.assertEqual(len(orders), 1, "Only 1 order expected as in testing!")
        self.assertTrue(self.await_order_status_code(OPEN, new_order))

        expiration_date = datetime.utcnow() + timedelta(seconds=10)
        DBCommunication.update_option(
            new_order["option_id"], {"expiration_date": expiration_date}
        )
        self.assertTrue(self.await_order_status_code(EXPIRED, new_order))

    def test_does_ah_expire_otm_btc_put_option(self):
        # now the ah will retrieve this order from the db an execute it.
        order_params = deepcopy(self.order_params)
        order_params["market"] = "BTC"
        self.set_price(int(order_params["strike_price"]), "btcpriceprovider")
        new_order = DBCommunication.create_new_option(**order_params)
        self.set_price(int(order_params["strike_price"] * 1.05), "btcpriceprovider")
        orders = DBCommunication.get_options()
        self.assertEqual(len(orders), 1, "Only 1 order expected as in testing!")
        self.assertTrue(self.await_order_status_code(OPEN, new_order))

        expiration_date = datetime.utcnow() + timedelta(seconds=10)
        DBCommunication.update_option(
            new_order["option_id"], {"expiration_date": expiration_date}
        )
        self.assertTrue(self.await_order_status_code(EXPIRED, new_order))

    def test_does_ah_expire_otm_btc_call_option(self):
        # now the ah will retrieve this order from the db an execute it.
        order_params = deepcopy(self.order_params)
        order_params["option_type"] = 2
        order_params["market"] = "BTC"
        self.set_price(int(order_params["strike_price"]), "btcpriceprovider")
        new_order = DBCommunication.create_new_option(**order_params)
        self.set_price(int(order_params["strike_price"] * 0.95), "btcpriceprovider")
        orders = DBCommunication.get_options()
        self.assertEqual(len(orders), 1, "Only 1 order expected as in testing!")
        self.assertTrue(self.await_order_status_code(OPEN, new_order))

        expiration_date = datetime.utcnow() + timedelta(seconds=10)
        DBCommunication.update_option(
            new_order["option_id"], {"expiration_date": expiration_date}
        )
        self.assertTrue(self.await_order_status_code(EXPIRED, new_order))

    def await_order_status_code(self, status_code, order_params):
        done = False
        timeout = 20
        start = datetime.utcnow()
        while not done:
            if datetime.now() - timedelta(seconds=timeout) > start:
                return False
            time.sleep(1)
            order = DBCommunication.get_option(order_params["option_id"])
            if order.status_code.id == status_code:
                done = True
        return done


#   def test_does_ah_excercise_btc_call_option(self):
#       pass

#   def test_does_ah_excercise_eth_put_option(self):
#       pass

#   def test_does_ah_excercise_btc_put_option(self):
#       pass


def deploy_test_net_contract_via_ah():
    pass


def tear_down_deployer():
    # after we have conducted our tests, we can revert the deployer to null state ready for the next tests

    pass


def setup_deployer_from_config():
    pass
    # shutil.copyfile("../hegic_deployer/contract_config.yaml", "../hegic_deployer/skills/hegic_deployer/skill.yaml")


if __name__ == "__main__":
    agent = launch_autonomous_hegician()
    if True:
        unittest.main()
    else:
        partial = unittest.TestSuite()
        partial.addTests(
            [TestOptionExecutionTester("test_does_ah_excercise_eth_atm_put_option",)]
        )
        unittest.TextTestRunner().run(partial)
    agent.terminate()
    sys.exit()
    sys.run("pkill -f aea")
    quit()
