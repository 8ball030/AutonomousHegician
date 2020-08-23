Info Visualisation Project


Description

I have implemented a data Visualisation framework for an active trader of crypto currencues.

The project brings together a number of different data sources.
  Live Data Feeds
   - Order books 
   - OHLC timeries
   - Balances
  Market Data Feeds
   - Our market data is sourced from coinmarketcap.com

We have a number of Views of the data
  - Portfolio overview
    We show holding of assets, along with the allocation of those assets
  - Live Markets
    We read the orderbook directly from the exchange and render it live as a pair of column charts
    We also use Trading views widget to provide a data feed
  - Industry Overview 
    Treemap to show daily returns and also the market cap of bitcoin compared to other coins
    We also show the correlation between different futures markets
  - Bot Management
    We show the performance of different strategies over time. Note, this is note yet using real data for the performance of the strategies as this was beyond scope,


To Install

```
touch Pipfile pipenv --python 3.7 
pipenv shell
pip install -r requirements.txt
```
We need to launch the back end apis, this is done from the api directory

```
cd apis
pipenv shell
python3 app_react_version.py
```


Once the Apis are launched, we can launch the application

```
npm start
```
