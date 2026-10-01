// 路由表：path/名称/允许角色；路由守卫用 roles 控制访问
export interface AppRoute {
  name: string;
  path: string;
  roles: Array<"INSPECTOR" | "MAINTAINER" | "SUPERVISOR" | "AUDITOR">;
  description: string;
}

export const routes: AppRoute[] = [
  {
    name: "消防合规总览",
    path: "/dashboard",
    roles: ["INSPECTOR", "MAINTAINER", "SUPERVISOR", "AUDITOR"],
    description: "设备状态、待补检、作废待复核与停用占用"
  },
  {
    name: "停机保养排期",
    path: "/outages",
    roles: ["MAINTAINER", "SUPERVISOR", "AUDITOR"],
    description: "停用时段、冲突草稿、失败续传与改派联动"
  },
  {
    name: "消防设备台账",
    path: "/devices",
    roles: ["INSPECTOR", "MAINTAINER", "SUPERVISOR", "AUDITOR"],
    description: "设备状态、复役手续与复役闸口"
  },
  {
    name: "巡检任务",
    path: "/tasks",
    roles: ["INSPECTOR", "MAINTAINER", "SUPERVISOR", "AUDITOR"],
    description: "备用设备改派、待补检排队与检查项"
  },
  {
    name: "隐患整改",
    path: "/hazards",
    roles: ["INSPECTOR", "MAINTAINER", "SUPERVISOR", "AUDITOR"],
    description: "隐患分级、派单、复验与作废复核"
  },
  {
    name: "合规报表",
    path: "/reports",
    roles: ["SUPERVISOR", "AUDITOR"],
    description: "巡检率、整改率、停用冲突统计"
  }
];
