Hegic Helper
======
The aim of this project is to provide an agent based approach to managing Hegic decentralised options contracts.

The project uses Fetch.ai as a base and consists of an agent with a skills to provide different functionality.

The behviour  implemented is ITM option expiration auto-execution behaviour,  the implementation of this behaviour which will swiftly be augmented with additional advanced order types.

Presently, the Autonomous Hegician provides the functionality of
	- Excercising ITM Hegic contracts.
	- Auto Excercising ITM contacts with *no* user interaction


## Instructions
Please build the documents using the following commands to set the documentation up.


## Clone repo

``` bash
git clone git@github.com:8ball030/hegichelper.git
```


## Installation of User Application
The Autonomous Hegician has been designed to be as easy to use as possible. The application is designed to run on a raspberry pi to allow for users to remain fully in control of their keys.

The easiest/fastest way to install the application is to use the soon to come pre-built Raspberry Pi images. In the interim, the application can be launched using docker-compose as so;
```
docker-compose up -d
```

This will launch 4 containers

- *Postgres database* - For storage of option parameters
- *Swagger api* - To allow interaction with the database 
- *React Front end* - To allow user interaction with the AH.
- *Live Autonomous Hegician* - Connected to the Mainnet.

Once the containers have built and launched, the front end is accessible from;

[Autonomous Hegician](http://0.0.0.0:3001) 





## Architecture
![Proposal for Poc of Behavior Auto-Execution](https://github.com/8ball030/hegichelper/blob/master/schema/Architecture.jpg)





## Development Environment Installation

To develop the agent independently, it is useful to refer to the docs to understand how the exisiting behaviours are interacting with each other.

## Set up and Docs

``` bash
pipenv shell && pipenv install --skip-lock
mkdocs serve
exit
```

## Dev Env

First, make sure ganache is installed:
``` bash
npm install -g ganache-cli
```

Second, install the python dependencies in a virtual environment:
``` bash
cd fetch && pipenv shell && pipenv install --skip-lock
exit
cd ..
```

## Running the agent as a AEA

First, run a local ganache client (with seed so we get same private keys each time):
``` bash
cd fetch && ganache-cli -p 7545 --seed 1
```

Second, in another terminal:
``` bash
cd fetch && pipenv shell
cd AutonomousHegician
aea install
aea run
```

## Temporarily running the db as a webserver

``` bash
pipenv shell
cd fetch/AutonomousHegician/skills/option_monitoring
python web_server.py
aea run
```
## Running the Frontend

``` bash
cd frontend/
npm install
npm start
```


## Contributors

### Contributors on GitHub
* [Contributors](https://github.com/username/sw-name/graphs/contributors)


### Third party libraries
[Fetch.Ai](https://docs.fetch.ai/aea/quickstart/)

## License
* see [LICENSE](https://github.com/username/sw-name/blob/master/LICENSE.md) file

## Version
* Version 0.0.1

## Contact
#### Developer/Company
* Homepage:
* e-mail:
* Twitter: [@twitterhandle](https://twitter.com/twitterhandle "twitterhandle on twitter")
* other communication/social media

[![Flattr this git repo](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=
