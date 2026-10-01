import { useEffect, useState } from "react";
import { useHazardTicketStore } from "../stores/HazardTicketStore";
import { listInspectionResult } from "../api/InspectionResult";
import { reviewHazardTicket } from "../api/HazardTicket";
import { HazardSeverityTag } from "../components/common/HazardSeverityTag";
import { ReviewFlag } from "../components/common/ReviewFlag";
import { StatusBadge } from "../components/common/StatusBadge";
import { EmptyState } from "../components/common/EmptyState";
import { usePagination } from "../hooks/usePagination";
import type { InspectionResult } from "../types/InspectionResult";

export function HazardsPage() {
  const store = useHazardTicketStore();
  const [results, setResults] = useState<InspectionResult[]>([]);
  const [notice, setNotice] = useState<string>("");

  useEffect(() => {
    void store.load();
    listInspectionResult().then(setResults).catch(() => setResults([]));
  }, []);

  const voidTickets = store.rows.filter((h) => h.review_status === "VOID_PENDING");
  const { pageRows, page, setPage, total, pageSize } = usePagination(store.rows);
  const deviceByResultId = new Map(results.map((r) => [r.id, r.device_id]));

  const review = async (id: number, status: "RECONFIRMED" | "REJECTED") => {
    await reviewHazardTicket(id, status);
    setNotice(status === "RECONFIRMED" ? `隐患 #${id} 复核通过` : `隐患 #${id} 维持作废`);
    await store.load();
  };

  return (
    <main className="page">
      <section className="page-head">
        <div>
          <p className="eyebrow">hazard rectification</p>
          <h1>隐患整改</h1>
        </div>
        <span className="muted">共 {total} 条</span>
      </section>

      {notice && <div className="alert ok">{notice}</div>}

      <section className="panel stack">
        <h2>作废待复核（停用时段变更触发）</h2>
        {voidTickets.length === 0 ? (
          <EmptyState title="暂无待复核单据" description="停用时段变更后相关单据会进入这里" />
        ) : (
          voidTickets.map((h) => (
            <div key={h.id} className="row" style={{ gridTemplateColumns: "1fr auto auto" }}>
              <div>
                <HazardSeverityTag value={h.severity} />
                <div className="muted">
                  来源巡检结果 #{h.result_id} · 设备 #{deviceByResultId.get(h.result_id) ?? "—"}
                </div>
              </div>
              <ReviewFlag reviewStatus={h.review_status} windowId={h.voided_by_window_id} />
              <span className="tag-list">
                <button className="btn" onClick={() => review(h.id, "RECONFIRMED")}>复核通过</button>
                <button className="btn secondary" onClick={() => review(h.id, "REJECTED")}>维持作废</button>
              </span>
            </div>
          ))
        )}
      </section>

      <section className="panel stack">
        <h2>全部隐患单</h2>
        <table className="grid">
          <thead><tr><th>单号</th><th>等级</th><th>整改状态</th><th>复核状态</th></tr></thead>
          <tbody>
            {pageRows.map((h) => (
              <tr key={h.id}>
                <td>#{h.id}</td>
                <td><HazardSeverityTag value={h.severity} /></td>
                <td><StatusBadge value={h.rectify_status} /></td>
                <td>
                  {h.review_status === "ACTIVE"
                    ? "—"
                    : <ReviewFlag reviewStatus={h.review_status} windowId={h.voided_by_window_id} />}
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
      </section>
    </main>
  );
}
