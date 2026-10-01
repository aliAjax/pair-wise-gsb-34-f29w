// 设备位置单元格：设备台账页与总览共享
export function DeviceLocationCell({
  floor,
  location
}: {
  floor: string;
  location: string;
}) {
  return (
    <span className="device-location">
      <strong>{floor}F</strong>
      <span className="muted"> · {location}</span>
    </span>
  );
}
