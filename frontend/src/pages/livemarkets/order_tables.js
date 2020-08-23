import React, { Component } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import Button from '@material-ui/core/Button';

import range from "lodash/range";
import {
  Table,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from "@material-ui/core";


import Highcharts from 'highcharts';
import {
  HighchartsChart, Chart, AreaSplineSeries, Tooltip, withHighcharts, XAxis, YAxis, Title, Subtitle, Legend, LineSeries, Caption, ColumnSeries, SplineSeries, PieSeries
} from 'react-jsx-highcharts';

const useStyles = makeStyles((theme) => ({
  button: {
    display: 'block',
    marginTop: theme.spacing(2),
  },
  formControl: {
    margin: theme.spacing(1),
    minWidth: 120,
  },
}));



const states = {
  running: "success",
  paused: "secondary",
  error: "warning",
};

class OptionList extends React.Component {
  state = {
      options: []
  }
  
  componentDidMount() {
    const url='http://localhost:8080/get_all_options';
    fetch(url)
      .then((response) => response.json())
      .then(optionsList => {
          this.setState({ options: optionsList });
      });
  }
  
  render() {
    return(
          <ul>
              {this.state.options.map((option) => (
                  <li key={option.optionID}> {option.type_of_option} {option.strike_price} {option.expiration_date} {option.status} </li>
              ))}
          </ul>
    )}
}
export default withHighcharts(OptionList, Highcharts);