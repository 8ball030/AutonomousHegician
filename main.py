#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: 8baller
Authorised use only
"""
import os
import sys
from argparse import ArgumentParser

AH_LOGO = "    _         _                                              \n   / \\  _   _| |_ ___  _ __   ___  _ __ ___   ___  _   _ ___ \n  / _ \\| | | | __/ _ \\| '_ \\ / _ \\| '_ ` _ \\ / _ \\| | | / __|\n / ___ \\ |_| | || (_) | | | | (_) | | | | | | (_) | |_| \\__ \\\n/_/   \\_\\__,_|\\__\\___/|_| |_|\\___/|_| |_| |_|\\___/ \\__,_|___/\n                                                             \n _   _            _      _             \n| | | | ___  __ _(_) ___(_) __ _ _ __  \n| |_| |/ _ \\/ _` | |/ __| |/ _` | '_ \\ \n|  _  |  __/ (_| | | (__| | (_| | | | |\n|_| |_|\\___|\\__, |_|\\___|_|\\__,_|_| |_|\n            |___/                      \n"


def parse_args():
    """Parse arguments."""
    parser = ArgumentParser(description="Cli tool for the Autonomouse Hegician.")
    parser.add_argument(
        "-o",
        "--options",
        help="Comma seperated list of actions to take.",
        required=True,
    )
    return parser.parse_args()


def run_tests():
    """Run all tests."""
    # remove all containers
    code = os.system("docker-compose down")
    if code != 0:
        raise RuntimeError(f"Failed to destroy existing containers!")
    # start required containers
    code = os.system("docker-compose up -d postgresdb ganachecli")
    if code != 0:
        raise RuntimeError(f"Failed to start test environment containers!")
    # create db schema
    code = os.system(
        "cd agents; pipenv run python autonomous_hegician/skills/option_management/db_communication.py"
    )
    if code != 0:
        raise RuntimeError(f"Failed to create database!")
    # run tests
    code = os.system("cd agents; pipenv install --skip-lock")
    if code != 0:
        raise RuntimeError(f"Failed to install dependencies!")
    deploy_contracts_to_testnet()
    code = os.system("cd agents; pipenv run update_configs")
    if code != 0:
        raise RuntimeError(f"Failed to update configs of Autonomous Hegician!")
    code = os.system("cd agents; pipenv run tests")
    if code != 0:
        raise RuntimeError(f"Failed to run integration tests successfully!")



def deploy_contracts_to_testnet():
    """Deploy contracts to testnet."""
    code = os.system("cd agents; pipenv run deploy_contracts")
    if code != 0:
        raise RuntimeError("Deploying contracts has failed!")
        


def launch_containers():
    """Launch docker containers."""
    code = os.system("docker-compose up -d --build")
    if code != 0:
        raise RuntimeError("Launching containers has failed!")


def update_ah_config(config="testnet"):
    """Update the AH config."""
    if config != "testnet":
        i = os.system("cd agents; pipenv install --skip-lock")
        i2 = os.system("cd agents; pipenv run update_configs")

        if sum([i, i2]) != 0:
            raise RuntimeError("Updateing the AH config has failed!")



choices = {
    1: ["1. Deploy contracts to Ganache Testnet.", deploy_contracts_to_testnet],
    2: ["2. Update Autonomous Hegicician with Test Contracts", update_ah_config],
    3: ["3. Update Autonomous Hegicician with Live Contracts", update_ah_config],
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
            name, func = choices[i]
            print(f"\nRunning:\n\n{name}\n")
        except KeyError:
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


def check_python_version():
    """Check python version satisfies requirements."""
    if not (sys.version_info[0] >= 3 and sys.version_info[1] >= 6):
        print("Python 3.6 or higher required!")
        sys.exit(1)


if __name__ == "__main__":
    print(AH_LOGO)
    check_python_version()
    main()
    print("Completed Successfully \0/!")
