"""Main entry script to application. Will check globals for debug and tests."""
import os
import subprocess
import sys
import time
from pprint import pprint


def wait():
    while True:
        time.sleep(10)


def tests():
    print("Checking for Tests")
    x = os.environ.get("TESTS")
    x = str(x).replace('"', "")
    if x == "True":
        print("Running tests")
        results = str(subprocess.check_output("tox"))
        if results.find("congratulations :)") < 0:
            print("ERROR PAUSE EXECUTION !!! TESTS FAILED")
            pprint(results.replace("b'", "").split("\\n"))
            wait()
        pprint(results.replace("b'", "").split("\\n"))


def debug():
    print("Checking for debugging")
    x = os.environ.get("DEBUG")
    x = str(x).replace('"', "")
    print(sys.argv)
    if (x == "True") and (len(sys.argv) == 1):
        print("Debugging!")
        wait()


def task():
    print("Running app",)
    # subprocess.run("./bootstart.sh",)
    command = os.environ.get("RUN_CMD").replace('"', "").split(" ")
    print(command)
    rc = subprocess.run(command,)
    print(rc)


def main():
    tests()
    debug()
    task()


if __name__ == "__main__":
    main()
