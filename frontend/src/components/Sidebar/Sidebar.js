import React, { useState, useEffect } from "react";
import { Drawer, IconButton, List } from "@material-ui/core";
import {
  Android as RobotIcon,
  Business as IndustryIcon,
  ArrowBack as ArrowBackIcon,
} from "@material-ui/icons";
import { useTheme } from "@material-ui/styles";
import { withRouter } from "react-router-dom";
import classNames from "classnames";

// styles
import useStyles from "./styles";

// components
import SidebarLink from "./components/SidebarLink/SidebarLink";

// context
import {
  useLayoutState,
  useLayoutDispatch,
  toggleSidebar,
} from "../../context/LayoutContext";

const structure = [
  { id: 1, label: "Live Markets", link: "/app/livemarkets", icon: <IndustryIcon/> },
  { id: 3, label: "Bot Management", link: "/app/bot_management", icon: <RobotIcon/> },
//    id: 5,
//    label: "Notifications",
//    link: "/app/notifications",
//    icon: <NotificationsIcon />,
//  },
//  {
//    id: 6,
//    label: "UI Elements",
//    link: "/app/ui",
//    icon: <UIElementsIcon />,
//    children: [
//      { label: "Icons", link: "/app/ui/icons" },
//      { label: "Charts", link: "/app/ui/charts" },
//      { label: "Maps", link: "/app/ui/maps" },
//    ],
//  },
//  { id: 7, type: "divider" },
//  { id: 8, type: "title", label: "HELP" },
//  { id: 9, label: "Library", link: "", icon: <LibraryIcon /> },
//  { id: 10, label: "Support", link: "", icon: <SupportIcon /> },
//  { id: 11, label: "FAQ", link: "", icon: <FAQIcon /> },
//  { id: 12, type: "divider" },
//  { id: 13, type: "title", label: "PROJECTS" },
//  {
//    id: 14,
//    label: "My recent",
//    link: "",
//    icon: <Dot size="small" color="warning" />,
//  },
//  {
//    id: 15,
//    label: "Starred",
//    link: "",
//    icon: <Dot size="small" color="primary" />,
//  },
//  {
//    id: 16,
//    label: "Background",
//    link: "",
//    icon: <Dot size="small" color="secondary" />,
//  },
];

function Sidebar({ location }) {
  var classes = useStyles();
  var theme = useTheme();

  // global
  var { isSidebarOpened } = useLayoutState();
  var layoutDispatch = useLayoutDispatch();

  // local
  var [isPermanent, setPermanent] = useState(true);

  useEffect(function() {
    window.addEventListener("resize", handleWindowWidthChange);
    handleWindowWidthChange();
    return function cleanup() {
      window.removeEventListener("resize", handleWindowWidthChange);
    };
  });

  return (
    <Drawer
      variant={isPermanent ? "permanent" : "temporary"}
      className={classNames(classes.drawer, {
        [classes.drawerOpen]: isSidebarOpened,
        [classes.drawerClose]: !isSidebarOpened,
      })}
      classes={{
        paper: classNames({
          [classes.drawerOpen]: isSidebarOpened,
          [classes.drawerClose]: !isSidebarOpened,
        }),
      }}
      open={isSidebarOpened}
    >
      <div className={classes.toolbar} />
      <div className={classes.mobileBackButton}>
        <IconButton onClick={() => toggleSidebar(layoutDispatch)}>
          <ArrowBackIcon
            classes={{
              root: classNames(classes.headerIcon, classes.headerIconCollapse),
            }}
          />
        </IconButton>
      </div>
      <List className={classes.sidebarList}>
        {structure.map(link => (
          <SidebarLink
            key={link.id}
            location={location}
            isSidebarOpened={isSidebarOpened}
            {...link}
          />
        ))}
      </List>
    </Drawer>
  );

  // ##################################################################
  function handleWindowWidthChange() {
    var windowWidth = window.innerWidth;
    var breakpointWidth = theme.breakpoints.values.md;
    var isSmallScreen = windowWidth < breakpointWidth;

    if (isSmallScreen && isPermanent) {
      setPermanent(false);
    } else if (!isSmallScreen && !isPermanent) {
      setPermanent(true);
    }
  }
}

export default withRouter(Sidebar);
