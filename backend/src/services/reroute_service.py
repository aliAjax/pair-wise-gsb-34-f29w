"""停用与巡检冲突的改派引擎。

规则：
1. 负责人确认停用时段后，同楼栋同类型且巡检计划落在停用窗口内的任务槽位受影响；
2. 受影响槽位优先改派给“同栋、同类型、正常、自身在该窗口未停用”的备用设备；
3. 每台备用设备在重叠窗口内容量有限（BACKUP_SLOT_CAPACITY），容量不足排队转成待补检；
4. 原任务关系（ORIGINAL）保留；BACKUP / QUEUED 是新增关系，不覆盖旧数据；
5. (task_id, outage_id, device_id, relation) 唯一，续传/重算时已占名额不重复也不丢失。
"""

from src.constants.log_templates import LOG_TEMPLATES
from src.constants.outage_status import BACKUP_SLOT_CAPACITY
from src.repositories.fire_device_repository import FireDeviceRepository
from src.repositories.inspection_result_repository import InspectionResultRepository
from src.repositories.inspection_task_repository import InspectionTaskRepository
from src.repositories.task_reroute_repository import TaskRerouteRepository


class RerouteService:
    def __init__(self, db, audit):
        self.db = db
        self.audit = audit
        self.device_repo = FireDeviceRepository(db)
        self.task_repo = InspectionTaskRepository(db)
        self.result_repo = InspectionResultRepository(db)
        self.reroute_repo = TaskRerouteRepository(db)

    def apply_for_outage(self, outage, actor):
        """对一条已确认停用时段执行改派，返回汇总。幂等：重复调用不产生重复名额。"""
        device = self.device_repo.get(outage.device_id)
        affected = self._affected_slots(device, outage)

        # 该设备自身之外的备用候选
        candidates = self.device_repo.find_backup_candidates(
            building_id=device.building_id,
            device_type=device.device_type,
            exclude_ids=[device.id],
        )
        # 剔除在同一窗口也处于已确认停用的候选
        usable = [c for c in candidates if not self._candidate_outage_in_window(c, outage)]

        rerouted = []
        queued = []
        for slot in affected:
            if self.reroute_repo.exists(slot["task"].id, outage.id, device.id, slot["relation"]):
                # 续跑/重算：原关系已占位，跳过
                continue
            # 始终保留原任务关系
            self.reroute_repo.create(
                task_id=slot["task"].id,
                outage_id=outage.id,
                device_id=device.id,
                backup_device_id=None,
                relation="ORIGINAL",
                note=f"停用前原检 {device.device_code}",
            )
            backup = self._pick_backup(usable, outage)
            if backup is not None:
                self.reroute_repo.create(
                    task_id=slot["task"].id,
                    outage_id=outage.id,
                    device_id=device.id,
                    backup_device_id=backup["device"].id,
                    relation="BACKUP",
                    note=f"改用备用设备 {backup['device'].device_code}",
                )
                rerouted.append({"task_id": slot["task"].id, "backup_device_id": backup["device"].id})
                self.audit.log(
                    actor, "InspectionTask", "InspectionTask.reroute", slot["task"].id,
                    detail=LOG_TEMPLATES["InspectionTask"][3].format(
                        task_id=slot["task"].id,
                        from_device_id=device.device_code,
                        to_device_id=backup["device"].device_code,
                    ),
                )
            else:
                self.reroute_repo.create(
                    task_id=slot["task"].id,
                    outage_id=outage.id,
                    device_id=device.id,
                    backup_device_id=None,
                    relation="QUEUED",
                    note="备用设备容量不足，排队待补检",
                )
                task = slot["task"]
                if task.status not in (
                    "SUBMITTED", "REVIEWED",
                ):
                    task.status = "PENDING_MAKEUP"
                queued.append({"task_id": task.id, "device_id": device.id})
                self.audit.log(
                    actor, "InspectionTask", "InspectionTask.makeup", task.id,
                    detail=LOG_TEMPLATES["InspectionTask"][4].format(
                        task_id=task.id, device_id=device.device_code,
                    ),
                )

        return {
            "affected_slot_count": len(affected),
            "rerouted": rerouted,
            "queued": queued,
            "backup_capacity": BACKUP_SLOT_CAPACITY,
        }

    def _affected_slots(self, device, outage):
        """找出巡检计划落在停用窗口、且确实引用该设备的任务槽位。

        判定：任务下存在任意一条该设备的检查结果（不管其他结果在什么时间），
        且任务的 plan_date 落在窗口内。每个任务只产生一个槽位。
        """
        slots = []
        task_ids = {
            result.task_id
            for result in self.result_repo.find_by_devices([device.id], only_active=False)
        }
        for task_id in sorted(task_ids):
            task = self.task_repo.get(task_id)
            if task is None:
                continue
            if self._in_window(task.plan_date, outage.start_at, outage.end_at):
                slots.append({"task": task, "relation": "ORIGINAL"})
        return slots

    @staticmethod
    def _in_window(moment, start_at, end_at):
        return start_at <= moment < end_at

    def _candidate_outage_in_window(self, candidate, outage):
        from src.repositories.device_outage_repository import DeviceOutageRepository

        repo = DeviceOutageRepository(self.db)
        for other in repo.find_confirmed_by_device(candidate.id):
            if other.id == outage.id:
                continue
            if other.start_at < outage.end_at and other.end_at > outage.start_at:
                return True
        return False

    def _pick_backup(self, usable, outage):
        """按剩余槽位挑选第一台还能承载的备用设备；容量按重叠窗口占用数量计。"""
        for candidate in usable:
            rows = self.reroute_repo.find_backup_rows_with_window(candidate.id)
            overlap_load = sum(
                1 for _, other_outage in rows
                if other_outage.start_at < outage.end_at
                and other_outage.end_at > outage.start_at
            )
            if overlap_load < BACKUP_SLOT_CAPACITY:
                return {"device": candidate, "load": overlap_load}
        return None
