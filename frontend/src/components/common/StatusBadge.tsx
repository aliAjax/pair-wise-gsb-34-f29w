import { formatStatus } from "../../utils/formatters";

type StatusGroup =
  | "DeviceStatus"
  | "OutageStatus"
  | "AssignmentStatus"
  | "ReviewStatus"
  | "ProcedureType"
  | "InspectionStatus";

export function StatusBadge({
  value,
  group
}: {
  value: string;
  group?: StatusGroup;
}) {
  const label = group ? formatStatus(value, group) : value.replace(/_/g, " ");
  return (
    <span
      className={
        "badge " + String(value).toLowerCase().replace(/_/g, "-")
      }
    >
      {label}
    </span>
  );
}
