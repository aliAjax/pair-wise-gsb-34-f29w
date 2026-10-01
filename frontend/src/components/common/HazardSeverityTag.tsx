import { HazardSeverityText } from "../../constants/HazardSeverity";

// 隐患等级标签：总览、隐患页共享
export function HazardSeverityTag({ value }: { value: string }) {
  const text = HazardSeverityText[value as keyof typeof HazardSeverityText] ?? value;
  return (
    <span className={"badge severity-" + value.toLowerCase()} title={`隐患等级：${text}`}>
      {text}
    </span>
  );
}
