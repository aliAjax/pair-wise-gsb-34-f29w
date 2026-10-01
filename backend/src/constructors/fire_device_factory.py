from src.utils.formatters import to_iso


def build_fire_device_dto(row):
    """ORM 设备 -> 响应 DTO。reuse_paperwork 同时给数组和逗号串，供前端手续清单使用。"""
    paperwork = [p for p in (row.reuse_paperwork or "").split(",") if p]
    return {
        "id": row.id,
        "building_id": row.building_id,
        "device_code": row.device_code,
        "device_type": row.device_type,
        "floor": row.floor,
        "location_desc": row.location_desc,
        "install_date": to_iso(row.install_date),
        "status": row.status,
        "next_maintenance_at": to_iso(row.next_maintenance_at),
        "reuse_paperwork": paperwork,
    }
