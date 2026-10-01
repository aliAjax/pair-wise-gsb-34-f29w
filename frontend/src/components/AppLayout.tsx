import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import { NavLink, Outlet } from "react-router-dom";

import { DEMO_USERS, RoleText } from "../constants/roles";
import { routes } from "../router/routes";
import { useAppDispatch, useAppSelector } from "../stores/hooks";
import { switchActor } from "../stores/SessionStore";

const DRAWER_WIDTH = 240;

export function AppLayout() {
  const dispatch = useAppDispatch();
  const actorId = useAppSelector((state) => state.session.actorId);
  const actor = DEMO_USERS.find((user) => user.id === actorId) ?? DEMO_USERS[2];
  const visibleRoutes = routes.filter((route) => route.roles.includes(actor.role));

  return (
    <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "#eef1e8" }}>
      <AppBar
        position="fixed"
        sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, bgcolor: "#223126", width: "100%" }}
      >
        <Toolbar sx={{ justifyContent: "space-between" }}>
          <Typography variant="h6" sx={{ fontWeight: 800 }}>
            消防设施巡检维保平台
          </Typography>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Typography variant="body2">演示身份</Typography>
            <Select
              size="small"
              value={actor.id}
              onChange={(event) => dispatch(switchActor(Number(event.target.value)))}
              sx={{
                bgcolor: "#f5f1e6",
                color: "#223126",
                borderRadius: 1,
                "& .MuiOutlinedInput-notchedOutline": { border: 0 }
              }}
            >
              {DEMO_USERS.map((user) => (
                <MenuItem key={user.id} value={user.id}>
                  {user.name} · {RoleText[user.role]}
                </MenuItem>
              ))}
            </Select>
          </Box>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="permanent"
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: {
            width: DRAWER_WIDTH,
            boxSizing: "border-box",
            bgcolor: "#2c3f31",
            color: "#f5f1e6",
            borderRight: "4px solid #d39b46",
            paddingTop: 8
          }
        }}
      >
        <List>
          {visibleRoutes.map((route) => (
            <ListItemButton
              key={route.path}
              component={NavLink}
              to={route.path}
              sx={{
                mx: 1,
                borderRadius: 1,
                color: "#f5f1e6",
                "&.active": { bgcolor: "#f5f1e6", color: "#223126", fontWeight: 800 }
              }}
            >
              <ListItemText
                primary={route.name}
                secondary={
                  <Typography
                    component="span"
                    variant="caption"
                    sx={{ color: "inherit", opacity: 0.7 }}
                  >
                    {route.description}
                  </Typography>
                }
              />
            </ListItemButton>
          ))}
        </List>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3, width: `calc(100% - ${DRAWER_WIDTH}px)` }}>
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
}
