import React from "react";
import type { ReactNode } from "react";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";
import { createBrowserRouter, Navigate, RouterProvider } from "react-router-dom";
import { CssBaseline } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";

import { AppLayout } from "./components/AppLayout";
import { ToastProvider } from "./components/common/Toast";
import { DEMO_USERS, type Role } from "./constants/roles";
import { DashboardPage } from "./pages/DashboardPage";
import { DevicesPage } from "./pages/DevicesPage";
import { OutagesPage } from "./pages/OutagesPage";
import { TasksPage } from "./pages/TasksPage";
import { HazardsPage } from "./pages/HazardsPage";
import { ReportsPage } from "./pages/ReportsPage";
import { RoleGuard } from "./router/RoleGuard";
import { store } from "./stores";
import { useAppSelector } from "./stores/hooks";
import "./styles.css";

const theme = createTheme({
  palette: {
    primary: { main: "#274335" },
    secondary: { main: "#d39b46" },
    warning: { main: "#8a5a12" },
    error: { main: "#8a2b2b" },
    background: { default: "#eef1e8" }
  },
  typography: {
    fontFamily: `"PingFang SC", "Microsoft YaHei", system-ui, sans-serif`
  }
});

// 按当前会话角色做路由守卫（菜单显隐与页面访问都走这里）
function Guarded({ roles, children }: { roles: Role[]; children: ReactNode }) {
  const actorId = useAppSelector((state) => state.session.actorId);
  const actor = DEMO_USERS.find((user) => user.id === actorId) ?? DEMO_USERS[2];
  if (!roles.includes(actor.role)) return <Navigate to="/dashboard" replace />;
  return <RoleGuard role={actor.role}>{children}</RoleGuard>;
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      {
        path: "dashboard",
        element: (
          <Guarded roles={["INSPECTOR", "MAINTAINER", "SUPERVISOR", "AUDITOR"]}>
            <DashboardPage />
          </Guarded>
        )
      },
      {
        path: "outages",
        element: (
          <Guarded roles={["MAINTAINER", "SUPERVISOR", "AUDITOR"]}>
            <OutagesPage />
          </Guarded>
        )
      },
      {
        path: "devices",
        element: (
          <Guarded roles={["INSPECTOR", "MAINTAINER", "SUPERVISOR", "AUDITOR"]}>
            <DevicesPage />
          </Guarded>
        )
      },
      {
        path: "tasks",
        element: (
          <Guarded roles={["INSPECTOR", "MAINTAINER", "SUPERVISOR", "AUDITOR"]}>
            <TasksPage />
          </Guarded>
        )
      },
      {
        path: "hazards",
        element: (
          <Guarded roles={["INSPECTOR", "MAINTAINER", "SUPERVISOR", "AUDITOR"]}>
            <HazardsPage />
          </Guarded>
        )
      },
      {
        path: "reports",
        element: (
          <Guarded roles={["SUPERVISOR", "AUDITOR"]}>
            <ReportsPage />
          </Guarded>
        )
      },
      { path: "*", element: <Navigate to="/dashboard" replace /> }
    ]
  }
]);

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <ToastProvider>
          <RouterProvider router={router} />
        </ToastProvider>
      </ThemeProvider>
    </Provider>
  </React.StrictMode>
);
