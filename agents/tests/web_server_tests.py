"""Tests of the AH via webserver."""
import json
import os
import subprocess
import sys
import time
import unittest
from argparse import ArgumentParser
from copy import deepcopy
from datetime import datetime, timedelta
from multiprocessing import Process

import requests
import web3
import yaml


# we need access to the database, so we will piggy back off the option monitoring skill

try:
    sys.path += [os.path.sep.join(os.getcwd().split(os.path.sep)[:-1])]
    from agents.autonomous_hegician.skills.option_management.db_communication import (  # type: ignore
        DBCommunication,
        FAILED,
        OPEN,
    )

except ImportError as e:
    raise e

#   connection_string = {
#       "ganache_local": "http://localhost:7545",
#       "ganache_container": "http://ganachecli:7545",
#       "live": "https://mainnet.infura.io/v3/f00f7b3ba0e848ddbdc8941c527447fe",  # todo
#   }

HOST = "http://localhost:8080"
LEDGER = "http://127.0.0.1:7545"
w3 = web3.Web3(web3.HTTPProvider(LEDGER))
w3.isConnected()
deployer_address = "0x1cb8a2d2a75747f0be56180619ba1aaf0ab74c72e7c1892758d210cbf36742e2"


def setup_db():
    ds = DBCommunication()
    ds.add_data()
    return ds


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


class TestWebserverIntegration(unittest.TestCase):
    currentResult = None
    base_order_params = {
        "amount": 10000000,
        "strike_price": 200,
        "period": 2 * 24 * 60 * 60,  # in days
        "option_type": 1,
        "market": "ETH",
        "execution_strategy_id": 0,
    }

    @classmethod
    def tearDownClass(cls):
        agent.terminate()
        os.system("pkill -f libp2p_node")

    @classmethod
    def setUpClass(cls):
        setup_db()
        cls.addresses = get_current_addresses()
        cls.contracts = load_contracts(cls.addresses)

    def set_price(self, new_price, provider):
        price_provider = self.contracts[provider]
        price_provider.functions.setPrice(new_price).transact(
            {"from": deployer_address}
        )

    def tearDown(self):
        DBCommunication.delete_options()
        ok = self.currentResult.wasSuccessful()
        errors = self.currentResult.errors
        failures = self.currentResult.failures
        print(
            " All tests passed so far!"
            if ok
            else " %d errors and %d failures so far" % (len(errors), len(failures))
        )

    def run(self, result=None):
        self.currentResult = result  # remember result for use in tearDown
        unittest.TestCase.run(self, result)  # call superclass run method

    def await_order_status_code(self, status_code, order_params):
        done = False
        timeout = 15
        start = datetime.utcnow()
        while not done:
            order = DBCommunication.get_option(order_params)
            print(order, status_code)
            if order.status_code.id == status_code:
                done = True
            if datetime.now() - timedelta(seconds=timeout) > start:
                return order.status_code.id
            time.sleep(1)
        return done

    def _create_option_via_api(self, order_params):
        res = requests.post(
            f"{HOST}/create_new_option", data=json.dumps({"data": order_params})
        )
        return res

    def test_does_api_create_btc_put_option_api(self):
        # now the ah will retrieve this order from the db an execute it.
        order_params = deepcopy(self.base_order_params)
        order_params["market"] = "BTC"
        self.set_price(order_params["strike_price"], "btcpriceprovider")

        res = self._create_option_via_api(order_params)
        self.assertEqual(res.status_code, 200)
        orders = DBCommunication.get_options()
        self.assertEqual(len(orders), 1, "Only 1 order expected as in testing!")
        self.assertTrue(self.await_order_status_code(OPEN, json.loads(res.content)))

    def test_does_api_fail_btc_put_option_api_wrong_params(self):
        # now the ah will retrieve this order from the db an execute it.
        order_params = deepcopy(self.base_order_params)
        order_params["period"] = 10
        order_params["market"] = "BTC"
        self.set_price(order_params["strike_price"], "btcpriceprovider")

        res = self._create_option_via_api(order_params)
        self.assertEqual(res.status_code, 200)
        orders = DBCommunication.get_options()
        self.assertEqual(len(orders), 1, "Only 1 order expected as in testing!")
        self.assertTrue(self.await_order_status_code(FAILED, json.loads(res.content)))

    def test_does_api_create_eth_put_option_api(self):
        # now the ah will retrieve this order from the db an execute it.
        order_params = deepcopy(self.base_order_params)
        self.set_price(order_params["strike_price"], "priceprovider")

        res = self._create_option_via_api(order_params)
        self.assertEqual(res.status_code, 200)
        orders = DBCommunication.get_options()
        self.assertEqual(len(orders), 1, "Only 1 order expected as in testing!")
        self.assertTrue(self.await_order_status_code(OPEN, json.loads(res.content)))

    def test_does_api_fail_eth_put_option_api_wrong_params(self):
        # now the ah will retrieve this order from the db an execute it.
        order_params = deepcopy(self.base_order_params)
        order_params["period"] = 10
        self.set_price(order_params["strike_price"], "priceprovider")

        res = self._create_option_via_api(order_params)
        self.assertEqual(res.status_code, 200)
        orders = DBCommunication.get_options()

        self.assertEqual(len(orders), 1, "Only 1 order expected as in testing!")
        self.assertTrue(self.await_order_status_code(FAILED, json.loads(res.content)))

    def test_ah_handles_multiple_correct_orders(self):
        for _ in range(10):
            order_params = deepcopy(self.base_order_params)
            self.set_price(order_params["strike_price"], "priceprovider")
            res = self._create_option_via_api(order_params)
            self.assertEqual(res.status_code, 200)
        orders = DBCommunication.get_options()

        self.assertEqual(len(orders), 10)
        [self.assertTrue(self.await_order_status_code(OPEN, o.id)) for o in orders]

    def test_ah_handles_multiple_incorrect_orders(self):
        for _ in range(10):
            order_params = deepcopy(self.base_order_params)
            order_params["period"] = 10
            self.set_price(order_params["strike_price"], "priceprovider")
            res = self._create_option_via_api(order_params)
            self.assertEqual(res.status_code, 200)
        orders = DBCommunication.get_options()

        self.assertEqual(len(orders), 10)
        [self.assertTrue(self.await_order_status_code(FAILED, o.id)) for o in orders]

    def test_get_all_agents(self):
        route = "get_all_agents"
        res = requests.get(f"{HOST}/{route}")
        res = res.status_code
        self.assertEqual(res, 200)

    def test_get_all_options(self):
        route = "get_all_options"
        res = requests.get(f"{HOST}/{route}")
        res = res.status_code
        self.assertEqual(res, 200)

    def test_get_snap_shots(self):
        route = "get_snapshots"
        res = requests.get(f"{HOST}/{route}")
        res = res.status_code
        self.assertEqual(res, 200)

    def test_get_web3_config(self):
        route = "get_web3_config"
        res = requests.get(f"{HOST}/{route}")
        res = res.status_code
        self.assertEqual(res, 200)


if __name__ == "__main__":
    agent = launch_autonomous_hegician()
    parser = ArgumentParser("Launch Webserver tests")
    parser.add_argument(
        "-f",
        "--full_tests",
        help="Run full tests or run an isolated test.",
        default=True,
        type=bool,
    )
    args = parser.parse_args()
    if args.full_tests:
        results = unittest.main()
    else:
        partial = unittest.TestSuite()
        partial.addTests(
            [
                TestWebserverIntegration(
                    "test_does_ah_excercise_eth_atm_put_option",
                )
            ]
        )
        results = unittest.TextTestRunner().run(partial)
    if len(results.failures) == 0 and len(results.errors) == 0:  # type: ignore
        print("All tests passed!")
        sys.exit(0)
    else:
        sys.exit(1)
