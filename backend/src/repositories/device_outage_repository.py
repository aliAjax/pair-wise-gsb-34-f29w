from src.models.device_outage import DeviceOutage
from src.models.outage_batch import OutageBatch


class DeviceOutageRepository:
    def __init__(self, db):
        self.db = db

    # ---- 批次 ----
    def create_batch(self, **fields):
        row = OutageBatch(**fields)
        self.db.add(row)
        self.db.flush()
        return row

    def get_batch(self, batch_id):
        return self.db.query(OutageBatch).filter(OutageBatch.id == batch_id).one_or_none()

    def find_all_batches(self):
        return self.db.query(OutageBatch).order_by(OutageBatch.id.desc()).all()

    # ---- 停用时段 ----
    def create_outage(self, **fields):
        row = DeviceOutage(**fields)
        self.db.add(row)
        self.db.flush()
        return row

    def get_outage(self, outage_id):
        return self.db.query(DeviceOutage).filter(DeviceOutage.id == outage_id).one_or_none()

    def find_by_batch(self, batch_id):
        return (
            self.db.query(DeviceOutage)
            .filter(DeviceOutage.batch_id == batch_id)
            .order_by(DeviceOutage.id.asc())
            .all()
        )

    def find_pending_by_batch(self, batch_id):
        return (
            self.db.query(DeviceOutage)
            .filter(DeviceOutage.batch_id == batch_id, DeviceOutage.status == "PENDING")
            .order_by(DeviceOutage.id.asc())
            .all()
        )

    def find_confirmed_by_device(self, device_id):
        return (
            self.db.query(DeviceOutage)
            .filter(DeviceOutage.device_id == device_id, DeviceOutage.status == "CONFIRMED")
            .order_by(DeviceOutage.start_at.asc())
            .all()
        )

    def find_all_confirmed(self):
        return (
            self.db.query(DeviceOutage)
            .filter(DeviceOutage.status == "CONFIRMED")
            .order_by(DeviceOutage.start_at.asc())
            .all()
        )

    def find_all(self, device_id=None, status=None):
        query = self.db.query(DeviceOutage)
        if device_id is not None:
            query = query.filter(DeviceOutage.device_id == device_id)
        if status:
            query = query.filter(DeviceOutage.status == status)
        return query.order_by(DeviceOutage.id.desc()).all()
