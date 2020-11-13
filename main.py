#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entrypoint script for AH.

Author: 8baller
Authorised use only
"""
import os
import sys
import time
from argparse import ArgumentParser

AH_LOGO = "    _         _                                              \n   / \\  _   _| |_ ___  _ __   ___  _ __ ___   ___  _   _ ___ \n  / _ \\| | | | __/ _ \\| '_ \\ / _ \\| '_ ` _ \\ / _ \\| | | / __|\n / ___ \\ |_| | || (_) | | | | (_) | | | | | | (_) | |_| \\__ \\\n/_/   \\_\\__,_|\\__\\___/|_| |_|\\___/|_| |_| |_|\\___/ \\__,_|___/\n                                                             \n _   _            _      _             \n| | | | ___  __ _(_) ___(_) __ _ _ __  \n| |_| |/ _ \\/ _` | |/ __| |/ _` | '_ \\ \n|  _  |  __/ (_| | | (__| | (_| | | | |\n|_| |_|\\___|\\__, |_|\\___|_|\\__,_|_| |_|\n            |___/                      \n"
NUMBER_DB_CREATIONS = 1


def parse_args():
    """Parse arguments."""
    parser = ArgumentParser(description="Cli tool for the Autonomouse Hegician.")
    parser.add_argument("-d", "--dev_mode", action="store_true")
    parser.add_argument(
        "-o",
        "--options",
        help="Comma seperated list of actions to take.",
        default="",
    )
    return parser.parse_args()


def docker_cleanup(func):
    """Decorator that manages docker teardown before and after."""

    def wrap(*args, **kwargs):
        print("Removing exising docker containers...")
        code = os.system("docker-compose down")
        if code != 0:
            raise RuntimeError("Failed to destroy existing containers!")
        try:
            result = func(*args, **kwargs)
        except RuntimeError:
            raise
        finally:
            print("Removing exising docker containers...")
            code = os.system("docker-compose down")
            if code != 0:
                print(f"Error on `docker-compose down`. Code={code}")

        return result

    return wrap


@docker_cleanup
def run_tests():
    """Run all tests."""
    print("Starting backend services....")
    code = os.system("docker-compose up -d postgresdb ganachecli api")
    if code != 0:
        raise RuntimeError("Failed to start test environment containers!")
    print("Installing virtual environment with dependencies....")
    code = os.system("cd agents; pipenv install --skip-lock")
    if code != 0:
        raise RuntimeError("Failed to install dependencies!")
    print("Creating database schema....")
    cmd = "cd agents; pipenv run python autonomous_hegician/skills/option_management/db_communication.py"
    for _ in range(NUMBER_DB_CREATIONS):
        code = os.system(cmd)
        if code == 0:
            continue
    if code != 0:
        raise RuntimeError("Failed to create database!")
    print("Updating the ledger from the environment vars....")
    code = os.system("cd agents; pipenv run update_ledger")
    if code != 0:
        raise RuntimeError("Failed to update ledger of Autonomous Hegician!")
    print("Attempting to deploy contracts to the chain....")
    code = os.system("cd agents; pipenv run deploy_contracts")
    if code != 0:
        raise RuntimeError("Deploying contracts has failed!")
    print("Updating contracts from testnet in Autonomous Hegician config...")
    code = os.system("cd agents; pipenv run update_contracts_testnet")
    if code != 0:
        raise RuntimeError(
            "Failed to update newly deployed contracts to Autonomous Hegician!"
        )
    print("Running agent functionality tests ....")
    code = os.system("cd agents; pipenv run test_ah")
    if code != 0:
        raise RuntimeError("Failed to run integration tests successfully!")
    print("Running api functionality tests ....")
    code = os.system("cd agents; pipenv run test_ah_via_api")
    if code != 0:
        raise RuntimeError("Failed to run api integration tests successfully!")


@docker_cleanup
def deploy_contracts_to_testnet():
    """Deploy contracts to testnet."""
    print("Starting backend services....")
    code = os.system("docker-compose up -d ganachecli")
    if code != 0:
        raise RuntimeError("Failed to started local chain")
    print("Installing virtual environment with dependencies....")
    code = os.system("cd agents; pipenv install --skip-lock")
    if code != 0:
        raise RuntimeError("Failed to install dependencies!")
    code = os.system("cd agents; pipenv run deploy_contracts")
    if code != 0:
        raise RuntimeError("Deploying contracts has failed!")


def launch_containers():
    """Launch docker containers."""
    code = os.system("docker-compose up -d --build")
    if code != 0:
        raise RuntimeError("Launching containers has failed!")
    print(
        "Containers running in background.\nVisit: `http://0.0.0.0:3001`.\nTo shut down: `docker-compose down`."
    )


def setup_live():
    code = os.system("cd agents; pipenv run update_contracts_live")
    if code != 0:
        raise RuntimeError("Deploying contracts has failed!")
    launch_containers()


def update_ah_config(config="testnet"):
    """Update the AH config."""
    if config != "testnet":
        i = os.system("cd agents; pipenv install --skip-lock")
        i2 = os.system("cd agents; pipenv run update_contracts")
        i3 = os.system("cd agents; pipenv run update_ledger")

        if sum([i, i2, i3]) != 0:
            raise RuntimeError("Updateing the AH config has failed!")


def main():
    """Run the main method."""
    choices = {
        k + 1: v
        for k, v in enumerate(
            [
                ["Run local tests.", run_tests],
                ["Launch live containerised Autonomous Hegician.", setup_live],
            ]
        )
    }
    args = parse_args()
    if args.dev_mode:
        print("Dev mode currently inconsequential!")
    if args.options != "":
        for k in [k for k in args.options.split(",") if k != ""]:
            try:
                name, func = choices[int(k)]
                print(f"Executing {k}...   {name}")
                func()
            except KeyError:
                print("Invalid options selected!")
        return
    print("Please choose from the following actions;")
    [print(f"\n{i[0]}. {i[1][0]}") for i in choices.items()]
    try:
        i = int(input())
        name, func = choices[i]
        print(f"\nRunning:\n\n{name}\n")
    except KeyError:
        print("Invalid option!")
    func()


def check_python_version():
    """Check python version satisfies requirements."""
    if not (sys.version_info[0] >= 3 and sys.version_info[1] >= 6):
        print("Python 3.6 or higher required!")
        sys.exit(1)


if __name__ == "__main__":
    print(AH_LOGO)
    check_python_version()
    main()
    sys.exit(0)
