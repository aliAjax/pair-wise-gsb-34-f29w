import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import { routes, type RoutePage } from "./router/routes";
import { DashboardPage } from "./pages/DashboardPage";
import { DevicesPage } from "./pages/DevicesPage";
import { OutagePage } from "./pages/OutagePage";
import { TasksPage } from "./pages/TasksPage";
import { HazardsPage } from "./pages/HazardsPage";
import { ReportsPage } from "./pages/ReportsPage";
import "./styles.css";

const PAGE_VIEWS: Record<RoutePage, React.ComponentType> = {
  dashboard: DashboardPage,
  devices: DevicesPage,
  outages: OutagePage,
  tasks: TasksPage,
  hazards: HazardsPage,
  reports: ReportsPage
};

function App() {
  const [active, setActive] = useState<string>(routes[0].route);
  const current = routes.find((route) => route.route === active) ?? routes[0];
  const View = PAGE_VIEWS[current.page];

  return (
    <div className="shell">
      <aside>
        <div className="brand">消防设施巡检维保平台</div>
        <nav>
          {routes.map((route) => (
            <button
              key={route.route}
              className={active === route.route ? "active" : ""}
              onClick={() => setActive(route.route)}
            >
              {route.name}
            </button>
          ))}
        </nav>
      </aside>
      <View key={current.page} />
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
