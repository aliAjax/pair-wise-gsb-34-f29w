from src.models.device_outage import DeviceOutage
from src.models.task_reroute import TaskReroute


class TaskRerouteRepository:
    def __init__(self, db):
        self.db = db

    def find_for_task_outage(self, task_id, outage_id):
        return (
            self.db.query(TaskReroute)
            .filter(TaskReroute.task_id == task_id, TaskReroute.outage_id == outage_id)
            .all()
        )

    def find_by_outage(self, outage_id):
        return (
            self.db.query(TaskReroute)
            .filter(TaskReroute.outage_id == outage_id)
            .order_by(TaskReroute.id.asc())
            .all()
        )

    def find_backup_rows_with_window(self, backup_device_id):
        """取某备用设备承担的全部改派记录及其停用窗口（窗口重叠在 service 判）。"""
        return (
            self.db.query(TaskReroute, DeviceOutage)
            .join(DeviceOutage, DeviceOutage.id == TaskReroute.outage_id)
            .filter(
                TaskReroute.backup_device_id == backup_device_id,
                TaskReroute.relation == "BACKUP",
            )
            .all()
        )

    def exists(self, task_id, outage_id, device_id, relation):
        # 续传幂等：已占名额不重复也不丢失
        return (
            self.db.query(TaskReroute)
            .filter(
                TaskReroute.task_id == task_id,
                TaskReroute.outage_id == outage_id,
                TaskReroute.device_id == device_id,
                TaskReroute.relation == relation,
            )
            .first()
            is not None
        )

    def create(self, **fields):
        row = TaskReroute(**fields)
        self.db.add(row)
        self.db.flush()
        return row
