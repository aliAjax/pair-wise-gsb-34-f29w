export const routes = [
  { name: "消防合规总览", route: "/dashboard", page: "dashboard" },
  { name: "消防设备台账", route: "/devices", page: "devices" },
  { name: "停用保养与排期", route: "/outages", page: "outages" },
  { name: "巡检任务", route: "/tasks", page: "tasks" },
  { name: "隐患整改", route: "/hazards", page: "hazards" },
  { name: "合规报表", route: "/reports", page: "reports" }
] as const;

export type RoutePage = (typeof routes)[number]["page"];
