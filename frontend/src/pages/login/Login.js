import React, { useState } from "react";
import {
  Grid,
  CircularProgress,
  Button,
  Tabs,
  Tab,
  TextField,
  Fade,
} from "@material-ui/core";
import { withRouter } from "react-router-dom";
import classnames from "classnames";
import Widget from "../../components/Widget";
import { Typography } from "../../components/Wrappers";

// styles
import useStyles from "./styles";

// logo
import logo from "./logo.png";

// context
import { useUserDispatch, loginUser } from "../../context/UserContext";
import { makeStyles } from "@material-ui/styles";

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
    <Grid container className={classes.container} jusify-content={"center"} alignItems={"center"}>
        <Grid item xs={12} md={6}>
          <Widget disableWidgetMenu>
            <div className={classes.dashedBorder}>
        <Typography variant="h1" jusify={"center"} alignItems={"center"}>The Autonomous Hegician</Typography>
        <img src={logo} alt="logo" size="small" jusify={"center"} alignItems={"center"} width="600"/>
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
        margin-left={"auto"} alignItems={"center"} 
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
