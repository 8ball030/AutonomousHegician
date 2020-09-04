import React from 'react';
import { makeStyles } from '@material-ui/core/styles';



import Highcharts from 'highcharts';
import {
  withHighcharts
} from 'react-jsx-highcharts';


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
                  <li key={option.ledger_id}> {option.type_of_option} {option.strike_price} {option.expiration_date} {option.status_code_id} </li>
              ))}
          </ul>
    )}
}
export default withHighcharts(OptionList, Highcharts);