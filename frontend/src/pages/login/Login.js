import React, { useState } from "react";
import {
  Grid,
  CircularProgress,
  Typography,
  Button,
  Tabs,
  Tab,
  TextField,
  Fade,
} from "@material-ui/core";
import { withRouter } from "react-router-dom";
import classnames from "classnames";

// styles
import useStyles from "./styles";

// logo
import logo from "./logo.svg";
import google from "../../images/google.svg";

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
    <Grid container className={classes.container}>
      <div className={classes.logotypeContainer}>
        <img src={logo} alt="logo" className={classes.logotypeImage} />
        <Typography variant="h1">The Autonomous Hegician</Typography>
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
      >
        Enter
      </Button>
      </div>
    </Grid>
  );
}

export default withRouter(Login);
