import React, { Component } from 'react';
import Highcharts from 'highcharts';
import axios from 'axios';
import {
  HighchartsChart, Chart, withHighcharts, XAxis, YAxis, Legend, LineSeries, Caption
} from 'react-jsx-highcharts';

import API from '../../api'

class Equity extends Component {
  UpdateGraph = () => {
    API.get('get_snapshots')
    .then(snapshots => {
      const data = snapshots.data;
      console.log(data);
      this.setState({data: data.map(function (i){ return i.usd_val})
      })})
  }

  constructor (props) {
    super(props);
    this.state = {
      data: [],
      name: "Auto ITM Closure Agent"
    }
    setInterval(() => this.UpdateGraph(), 2000);
  }

  render() {
    const plotOptions = {
      areaspline: {
        fillOpacity: 1,
        lineWidth: 0,
        marker: {
          enabled: false,
          states: {
            hover: { enabled: false }
          }
        }
      }
    };

    const {data, name} = this.state;

    return (
        <div className="bot_performance">
          <HighchartsChart plotOptions={plotOptions}>
            <Chart />
            <Legend layout="vertical" align="right" verticalAlign="middle" />
            <XAxis>
              <XAxis.Title>Time</XAxis.Title>
            </XAxis>
            <YAxis>
              <YAxis.Title>Equity (USD)</YAxis.Title>


                  <LineSeries name={name} data={data} />

            </YAxis>
            <Caption align="center">Here we can see the current equity of our agents</Caption>
          </HighchartsChart>
        </div>
      );
    }
  }

export default withHighcharts(Equity, Highcharts);
