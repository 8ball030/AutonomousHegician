"""Script to update AH with contract configs."""

import contextlib
import json
import os

import yaml


@contextlib.contextmanager
def cd(path):
    """Change directory with context manager."""
    old_cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
        os.chdir(old_cwd)
    except Exception as e:  # pylint: disable=broad-except  # pragma: nocover
        os.chdir(old_cwd)
        raise e from e


def get_new_addresses(config_path="./hegic_deployer/contract_config.yaml"):
    """Get the contract addresses from the deployer."""
    with open(config_path, "r") as f:
        addresses = yaml.safe_load(f)
        print(addresses)
    return addresses


def update_ah_config_with_new_config(
    addresses, file_path: str = "./autonomous_hegician"
):
    """Get the AH config and update it with contract addresses."""
    dict_ = json.dumps(addresses)
    with cd(file_path):
        os.system(
            f"aea config set --type dict skills.option_management.models.strategy.args '{dict_}'"
        )


def do_work():
    addresses = get_new_addresses()
    update_ah_config_with_new_config(addresses)
    print("Configurations copied.")


if __name__ == "__main__":
    do_work()
