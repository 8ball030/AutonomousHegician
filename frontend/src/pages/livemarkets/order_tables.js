import React from 'react';
import { makeStyles } from '@material-ui/core/styles';

import axios from 'axios';
import API from '../../api'

import Highcharts from 'highcharts';
import {
  withHighcharts
} from 'react-jsx-highcharts';

class OptionList extends React.Component {
  state = {
      options: []
  }
  
  componentDidMount() {
    API.get('get_all_options')
      .then(options => options.data)
      .then(optionsList => {
          this.setState({ options: optionsList });
      });
  }
  
  render() {
    return(
          <ul>
              {this.state.options.map((option) => (
                  <li key={option.ledger_id}> {option.type_of_option} {option.strike_price} {option.expiration_date} {option.status_code_id} </li>
              ))}
          </ul>
    )}
}
export default withHighcharts(OptionList, Highcharts);