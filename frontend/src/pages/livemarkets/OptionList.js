import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { CircularProgress, Typography } from '@material-ui/core';
import MUIDataTable from "mui-datatables";
import { createMuiTheme, MuiThemeProvider } from '@material-ui/core/styles';


import Themes from "./../../themes";

import axios from 'axios';
import API from '../../api'

import Highcharts from 'highcharts';
import {
  withHighcharts
} from 'react-jsx-highcharts';



class OptionList extends React.Component {
  getMuiTheme = () => createMuiTheme(
    {...Themes.default, 
    ...{overrides: {
      MUIDataTableCell: {
        root: {
          backgroundColor: "#121c36"
      },
    },
    MuiTableHead: {
        root: {
          backgroundColor: "#121c36"
      },
    },

    MUIDataTableHead: {
        root: {
          backgroundColor: "#121c36"
      },
    },
    MUIDataTableHeadCell: {
        root: {
          backgroundColor: "#121c36"
      },
    },

    MUIDataTable: {
      root: {
        backgroundColor: '#121c36',
      },
      paper: {
        boxShadow: 'none',
        backgroundColor: '#121c36'
      },
    },
    MuiToolbar: {
      root: {
        backgroundColor: '#121c36',
      },
    },
    MUITableHeader: {
      root: {
        backgroundColor: '#121c36',
      },
    },
    MUITableHead: {
      root: {
        backgroundColor: '#121c36',
      },
    },
    MuiTableCell: {
      root: {
        backgroundColor: '#121c36',
      },
    },
    MUIDataTableSelectCell: {
      headerCell: {
        backgroundColor: '#121c36',
      },
    },
    MuiTableFooter: {
      root: {
        '& .MuiToolbar-root': {
          backgroundColor: '#121c36',
        },
      },
    },



    }}}
  )

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
          customBodyRender: (value, tableMeta, updateValue) => {
            return value;
          }
        },
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
    setInterval(() => this.UpdateGraph(), 10000);
  }


  UpdateGraph() {
    API.get('get_all_options')
      .then(options => options.data)
      .then(optionsList => {
          this.setState({ option_data: optionsList });
      });
  }
  //componentDidMount() {
  //  this.UpdateGraph();
  //}


  render() {

    const { option_data, count, isLoading, rowsPerPage, sortOrder } = this.state;

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
        <MuiThemeProvider theme={this.getMuiTheme()}>
          <MUIDataTable title={<Typography variant="h6">
            {isLoading && <CircularProgress size={24} style={{marginLeft: 15, position: 'relative', top: 4}} />}
            </Typography>
            } data={this.state.option_data} columns={this.state.columns} options={options} />
        </MuiThemeProvider>
      </div>
    );

  }
}

export default withHighcharts(OptionList, Highcharts);