Hegic Helper
======
The aim of this project is to provide an agent based approach to managing Hegic decentralised options contracts.

The project uses Fetch.ai as a base and consists of an agent with a skills to provide different functionality.

The first skill to implement is ITM option expiration auto-execution behaviour,  the implementation of this behaviour will be allow us to move forwards in a very swift manner.

This skill provides the functionality of

- Excercising ITM Hegic contracts.
The user can configure the exact parameters for the exercision of a contract.

  - ITM at expiration

  - Stop loss

  - Take Profit


## Instructions
Please build the documents using the following commands to set the documentation up.

## Architecture
![Proposal for Poc of Behavior Auto-Execution](https://github.com/8ball030/hegichelper/blob/master/schema/Architecture.jpg)

## Clone repo

``` bash
git clone git@github.com:8ball030/hegichelper.git
```

## Set up and Docs

``` bash
pipenv shell && pipenv install --skip-lock
mkdocs serve
exit
```

## Installing

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

Navigate to localhost:3000 to see the front end

##TODO
- Complete contract - Excersise and create pending.
- Create pleasent way to add new contracts to the sqllite db




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
