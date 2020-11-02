import React from 'react';
import { CircularProgress, Typography } from '@material-ui/core';
import MUIDataTable from "mui-datatables";
import { MuiThemeProvider } from '@material-ui/core/styles';

import API from '../../api'

import Highcharts from 'highcharts';
import {
  withHighcharts
} from 'react-jsx-highcharts';

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
        name: "pnl",
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
