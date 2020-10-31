# Strategy

The strategy.py file contains the main logic for the implementation of the AH behaviour.

The strategy is responsible for deciding the appropriate actions to be executed through the behaviour classes. 

The strategy uses order_status codes identify what actions to take at each step.

# Order Status Codes
- 0 - received -> The order has just been received from the user/frontend.
- 1 - estimating -> Calls out to the smart contract to estimate the fees for the option. Stores the results. 
- 2 - placing -> The Ah has submitted the TX to create the option on the blockchain
- 3 - open -> The option is open.
- 4 - closed -> The option has been exercised.
- 5 - failed. -> The transaction has failed.
