export function EmptyState({
  title = "暂无数据",
  description
}: {
  title?: string;
  description?: string;
}) {
  return (
    <div className="empty">
      <strong>{title}</strong>
      {description ? <p className="muted" style={{ margin: "6px 0 0" }}>{description}</p> : null}
    </div>
  );
}
