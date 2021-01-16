"""Script to update AH with contract configs."""
import contextlib
import os
from typing import Tuple


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


connection_strings = {
    "ganache_local": "http://localhost:7545",
    "ganache_container": "http://ganachecli:7545",
    "live": "https://mainnet.infura.io/v3/f00f7b3ba0e848ddbdc8941c527447fe",  # todo
}


def parse_args():
    def is_acceptable_input(input_):
        acceptable = list(connection_strings.values())
        if input_ in acceptable:
            return input_
        else:
            raise ValueError(
                f"{input_} is not a valid option. Must be one of {acceptable}"
            )

    var = os.environ.get("LEDGER")
    return is_acceptable_input(var)


def update_ah_config_with_new_config(
    ledger_string,
    file_paths: Tuple[str, ...] = (
        "./autonomous_hegician",
        "./hegic_deployer",
    ),
):
    """Get the AH config and update it with ledger string."""
    for file_path in file_paths:
        with cd(file_path):
            os.system(
                f"aea -s config set vendor.fetchai.connections.ledger.config.ledger_apis.ethereum.address {ledger_string}"
            )


def do_work():
    """Run the script."""
    ledger_string = parse_args()
    update_ah_config_with_new_config(
        ledger_string,
    )
    print("Configurations copied.")


if __name__ == "__main__":
    do_work()
