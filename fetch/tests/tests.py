from unittest import TestCase
from copy import deepcopy

import os, sys
import web3
import time


# we need access to the database, so we will piggy back off the option monitoring skill


sys.path += [os.path.sep.join(os.getcwd().split(os.path.sep)[:-1])]

from AutonomousHegician.skills.option_management.db_communication import DBCommunication
import data_store
# the ah must be run in demo mode after the hegicContractDeployer has deployed the contracts to a local ganache cli

# we first create an option within the database







class TestOptionExecutionTester(TestCase):
    order_params = {"amount": 0.1,         
         "strike_price": 200, 
         "period": 60 * 60 * 24 * 2,
         "option_type": 1,
         "market": "ETH"
    }

    def setUp(self):
        pass

    @classmethod
    def tearDownClass(cls):
        # clear all orders from the database
        DBCommunication.delete_options()
        
    @classmethod
    def tearDownClass(cls):
        # clear all orders from the database
        pass
#        DBCommunication.delete_options()
    
    def tearDown(self):
        pass
#        DBCommunication.delete_options()

    @classmethod
    def setUpClass(cls):
        # clear all orders from the database
        DBCommunication.delete_options()
    

    def test_does_ah_create_eth_call_option(self):
        # now the ah will retrieve this order from the db an execute it.
        new_order = DBCommunication.create_new_option(**self.order_params)
        time.sleep(1)
        # we now expect the agent to have created the call option.
        orders = DBCommunication.get_orders()
        self.assertEqual(len(orders), 1, "Only 1 order expected as in testing!")
        print(dir(orders[0]))
        # we are expecting the status code to be in 2 (pending placement)
        self.assertEquals(orders[0].status_code.id, 2, "the option has not been been acted upon by the agent!")
        time.sleep(5)
        # we now expect the agent to have created the call option.
        orders = DBCommunication.get_orders()
        self.assertEqual(len(orders), 1, "Only 1 order expected as in testing!")
        print(dir(orders[0]))
        # we are expecting the status code to be in 3 (open)
        self.assertEquals(orders[0].status_code.id, 3, "the option has not been been acted upon by the agent!")

        
    
    def test_does_ah_create_btc_call_option(self):
        # now the ah will retrieve this order from the db an execute it.
        order_params = deepcopy(self.order_params)
        order_params["market"] = "BTC"
        new_order = DBCommunication.create_new_option(**order_params)
        time.sleep(4)
        # we now expect the agent to have created the call option.
        orders = DBCommunication.get_orders()
        self.assertEqual(len(orders), 1, "Only 1 order expected as in testing!")
        print(dir(orders[0]))
        # we are expecting the status code to be in 3 (open)
        self.assertEquals(orders[0].status_code.id, 3, "the option has not been been acted upon by the agent!")
        
        pass
    
    def test_does_ah_create_eth_put_option(self):
        pass
    
    def test_does_ah_create_btc_put_option(self):
        pass
    
    def test_does_ah_excercise_eth_call_option(self):
        pass
    
    def test_does_ah_excercise_btc_call_option(self):
        pass
    
    def test_does_ah_excercise_eth_put_option(self):
        pass
    
    def test_does_ah_excercise_btc_put_option(self):
        pass
    

if __name__ == '__main__':
    pass
    