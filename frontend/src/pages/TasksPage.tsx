import { useEffect, useState } from "react";
import { listInspectionTask, listAssignments } from "../api/InspectionTask";
import { useFireDeviceStore } from "../stores/FireDeviceStore";
import { StatusBadge } from "../components/common/StatusBadge";
import { ChecklistPanel } from "../components/common/ChecklistPanel";
import { EmptyState } from "../components/common/EmptyState";
import { usePagination } from "../hooks/usePagination";
import { InspectionStatusText } from "../constants/InspectionStatus";
import { formatDate } from "../utils/formatters";
import type { InspectionTask } from "../types/InspectionTask";
import type { TaskDeviceAssignment } from "../types/TaskDeviceAssignment";

export function TasksPage() {
  const deviceStore = useFireDeviceStore();
  const [tasks, setTasks] = useState<InspectionTask[]>([]);
  const [assignments, setAssignments] = useState<TaskDeviceAssignment[]>([]);
  const [selected, setSelected] = useState<number | null>(null);

  useEffect(() => {
    void deviceStore.load();
    listInspectionTask().then(setTasks).catch(() => setTasks([]));
    listAssignments().then(setAssignments).catch(() => setAssignments([]));
  }, []);

  const { pageRows, page, setPage, total, pageSize } = usePagination(tasks);
  const deviceCode = (id: number | null) =>
    id == null ? "—" : deviceStore.rows.find((d) => d.id === id)?.device_code ?? `#${id}`;

  return (
    <main className="page">
      <section className="page-head">
        <div>
          <p className="eyebrow">inspection tasks</p>
          <h1>巡检任务</h1>
        </div>
        <span className="muted">共 {total} 个任务</span>
      </section>

      <section className="workbench">
        <div className="panel wide stack">
          <h2>任务排期</h2>
          <table className="grid">
            <thead><tr><th>任务</th><th>计划时间</th><th>类型</th><th>状态</th><th>清单</th></tr></thead>
            <tbody>
              {pageRows.map((t) => (
                <tr key={t.id} onClick={() => setSelected(t.id)} style={{ cursor: "pointer" }}>
                  <td><strong>#{t.id}</strong></td>
                  <td>{formatDate(t.plan_date)}</td>
                  <td>{t.task_type}</td>
                  <td>
                    <StatusBadge value={t.status} group="InspectionStatus" />
                    <span className="muted"> {InspectionStatusText[t.status as keyof typeof InspectionStatusText]}</span>
                  </td>
                  <td>
                    <ChecklistPanel version={t.checklist_version} completed={t.status === "REVIEWED" ? 1 : 0} total={1} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="tag-list">
            <button className="btn secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>上一页</button>
            <span className="muted">{page} / {Math.max(1, Math.ceil(total / pageSize))}</span>
            <button className="btn secondary" disabled={page * pageSize >= total} onClick={() => setPage(page + 1)}>下一页</button>
          </div>
        </div>

        <div className="panel stack">
          <h2>设备绑定关系</h2>
          {selected == null ? (
            <EmptyState title="选择任务" description="点击左侧任务查看原设备 / 备用 / 待补检关系" />
          ) : (
            assignments
              .filter((a) => a.task_id === selected)
              .map((a) => (
                <div key={a.id} className="row" style={{ gridTemplateColumns: "1fr auto" }}>
                  <div>
                    计划 {deviceCode(a.planned_device_id)}
                    {a.actual_device_id && a.actual_device_id !== a.planned_device_id
                      ? <> → 实际 <strong>{deviceCode(a.actual_device_id)}</strong></>
                      : null}
                    {a.queue_position ? <div className="muted">队列位置 {a.queue_position}</div> : null}
                  </div>
                  <StatusBadge value={a.assignment_status} group="AssignmentStatus" />
                </div>
              ))
          )}
        </div>
      </section>
    </main>
  );
}
