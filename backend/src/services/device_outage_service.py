from datetime import datetime, timezone

from src.constants.log_templates import LOG_TEMPLATES
from src.constants.outage_status import BACKUP_SLOT_CAPACITY
from src.constructors.device_outage_factory import (
    build_device_outage_dto,
    build_outage_batch_dto,
)
from src.models.hazard_ticket import HazardTicket
from src.models.inspection_result import InspectionResult
from src.repositories.device_outage_repository import DeviceOutageRepository
from src.repositories.fire_device_repository import FireDeviceRepository
from src.services.audit_service import AuditService
from src.services.cascade_void_service import CascadeVoidService
from src.services.reroute_service import RerouteService
from src.utils.exceptions import ServiceException
from src.utils.formatters import format_paperwork, parse_dt


class DeviceOutageService:
    def __init__(self, db):
        self.db = db
        self.repo = DeviceOutageRepository(db)
        self.device_repo = FireDeviceRepository(db)
        self.audit = AuditService(db)
        self.reroute = RerouteService(db, self.audit)
        self.cascade = CascadeVoidService(db, self.audit)

    # ---------------- 查询 ----------------
    def list_outages(self, device_id=None, status=None):
        return [build_device_outage_dto(row) for row in self.repo.find_all(device_id, status)]

    def list_batches(self):
        result = []
        for batch in self.repo.find_all_batches():
            items = self.repo.find_by_batch(batch.id)
            result.append(build_outage_batch_dto(batch, [self._build_outage_detail(i) for i in items]))
        return result

    def get_batch(self, batch_id):
        batch = self.repo.get_batch(batch_id)
        if batch is None:
            raise ServiceException("OUTAGE_BATCH_NOT_FOUND", 404, batch_id=batch_id)
        items = [self._build_outage_detail(row) for row in self.repo.find_by_batch(batch.id)]
        return build_outage_batch_dto(batch, items)

    def _build_outage_detail(self, row):
        """条目详情：改派/排队/作废汇总都从已落库记录回填，保证续传前后一致。"""
        dto = build_device_outage_dto(row)
        reroutes = self.reroute.reroute_repo.find_by_outage(row.id)
        dto["reroute"] = {
            "affected_slot_count": sum(1 for r in reroutes if r.relation == "ORIGINAL"),
            "rerouted": [
                {"task_id": r.task_id, "backup_device_id": r.backup_device_id}
                for r in reroutes if r.relation == "BACKUP"
            ],
            "queued": [
                {"task_id": r.task_id, "device_id": r.device_id}
                for r in reroutes if r.relation == "QUEUED"
            ],
            "backup_capacity": BACKUP_SLOT_CAPACITY,
        }
        dto["cascade"] = {
            "voided_result_ids": [
                r_id for (r_id,) in self.db.query(InspectionResult.id)
                .filter(InspectionResult.voided_by_outage_id == row.id).all()
            ],
            "voided_ticket_ids": [
                t_id for (t_id,) in self.db.query(HazardTicket.id)
                .filter(HazardTicket.voided_by_outage_id == row.id).all()
            ],
        }
        dto["cascade"]["voided_count"] = (
            len(dto["cascade"]["voided_result_ids"]) + len(dto["cascade"]["voided_ticket_ids"])
        )
        dto["occupied"] = row.status == "DRAFT" and row.occupied_count > 0
        return dto

    def get_outage(self, outage_id):
        row = self.repo.get_outage(outage_id)
        if row is None:
            raise ServiceException("OUTAGE_NOT_FOUND", 404, outage_id=outage_id)
        return self._build_outage_detail(row)

    def occupied_preview(self, device_id, start_at, end_at):
        """后到者确认前先看：该窗口内已占用名额数量。"""
        start_at, end_at = self._valid_window(start_at, end_at)
        confirmed = self._overlapping_confirmed(device_id, start_at, end_at)
        return {
            "device_id": device_id,
            "start_at": start_at.isoformat(),
            "end_at": end_at.isoformat(),
            "occupied_count": len(confirmed),
            "occupied_outage_ids": [o.id for o in confirmed],
        }

    # ---------------- 提交（带模拟写入失败） ----------------
    def submit(self, payload, actor):
        if not payload.items:
            raise ServiceException("VALIDATION_FAILED", 422, detail="停用设备列表不能为空")
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        batch = self.repo.create_batch(
            submitted_by=actor,
            submitted_at=now,
            status="PARTIAL_FAILED",
            note=payload.note,
            fail_device_codes=",".join(payload.fail_device_codes),
        )
        self.db.flush()

        item_results = []
        fail_codes = set(payload.fail_device_codes)
        for item in payload.items:
            device = self.device_repo.get_by_code(item.device_code)
            if device is None:
                raise ServiceException("DEVICE_NOT_FOUND", 404, device_id=item.device_code)
            start_at, end_at = self._valid_window(item.start_at, item.end_at)
            self.audit.log(
                actor, "DeviceOutage", "DeviceOutage.submit", None,
                detail=LOG_TEMPLATES["DeviceOutage"][0].format(
                    device_id=device.device_code,
                    start_at=start_at.strftime("%Y-%m-%d %H:%M"),
                    end_at=end_at.strftime("%Y-%m-%d %H:%M"),
                ),
            )
            if item.device_code in fail_codes:
                # 模拟写入失败：只落 PENDING 占位，设备状态/名额都不动
                outage = self.repo.create_outage(
                    batch_id=batch.id, device_id=device.id, start_at=start_at, end_at=end_at,
                    reason=item.reason, status="PENDING", confirmed_by=actor, created_at=now,
                )
                item_results.append({
                    "device_code": item.device_code, "outage_id": outage.id, "status": "PENDING",
                })
            else:
                outage = self.repo.create_outage(
                    batch_id=batch.id, device_id=device.id, start_at=start_at, end_at=end_at,
                    reason=item.reason, status="DRAFT", confirmed_by=actor, created_at=now,
                )
                item_results.append(self._confirm_locked(outage, device, actor))

        has_pending = any(r["status"] == "PENDING" for r in item_results)
        batch.status = "PARTIAL_FAILED" if has_pending else "COMPLETED"
        self.db.commit()
        return self.get_batch(batch.id)

    # ---------------- 失败恢复：续传未生效设备 ----------------
    def resume_batch(self, batch_id, actor):
        """重开续传：只处理 PENDING 条目。

        已 CONFIRMED/DRAFT 的条目不重放（不重复），PENDING 重新走确认逻辑（不丢失）。
        """
        batch = self.repo.get_batch(batch_id)
        if batch is None:
            raise ServiceException("OUTAGE_BATCH_NOT_FOUND", 404, batch_id=batch_id)
        pending = self.repo.find_pending_by_batch(batch.id)
        if not pending:
            raise ServiceException("OUTAGE_BATCH_NOT_RESUMABLE", 409, batch_id=batch_id)

        resumed = []
        for outage in pending:
            device = self.device_repo.get(outage.device_id)
            # 幂等：只有 PENDING 才会走到这里，已占名额不重复也不丢失
            resumed.append(self._confirm_locked(outage, device, actor))

        still_pending = self.repo.find_pending_by_batch(batch.id)
        batch.status = "PARTIAL_FAILED" if still_pending else "RESUMED"
        resumed_count = len(resumed)
        self.audit.log(
            actor, "DeviceOutage", "DeviceOutage.resume", batch.id,
            detail=LOG_TEMPLATES["DeviceOutage"][4].format(
                batch_id=batch.id, resumed_count=resumed_count,
            ),
        )
        self.db.commit()
        return self.get_batch(batch.id)

    # ---------------- 单条草稿处理 / 改窗 / 撤销 ----------------
    def review_draft(self, outage_id, payload, actor):
        outage = self.repo.get_outage(outage_id)
        if outage is None:
            raise ServiceException("OUTAGE_NOT_FOUND", 404, outage_id=outage_id)
        if outage.status != "DRAFT":
            raise ServiceException("CONFLICT_STATE", 409)
        device = self.device_repo.get(outage.device_id)
        if payload.action == "CANCEL":
            outage.status = "CANCELLED"
            self.db.commit()
            return self.get_outage(outage_id)
        if payload.action == "CONFIRM":
            result = self._confirm_locked(outage, device, actor)
            self.db.commit()
            return result
        raise ServiceException("VALIDATION_FAILED", 422, detail="action 只支持 CONFIRM/CANCEL")

    def change_window(self, outage_id, payload, actor):
        """停用时段一变化：旧版本作废，引用该设备的结果/隐患单作废待复核；

        新版本重新确认并按新窗口重算改派。
        """
        old = self.repo.get_outage(outage_id)
        if old is None:
            raise ServiceException("OUTAGE_NOT_FOUND", 404, outage_id=outage_id)
        if old.status != "CONFIRMED":
            raise ServiceException("CONFLICT_STATE", 409)

        device = self.device_repo.get(old.device_id)
        start_at = parse_dt(payload.start_at) if payload.start_at else old.start_at
        end_at = parse_dt(payload.end_at) if payload.end_at else old.end_at
        self._valid_window(start_at, end_at)

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        old.status = "SUPERSEDED"
        void_summary = self.cascade.void_for_outage(old, actor)

        new_outage = self.repo.create_outage(
            batch_id=old.batch_id, device_id=old.device_id, start_at=start_at, end_at=end_at,
            reason=payload.reason if payload.reason is not None else old.reason,
            status="DRAFT", version=old.version + 1, confirmed_by=actor, created_at=now,
        )
        self.audit.log(
            actor, "DeviceOutage", "DeviceOutage.change", new_outage.id,
            detail=LOG_TEMPLATES["DeviceOutage"][3].format(
                outage_id=new_outage.id, voided_count=void_summary["voided_count"],
            ),
        )
        result = self._confirm_locked(new_outage, device, actor, voided_summary=void_summary)
        self.db.commit()
        return result

    def cancel_outage(self, outage_id, actor):
        outage = self.repo.get_outage(outage_id)
        if outage is None:
            raise ServiceException("OUTAGE_NOT_FOUND", 404, outage_id=outage_id)
        if outage.status not in ("CONFIRMED", "DRAFT"):
            raise ServiceException("CONFLICT_STATE", 409)
        outage.status = "CANCELLED"
        # 停用撤销：时段变化同样触发作废待复核
        summary = self.cascade.void_for_outage(outage, actor)
        device = self.device_repo.get(outage.device_id)
        if device and device.status == "OUTAGE":
            device.status = "PENDING_REUSE"
        self.db.commit()
        return {"outage": self.get_outage(outage_id), "cascade": summary}

    # ---------------- 核心：确认（行锁 + 占用数量 + 冲突草稿） ----------------
    def _confirm_locked(self, outage, device, actor, voided_summary=None):
        """两个负责人同时确认重叠时段时，后到者看到占用数量并保留草稿。

        靠 (device_id, 时间窗) 内 CONFIRMED 集合判定；为避免并发双写，
        对设备行加锁后再二次检查。
        """
        # SELECT ... FOR UPDATE：同一台设备的确认串行化（SQLite 退化为普通查询）
        locked = self.db.query(type(device)).filter(type(device).id == device.id)
        if self.db.bind.dialect.name == "postgresql":
            locked = locked.with_for_update()
        locked.one_or_none()

        overlaps = self._overlapping_confirmed(device.id, outage.start_at, outage.end_at)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        occupied_count = len(overlaps)
        outage.occupied_count = occupied_count
        outage.conflict_outage_ids = format_paperwork([str(o.id) for o in overlaps])

        if occupied_count > 0:
            # 后到者：保留草稿，不抢名额、不改设备状态
            outage.status = "DRAFT"
            outage.confirmed_at = now
            self.audit.log(
                actor, "DeviceOutage", "DeviceOutage.draft", outage.id,
                detail=LOG_TEMPLATES["DeviceOutage"][2].format(
                    outage_id=outage.id, occupied_count=occupied_count,
                ),
            )
            self.db.flush()
            result = build_device_outage_dto(outage)
            result["occupied"] = True
            if voided_summary:
                result["cascade"] = voided_summary
            return result

        # 先到者：占名额生效
        outage.status = "CONFIRMED"
        outage.confirmed_at = now
        device.status = "OUTAGE"
        device.reuse_paperwork = ""
        self.audit.log(
            actor, "DeviceOutage", "DeviceOutage.confirm", outage.id,
            detail=LOG_TEMPLATES["DeviceOutage"][1].format(
                outage_id=outage.id, occupied_count=occupied_count,
            ),
        )
        self.db.flush()
        reroute_summary = self.reroute.apply_for_outage(outage, actor)
        if voided_summary is None:
            # 首次确认也要把窗口内引用该设备的历史结果/隐患单标作废待复核
            voided_summary = self.cascade.void_for_outage(outage, actor)
        self.db.flush()
        result = build_device_outage_dto(outage)
        result["occupied"] = False
        result["reroute"] = reroute_summary
        result["cascade"] = voided_summary
        return result

    # ---------------- helpers ----------------
    def _overlapping_confirmed(self, device_id, start_at, end_at):
        return [
            o for o in self.repo.find_confirmed_by_device(device_id)
            if o.start_at < end_at and o.end_at > start_at
        ]

    @staticmethod
    def _valid_window(start_value, end_value):
        start_at = parse_dt(start_value)
        end_at = parse_dt(end_value)
        if start_at is None or end_at is None or start_at >= end_at:
            raise ServiceException("OUTAGE_WINDOW_INVALID", 422)
        return start_at, end_at
