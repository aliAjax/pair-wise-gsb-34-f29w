"""消防设备响应构造器：ORM -> DTO。"""


def create_fire_device_dto(row, **overrides):
    data = {
        "id": row.id,
        "building_id": row.building_id,
        "device_code": row.device_code,
        "device_type": row.device_type,
        "floor": row.floor,
        "location_desc": row.location_desc,
        "install_date": row.install_date.isoformat() if getattr(row, "install_date", None) else None,
        "status": row.status,
        "capacity": getattr(row, "capacity", 3),
        "next_maintenance_at": row.next_maintenance_at.isoformat() if getattr(row, "next_maintenance_at", None) else None,
    }
    data.update(overrides)
    return data
