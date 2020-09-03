import os
import pprint
import json
import pdb

from hexbytes import HexBytes
from web3 import Web3, HTTPProvider
from solcx import compile_source, compile_files, set_solc_version_pragma

set_solc_version_pragma("0.6.8")

pub_address = "0xe97fe448C9E032e96ce548A98D4fD28a47eCB013"




class ContractInterface(object):
    """A convenience interface for interacting with ethereum smart contracts

    This interface will handle a main contract and it's dependencies. All it
    requires is a path to the directory where your solidity files are stored.
    It will then compile, deploy, fetch a contract instance, and provide
    methods for transacting and calling with gas checks and event output.
    """

    default_vars_path = os.path.join(os.getcwd(), 'deployment_variables.json')

    def __init__(
        self,
        web3,
        contract_to_deploy,
        contract_directory,
        max_deploy_gas = 500000,
        max_tx_gas = 50000,
        deployment_vars_path = default_vars_path
        ):
        """Accepts contract, directory, and an RPC connection and sets defaults

        Parameters:
            web3 (Web3 object): the RPC node you'll make calls to (e.g. geth, ganache-cli)
            contract_to_deploy (str): name of the contract you want to interface with
            contract_directory (path): location of Solidity source files
            max_deploy_gas (int): max gas to use on deploy, see 'deploy_contract'
            max_tx_gas (int): max gas to use for transactions, see 'send'
            deployment_vars_path (path): default path for storing deployment variables

        Also sets web3.eth.defaultAccount as the coinbase account (e.g. the
        first key pair/account in ganache) for all send parameters
        """

        self.web3 = web3
        self.contract_to_deploy = contract_to_deploy
        self.contract_directory = contract_directory
        self.max_deploy_gas = max_deploy_gas
        self.max_tx_gas = max_tx_gas
        self.deployment_vars_path = deployment_vars_path
        self.web3.eth.defaultAccount = web3.eth.coinbase

    def compile_source_files(self):
        """Compiles 'contract_to_deploy' from specified contract.

        Loops through contracts in 'contract_directory' and creates a list of
        absolute paths to be passed to the py-solc-x's 'compile_files' method.

        Returns:
            self.all_compiled_contracts (dict): all the compiler outputs (abi, bin, ast...)
            for every contract in contract_directory
        """

        deployment_list = []

        for contract in os.listdir(self.contract_directory):
            if contract.find("HegicHedgeContract") >=0: continue
            deployment_list.append(os.path.join(self.contract_directory, contract))

        self.all_compiled_contracts = compile_files(deployment_list,  import_remappings=[
            "@openzeppelin=/home/tom/Desktop/Medium/defi_cefi_bridge/tontine/hedge-contracts-v1/node_modules/@openzeppelin",
            "@uniswap=/home/tom/Desktop/Medium/defi_cefi_bridge/tontine/hedge-contracts-v1/node_modules/@uniswap",
            "@chainlink=/home/tom/Desktop/Medium/defi_cefi_bridge/tontine/hedge-contracts-v1/node_modules/@chainlink",
        ])

        #print("Compiled contract keys:\n{}".format(
        #    '\n'.join(self.all_compiled_contracts.keys()
        #     )))

    def deploy_contract(self, contract_key, deployment_params=None):
        """Deploys contract specified by 'contract_to_deploy'

        Estimates deployment gas and compares that to max_deploy_gas before
        deploying. Also writes out variables required to create a contract
        instance to 'deployment_vars' to easily recreate it after exiting
        program.

        Parameters:
            deployment_params (dict): optional dictionary for overloading the
            default deployment transaction parameters. See web3.py's
            eth.sendTransaction for more info.
        """

        try:
            self.all_compiled_contracts is not None
        except AttributeError:
            print("Source files not compiled, compiling now and trying again...")
            self.compile_source_files()


        # print("All Contracts to deploy;", list(self.all_compiled_contracts.keys()))
        # [print(i) for i in self.all_compiled_contracts.keys()]
        # for compiled_contract_key in self.all_compiled_contracts.keys():
        print(f"Deploying Contract {contract_key}")
        deployment_compiled = self.all_compiled_contracts[contract_key]



        deployment = self.web3.eth.contract(
            abi=deployment_compiled['abi'],
            bytecode=deployment_compiled['bin']
            )


        if deployment_params is None:
            tx_hash = deployment.constructor().transact()
        else:
            tx_hash = deployment.constructor(*deployment_params).transact()
            

        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        contract_address = tx_receipt['contractAddress']

        print("Deployed {0} to: {1} using {2} gas.".format(
            self.contract_to_deploy,
            contract_address,
            tx_receipt['cumulativeGasUsed']
            ))

        self.vars = {
            'contract_address' : contract_address,
            'contract_abi' : deployment_compiled['abi']
        }


        with open (self.deployment_vars_path, 'w') as write_file:
            json.dump(self.vars, write_file, indent=4)

        print(f"Address and interface ABI for {self.contract_to_deploy} written to {self.deployment_vars_path}\n")
        return self.vars

    def get_instance(self):
        """Returns a contract instance object from variables in 'deployment_vars'

        Checks there is in fact an address saved. Also does a (crude) check
        that the deployment at that address is not empty. Reads variables
        created in 'deploy_contract' and creates a contract instance
        for use with all the 'Contract' methods specified in web3.py

        Returns:
            self.contract_instance(class ContractInterface): see above
        """

        with open (self.deployment_vars_path, 'r') as read_file:
            vars = json.load(read_file)
        vars = self.vars
        try:
            self.contract_address = vars['contract_address']
        except ValueError(
            f"No address found in {self.deployment_vars_path}, please call 'deploy_contract' and try again."
            ):
            raise

        contract_bytecode_length = len(self.web3.eth.getCode(self.contract_address).hex())

        try:
            assert (contract_bytecode_length > 4), f"Contract not deployed at {self.contract_address}."
        except AssertionError as e:
            print(e)
            raise
        else:
            print(f"Contract deployed at {self.contract_address}. This function returns an instance object.")

        self.contract_instance = self.web3.eth.contract(
            abi = vars['contract_abi'],
            address = vars['contract_address']
        )

        return self.contract_instance

    def send (self, function_, *tx_args, event=None, tx_params=None):
        """Contract agnostic transaction function with extras

        Builds a transaction, estimates its gas and compares that to max_tx_gas
        defined on init. Sends the transaction, waits for the receipt and prints
        a number of values about the transaction. If an event is supplied, it
        will capture event output, clean it, and return it.

        Parameters:
            function_(str): name of the function in your contract you wish to
            send the transaction to
            tx_args(list): non-keyworded function arguments to be supplied
            in the order they are defined in contract source
            event(str): name of event (if any) you expect to be emmitted from
            contract
            tx_params(dict): optional dictionary for overloading the
            default deployment transaction parameters. See web3.py's
            eth.sendTransaction for more info.

        Returns:
            receipt(AttributeDict): immutable dict containing various
            transaction outputs
            cleaned_events(dict): optional output of cleaned event logs
        """

        fxn_to_call = getattr(self.get_instance().functions, function_)
        print(fxn_to_call)
        built_fxn = fxn_to_call(*tx_args)

        gas_estimate = built_fxn.estimateGas(transaction=tx_params)
        print(f"Gas estimate to transact with {function_}: {gas_estimate}\n")

        if gas_estimate < self.max_tx_gas:

            print(f"Sending transaction to {function_} with {tx_args} as arguments.\n")

            tx_hash = built_fxn.transact(transaction=tx_params)

            receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)

            print((
                f"Transaction receipt mined with hash: {receipt['transactionHash'].hex()} "
                f"on block number {receipt['blockNumber']} "
                f"with a total gas usage of {receipt['cumulativeGasUsed']}\n"
                ))

            if event is not None:

                event_to_call = getattr(self.contract_instance.events, event)
                raw_log_output = event_to_call().processReceipt(receipt)
                indexed_events = clean_logs(raw_log_output)

                return receipt, indexed_events

            else:
                return receipt

        else:
            print("Gas cost exceeds {}".format(self.max_tx_gas))

    def retrieve (self, function_, *call_args, tx_params=None):
        """Contract.function.call() with cleaning"""

        fxn_to_call = getattr(self.contract_instance.functions, function_)
        built_fxn = fxn_to_call(*call_args)

        return_values = built_fxn.call(transaction=tx_params)

        if type(return_values) == bytes:
            return_values = return_values.decode('utf-8').rstrip("\x00")

        return return_values

def clean_logs(log_output):
    indexed_events = log_output[0]['args']
    cleaned_events = {}
    for key, value in indexed_events.items():
        if type(value) == bytes:
            try:
                cleaned_events[key] = value.decode('utf-8').rstrip("\x00")
            except UnicodeDecodeError:
                cleaned_events[key] = Web3.toHex(value)
        else:
            cleaned_events[key] = value
    print(f"Indexed Events: {cleaned_events}")
    return cleaned_events
