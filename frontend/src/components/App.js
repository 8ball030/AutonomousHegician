import React from "react";
import { HashRouter, Route, Switch, Redirect } from "react-router-dom";
import { MobileProvider } from '../context/MobileContext';
import { createMuiTheme, MuiThemeProvider } from '@material-ui/core/styles';
import Themes from "../themes";

// components
import Layout from "./Layout";

// pages
import Error from "../pages/error";
import Login from "../pages/login";

// context
import { useUserState } from "../context/UserContext";

export default function App() {
  // global
  var { isAuthenticated } = useUserState();

  const getMuiTheme = () => createMuiTheme(
    {...Themes.default, 
    ...{overrides: {
      MUIDataTableCell: {
        root: {
          backgroundColor: "#121c36"
      },
    },
    MuiTableHead: {
        root: {
          backgroundColor: "#121c36"
      },
    },

    MUIDataTableHead: {
        root: {
          backgroundColor: "#121c36"
      },
    },
    MUIDataTableHeadCell: {
      root: {
          backgroundColor: "#0a101f !important"
      },
      paper: {
        backgroundColor: '#0a101f',
      }
    },
      MUIIconButton: {
        label: {
          backgroundColor: '#fff',
          color: '#fff',
        }
      },

    MUIDataTable: {
      root: {
        backgroundColor: '#121c36',
      },
      paper: {
        boxShadow: 'none',
        backgroundColor: '#121c36'
      },
    },
    MuiToolbar: {
      root: {
        backgroundColor: '#121c36',
      },
    },
    MUITableHeader: {
      root: {
        backgroundColor: '#121c36',
      },
      paper: {
        backgroundColor: '#0a101f',
      },
    },
    MUITableHead: {
      root: {
        backgroundColor: '#121c36',
      },
    },
    MuiTableCell: {
      root: {
        backgroundColor: '#121c36',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
      },
    },
    MUIDataTableSelectCell: {
      headerCell: {
        backgroundColor: '#121c36',
      },
    },
    MuiTableFooter: {
      root: {
        '& .MuiToolbar-root': {
          backgroundColor: '#121c36',
        },
      },
    },



    }}}
  )

  return (
    <MuiThemeProvider theme={getMuiTheme()}>
      <MobileProvider>
        <HashRouter>
          <Switch>
            <Route exact path="/" component={Login} />
            <PrivateRoute path="/app" component={Layout} />
            <Route component={Error} />
          </Switch>
        </HashRouter>
      </MobileProvider>
    </MuiThemeProvider>
  );

  // #######################################################################

  function PrivateRoute({ component, ...rest }) {
    return (
      <Route
        {...rest}
        render={props =>
          isAuthenticated ? (
            React.createElement(component, props)
          ) : (
            <Redirect
              to={{
                pathname: "/login",
                state: {
                  from: props.location,
                },
              }}
            />
          )
        }
      />
    );
  }

  function PublicRoute({ component, ...rest }) {
    return (
      <Route
        {...rest}
        render={props =>
          isAuthenticated ? (
            <Redirect
              to={{
                pathname: "/",
              }}
            />
          ) : (
            React.createElement(component, props)
          )
        }
      />
    );
  }
}
