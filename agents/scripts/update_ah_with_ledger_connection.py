"""Script to update AH with contract configs."""
import os
from typing import Any, Dict, List

from aea.helpers.yaml_utils import yaml_dump_all, yaml_load_all


connection_strings = {
    "ganache_local": "http://localhost:7545",
    "ganache_container": "http://ganachecli:7545",
    "live": "http://ganachecli:7545",  # todo
}


def parse_args():
    def is_acceptable_input(input_):
        if input_ is None:
            raise
        acceptable = ["ganache_local", "ganache_container", "live"]
        if input_ in acceptable:
            return connection_strings[input_]
        else:
            raise ValueError(f"{input_} is not a valid option {acceptable}")

    var = os.environ.get("LEDGER")
    return is_acceptable_input(var)


def update_ah_config_with_new_config(
    ledger_string,
    file_paths: str = (
        "./autonomous_hegician/aea-config.yaml",
        "./hegic_deployer/aea-config.yaml",
    ),
):
    """Get the AH config and update it with ledger string."""
    for file_path in file_paths:
        with open(file_path, "r") as fp:
            full_config: List[Dict[str, Any]] = yaml_load_all(fp)
        assert len(full_config) >= 2, "Expecting at least one override defined!"
        connection_config = full_config[2]
        assert connection_config["public_id"] in ["fetchai/ledger:0.9.0"]
        connection_config["config"]["ledger_apis"]["ethereum"][
            "address"
        ] = ledger_string

        full_config_updated = full_config[:2] + [full_config[2]] + full_config[3:]
        with open(file_path, "w") as fp:
            yaml_dump_all(full_config_updated, fp)


def do_work():
    """Run the script."""
    ledger_string = parse_args()
    update_ah_config_with_new_config(
        ledger_string,
    )
    print("Configurations copied.")


if __name__ == "__main__":
    do_work()
