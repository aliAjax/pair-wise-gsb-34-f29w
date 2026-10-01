import { useEffect, useMemo, useState } from "react";
import { listInspectionTask } from "../api/InspectionTask";
import { listHazardTicket } from "../api/HazardTicket";
import { listFireDevice } from "../api/FireDevice";
import { StatCard } from "../components/common/StatCard";
import { EmptyState } from "../components/common/EmptyState";
import type { InspectionTask } from "../types/InspectionTask";
import type { HazardTicket } from "../types/HazardTicket";
import type { FireDevice } from "../types/FireDevice";

// 轻量月度合规率报表（本地数据计算，不接第三方图表服务）
export function ReportsPage() {
  const [tasks, setTasks] = useState<InspectionTask[]>([]);
  const [hazards, setHazards] = useState<HazardTicket[]>([]);
  const [devices, setDevices] = useState<FireDevice[]>([]);

  useEffect(() => {
    listInspectionTask().then(setTasks).catch(() => setTasks([]));
    listHazardTicket().then(setHazards).catch(() => setHazards([]));
    listFireDevice().then(setDevices).catch(() => setDevices([]));
  }, []);

  const monthly = useMemo(() => {
    const map = new Map<string, { total: number; reviewed: number; hazards: number }>();
    tasks.forEach((t) => {
      const month = t.plan_date?.slice(0, 7) ?? "未知";
      const bucket = map.get(month) ?? { total: 0, reviewed: 0, hazards: 0 };
      bucket.total += 1;
      if (t.status === "REVIEWED") bucket.reviewed += 1;
      map.set(month, bucket);
    });
    hazards.forEach((h) => {
      // 隐患没有月份字段时归入“—”
      const bucket = map.get("—") ?? { total: 0, reviewed: 0, hazards: 0 };
      bucket.hazards += 1;
      map.set("—", bucket);
    });
    return [...map.entries()].sort(([a], [b]) => a.localeCompare(b));
  }, [tasks, hazards]);

  const outageCount = devices.filter((d) => d.status === "OUT_OF_SERVICE").length;
  const faultRate = devices.length ? Math.round((outageCount / devices.length) * 100) : 0;

  return (
    <main className="page">
      <section className="page-head">
        <div>
          <p className="eyebrow">compliance reports</p>
          <h1>合规报表</h1>
        </div>
      </section>

      <section className="metrics">
        <StatCard label="任务总数" value={tasks.length} />
        <StatCard label="隐患总数" value={hazards.length} />
        <StatCard label="设备停用率" value={`${faultRate}%`} />
      </section>

      <section className="panel stack">
        <h2>月度巡检 / 整改</h2>
        {monthly.length === 0 ? (
          <EmptyState title="暂无报表数据" />
        ) : (
          <table className="grid">
            <thead><tr><th>月份</th><th>巡检任务</th><th>已复核</th><th>巡检率</th></tr></thead>
            <tbody>
              {monthly.map(([month, b]) => (
                <tr key={month}>
                  <td>{month}</td>
                  <td>{b.total}</td>
                  <td>{b.reviewed}</td>
                  <td>{b.total ? Math.round((b.reviewed / b.total) * 100) : 0}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}
