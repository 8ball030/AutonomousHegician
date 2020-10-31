Autonomous Hegician
======

The aim of this project is to provide an agent based approach to managing Hegic decentralised options contracts.

The project uses Fetch.ai's [AEA framework](https://github.com/fetchai/agents-aea) as a basis and consists of agents with skills to provide different functionality.

The behviour  implemented is an ITM option expiration auto-execution behaviour,  the implementation of this behaviour will eventually be augmented with additional advanced order types.

Presently, the Autonomous Hegician (AH) provides the functionality of

- Excercising ITM Hegic contracts, and
- Auto Excercising ITM contacts with *no* user interaction.


## Instructions for Users

To use the AH follow these steps.

### 1. Clone repo

``` bash
git clone git@github.com:8ball030/AutonomousHegician.git
```


### 2. Install

The Autonomous Hegician has been designed to be as easy to use as possible. The application is designed to run on a raspberry pi to allow for users to remain fully in control of their keys.

The easiest and fastest way to install the application is to use the soon to come pre-built Raspberry Pi images. In the interim, the application can be launched using docker-compose.

First, install docker as per their [guide](https://docs.docker.com/get-docker/).

Second, run the following command:
``` bash
docker-compose up -d
```

This will launch 4 containers

- *Postgres database* - For storage of option parameters
- *Swagger api* - To allow interaction with the database 
- *React Front end* - To allow user interaction with the AH.
- *Live Autonomous Hegician* - AEA interacting with the Ethereum Mainnet.

Once the containers have built and launched, the front end is accessible from;

[Autonomous Hegician](http://0.0.0.0:3001) 


## 3. Optionally learn about the Architecture

![Proposal for Poc of Behavior Auto-Execution](https://github.com/8ball030/AutonomousHegician/blob/master/schema/Architecture.jpg)


## Instructions for Developers

To develop the agent independently, it is useful to refer to the docs to understand how the exisiting behaviours are interacting with each other.

## Set up and Docs

To serve the docs run:

``` bash
pipenv shell
pipenv install --skip-lock
mkdocs serve
exit
```

## Dev Env

Development is split across the `agents` and `frontend` directories. Navigate to the respective `README.md`s for further guidance.

The submodule `ganachecli` is used to run a local instance of the Ethereum blockchain.

Make sure ganache is installed:
``` bash
npm install -g ganache-cli
```

The directories `hegic_contracts` and `scripts` are kept for reference.

## Contributors

### Contributors on GitHub
* [Contributors](https://github.com/8ball030/AutonomousHegician/graphs/contributors)


### Third party libraries
[Fetch.Ai](https://docs.fetch.ai/aea/quickstart/)

## License
* see [LICENSE](https://github.com/8ball030/AutonomousHegician/blob/master/LICENSE.md) file

## Version
* Version 0.0.1
