import shutil
import yaml
import json
from web3 import Web3
import os
from web3 import Web3, HTTPProvider
from interface import ContractInterface

try:
    w3 = Web3(HTTPProvider('http://ganachecli:7545'))
    print(w3.eth.accounts[0])
except:
    w3 = Web3(HTTPProvider('http://127.0.0.1:7545'))
    print(w3.eth.accounts[0])


PATH = os.getcwd()


def deploy_contracts():
    contract_dir = PATH + "/contracts"
    deploy_dir = PATH + "/deployment_vars"

    print("deploy_dir", deploy_dir)
    # setup fake stablecoin
    path = PATH + "/contracts/TestContracts.sol:FakeUSD"
    StableCoin = ContractInterface(
        w3, path, contract_dir, deployment_vars_path=deploy_dir)
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
    HegicCallOptions.deploy_contract(
        path, [PriceProvider.vars["contract_address"]])

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


def load_contracts():
    contract_dir = PATH + "/deployment_vars"
    deploy_dir = PATH + "/deployment_vars"

    # setup fake stablecoin
    path = PATH + "/contracts/TestContracts.sol:FakeUSD"
    StableCoin = ContractInterface(
        w3, path, contract_dir, deployment_vars_path=deploy_dir)
    StableCoin.deploy_contract(path)

    # setup price feed
    path = PATH + "/contracts/TestContracts.sol:FakePriceProvider"
    PriceProvider = ContractInterface(
        w3, path, contract_dir, deployment_vars_path=deploy_dir)
    PriceProvider.deploy_contract(path, [20000000000])

    # setup exchange
    path = PATH + "/contracts/TestContracts.sol:FakeExchange"
    Exchange = ContractInterface(
        w3, path, contract_dir, deployment_vars_path=deploy_dir)
    Exchange.deploy_contract(path, [PriceProvider.vars["contract_address"],
                                    StableCoin.vars["contract_address"]
                                    ])

    # setup CallOptions
    path = PATH + "/contracts/HegicCallOptions.sol:HegicCallOptions"
    HegicCallOptions = ContractInterface(
        w3, path, contract_dir, deployment_vars_path=deploy_dir)
    HegicCallOptions.deploy_contract(
        path, [PriceProvider.vars["contract_address"]])

    # setup PutOptions
    path = PATH + "/contracts/HegicPutOptions.sol:HegicPutOptions"
    HegicPutOptions = ContractInterface(
        w3, path, contract_dir, deployment_vars_path=deploy_dir)
    HegicPutOptions.deploy_contract(path, [StableCoin.vars["contract_address"],
                                           PriceProvider.vars["contract_address"],
                                           Exchange.vars["contract_address"]])

    # setupERCPool
    path = PATH + "/contracts/HegicERCPool.sol:HegicERCPool"
    HegicERCPool = ContractInterface(
        w3, path, contract_dir, deployment_vars_path=deploy_dir)
    HegicERCPool.deploy_contract(path, [StableCoin.vars["contract_address"]])

    # setupETHPool
    path = PATH + "/contracts/HegicETHPool.sol:HegicETHPool"
    HegicETHPool = ContractInterface(
        w3, path, contract_dir, deployment_vars_path=deploy_dir)
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


FILES = {"ethpool": f"{PATH}/deployment_vars/HegicETHPool_deploy_vars.json",
         "ercpool": f"{PATH}/deployment_vars/HegicERCPool_deploy_vars.json",
         "calloptions": f"{PATH}/deployment_vars/HegicCallOptions_deploy_vars.json"}


def retrieve_contract_instance(address, type_contract):
    print(f"retrieving .. {type_contract} from address {address}")
    with open(FILES[type_contract], "r") as f:
        c = json.loads(f.read())

    key = "abi" if "abi" in c.keys() else "contract_abi"
    contract_instance = w3.eth.contract(address=address,
                                        abi=c[key]
                                        )
    # [print(f"Available {f}") for f in dir(contract_instance.functions) if f.find("_") != 0]
    return contract_instance


def provide_liquidity_eth(call_contract_instance):
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


def provide_liquidity_erc(put_contract_instance, stable_contract_instance):
    #
    amount = 1000000000000000000
    stable_contract_instance.get_instance().functions.mint(
        amount).transact({"from": w3.eth.coinbase})

    ercpool_address = put_contract_instance.functions.pool().call()
    stable_contract_instance.get_instance().functions.approve(
        ercpool_address, int(amount / 10)).transact({"from": w3.eth.coinbase})
    contract_instance = retrieve_contract_instance(ercpool_address, "ercpool")
    print(f"Total Supply : ", contract_instance.functions.totalSupply().call())
    print("Total balance ", contract_instance.functions.totalBalance().call())
    print("Providing liqudity..")
    contract_instance.functions.provide(int(amount / 10), 0).transact({'to': ercpool_address,
                                                                       'from': w3.eth.coinbase,
                                                                       'value': 0})
    print(f"Total Supply : ", contract_instance.functions.totalSupply().call())
    print("Total balance ", contract_instance.functions.totalBalance().call())


def create_calloption(call_contract_instance, call_option_address):
    period = 24 * 3600 * 2
    amount = w3.toWei(0.1, "ether")
    strike_price = 200
    fees = call_contract_instance.functions.fees(
        period, amount, strike_price).call()
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


def confirm_provide_create_and_excercise_call(HegicInterface):
    call_option_contract = HegicInterface.get_instance()
    call_option_address = HegicInterface.vars["contract_address"]
    provide_liquidity_eth(call_option_contract)
    option_id = create_calloption(call_option_contract, call_option_address)
    excercise(call_option_contract, option_id, call_option_address)


def confirm_provide_create_and_excercise_put(HegicInterface, StableCoin):
    put_option_contract = HegicInterface.get_instance()
    put_option_address = HegicInterface.vars["contract_address"]
    provide_liquidity_erc(put_option_contract, StableCoin)
    option_id = create_calloption(put_option_contract, put_option_address)
    excercise(put_option_contract, option_id, put_option_address)


def setprice(HegicInterface):
    fake_price_feed_contract = HegicInterface.get_instance()
    fake_price_feed_address = HegicInterface.vars["contract_address"]
    print(f"Latest Price :", fake_price_feed_contract.functions.latestAnswer().call())
    fake_price_feed_contract.functions.setPrice(200).transact({'to': fake_price_feed_address,
                                                               'from': w3.eth.coinbase,
                                                               'value': w3.toWei(0.00, "ether")})
    print(f"Latest Price :", fake_price_feed_contract.functions.latestAnswer().call())


def generate_config(env, deployment_type, update_agent):
    output = {k: v.vars["contract_address"] for k, v in env.items()}
    output["HegicETHPool"] = env["HegicCallOptions"].get_instance(
    ).functions.pool().call()
    output["HegicERCPool"] = env["HegicPutOptions"].get_instance(
    ).functions.pool().call()
    for k, v in output.items():
        print(f"Contract : {k} @ address {v}")
    for k, v in output.items():
        k = k.replace("Hegic", "")
        print(f"      {k.lower()}: '{v}'")
    output = {k.replace("Hegic", "").lower(): v for k, v in output.items()}

    if deployment_type == "pi":
        agent_skill_path = '../AutonomousHegician/skills/option_monitoring/skill.yaml'
    else:
        agent_skill_path = '../fetch/AutonomousHegician/skills/option_monitoring/skill.yaml'
    with open(agent_skill_path) as file:
        yaml_file = yaml.load(file, Loader=yaml.FullLoader)

    yaml_file['models']['strategy']['args'].update(output)

    with open('new_skill.yaml', 'w') as f:
        yaml.dump(yaml_file, f)

    if update_agent is True:
        shutil.move("new_skill.yaml", agent_skill_path)


if __name__ == "__main__":
    DEPLOY = True
    TEST = True
    UPDATE = False
    DEPLOYMENT_TYPE = "pii"
    if DEPLOY:
        env = deploy_contracts()
    else:
        env = load_contracts()

    setprice(env["PriceFeed"])
    confirm_provide_create_and_excercise_call(env["HegicCallOptions"])
    confirm_provide_create_and_excercise_put(
        env["HegicPutOptions"],
        env["StableCoin"])
    generate_config(env, deployment_type=DEPLOYMENT_TYPE, update_agent=UPDATE)
