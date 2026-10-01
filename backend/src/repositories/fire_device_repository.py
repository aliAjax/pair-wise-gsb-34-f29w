from src.models.fire_device import FireDevice


class FireDeviceRepository:
    def __init__(self, db):
        self.db = db

    def find_all(self, building_id=None, status=None, device_type=None):
        query = self.db.query(FireDevice)
        if building_id is not None:
            query = query.filter(FireDevice.building_id == building_id)
        if status:
            query = query.filter(FireDevice.status == status)
        if device_type:
            query = query.filter(FireDevice.device_type == device_type)
        return query.order_by(FireDevice.id.asc()).all()

    def get(self, device_id):
        return self.db.query(FireDevice).filter(FireDevice.id == device_id).one_or_none()

    def get_by_code(self, device_code):
        return (
            self.db.query(FireDevice)
            .filter(FireDevice.device_code == device_code)
            .one_or_none()
        )

    def find_backup_candidates(self, building_id, device_type, exclude_ids):
        query = (
            self.db.query(FireDevice)
            .filter(
                FireDevice.building_id == building_id,
                FireDevice.device_type == device_type,
                FireDevice.status == "NORMAL",
            )
        )
        if exclude_ids:
            query = query.filter(~FireDevice.id.in_(exclude_ids))
        return query.order_by(FireDevice.id.asc()).all()

    def create(self, **fields):
        row = FireDevice(**fields)
        self.db.add(row)
        self.db.flush()
        return row
