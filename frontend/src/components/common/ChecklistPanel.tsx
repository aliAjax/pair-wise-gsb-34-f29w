// 检查清单面板：巡检任务页展示清单版本与完成进度
export function ChecklistPanel({
  version,
  completed,
  total
}: {
  version: string;
  completed: number;
  total: number;
}) {
  const percent = total > 0 ? Math.round((completed / total) * 100) : 0;
  return (
    <div className="shared-widget checklist">
      <strong>清单 {version}</strong>
      <div className="capacity-track" style={{ marginTop: 6 }}>
        <div className="capacity-fill" style={{ width: `${percent}%` }} />
      </div>
      <span className="muted">{completed}/{total} 项</span>
    </div>
  );
}
