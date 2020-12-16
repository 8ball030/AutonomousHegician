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
git clone git@github.com:8ball030/AutonomousHegician
```


### 2. Install

The Autonomous Hegician has been designed to be as easy to use as possible. The application is designed to run on a raspberry pi to allow for users to remain fully in control of their keys.

The easiest and fastest way to install the application is to use the soon to come pre-built Raspberry Pi images. In the interim, the application can be launched using docker-compose.

#### 2.a) Dependancies
    - First, install docker as per their [guide](https://docs.docker.com/get-docker/).
    - Second, install go as per their [guide](https://golang.org/doc/install).

### 3. Run.
Run the following command in a terminal:
``` bash
python main.py
```
This will give you the choice of

- A) Run full local tests. - As expected this will deploy the full test suite locally.
- B) Launch Local Live Autonomous Hegician.

This will launch 4 containers

- *Postgres database* - For storage of option parameters
- *Swagger api* - To allow interaction with the database 
- *React Front end* - To allow user interaction with the AH.
- *Live Autonomous Hegician* - AEA interacting with the Ethereum Mainnet.

Once the containers have built and launched, the front end is accessible from;

[Autonomous Hegician](http://0.0.0.0:3001) 


## 3. Optionally learn about the Architecture

Please review the documentation available;

[Documents](./docs)


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

## Tests
To run tests, the Hegic contracts must first be deployed.

In order to deploy the contracts, first launch the underlying containers for the local blockchain;

```bash
docker-compose up -d api postgresdb ganachecli
```

Once these containers have launched, the hegic contracts can be deployed using the deployer agent as so;

```bash
cd agents
pipenv shell
cd hegic_deployer
aea -s run
```
Once the contracts have been successfully deployed, the deployer agent will stop running. 
The deployer agent will have created a new contract_configuration file which contains the addresses for the newly deployed contracts.

The autonomous_hegician agents aea-config.yaml must be updated with the generated addresses.

Now we can launch the test suite available;

```bash
cd agents
pipenv shell
python tests/tests.py
```


## Running on Mainnet

Update the connection.yaml for the Ledger connection.


## Contributors

### Contributors on GitHub
* [Contributors](https://github.com/8ball030/AutonomousHegician/graphs/contributors)

### Third party libraries
[Fetch.Ai](https://docs.fetch.ai/aea/quickstart/)

## License
* see [LICENSE](https://github.com/8ball030/AutonomousHegician/blob/master/LICENSE.md) file

## Version
* Version 0.0.1
