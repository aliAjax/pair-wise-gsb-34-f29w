import { useEffect, useMemo, useState } from "react";
import { useFireDeviceStore } from "../stores/FireDeviceStore";
import { StatusBadge } from "../components/common/StatusBadge";
import { DeviceLocationCell } from "../components/common/DeviceLocationCell";
import { DeviceTypeText } from "../constants/DeviceType";
import { DeviceStatus, DeviceStatusText } from "../constants/DeviceStatus";

export function DevicesPage() {
  const store = useFireDeviceStore();
  const [typeFilter, setTypeFilter] = useState<string>("ALL");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");

  useEffect(() => {
    void store.load();
  }, []);

  const rows = useMemo(
    () =>
      store.rows.filter(
        (d) =>
          (typeFilter === "ALL" || d.device_type === typeFilter) &&
          (statusFilter === "ALL" || d.status === statusFilter)
      ),
    [store.rows, typeFilter, statusFilter]
  );

  return (
    <main className="page">
      <section className="page-head">
        <div>
          <p className="eyebrow">device ledger</p>
          <h1>消防设备台账</h1>
        </div>
      </section>

      <section className="panel stack">
        <div className="form-grid">
          <div className="field">
            <label>设备类型</label>
            <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
              <option value="ALL">全部类型</option>
              {Object.entries(DeviceTypeText).map(([value, text]) => (
                <option key={value} value={value}>{text}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>设备状态</label>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="ALL">全部状态</option>
              {DeviceStatus.map((s) => (
                <option key={s} value={s}>{DeviceStatusText[s]}</option>
              ))}
            </select>
          </div>
        </div>

        <table className="grid">
          <thead>
            <tr><th>编号</th><th>类型</th><th>位置</th><th>备用容量</th><th>状态</th></tr>
          </thead>
          <tbody>
            {rows.map((d) => (
              <tr key={d.id}>
                <td><strong>{d.device_code}</strong></td>
                <td>{DeviceTypeText[d.device_type as keyof typeof DeviceTypeText] ?? d.device_type}</td>
                <td>
                  <DeviceLocationCell floor={d.floor} location={d.location_desc} />
                </td>
                <td>{d.capacity}</td>
                <td><StatusBadge value={d.status} group="DeviceStatus" /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}
