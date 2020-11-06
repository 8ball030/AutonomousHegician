# Option Management
## Description

This is a skill for managing Hegic options.

## Behaviours

* price_ticker: Queries the smart contract specified in the aea-config
* snapshot: Takes a snapshot fo the current position of the agent and saves them to the database
* option_management: Monitors the database and executes the orders specified by the strategy

## Handlers

* contract_api: handles contract_api messages for interactions with the smart contract
* ledger_api: handles ledger_api messages for payment
* signing: handles signing messages for transaction signing by the decision maker
