# Development

Install the python dependencies in a virtual environment:
``` bash
pipenv shell
pipenv install --skip-lock
```

## Running the agent as a AEA

First, run a local ganache client (with seed so we get same private keys each time):
``` bash
cd .. && ganache-cli -p 7545 --seed 1
```

Second, in another terminal:
``` bash
pipenv shell
cd autonomous_hegician
aea install
aea run
```

## Temporarily running the db as a webserver

``` bash
pipenv shell
cd autonomous_hegician/skills/option_monitoring
python web_server.py
aea run
```

## Running the Frontend

``` bash
cd ../frontend/
npm install
npm start
```
