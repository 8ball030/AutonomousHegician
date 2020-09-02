#  Strategy
The intial strategy we have implemented as a proof of concept is design to monitor options and to execute them if they are:

 - A) in the money.
 - B) within 5 minutes of execution.


![image](../schema/strategy_behaviour.png)

# Behaviours
We have implmented 4 behaviours.

 - WebServer
This behaviour runs a local web server to provide a swagger based api for interaction with the agents internal datastore.

 - PriceTicker behaviour.
This behaviour polls uniswap for the DAI ETH price and updates an internal state of the price.

 - Contract Deployment behaviour.
 This behaviour handles the intial setup of the contracts when the agent is deployed on a local tet net. It also handles deploying the Contract Api messages to the Ledger.

- Snapshot Behaviour.
This behaviour uses the price from the Price Ticker behaviour, and the current balance of the agent to take a snap of the total value of the agent.
The snapshots are used to contract the equity charts from the front end.

 - Option Management behaviour.
 This beaviour handles interactions with options contracts. 
 Using orders retrieved from the strategy class the agent will decide which orders to;
 A) create
 B) exercise

 


# Front End
The front end for user interaction is built on on react.
The user has the ability to cerate new options contracts from the from end, which the agent will then monitor for execution.
We use http request to communicate with the database. 
Our agent will then read the pending tx from this datastore.
NOTE, this means that any options contracts which have not been added to the datastore will not be monitored!

# Architecture

(/schema/Architecture.jpg)
Format: ![Alt Text](url)




# Architecture schema

![image](../schema/Architecture.jpg)




