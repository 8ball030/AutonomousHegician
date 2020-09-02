import React, { Component } from 'react';
import Highcharts from 'highcharts';
import {
  HighchartsChart, Chart, withHighcharts, XAxis, YAxis, Title, Subtitle, Legend, LineSeries, Caption
} from 'react-jsx-highcharts';

const plotOptions = {
  series: {
    pointStart: 2020
  }
};

const agent_data = [
  {
    name: "Auto ITM Closure Agent",
    data: [1548.46 ,
      1258.81 ,
      1576.72 ,
      1682.25 ,
      1707.36 ,
      1493.89 ,
      1077.43 ,
      1240.95 ,
      1940.68 ,
      1495.97 ,
      1461.47 ,
      1346.6 ,
      1891.28 ,
      1727.17 ,
      1341.99 ,
      1260.04 ,
      1235.68 ,
      1083.6 ,
      1278.34 ,
      1712.54 ,
      1498.89 ,
      1047.83 ,
      1065.37 ,
      1615.02 ,
      1491.75 ,
      1012.56 ,
      1988.55 ,
      1314.53 ,
      1910.28 ,
      1219.29 ,
      ]
  },

]
class Equity extends Component {
  UpdateGraph = () => {
    const url='http://localhost:8080/get_snapshots';
    
    var http = new XMLHttpRequest();
    http.open("GET", url, false);
    http.setRequestHeader("Content-type", "application/json; charset=utf-8");
    http.onreadystatechange = () => {
      const data = JSON.parse(http.responseText);
      console.log(data);
      this.setState({data: data.map(function (i){ return i.usd_val}),
      })}
    http.send();
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

    const positioner = (w, h, point) => ({x: 0, y: point.plotY + (h / 2) + 8});

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
