import { formatCapacityRatio } from "../../utils/formatters";

/**
 * 备用容量占用条：停用确认时展示“已占用 / 总容量”。
 * >=100% 用 danger 配色（容量不足，排队转待补检）。
 */
export function OutageCapacityBar({
  used,
  total,
  showText = true
}: {
  used: number;
  total: number;
  showText?: boolean;
}) {
  const ratio = formatCapacityRatio(used, total);
  const exhausted = used >= total && total > 0;
  return (
    <div className={"capacity" + (exhausted ? " danger" : "")}>
      <div className="capacity-track">
        <div className="capacity-fill" style={{ width: `${ratio}%` }} />
      </div>
      {showText && (
        <span className="capacity-text">
          已占用 {used} / {total}（{ratio}%）
          {exhausted ? " · 容量不足，转待补检" : ""}
        </span>
      )}
    </div>
  );
}
