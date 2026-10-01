export const ROLES = ["INSPECTOR", "MAINTAINER", "SUPERVISOR", "AUDITOR"] as const;
export type Role = (typeof ROLES)[number];

export const RoleText: Record<Role, string> = {
  INSPECTOR: "巡检员",
  MAINTAINER: "维保商",
  SUPERVISOR: "物业主管",
  AUDITOR: "审计员"
};

// 本地演示账号，配合后端 x-user-id 头切换
export const DEMO_USERS = [
  { id: 1, name: "周巡检", role: "INSPECTOR" },
  { id: 2, name: "吴维保", role: "MAINTAINER" },
  { id: 3, name: "郑主管", role: "SUPERVISOR" },
  { id: 4, name: "王审计", role: "AUDITOR" }
] as const;
