#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: 8baller
Authorised use only
"""
import os
import sys
from argparse import ArgumentParser

import pyfiglet


def parse_args():
    parser = ArgumentParser(
        description="Cli tool for the Autonomouse Hegician.")
    parser.add_argument(
        "-o",
        "--options",
        help="Comma seperated list of actions to take.",
        required=True,
    )
    return parser.parse_args()


def _stop():
    os.system("docker-compose down")


def run_tests():
    # remove all containers
    _stop()
    # start required containers
    os.system("docker-compose up -d postgresdb ganachecli")
    # create db schema
    os.system(
        "cd agents; pipenv run python autonomous_hegician/skills/option_management/db_communication.py"
    )
    # run tests
    os.system("cd agents; pipenv install --skip-lock")
    os.system("cd agents; pipenv run deploy_contracts")
    os.system(
        "cd agents; python scripts/update_ah_with_deployed_testnet_contracts.py"
    )
    os.system("cd agents; pipenv run tests")


def deploy_contracts_to_testnet():
    os.system("cd agents; pipenv run deploy_contracts")


def launch_containers():
    os.system("docker-compose up -d --build")


def update_ah_config(config="testnet"):
    if config != "testnet":
        os.system(
            "cd agents; python3 scripts/update_ah_with_deployed_testnet_contracts.py"
        )


choices = {
    1: ["1. Deploy Testnet Contracts.", deploy_contracts_to_testnet],
    2:
    ["2. Update Autonomous Hegicician with Test Contracts", update_ah_config],
    3:
    ["3. Update Autonomous Hegicician with Live Contracts", update_ah_config],
    4: ["4. Run local tests.", run_tests],
    5: ["5. Launch Live Autonomous Hegician.", launch_containers],
}


def main():
    """Run the main method."""
    if len(sys.argv) == 1:
        print("Please choose from the following actions;")
        [print(f"\n{i[0]}\n") for i in choices.values()]
        try:
            i = int(input())
            print(i)
            func = choices[i][1]
        except:
            print("Invalid option!")
        func()
    else:
        args = parse_args()
        for k in [k for k in args.options.split(",") if k != ""]:
            try:
                print(choices[int(k)][0])
                choices[int(k)][1]()
            except KeyError:
                print("Invalid options selected!")

    pass


if __name__ == "__main__":
    print(pyfiglet.figlet_format("Autonomous Hegician"))
    main()
