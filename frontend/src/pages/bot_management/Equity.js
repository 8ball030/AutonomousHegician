import React, { Component } from 'react';
import Highcharts from 'highcharts';
import {
  HighchartsChart, Chart, withHighcharts, XAxis, YAxis, Legend, LineSeries
} from 'react-jsx-highcharts';

import './style.css'; // CSS Styles
import API from '../../api'

class Equity extends Component {
  UpdateGraph = () => {
    API.get('get_snapshots')
    .then(snapshots => {
      const data = snapshots.data;
      this.setState({data: data.map(function (i){ return i.usd_val})
      })})
  }

  constructor (props) {
    super(props);
    this.state = {
      data: [],
      name: "Auto ITM Closure Agent"
    }
    setInterval(() => this.UpdateGraph(), 5000);
  }

  render() {
    const plotOptions = {
      areaspline: {
        fillOpacity: 10,
        lineWidth: 1,
        marker: {
          enabled: true,
          states: {
            hover: { enabled: true}
          }
        }
      }
    };
    const chart = {
      backgroundColor: null
    }

    const {data, name} = this.state;

    return (
        <div className="bot_performance">
          <HighchartsChart plotOptions={plotOptions} styledMode>
            <Chart />
            <Legend layout="vertical" align="right" verticalAlign="middle" />
            <XAxis>
              <XAxis.Title>Time</XAxis.Title>
            </XAxis>
            <YAxis>
              <YAxis.Title>Equity (USD)</YAxis.Title>
                  <LineSeries name={name} data={data} chart={chart}/>
            </YAxis>
          </HighchartsChart>
        </div>
      );
    }
  }

export default withHighcharts(Equity, Highcharts);
