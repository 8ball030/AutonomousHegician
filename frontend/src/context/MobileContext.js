import React from "react";

var MobileStateContext = React.createContext();
var IsMobileDispatchContext = React.createContext();

function IsMobileReducer(state, action) {
  switch (action.type) {
    case "SET_MOBILE":
      return true;
    default: {
      throw new Error(`Unhandled action type: ${action.type}`);
    }
  }
}

export const MobileProvider = ({ children }) => {
  var [state, dispatch] = React.useReducer(IsMobileReducer, document.width < 500);
  return (
    <MobileStateContext.Provider value={state}>
      <IsMobileDispatchContext.Provider value={dispatch}>
        {children}
      </IsMobileDispatchContext.Provider>
    </MobileStateContext.Provider>
  );
}

export const useIsMobile = () => {
  var context = React.useContext(MobileStateContext);
  if (context === undefined) {
    throw new Error("useIsMobileState must be used within a IsMobileProvider");
  }
  return context;
}

export const useIsMobileDispatch = () => {
  var context = React.useContext(IsMobileDispatchContext);
  if (context === undefined) {
    throw new Error("useIsMobileDispatch must be used within a IsMobileProvider");
  }
  return context;
}

export const setMobile = (dispatch) => {
  dispatch({
    type: "SET_MOBILE",
  });
}
