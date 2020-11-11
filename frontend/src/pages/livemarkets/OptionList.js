import React from 'react';
import { CircularProgress, Typography } from '@material-ui/core';
import MUIDataTable from "mui-datatables";
import { MuiThemeProvider } from '@material-ui/core/styles';
import API from '../../api'

import Highcharts from 'highcharts';
import {
  withHighcharts
} from 'react-jsx-highcharts';

const Web3 = require('web3');

class HegicOptions {
  constructor() {
    API.get('get_web3_config')
      .then(results=> results.data)
      .then(results=> {
        this.config = results
        console.log(results);
        this.w3 = new Web3(new Web3.providers.HttpProvider(results.ledger_string))
        this.btc_contract = new this.w3.eth.Contract(results.contract_abis.btcoptions.abi, results.contract_addresses.btcoptions);
        this.eth_contract = new this.w3.eth.Contract(results.contract_abis.ethoptions.abi, results.contract_addresses.ethoptions);
        this.estimate_cost("ETH", 60*60*24*2, 1000000, 200, 1 );
      });

  }
    estimate_cost(market, period, amount, strike, type) {

    if (market == "ETH"){ 
      let contract = this.eth_contract;
          contract.methods.fees(period, amount, strike, type).call(function(err,res){
             if(!err){
                 console.log(res);
             } else {
                 console.log(err);
             }
              }  )
        
    }else{
      let contract = this.btc_contract;
      console.log(contract.methods.fees(period, amount, strike, type).call());
    }
  

};}

const Pricer = new HegicOptions()


class OptionList extends React.Component {
  state = {
    page: 0,
    count: 1,
    rowsPerPage: 5,
    sortOrder: {},
    data: [["Loading Data..."]],
    columns: [
      {
        name: "id",
        label: "Option Id",
        options: {
          customBodyRender: value => value,
        },
      },
      {
        name: "tx_hash",
        label: "TX Hash",
        options: {},
      },

      {
        name: "breakeven",
        label: "Breakeven Price",
        options: {},
      },

      {
        name: "current_pnl",
        label: "P&L",
        options: {},
      },

      {
        name: "date_created",
        label: "Date Created",
        options: {},
      },
      {
        name: "option_type",
        label: "Option Type",
        options: {},
      },
      {
        name: "expiration_date",
        label: "Expiration Date",
        options: {},
      },
      {
        name: "strike_price",
        label: "Strike Price",
        options: {},
      },
      {
        name: "status_code_id",
        label: "Option Status",
        options: {},
      },
      {
        name: "amount",
        label: "Amount",
        options: {},
      },
    ],
    isLoading: false
  };

  constructor (props) {
    super(props);
    setInterval(() => this.UpdateGraph(), 1000);
  }

  componentDidMount() {
    this._isMounted = true;
    this.UpdateGraph();
  }

  componentWillUnmount() {
    this._isMounted = false;
  }

  UpdateGraph() {
    API.get('get_all_options')
      .then(options => options.data)
      .then(optionsList => {
          this.setState({ option_data: optionsList });
      });
  }

  render() {

    const { count, isLoading, rowsPerPage } = this.state;

    const options = {
      filter: false,
      filterType: 'dropdown',
      responsive: 'stacked',
      selectableRows: false,
      serverSide: true,
      count: count,
      rowsPerPage: rowsPerPage,
      rowsPerPageOptions: [],
    };


    return (
      <div>
        <MUIDataTable title={<Typography variant="h6">
          {isLoading && <CircularProgress size={24} style={{marginLeft: 15, position: 'relative', top: 4}} />}
          </Typography>
          } data={this.state.option_data} columns={this.state.columns} options={options} />
      </div>
    );

  }
}

export default withHighcharts(OptionList, Highcharts);
