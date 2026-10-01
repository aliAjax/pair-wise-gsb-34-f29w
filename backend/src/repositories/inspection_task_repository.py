from src.models.inspection_task import InspectionTask


class InspectionTaskRepository:
    def __init__(self, db):
        self.db = db

    def find_all(self, status=None, building_id=None):
        query = self.db.query(InspectionTask)
        if status:
            query = query.filter(InspectionTask.status == status)
        if building_id is not None:
            query = query.filter(InspectionTask.building_id == building_id)
        return query.order_by(InspectionTask.plan_date.asc()).all()

    def get(self, task_id):
        return self.db.query(InspectionTask).filter(InspectionTask.id == task_id).one_or_none()

    def create(self, **fields):
        row = InspectionTask(**fields)
        self.db.add(row)
        self.db.flush()
        return row
