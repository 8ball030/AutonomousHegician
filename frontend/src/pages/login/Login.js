import React, { useState } from "react";
import {
  Grid,
  Button,
} from "@material-ui/core";
import { withRouter } from "react-router-dom";
import Widget from "../../components/Widget";
import { Typography } from "../../components/Wrappers";

// styles
import useStyles from "./styles";

// logo
import logo from "./logo.png";

// context
import { useUserDispatch, loginUser } from "../../context/UserContext";

function Login(props) {
  var classes = useStyles();

  // global
  var userDispatch = useUserDispatch();

  // local
  var [isLoading, setIsLoading] = useState(false);
  var [error, setError] = useState(null);
  var [activeTabId, setActiveTabId] = useState(0);
  var [nameValue, setNameValue] = useState("");
  var [loginValue, setLoginValue] = useState("");
  var [passwordValue, setPasswordValue] = useState("");

  return (
    <>
    <Grid container className={classes.container} style={{marginTop: '40px'}}>
        <Grid item xs={12} md={6}>
          <Widget disableWidgetMenu>
            <div className={classes.dashedBorder} style={{textAlign: 'center'}}>
        <Typography variant="h1">The Autonomous Hegician</Typography>
        <img src={logo} alt="logo" style={{width: 200, margin: '50px auto', display: 'block'}} />
        <br></br>
      <Button
        disabled={isLoading}
        onClick={() =>
          loginUser(
            userDispatch,
            loginValue,
            passwordValue,
            props.history,
            setIsLoading,
            setError,
          )
        }
        variant="contained"
        color="secondary"
        size="large"
        style={{margin: '0 auto', color: '#0a101f', display: 'block', backgroundColor: '#7fffd5'}}
      >
        Enter
      </Button>
      </div>
    </Widget>
      </Grid>
      </Grid>
    </>
  );
}

export default withRouter(Login);
