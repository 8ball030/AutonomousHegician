import React from 'react';

import {
  TableContainer,
  Table,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
  Paper,
  Button,
} from "@material-ui/core";

import API from '../../api'

import Highcharts from 'highcharts';
import {
  withHighcharts
} from 'react-jsx-highcharts';


function createData(name, calories, fat, carbs, protein, status, amount) {
  return { name, calories, fat, carbs, protein, status, amount };
}

const rows = [
  createData('Frozen yoghurt', 159, 6.0, 24, 4.0, 'paused' ,100),
];
const states = {
  running: {
    backgroundColor: 'rgb(18 58 18)',
    color: 'white',
  },
  paused: {
    backgroundColor: '#694e1d',
    color: 'white',
  },
  error: {
    backgroundColor: '#460a0a',
    color: 'white',
  },
};

class AgentList extends React.Component {

  constructor (props) {
    super(props);
    setInterval(() => this.UpdateGraph(), 10000);
  }

  componentDidMount() {
    this._isMounted = true;
    this.UpdateGraph();
  }

  componentWillUnmount() {
    this._isMounted = false;
  }


  UpdateGraph() {
    API.get('get_all_agents')
      .then(agents => agents.data)
      .then(agentsList => {
          console.log(agentsList );
          this.setState({ agentsData: agentsList });
      });
  }
  //componentDidMount() {
  //  this.UpdateGraph();
  //}


  render() {

    const{agentsData} = this.state;

    return (
        <TableContainer component={Paper}>
          <Table aria-label="simple table">
            <TableHead>
              <TableRow>
                <TableCell>Agent Public Address</TableCell>
                <TableCell align="right">Date Created</TableCell>
                <TableCell align="right">Last Updated</TableCell>
                <TableCell align="right">Status</TableCell>
                <TableCell align="right">USD Value</TableCell>
                <TableCell align="right">ETH Value</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {this.agentsData.map((row) => (
                <TableRow key={row.address}>
                  <TableCell component="th" scope="row">
                    {row.name}
                  </TableCell>
                  <TableCell align="right">{row.date_created}</TableCell>
                  <TableCell align="right">{row.date_updated}</TableCell>
                  <TableCell align="right">{row.usd_val}</TableCell>
                  <TableCell align="right">
                    <Button
                      style={states[row.status]}
                    >
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
    );

  }
}

export default withHighcharts(AgentList, Highcharts);
