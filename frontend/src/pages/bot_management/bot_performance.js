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
  {name: "Bullish Bot",
    data: [
      1447.22 ,
      1294.63 ,
      1006.59 ,
      1070.72 ,
      1254.01 ,
      1146.98 ,
      1582.03 ,
      1884.63 ,
      1852.75 ,
      1714.58 ,
      1674.05 ,
      1083.77 ,
      1331.62 ,
      1456.84 ,
      1101.92 ,
      1917.48 ,
      1241.69 ,
      1816.12 ,
      1957.97 ,
      1476.67 ,
      1392.52 ,
      1657.36 ,
      1586.1 ,
      1818.58 ,
      1367.47 ,
      1867.59 ,
      1456.25 ,
      1535.62 ,
      1434.57 ,
      1177.55 ,

          ]
  },
  {
    name: "Bearish Bot",
    data: [
      1474.34 ,
      1194.98 ,
      1168.15 ,
      1169.37 ,
      1607.24 ,
      1196.76 ,
      1665.54 ,
      1209.3 ,
      1843.24 ,
      1105.41 ,
      1697.97 ,
      1238.74 ,
      1274.98 ,
      1823.19 ,
      1375.3 ,
      1030.53 ,
      1231.79 ,
      1618.64 ,
      1669.29 ,
      1431.12 ,
      1868.86 ,
      1263.62 ,
      1833.37 ,
      1406.26 ,
      1502.44 ,
      1351.62 ,
      1546.33 ,
      1378.92 ,
      1596.0 ,
      1736.66 ,
          ]
  }

]

const Performance = () => (
  <div className="bot_performance">
    <HighchartsChart plotOptions={plotOptions}>
      <Chart />
      <Legend layout="vertical" align="right" verticalAlign="middle" />
      <XAxis>
        <XAxis.Title>Time</XAxis.Title>
      </XAxis>
      <YAxis>
        <YAxis.Title>Number of employees</YAxis.Title>
        
           {agent_data.map(agent =>(
            <LineSeries name={agent.name} data={agent.data} />
            ))}

      </YAxis>
      <Caption align="center">Here we can see the current equity of our agents</Caption>
    </HighchartsChart>
  </div>
);

export default withHighcharts(Performance, Highcharts);
