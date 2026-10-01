import { useEffect } from "react";
import { useFireDeviceStore } from "../stores/FireDeviceStore";
import { useHazardTicketStore } from "../stores/HazardTicketStore";
import { useInspectionResultStore } from "../stores/InspectionResultStore";
import { useOutageStore } from "../stores/OutageWindowStore";
import { StatCard } from "../components/common/StatCard";
import { StatusBadge } from "../components/common/StatusBadge";
import { ReviewFlag } from "../components/common/ReviewFlag";
import { DeviceTypeText } from "../constants/DeviceType";
import { formatRisk } from "../utils/formatters";

export function DashboardPage() {
  const devices = useFireDeviceStore();
  const hazards = useHazardTicketStore();
  const results = useInspectionResultStore();
  const outage = useOutageStore();

  useEffect(() => {
    void devices.load();
    void hazards.load();
    void results.load();
    void outage.loadWindows();
  }, []);

  const outOfService = devices.rows.filter((d) => d.status === "OUT_OF_SERVICE").length;
  const voidPending = hazards.rows.filter((h) => h.review_status === "VOID_PENDING").length;
  const abnormal = results.rows.filter((r) => r.result_status === "ABNORMAL").length;

  return (
    <main className="page">
      <section className="page-head">
        <div>
          <p className="eyebrow">compliance dashboard</p>
          <h1>消防合规总览</h1>
        </div>
        <StatusBadge value="NORMAL" group="DeviceStatus" />
      </section>

      <section className="metrics">
        <StatCard label="设备总数" value={devices.rows.length} />
        <StatCard label="停用保养中" value={outOfService} />
        <StatCard label="作废待复核单据" value={voidPending} />
      </section>

      <section className="workbench">
        <div className="panel wide stack">
          <h2>设备状态分布</h2>
          <table className="grid">
            <thead><tr><th>设备编号</th><th>类型</th><th>位置</th><th>状态</th><th>容量</th></tr></thead>
            <tbody>
              {devices.rows.map((d) => (
                <tr key={d.id}>
                  <td>{d.device_code}</td>
                  <td>{DeviceTypeText[d.device_type as keyof typeof DeviceTypeText] ?? d.device_type}</td>
                  <td>{d.floor}F · {d.location_desc}</td>
                  <td><StatusBadge value={d.status} group="DeviceStatus" /></td>
                  <td>{d.capacity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="panel stack">
          <h2>高危与异常</h2>
          <p className="muted">异常巡检结果：{abnormal}</p>
          {hazards.rows.slice(0, 6).map((h) => (
            <div key={h.id} className="row" style={{ gridTemplateColumns: "1fr auto" }}>
              <strong>隐患 #{h.id} · {formatRisk(h.severity)}</strong>
              {h.review_status === "VOID_PENDING" ? (
                <ReviewFlag reviewStatus={h.review_status} windowId={h.voided_by_window_id} />
              ) : (
                <StatusBadge value={h.rectify_status} />
              )}
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
