import React from "react";
import { Grid } from "@material-ui/core";
import MUIDataTable from "mui-datatables";
import { makeStyles } from '@material-ui/core/styles';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import Button from '@material-ui/core/Button';
// components
import PageTitle from "../../components/PageTitle";
import Widget from "../../components/Widget";

// Charts
import OptionForm from "./OptionForm.js";
import Performance from "./bot_performance.js";
import Assets from "./bot_assets.js";

// data
const agent_data= [
    {
      id: 0,
      name: "Auto ITM Closure Agent",
      starttime: "02 July 2020",
      status: "Running",
      equity: [10,11,12,23,23,123,344],
      balances: [{'coin': 'USDT', 'free': 0.0, 'total': 0.0, 'usdValue': 2.5031455e-09},
                 {'coin': 'BTC',
                  'free': 0.08552497,
                  'total': 0.11043491,
                  'usdValue': 1302.8794711600162},
                 {'coin': 'BEAR', 'free': 0.0, 'total': 0.0, 'usdValue': 0.0},
                 {'coin': 'PAXG', 'free': 0.0, 'total': 0.0, 'usdValue': 0.0},
                 {'coin': 'USD',
                  'free': 7.68805447,
                  'total': 7.68805447,
                  'usdValue': 7.688054475573361},
                 {'coin': 'ETH', 'free': 0.0, 'total': 0.0, 'usdValue': 0.0}]

    },
    {
      id: 1,
      name: "Bullish Bot",
      starttime: "05 July 2020",
      status: "Paused"
    },
    {
      id: 2,
      name: "Bearish Bot",
      starttime: "05 June 2020",
      status: "Running"
    },
  ]

        // <Grid item xs={6}>
        //   <Widget title="Equity by Agent" upperTitle noBodyPadding>
        //     <Performance />
        //   </Widget>
        // </Grid>
        // <Grid item xs={12}>
        //   <Widget title="Equity by Agent" upperTitle noBodyPadding>
        //     <Assets data={agent_data}/> 
        //   </Widget>
        // </Grid>


export default function BotManagement() {
  return (
    <>
      <PageTitle title="Agent Management" />
      <Grid container spacing={4}>
        <Grid item xs={12}>
          <Widget title="Equity by Agent" upperTitle noBodyPadding>
            <Performance />
          </Widget>
        </Grid>
      </Grid>

      <Grid container spacing={4}>
        <Grid item xs={12}>
          <Widget title="Submit New Option" upperTitle noBodyPadding>
            <OptionForm data={agent_data} />
          </Widget>
        </Grid>
      </Grid>
    </>
  );
}
