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
touch Pipfile & pipenv --python 3.7 & pipenv shell
pip install mkdocs
mkdocs serve
```

## Running the agent as a AEA

``` bash
cd fetch && pipenv shell && pipenv install --skip-lock
cd AutonomousHegician
aea install
aea run
```

## Temporaily running the db as a webserver

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
