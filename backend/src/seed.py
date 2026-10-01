"""本地数据库播种：全部本地数据，无任何第三方 API。

场景设计（时间相对当前日期动态生成，保证停用窗口/巡检窗口必然重叠）：
- 楼栋 A：2 台消火栓（HYD-001 在用 + HYD-002 备用），停用 HYD-001 时任务可改派；
- 楼栋 A：3 个烟感（SMK-001 在用 + SMK-002/003 备用），备用容量打满后排队待补检；
- 楼栋 B：1 台喷淋 SPR-001（无备用），停用即待补检；
- 巡检结果/隐患单已与上述设备关联，用于演示“停用一变就作废待复核”。
"""

from datetime import datetime, timedelta, timezone

from src.config.database import Base, SessionLocal, engine
from src.models import (
    AuditLog,
    Building,
    FireDevice,
    HazardTicket,
    InspectionResult,
    InspectionTask,
)


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Building).count() > 0:
            return
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0, tzinfo=None)
        day = timedelta(days=1)
        window_start = now + 2 * day

        b1 = Building(
            name="1 号研发楼", campus="江北产业园", floor_count=8,
            fire_grade="一级", manager_id=3, address_code="JB-A01",
        )
        b2 = Building(
            name="2 号仓储楼", campus="江北产业园", floor_count=3,
            fire_grade="二级", manager_id=3, address_code="JB-B02",
        )
        db.add_all([b1, b2])
        db.flush()

        def add_device(code, building_id, dtype, floor, loc, install):
            row = FireDevice(
                building_id=building_id, device_code=code, device_type=dtype,
                floor=floor, location_desc=loc, install_date=install,
                status="NORMAL", next_maintenance_at=now + 30 * day, reuse_paperwork="",
            )
            db.add(row)
            return row

        devices = [
            add_device("HYD-001", b1.id, "HYDRANT", "1F", "A 区消火栓", now - 400 * day),
            add_device("HYD-002", b1.id, "HYDRANT", "3F", "B 区消火栓", now - 300 * day),
            add_device("SMK-001", b1.id, "SMOKE_DETECTOR", "2F", "走廊东端", now - 500 * day),
            add_device("SMK-002", b1.id, "SMOKE_DETECTOR", "2F", "走廊西端", now - 500 * day),
            add_device("SMK-003", b1.id, "SMOKE_DETECTOR", "4F", "电梯厅", now - 500 * day),
            add_device("EXT-001", b1.id, "EXTINGUISHER", "1F", "前台旁", now - 200 * day),
            add_device("EXIT-001", b1.id, "EXIT_LIGHT", "1F", "安全出口", now - 200 * day),
            add_device("SPR-001", b2.id, "SPRINKLER", "1F", "货架区主管", now - 600 * day),
            add_device("EXT-002", b2.id, "EXTINGUISHER", "1F", "仓库出入口", now - 300 * day),
        ]
        db.flush()

        def add_task(building_id, plan, ttype, status="PLANNED", inspector=1):
            row = InspectionTask(
                building_id=building_id, inspector_id=inspector, plan_date=plan,
                task_type=ttype, status=status, checklist_version="v2026.1",
                finished_at=None,
            )
            db.add(row)
            return row

        plan_at = window_start + timedelta(hours=2)
        tasks = [
            add_task(b1.id, plan_at, "HYDRANT"),                                   # 0 -> HYD-001
            add_task(b1.id, plan_at + timedelta(hours=1), "SMOKE_DETECTOR"),      # 1 -> SMK-001
            add_task(b1.id, plan_at + timedelta(hours=2), "SMOKE_DETECTOR"),      # 2 -> SMK-001
            add_task(b1.id, plan_at + timedelta(hours=3), "SMOKE_DETECTOR"),      # 3 -> SMK-001
            add_task(b2.id, plan_at, "SPRINKLER"),                                # 4 -> SPR-001
            add_task(b1.id, now - 5 * day, "EXTINGUISHER", status="REVIEWED", inspector=1),
        ]
        db.flush()

        def add_result(task, device, item, status="NORMAL", note=""):
            row = InspectionResult(
                task_id=task.id, device_id=device.id, item_code=item,
                result_status=status, measured_value="0.35MPa" if status == "NORMAL" else "0.08MPa",
                photo_url="/mock/photo.png", note=note,
                review_flag="ACTIVE",
            )
            db.add(row)
            return row

        add_result(tasks[0], devices[0], "HYDRANT_PRESSURE")
        r2 = add_result(tasks[1], devices[2], "SMOKE_SENSITIVITY", status="ABNORMAL", note="响应偏慢")
        add_result(tasks[2], devices[2], "SMOKE_SENSITIVITY")
        add_result(tasks[3], devices[2], "SMOKE_POWER")
        add_result(tasks[4], devices[7], "SPRINKLER_VALVE")
        r6 = add_result(tasks[5], devices[5], "EXT_PRESSURE", status="ABNORMAL", note="压力不足")
        db.flush()

        t1 = HazardTicket(
            result_id=r2.id, device_id=devices[2].id, severity="HIGH", owner_id=2,
            deadline=now + 10 * day, rectify_status="ASSIGNED", rectify_note="已联系维保更换探头",
        )
        t2 = HazardTicket(
            result_id=r6.id, device_id=devices[5].id, severity="MEDIUM", owner_id=2,
            deadline=now + 7 * day, rectify_status="RECTIFIED", rectify_note="已充装",
        )
        db.add_all([t1, t2])

        db.add(AuditLog(
            actor="system", action="seed", target_type="System", target_id="seed",
            detail="初始化本地种子数据", created_at=now,
        ))
        db.commit()
    finally:
        db.close()
