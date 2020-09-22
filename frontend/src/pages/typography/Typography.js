import React from "react";
import { Grid } from "@material-ui/core";

// styles
import useStyles from "./styles";

// components
import PageTitle from "../../components/PageTitle";
import Widget from "../../components/Widget";
import { Typography } from "../../components/Wrappers";

export default function TypographyPage() {
  var classes = useStyles();

  return (
    <>
      <PageTitle title="About the Autonomous Hegician" />
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Widget title="Features" disableWidgetMenu>
            <div className={classes.dashedBorder}>
              <Typography variant="h6" color="info" className={classes.text}>
                - Monitor Wallet Equity Over Time.
              </Typography>
              <Typography variant="h6" color="info" className={classes.text}>
                - Create New Option Contracts.
              </Typography>
              <Typography variant="h6" color="info" className={classes.text}>
                - Implement Advanced Order Types.
              </Typography>
              <Typography variant="h6" color="info" className={classes.text}>
                - Manage Your Outstanding Positions.
              </Typography>
              <Typography variant="h6" color="info" className={classes.text}>
                - Light-weight application.
              </Typography>
              <Typography variant="h6" color="info" className={classes.text}>
                - Fully Open source code base. Read the code running your strategies.
              </Typography>
              <Typography variant="h6" color="info" className={classes.text}>
                - Real-time Price Feed.
              </Typography>
            </div>
          </Widget>
        </Grid>
        <Grid item xs={12} md={6}>
          <Widget title="Benefits" disableWidgetMenu>
            <div className={classes.dashedBorder}>
              <Typography variant="h6" color="info" className={classes.text}>
                - Your Keys Your Crypto.
              </Typography>
              <Typography variant="h6" color="info" className={classes.text}>
                - Manages your DeFi Options positions, so you dont have to.
              </Typography>
              <Typography variant="h6" color="info" className={classes.text}>
                - Advanced Order Types. Auto In the Money Closure, Take Profit.
              </Typography>
              <Typography variant="h6" color="info" className={classes.text}>
                - Run the application on a raspberry pi.
              </Typography>
              <Typography variant="h6" color="info" className={classes.text}>
                - Stop leaving money on the table.
              </Typography>
              <Typography variant="h6" color="info" className={classes.text}>
                - No need to monitor the price, the AH does it for you. Never miss a move.
              </Typography>
            </div>
          </Widget>
        </Grid>
        <Grid item xs={12} md={6}>
          <Widget title="About" disableWidgetMenu color="primary">
            <div className={classes.dashedBorder}>
              <Typography variant="h5" className={classes.text}>
                The Autonomous Hegician is an agent based approach to managing Hegic Options Contracts, built on the Fetch.ai Tech stack.
              </Typography>
              <Typography variant="h5" className={classes.text}>
                By using an agent based approach, the AH is able to implement a number of advanced features beyond the standard functionality of traditional Smart Contracts, whilst ensuring that the user is fully in control of their private keys.
              </Typography>
              <Typography variant="h5" className={classes.text}>
                As our objective is to level the playing field between advanced traders and retail by providing easy to use tools, the AH is designed to run on a raspberry pi.
              </Typography>
            </div>
          </Widget>
        </Grid>
        <Grid item xs={12} md={6}>
          <Widget title="Usage" disableWidgetMenu color="primary">
            <div className={classes.dashedBorder}>
              <Typography variant="h5" className={classes.text}>
                Running the Autonomous Hegician will create an agent with a unique Ethereum Identity.
              </Typography>
              <Typography variant="h5" className={classes.text}>
                Transfer the Agent an amount of Ethereum and create a new options contract, specifying the type of managed order.
              </Typography>
              <Typography variant="h5" className={classes.text}>
                The AH will now monitor this position and when the appropriate conditions are met, the AH will execute the appropriate action.

              </Typography>
            </div>
          </Widget>
        </Grid>
      </Grid>
    </>
  );
}
