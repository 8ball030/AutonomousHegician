import os
from web3 import Web3, HTTPProvider
from interface import ContractInterface

w3 = Web3(HTTPProvider('http://127.0.0.1:7545'))

import os

print(w3.eth.accounts[0])

PATH = os.getcwd()


def deploy_contracts():
    contract_dir = PATH + "/contracts"

    # setup fake stablecoin
    path = PATH + "/contracts/TestContracts.sol:FakeUSD"
    StableCoin= ContractInterface(w3, path, contract_dir)
    StableCoin.compile_source_files()
    StableCoin.deploy_contract(path)

    # setup price feed
    path = PATH + "/contracts/TestContracts.sol:FakePriceProvider"
    PriceProvider = ContractInterface(w3, path, contract_dir)
    PriceProvider.compile_source_files()
    PriceProvider.deploy_contract(path, [20000000000])

    # setup exchange
    path = PATH + "/contracts/TestContracts.sol:FakeExchange"
    Exchange = ContractInterface(w3, path, contract_dir)
    Exchange.compile_source_files()
    Exchange.deploy_contract(path, [PriceProvider.vars["contract_address"],
                                    StableCoin.vars["contract_address"]
                                    ])
                             
    # setup CallOptions
    path = PATH + "/contracts/HegicCallOptions.sol:HegicCallOptions" 
    HegicCallOptions = ContractInterface(w3, path, contract_dir)
    HegicCallOptions.compile_source_files()
    HegicCallOptions.deploy_contract(path, [PriceProvider.vars["contract_address"]])

    # setup PutOptions
    path = PATH + "/contracts/HegicPutOptions.sol:HegicPutOptions" 
    HegicPutOptions = ContractInterface(w3, path, contract_dir)
    HegicPutOptions.compile_source_files()
    HegicPutOptions.deploy_contract(path, [StableCoin.vars["contract_address"],
                                           PriceProvider.vars["contract_address"],
                                           Exchange.vars["contract_address"]])
    
    # setupERCPool
    path = PATH + "/contracts/HegicERCPool.sol:HegicERCPool" 
    HegicERCPool = ContractInterface(w3, path, contract_dir)
    HegicERCPool.compile_source_files()
    HegicERCPool.deploy_contract(path, [StableCoin.vars["contract_address"]])
    
    # setupETHPool
    path = PATH + "/contracts/HegicETHPool.sol:HegicETHPool" 
    HegicETHPool = ContractInterface(w3, path, contract_dir)
    HegicETHPool.compile_source_files()
    HegicETHPool.deploy_contract(path, [StableCoin.vars["contract_address"]])

    print("All Deployed!")
    return {"StableCoin": StableCoin,
            "PriceFeed": PriceProvider,
            "Exchange": Exchange,
            "HegicCallOptions": HegicCallOptions,
            "HegicPutOptions": HegicPutOptions,
            "HegicERCPool": HegicERCPool,
            "HegicETHPool": HegicETHPool
    }

from web3 import Web3

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
w3.isConnected()


import json 
        
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
w3.isConnected()


FILES = {"ethpool": "/home/tom/Desktop/Medium/defi_cefi_bridge/tontine/hedge-contracts-v1/build/contracts/HegicETHPool.json",
         "calloptions": "/home/tom/Desktop/Medium/defi_cefi_bridge/tontine/hedge-contracts-v1/build/contracts/HegicCallOptions.json"}

def retrieve_contract_instance(address, type_contract):
    print(f"retrieving .. {type_contract} from address {address}")
    with open(FILES[type_contract], "r") as f:
        c = json.loads(f.read())


    contract_instance = w3.eth.contract(address=address,
                                        abi=c["abi"]
                                       )
    # [print(f"Available {f}") for f in dir(contract_instance.functions) if f.find("_") != 0]
    return contract_instance

    
def provide_liquidity(call_contract_instance):
    ethpool_address = call_contract_instance.functions.pool().call()
    contract_instance = retrieve_contract_instance(ethpool_address, "ethpool")
    print(f"Total Supply : ", contract_instance.functions.totalSupply().call())
    print("Total balance ", contract_instance.functions.totalBalance().call())
    print("Providing liqudity..")
    contract_instance.functions.provide(0).transact({'to': ethpool_address,
                                                         'from': w3.eth.coinbase,
                                                        'value': w3.toWei(1, "ether")})
    print(f"Total Supply : ", contract_instance.functions.totalSupply().call())
    print("Total balance ", contract_instance.functions.totalBalance().call())


    
def create_calloption(call_contract_instance, call_option_address):
    period = 24 * 3600 * 2
    amount = w3.toWei(0.1, "ether")
    strike_price = 200
    fees = call_contract_instance.functions.fees(period, amount, strike_price).call()
    return_values = call_contract_instance.functions.create(period, amount, strike_price).call({'to': call_option_address,
                                                                                  'from': w3.eth.coinbase,
                                                                                  "value": fees[0]}
                                                                                            )

    call_contract_instance.functions.create(period, amount, strike_price).transact({'to': call_option_address,
                                                                                  'from': w3.eth.coinbase,
                                                                                  "value": fees[0]}
                                                                                            )
    print(f"Option id: {return_values}")
    if type(return_values) == bytes:
        return_values = return_values.decode('utf-8').rstrip("\x00")
    return return_values
    

def excercise(call_option_contract, option_id, call_option_address):
    tx_ref = call_option_contract.functions.exercise(option_id).transact({'to': call_option_address,
                                                         'from': w3.eth.coinbase,
                                                        'value': 0})
    print(f"Excercsied {option_id} : {tx_ref}")
    return tx_ref

# call_option_contract = retrieve_contract_instance(address, "calloptions")
# ethpool_address = call_option_contract.functions.pool().call()
# retrieve_contract_instance(ethpool_address, "ethpool")

def confirm_provide_create_and_excercise(HegicInterface):
    call_option_contract = HegicInterface.get_instance()
    call_option_address = HegicInterface.vars["contract_address"]
    provide_liquidity(call_option_contract)
    option_id = create_calloption(call_option_contract, call_option_address)
    excercise(call_option_contract, option_id, call_option_address)

    
def setprice(HegicInterface):
    fake_price_feed_contract = HegicInterface.get_instance()
    fake_price_feed_address = HegicInterface.vars["contract_address"]
    print(f"Latest Price :", fake_price_feed_contract.functions.latestAnswer().call())
    fake_price_feed_contract.functions.setPrice(200).transact({'to': fake_price_feed_address,
                                                      'from': w3.eth.coinbase,
                                                     'value': w3.toWei(0.00, "ether")})
    print(f"Latest Price :", fake_price_feed_contract.functions.latestAnswer().call())
    
    
def generate_config(env):
    
    output = { k: v.vars["contract_address"] for k, v in env.items()}
    
    output["HegicETHPool"] = env["HegicCallOptions"].get_instance().functions.pool().call()
    for k, v in output.items():
        print(f"Contract : {k} @ address {v}")
    for k, v in output.items():
        k = k.replace("Hegic", "")
        print(f"      {k.lower()}: '{v}'")
    

if __name__ == "__main__":
    env = deploy_contracts()
    setprice(env["PriceFeed"])
    confirm_provide_create_and_excercise(env["HegicCallOptions"])
    generate_config(env)
    # now we need to provide the pools with liquidity
#     provide_liquidity(env)
    # now we will create a put option
   # create_put_option()



