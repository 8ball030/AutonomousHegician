"""Script to update AH with contract configs."""

from collections import OrderedDict
from typing import Any, Dict, List

import yaml

from aea.helpers.yaml_utils import yaml_dump_all, yaml_load_all


def get_new_addresses(config_path="./hegic_deployer/contract_config.yaml"):
    """Get the contract addresses from the deployer."""
    with open(config_path, "r") as f:
        addresses = yaml.safe_load(f)
    return addresses


def update_ah_config_with_new_config(addresses):
    """Get the AH config and update it with contract addresses."""
    file_path = "./autonomous_hegician/aea-config.yaml"
    with open(file_path, "r") as fp:
        full_config: List[Dict[str, Any]] = yaml_load_all(fp)
    assert len(full_config) >= 2, "Expecting at least one override defined!"
    skill_config = full_config[1]
    assert skill_config["public_id"] == "eightballer/option_management:0.1.0"
    skill_config["models"]["strategy"]["args"] = OrderedDict(addresses)
    full_config_updated = [full_config[0], skill_config]
    with open(file_path, "w") as fp:
        yaml_dump_all(full_config_updated, fp)


def do_work():
    """Run the script."""
    addresses = get_new_addresses()
    update_ah_config_with_new_config(addresses)
    print("Configurations copied.")


if __name__ == "__main__":
    do_work()
