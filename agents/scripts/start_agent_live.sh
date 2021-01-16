#!/bin/bash
pipenv run update_ledger
cd autonomous_hegician
aea install
aea build
aea issue-certificates
aea run
