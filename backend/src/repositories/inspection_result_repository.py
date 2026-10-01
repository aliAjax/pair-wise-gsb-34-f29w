from src.models.inspection_result import InspectionResult


class InspectionResultRepository:
    def __init__(self, db):
        self.db = db

    def find_all(self, task_id=None, device_id=None, review_flag=None):
        query = self.db.query(InspectionResult)
        if task_id is not None:
            query = query.filter(InspectionResult.task_id == task_id)
        if device_id is not None:
            query = query.filter(InspectionResult.device_id == device_id)
        if review_flag:
            query = query.filter(InspectionResult.review_flag == review_flag)
        return query.order_by(InspectionResult.id.asc()).all()

    def find_by_devices(self, device_ids, only_active=True):
        if not device_ids:
            return []
        query = self.db.query(InspectionResult).filter(InspectionResult.device_id.in_(device_ids))
        if only_active:
            query = query.filter(InspectionResult.review_flag == "ACTIVE")
        return query.all()

    def get(self, result_id):
        return self.db.query(InspectionResult).filter(InspectionResult.id == result_id).one_or_none()

    def create(self, **fields):
        row = InspectionResult(**fields)
        self.db.add(row)
        self.db.flush()
        return row
