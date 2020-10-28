import { OptionForm } from '../bot_management/OptionForm';
import React from "react";
import {
  Grid,
} from "@material-ui/core";

// styles
import useStyles from "./styles";

// components
import Widget from "../../components/Widget";
import PageTitle from "../../components/PageTitle";
import TradingViewWidget, { Themes } from 'react-tradingview-widget';
// charts
import OptionList from "./OptionList.js";


export default function Dashboard(props) {
  var classes = useStyles();
  // var theme = useTheme();

  // local
  // var [mainChartState, setMainChartState] = useState("monthly");

  return (
    <>
      <PageTitle title="Live Markets View" button="Refresh" />
      <Grid container spacing={4}>
        <Grid item style={{minHeight: 400}} lg={8} md={12} sm={12} xs={12}>
          <Widget
            title="Live Price Feed"
            upperTitle
            bodyClass={classes.fullHeightBody}
            className={classes.card}>
            <TradingViewWidget
                 symbol="FTX:ETHPERP"
                 theme={Themes.DARK}
                 autosize={true}
                 locale="en"
                 />
          </Widget>
        </Grid>
        <Grid item lg={4} xs={12}>
          <Widget title="Submit New Option" upperTitle noBodyPadding>
            <OptionForm/>
          </Widget>
        </Grid>
        <Grid item lg={12} md={12} sm={12} xs={12}>
          <Widget
            title="Current Options"
            upperTitle
            bodyClass={classes.fullHeightBody}
            className={classes.card}>
                <div>
                  <OptionList/>
                </div>
          </Widget>
        </Grid>
      </Grid>
        <Grid item xs={12}>

        </Grid>

    </>
  );
}

