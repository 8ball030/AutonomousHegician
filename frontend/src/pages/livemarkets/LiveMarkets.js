import { Component } from 'react';
import React, { useState } from "react";
import {
  Grid,
} from "@material-ui/core";
import { useTheme } from "@material-ui/styles";

// styles
import useStyles from "./styles";

// components
import Widget from "../../components/Widget";
import PageTitle from "../../components/PageTitle";
import { Typography } from "../../components/Wrappers";


import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';

import TradingViewWidget, { Themes } from 'react-tradingview-widget';
// charts
import OrderTable from "./order_tables.js";



export default function Dashboard(props) {
  var classes = useStyles();
  var theme = useTheme();

  // local
  var [mainChartState, setMainChartState] = useState("monthly");

  return (
    <>
      <PageTitle title="Live Markets View" button="Refresh" />
      <Grid container spacing={4}>
        <Grid item lg={8} md={8} sm={8} xs={8}>
          <Widget
            title="Live Price Feed"
            upperTitle
            bodyClass={classes.fullHeightBody}
            className={classes.card}>
            <TradingViewWidget
                 symbol="FTX:ETHPERP"
                 theme={Themes.LIGHT}
                 locale="en"
                 autosize/>
          </Widget>
        </Grid>
        <Grid item lg={8} md={8} sm={8} xs={12}>
          <Widget
            title="Options"
            upperTitle
            bodyClass={classes.fullHeightBody}
            className={classes.card}>
                <div>
                  <OrderTable/>
                </div>
          </Widget>
        </Grid>
      </Grid>
        <Grid item xs={12}>

        </Grid>

    </>
  );
}

