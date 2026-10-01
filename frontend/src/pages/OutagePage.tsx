import { useEffect, useMemo, useState } from "react";
import { useOutageStore } from "../stores/OutageWindowStore";
import { useFireDeviceStore } from "../stores/FireDeviceStore";
import { listAssignments } from "../api/InspectionTask";
import { listProcedures } from "../api/OutageWindow";
import { useOutageScheduling, assignmentLabel } from "../hooks/useOutageScheduling";
import { OutageCapacityBar } from "../components/common/OutageCapacityBar";
import { StatusBadge } from "../components/common/StatusBadge";
import { StatCard } from "../components/common/StatCard";
import { EmptyState } from "../components/common/EmptyState";
import { ProcedureType, ProcedureTypeText } from "../constants/ProcedureType";
import { DeviceTypeText } from "../constants/DeviceType";
import { formatDate } from "../utils/formatters";
import { createOutageWindowForm } from "../constructors/OutageWindowConstructor";
import { ApiRequestError } from "../api/http";
import type { DeviceOutageWindow } from "../types/DeviceOutageWindow";
import type { TaskDeviceAssignment } from "../types/TaskDeviceAssignment";

export function OutagePage() {
  const outage = useOutageStore();
  const deviceStore = useFireDeviceStore();

  const [form, setForm] = useState(createOutageWindowForm());
  const [originals, setOriginals] = useState<TaskDeviceAssignment[]>([]);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [notice, setNotice] = useState<{ kind: "ok" | "warn" | "error"; text: string } | null>(null);

  useEffect(() => {
    void outage.loadWindows();
    void deviceStore.load();
  }, []);

  useEffect(() => {
    listAssignments().then(setOriginals).catch(() => setOriginals([]));
  }, [outage.windows.length]);

  // 拉取每个已确认窗口的派生排期
  useEffect(() => {
    outage.windows
      .filter((w) => w.outage_status !== "DRAFT" || w.write_stage !== "PERSIST_WINDOW")
      .forEach((w) => {
        if (!outage.assignments[w.id]) void outage.loadAssignments(w.id);
      });
  }, [outage.windows.length]);

  const devices = deviceStore.rows;
  const summary = useOutageScheduling(devices, outage.windows, outage.assignments, originals);

  const deviceById = useMemo(() => {
    const map = new Map<number, (typeof devices)[number]>();
    devices.forEach((d) => map.set(d.id, d));
    return map;
  }, [devices]);

  const flash = (kind: "ok" | "warn" | "error", text: string) => {
    setNotice({ kind, text });
  };

  const onSubmitDraft = async () => {
    setBusyId(-1);
    try {
      await outage.submit({
        ...form,
        start_at: new Date(form.start_at).toISOString(),
        end_at: new Date(form.end_at).toISOString()
      });
      flash("ok", "停用时段已提交为草稿，可在下方确认。");
    } catch (e) {
      flash("error", (e as ApiRequestError).message);
    } finally {
      setBusyId(null);
    }
  };

  const onConfirm = async (w: DeviceOutageWindow) => {
    setBusyId(w.id);
    try {
      await outage.confirm(w.id);
      flash("ok", `停用时段 #${w.id} 确认完成，同段巡检已改用备用设备或转入待补检。`);
    } catch (e) {
      flash("error", (e as ApiRequestError).message);
    } finally {
      setBusyId(null);
    }
  };

  const onConfirmGuard = async (w: DeviceOutageWindow) => {
    setBusyId(w.id);
    try {
      const res = await outage.confirmGuard(w.id, w.owner_id);
      if (res.conflict) {
        flash(
          "warn",
          `检测到重叠占用：已占用 ${res.occupied_capacity}/${res.backup_capacity_total}，需求 ${res.demanded_capacity}。容量不足，您的提交已保留为草稿。`
        );
      } else {
        flash("ok", "容量充足，停用时段已确认。");
      }
    } catch (e) {
      flash("error", (e as ApiRequestError).message);
    } finally {
      setBusyId(null);
    }
  };

  const onResume = async () => {
    const failure = outage.lastFailure;
    if (!failure) return;
    setBusyId(failure.windowId);
    try {
      await outage.resume(failure.windowId, failure.resumeKey);
      flash("ok", `窗口 #${failure.windowId} 已从断点恢复，名额不重复、不丢失。`);
    } catch (e) {
      flash("error", (e as ApiRequestError).message);
    } finally {
      setBusyId(null);
    }
  };

  const onRestore = async (deviceId: number) => {
    setBusyId(deviceId);
    try {
      const res = await outage.restore(deviceId);
      flash("ok", `设备已复役恢复正常，并补排 ${res.rescheduled} 个待补检项。`);
      await deviceStore.load();
    } catch (e) {
      flash("error", (e as ApiRequestError).message);
    } finally {
      setBusyId(null);
    }
  };

  return (
    <main className="page">
      <section className="page-head">
        <div>
          <p className="eyebrow">outage &amp; scheduling</p>
          <h1>停用保养与巡检排期</h1>
        </div>
        <StatusBadge value={outage.loading ? "DRAFT" : "CONFIRMED"} group="OutageStatus" />
      </section>

      <section className="metrics">
        <StatCard label="原任务关系（保留）" value={summary.totalOriginal} />
        <StatCard label="改用备用设备" value={summary.totalBackup} />
        <StatCard label="排队待补检" value={summary.totalPending} />
      </section>

      {notice && <div className={`alert ${notice.kind}`}>{notice.text}</div>}
      {outage.lastFailure && (
        <div className="alert warn">
          窗口 #{outage.lastFailure.windowId} 写入中断。{outage.lastFailure.message}
          <button className="btn secondary" style={{ marginLeft: 10 }} onClick={onResume}>
            使用恢复键续跑
          </button>
        </div>
      )}

      <section className="workbench">
        <div className="panel wide stack">
          <h2>提交设备停用时段</h2>
          <div className="form-grid">
            <div className="field">
              <label>停用设备</label>
              <select
                value={form.device_id}
                onChange={(e) => setForm({ ...form, device_id: Number(e.target.value) })}
              >
                {devices.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.device_code} · {DeviceTypeText[d.device_type as keyof typeof DeviceTypeText] ?? d.device_type}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>负责人 ID</label>
              <input
                type="number"
                value={form.owner_id}
                onChange={(e) => setForm({ ...form, owner_id: Number(e.target.value) })}
              />
            </div>
            <div className="field">
              <label>开始时间</label>
              <input
                type="datetime-local"
                value={form.start_at}
                onChange={(e) => setForm({ ...form, start_at: e.target.value })}
              />
            </div>
            <div className="field">
              <label>结束时间</label>
              <input
                type="datetime-local"
                value={form.end_at}
                onChange={(e) => setForm({ ...form, end_at: e.target.value })}
              />
            </div>
            <div className="field" style={{ gridColumn: "1 / -1" }}>
              <label>停用原因</label>
              <input
                value={form.reason}
                onChange={(e) => setForm({ ...form, reason: e.target.value })}
                placeholder="例如：年度保养 / 故障更换"
              />
            </div>
          </div>
          <div>
            <button className="btn" disabled={busyId === -1} onClick={onSubmitDraft}>
              提交停用时段（草稿）
            </button>
          </div>
        </div>

        <div className="panel stack">
          <h2>备用容量占用</h2>
          {summary.backupUsage.length === 0 ? (
            <EmptyState title="暂无占用" description="确认停用后这里展示各备用设备占用率" />
          ) : (
            summary.backupUsage.map(({ device, used, ratio }) => (
              <div key={device.id}>
                <div className="muted">
                  {device.device_code}（容量 {device.capacity}）
                </div>
                <OutageCapacityBar used={used} total={device.capacity} />
                <span className="muted">占用率 {Math.round(ratio * 100)}%</span>
              </div>
            ))
          )}
        </div>
      </section>

      <section className="panel stack">
        <h2>停用时段与排期联动</h2>
        {outage.windows.length === 0 ? (
          <EmptyState title="暂无停用时段" description="在上方提交第一个停用申请" />
        ) : (
          <table className="grid">
            <thead>
              <tr>
                <th>窗口</th>
                <th>设备</th>
                <th>停用时间</th>
                <th>状态</th>
                <th>占用 / 容量</th>
                <th>排期去向</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {outage.windows.map((w) => {
                const device = deviceById.get(w.device_id);
                const derived = outage.assignments[w.id] ?? [];
                const backupCount = derived.filter((a) => a.assignment_status === "BACKUP").length;
                const pendingCount = derived.filter((a) => a.assignment_status === "PENDING_RECHECK").length;
                const totalCap = device
                  ? devices
                      .filter((d) => d.building_id === device.building_id && d.device_type === device.device_type && d.id !== device.id && d.status === "NORMAL")
                      .reduce((s, d) => s + d.capacity, 0)
                  : 0;
                return (
                  <tr key={w.id}>
                    <td>
                      <strong>#{w.id}</strong>
                      <div className="muted">v{w.version} · 负责人 {w.owner_id}</div>
                      {w.write_stage !== "COMPLETED" && w.write_stage !== "PERSIST_WINDOW" && (
                        <div className="muted">断点：{w.write_stage}</div>
                      )}
                    </td>
                    <td>
                      {device?.device_code ?? w.device_id}
                      <div className="muted">
                        {device ? DeviceTypeText[device.device_type as keyof typeof DeviceTypeText] ?? device.device_type : ""}
                      </div>
                    </td>
                    <td>
                      <div>{formatDate(w.start_at)}</div>
                      <div className="muted">至 {formatDate(w.end_at)}</div>
                    </td>
                    <td><StatusBadge value={w.outage_status} group="OutageStatus" /></td>
                    <td>
                      <OutageCapacityBar used={w.occupied_capacity} total={totalCap} />
                      <div className="muted">需求 {w.demanded_capacity}</div>
                    </td>
                    <td>
                      <span className="tag-list">
                        <span className="chip done">备用 {backupCount}</span>
                        <span className={pendingCount ? "chip" : "chip done"}>待补检 {pendingCount}</span>
                      </span>
                      {derived.slice(0, 3).map((a) => (
                        <div key={a.id} className="muted">
                          任务#{a.task_id} → {assignmentLabel(a.assignment_status)}
                          {a.actual_device_id ? ` #${a.actual_device_id}` : `（队列 ${a.queue_position}）`}
                        </div>
                      ))}
                    </td>
                    <td>
                      <div className="tag-list">
                        {w.outage_status === "DRAFT" && (
                          <>
                            <button className="btn" disabled={busyId === w.id} onClick={() => onConfirm(w)}>
                              确认停用
                            </button>
                            <button className="btn secondary" disabled={busyId === w.id} onClick={() => onConfirmGuard(w)}>
                              并发确认（看占用）
                            </button>
                          </>
                        )}
                        {w.outage_status === "CONFIRMED" && device?.status === "OUT_OF_SERVICE" && (
                          <button className="btn secondary" disabled={busyId === device.id} onClick={() => onRestore(device.id)}>
                            复役
                          </button>
                        )}
                      </div>
                      <ProcedureChecklist windowId={w.id} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </section>

      <section className="panel stack">
        <h2>原任务关系（保留不删）→ 当前落地</h2>
        {originals.length === 0 ? (
          <EmptyState title="暂无巡检排期" description="创建巡检任务后这里展示原设备绑定" />
        ) : (
          <table className="grid">
            <thead>
              <tr><th>原排期</th><th>任务</th><th>计划设备</th><th>当前去向</th><th>目标设备</th></tr>
            </thead>
            <tbody>
              {summary.originResolution.map((r) => (
                <tr key={r.originId}>
                  <td>#{r.originId}</td>
                  <td>任务 #{r.taskId}</td>
                  <td>
                    {(() => {
                      const o = originals.find((x) => x.id === r.originId);
                      const d = o ? deviceById.get(o.planned_device_id) : undefined;
                      return d ? `${d.device_code}` : o?.planned_device_id;
                    })()}
                  </td>
                  <td><StatusBadge value={r.kind} group="AssignmentStatus" /></td>
                  <td>{r.targetDeviceId ? `#${r.targetDeviceId} ${deviceById.get(r.targetDeviceId)?.device_code ?? ""}` : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}

function ProcedureChecklist({ windowId }: { windowId: number }) {
  const outage = useOutageStore();
  const [done, setDone] = useState<string[]>([]);

  useEffect(() => {
    listProcedures(windowId)
      .then((rows) => setDone(rows.map((r) => r.procedure_type)))
      .catch(() => undefined);
  }, [windowId, outage.windows.length]);

  return (
    <div className="tag-list" style={{ marginTop: 8 }}>
      {ProcedureType.map((p) => {
        const registered = done.includes(p);
        return (
          <button
            key={p}
            className={"chip" + (registered ? " done" : "")}
            title={registered ? "已登记" : "点击登记该复役手续"}
            onClick={async () => {
              await outage.addProcedure(windowId, p);
              setDone((prev) => (prev.includes(p) ? prev : [...prev, p]));
            }}
          >
            {ProcedureTypeText[p]} {registered ? "✓" : ""}
          </button>
        );
      })}
    </div>
  );
}
