"""设备停用时段核心服务。

业务规则（对应需求逐条落地）：
1. 负责人提交停用时段 -> 先落 DRAFT 草稿。
2. 确认停用：同栋同类型备用设备按容量承接同段巡检；容量不足的排期排队转待补检；
   原 ORIGINAL 排期关系保留不删。
3. 两个负责人同时确认重叠时段：窗口行级锁串行化；后到者读取到已占用数量，
   在容量不足时其提交保留为草稿（不确认），并返回占用数量。
4. 写入失败后凭 resume_key 从 write_stage 断点续跑；已占名额按
   (window_id, assignment_id) 判重，不重复、不丢失。
5. 停用时段变更：旧版本置 SUPERSEDED，引用这些设备的巡检结果与隐患整改单
   一律作废待复核。
6. 复役前手续未补齐的设备不能回到正常。
"""
import json
import uuid
from datetime import datetime

from sqlalchemy import select

from src.constructors.outage_factory import (
    create_assignment_dto,
    create_draft_dto,
    create_holding_dto,
    create_outage_window_dto,
    create_procedure_dto,
)
from src.constants.procedure_type import ProcedureType
from src.repositories.capacity_holding_repository import CapacityHoldingRepository
from src.repositories.fire_device_repository import FireDeviceRepository
from src.repositories.hazard_ticket_repository import HazardTicketRepository
from src.repositories.inspection_result_repository import InspectionResultRepository
from src.repositories.outage_window_repository import (
    DeviceOutageWindowRepository,
    OutageDraftRepository,
    OutageProcedureRepository,
)
from src.repositories.task_device_assignment_repository import (
    TaskDeviceAssignmentRepository,
)
from src.services.audit_service import AuditService
from src.types.outage_payload import (
    OutageChangePayload,
    OutageDraftSavePayload,
    OutageProcedurePayload,
    OutageWindowCreatePayload,
)
from src.utils.exceptions import ServiceError


class OutageWindowService:
    def __init__(self, db):
        self.db = db
        self.window_repo = DeviceOutageWindowRepository(db)
        self.draft_repo = OutageDraftRepository(db)
        self.procedure_repo = OutageProcedureRepository(db)
        self.holding_repo = CapacityHoldingRepository(db)
        self.device_repo = FireDeviceRepository(db)
        self.assignment_repo = TaskDeviceAssignmentRepository(db)
        self.result_repo = InspectionResultRepository(db)
        self.ticket_repo = HazardTicketRepository(db)
        self.audit = AuditService(db)

    # ------------------------------------------------------------------ 查询

    def list_windows(self):
        from src.models.device_outage_window import DeviceOutageWindow

        rows = list(
            self.db.execute(
                select(DeviceOutageWindow).order_by(DeviceOutageWindow.id.asc())
            ).scalars().all()
        )
        return [create_outage_window_dto(row) for row in rows]

    def get_window_dto(self, window_id: int):
        row = self.window_repo.lock_row(window_id)
        if row is None:
            raise ServiceError("OUTAGE_WINDOW_NOT_FOUND", 404, window_id=window_id)
        return create_outage_window_dto(row)

    def list_assignments(self, window_id: int | None = None):
        from src.models.task_device_assignment import TaskDeviceAssignment

        stmt = select(TaskDeviceAssignment).order_by(TaskDeviceAssignment.id.asc())
        if window_id is not None:
            stmt = stmt.where(TaskDeviceAssignment.window_id == window_id)
        rows = list(self.db.execute(stmt).scalars().all())
        return [create_assignment_dto(row) for row in rows]

    def list_holdings(self, window_id: int):
        return [
            create_holding_dto(row)
            for row in self.holding_repo.list_by_window(window_id)
        ]

    def list_drafts(self, window_id: int):
        return [
            create_draft_dto(row) for row in self.draft_repo.list_by_window(window_id)
        ]

    # ------------------------------------------------------------------ 提交草稿

    def submit_draft(self, payload: OutageWindowCreatePayload, actor: str = "system"):
        """负责人提交停用时段：先以 DRAFT 落库，并计算当前同栋同类型的占用快照。"""
        if payload.end_at <= payload.start_at:
            raise ServiceError(
                "OUTAGE_WINDOW_INVALID_RANGE", 400,
                start_at=payload.start_at.isoformat(),
                end_at=payload.end_at.isoformat(),
            )
        device = self.device_repo.get(payload.device_id)
        if device is None:
            raise ServiceError("NOT_FOUND", 404, resource="消防设备",
                               entity_id=payload.device_id)

        group_id = self.window_repo.max_group_id() + 1
        occupied = self._occupied_for(device.building_id, device.device_type,
                                      exclude_device_ids=[device.id],
                                      start_at=payload.start_at,
                                      end_at=payload.end_at)
        total = self.device_repo.total_backup_capacity(
            building_id=device.building_id,
            device_type=device.device_type,
            exclude_device_ids=[device.id],
        )
        demanded = self._demanded_for(device.building_id, device.device_type,
                                      device.id, payload.start_at, payload.end_at)
        row = self.window_repo.add(
            window_group_id=group_id,
            version=1,
            device_id=device.id,
            owner_id=payload.owner_id,
            start_at=payload.start_at,
            end_at=payload.end_at,
            reason=payload.reason,
            outage_status="DRAFT",
            occupied_capacity=occupied,
            demanded_capacity=demanded,
            write_stage="PERSIST_WINDOW",
            created_at=datetime.utcnow(),
        )
        self.audit.log(
            "DeviceOutageWindow", 0, actor=actor, target_id=row.id,
            device_id=device.id, start_at=payload.start_at.isoformat(),
            end_at=payload.end_at.isoformat(), owner_id=payload.owner_id,
        )
        self.db.commit()
        dto = create_outage_window_dto(row)
        dto["backup_capacity_total"] = total
        return dto

    def save_draft_content(self, payload: OutageDraftSavePayload, actor: str = "system"):
        """后到者看到占用数量后，保留其编辑草稿（乐观锁版本）。"""
        window = self.window_repo.get(payload.window_id)
        if window is None:
            raise ServiceError("OUTAGE_WINDOW_NOT_FOUND", 404,
                               window_id=payload.window_id)
        row = self.draft_repo.upsert(
            window_id=payload.window_id,
            owner_id=payload.owner_id,
            payload=payload.payload,
            observed_occupied=window.occupied_capacity,
            lock_version=payload.lock_version,
        )
        self.db.commit()
        return create_draft_dto(row)

    # ------------------------------------------------------------------ 确认（含并发/续跑）

    def confirm(self, window_id: int, resume_key: str | None = None,
                actor: str = "system", *, force_fail_stage: str | None = None):
        """确认停用。force_fail_stage 仅用于演示/测试“写入失败后恢复”。

        每个阶段边界都提交一次：失败后 resume 从 write_stage 指向的阶段重跑，
        各阶段内部按 (window_id, assignment_id) 幂等判重。
        """
        window = self.window_repo.lock_row(window_id)
        if window is None:
            raise ServiceError("OUTAGE_WINDOW_NOT_FOUND", 404, window_id=window_id)

        if window.write_stage == "COMPLETED" and window.outage_status == "CONFIRMED":
            dto = create_outage_window_dto(window)
            dto["idempotent_replayed"] = True
            return dto

        # 断点续跑：恢复键必须与失败时返回的键一致。
        if resume_key is not None and window.resume_key and resume_key != window.resume_key:
            raise ServiceError("OUTAGE_RESUME_KEY_MISMATCH", 409)
        if window.resume_key is None:
            window.resume_key = uuid.uuid4().hex
            self.db.commit()  # 恢复键先持久化，失败回滚也不丢失
        current_resume_key = window.resume_key

        try:
            # 阶段 1：窗口确认落库（幂等：重跑时仅覆盖状态）。
            if window.write_stage == "PERSIST_WINDOW":
                window.outage_status = "CONFIRMED"
                window.confirmed_at = datetime.utcnow()
                window.write_stage = "HOLD_CAPACITY"
                self.db.commit()

            # 阶段 2 + 3：占用容量 & 任务重排（逐条提交，失败点在 _allocate 内）。
            if window.write_stage == "HOLD_CAPACITY":
                self._allocate(window_id, actor=actor,
                               force_fail_stage=force_fail_stage)
                window = self.window_repo.lock_row(window_id)
                window.write_stage = "MARK_DEVICE_OUTAGE"
                self.db.commit()
                self._maybe_fail(force_fail_stage, "MARK_DEVICE_OUTAGE", window_id)

            # 阶段 4：设备置为停用。
            if window.write_stage == "MARK_DEVICE_OUTAGE":
                window = self.window_repo.lock_row(window_id)
                self.device_repo.update_status(window.device_id, "OUT_OF_SERVICE")
                self.audit.log(
                    "FireDevice", 4, actor=actor, target_id=window.device_id,
                    device_code=self._device_code(window.device_id),
                    start_at=window.start_at.isoformat(),
                    end_at=window.end_at.isoformat(),
                    outage_status="CONFIRMED",
                )
                window.write_stage = "COMPLETED"
                self.db.commit()
        except ServiceError:
            raise
        except Exception as exc:
            # 写入失败：在独立事务中保存断点阶段，等待 resume。
            self.db.rollback()
            failed_stage = self._persist_failure(window_id, force_fail_stage, str(exc), actor)
            raise ServiceError(
                "CONFLICT", 500,
                detail=(
                    f"停用确认在阶段 {failed_stage} 写入失败，"
                    f"请使用 resume_key={current_resume_key} 调用恢复接口；"
                    f"已占名额不会重复或丢失。"
                ),
            )

        result = create_outage_window_dto(self.window_repo.get(window_id))
        result["resume_key"] = current_resume_key
        return result

    def resume(self, window_id: int, resume_key: str, actor: str = "system",
               *, force_fail_stage: str | None = None):
        """写入失败后恢复：从上次未完成阶段续跑。"""
        window = self.window_repo.get(window_id)
        if window is None:
            raise ServiceError("OUTAGE_WINDOW_NOT_FOUND", 404, window_id=window_id)
        if window.resume_key != resume_key:
            raise ServiceError("OUTAGE_RESUME_KEY_MISMATCH", 409)
        self.audit.log(
            "DeviceOutageWindow", 4, actor=actor, target_id=window_id,
            window_id=window_id, stage=window.write_stage,
        )
        return self.confirm(window_id, resume_key=resume_key, actor=actor,
                            force_fail_stage=force_fail_stage)

    def _allocate(self, window_id: int, *, actor: str,
                  force_fail_stage: str | None) -> int:
        """按备用设备容量逐个承接重叠排期；不足者排队转待补检。

        每个排期处理完立即 commit：写入失败后 resume 重入本阶段时，
        已派生（find_derived 命中）的排期跳过，保证名额不重复、不丢失。
        """
        window = self.window_repo.lock_row(window_id)
        device = self.device_repo.get(window.device_id)

        # 重叠确认：其它已确认停用的同类型设备也要排除，其占用计入“已占用”。
        overlapping_outage_device_ids = self._overlapping_outage_device_ids(
            building_id=device.building_id,
            device_type=device.device_type,
            start_at=window.start_at,
            end_at=window.end_at,
            exclude_window_id=window.id,
        )
        exclude = [device.id] + overlapping_outage_device_ids

        originals = self.assignment_repo.list_originals_for_window(
            building_id=device.building_id,
            device_type=device.device_type,
            device_ids=[device.id],
            plan_start=window.start_at,
            plan_end=window.end_at,
        )

        queue_pos = self.assignment_repo.max_queue_position(window.id)
        shortage = 0
        # 进入本次执行时已落库的名额数（可能来自上一次失败前）。
        holdings_at_entry = self.holding_repo.occupied_seats(window.id)
        for origin in originals:
            # 幂等：续跑时已派生过的排期直接跳过（已占名额不重复）。
            derived = self.assignment_repo.find_derived(origin.id, window.id)
            if derived is not None:
                continue

            # 注入失败点：本阶段至少已提交 1 条名额后，处理下一条之前失败，
            # 用于验证“已占名额不丢失，恢复后继续处理未生效项”。
            if (
                force_fail_stage == "HOLD_CAPACITY"
                and self.holding_repo.occupied_seats(window.id) > holdings_at_entry
            ):
                raise RuntimeError("injected write failure mid HOLD_CAPACITY")

            # 剩余容量在每次分配前实时计算（含本窗口已落库的名额），
            # 这样 resume 与并发重叠确认看到的都是最新占用。
            backup_id = self._pick_backup_device(
                building_id=device.building_id,
                device_type=device.device_type,
                exclude_device_ids=exclude,
                seats=origin.seats,
                window_id=window.id,
                start_at=window.start_at,
                end_at=window.end_at,
            )

            if backup_id is not None:
                self.holding_repo.hold(
                    window_id=window.id,
                    backup_device_id=backup_id,
                    assignment_id=origin.id,
                    seats=origin.seats,
                )
                self.assignment_repo.add(
                    task_id=origin.task_id,
                    building_id=origin.building_id,
                    device_type=origin.device_type,
                    planned_device_id=origin.planned_device_id,
                    actual_device_id=backup_id,
                    assignment_status="BACKUP",
                    window_id=window.id,
                    origin_assignment_id=origin.id,
                    seats=origin.seats,
                )
                self.audit.log(
                    "InspectionTask", 4, actor=actor, target_id=origin.task_id,
                    task_id=origin.task_id,
                    from_device_id=origin.planned_device_id,
                    to_device_id=backup_id,
                )
                self.db.commit()  # 名额逐条落库：失败不回滚已占名额
            else:
                queue_pos += 1
                shortage += 1
                self.assignment_repo.add(
                    task_id=origin.task_id,
                    building_id=origin.building_id,
                    device_type=origin.device_type,
                    planned_device_id=origin.planned_device_id,
                    actual_device_id=None,
                    assignment_status="PENDING_RECHECK",
                    window_id=window.id,
                    origin_assignment_id=origin.id,
                    queue_position=queue_pos,
                    seats=origin.seats,
                )
                self.audit.log(
                    "InspectionTask", 5, actor=actor, target_id=origin.task_id,
                    task_id=origin.task_id, device_id=origin.planned_device_id,
                )
                self.db.commit()

        window = self.window_repo.lock_row(window.id)
        window.occupied_capacity = self.holding_repo.occupied_seats(window.id)
        window.demanded_capacity = len(originals)
        self.db.commit()

        self.audit.log(
            "DeviceOutageWindow", 1 if shortage == 0 else 2,
            actor=actor, target_id=window.id,
            window_id=window.id, device_id=window.device_id,
            occupied=window.occupied_capacity,
            demanded=window.demanded_capacity,
        )
        if shortage:
            self.db.commit()
        return shortage

    def _pick_backup_device(self, *, building_id: int, device_type: str,
                            exclude_device_ids: list[int], seats: int,
                            window_id: int, start_at, end_at) -> int | None:
        """挑选一台剩余容量足够的备用设备（按 id 稳定排序）。"""
        candidates = self.device_repo.list_backup_candidates(
            building_id=building_id,
            device_type=device_type,
            exclude_device_ids=exclude_device_ids,
        )
        for cand in candidates:
            used = self._occupied_seats_on_device(
                cand.id, start_at, end_at, exclude_window_id=window_id,
            )
            # 本窗口已落库名额也必须计入（逐条提交后 resume/并发可见）。
            used += self.holding_repo.occupied_seats_on_device_for_window(
                cand.id, window_id,
            )
            if cand.capacity - used >= seats:
                return cand.id
        return None

    def _occupied_self_window(self, device_id: int, window_id: int) -> int:
        return self.holding_repo.occupied_seats_on_device_for_window(
            device_id, window_id
        )

    # ------------------------------------------------------------------ 并发：后到者保留草稿

    def confirm_with_conflict_guard(self, window_id: int, owner_id: int,
                                    actor: str = "system"):
        """两个负责人同时确认重叠时段时的入口。

        - 若容量仍够：正常确认。
        - 若容量不足（已占用数量 >= 需求可承接量）：后到者不确认，
          其提交内容保留为草稿，并返回当前占用数量。
        """
        window = self.window_repo.lock_row(window_id)
        if window is None:
            raise ServiceError("OUTAGE_WINDOW_NOT_FOUND", 404, window_id=window_id)
        if window.outage_status == "CONFIRMED" and window.write_stage == "COMPLETED":
            raise ServiceError("OUTAGE_ALREADY_CONFIRMED", 409, window_id=window_id)

        device = self.device_repo.get(window.device_id)
        occupied = self._occupied_for(
            device.building_id, device.device_type,
            exclude_device_ids=[window.device_id],
            start_at=window.start_at, end_at=window.end_at,
        )
        total = self.device_repo.total_backup_capacity(
            building_id=device.building_id,
            device_type=device.device_type,
            exclude_device_ids=[window.device_id],
        )
        demanded = self._demanded_for(
            device.building_id, device.device_type,
            window.device_id, window.start_at, window.end_at,
        )

        if occupied + demanded > total and total >= 0:
            # 后到者：保留草稿并回传占用数量。
            window.occupied_capacity = occupied
            window.demanded_capacity = demanded
            self.draft_repo.upsert(
                window_id=window.id,
                owner_id=owner_id,
                payload=json.dumps(
                    create_outage_window_dto(window), ensure_ascii=False
                ),
                observed_occupied=occupied,
                lock_version=1,
            )
            self.db.commit()
            self.audit.log(
                "DeviceOutageWindow", 2, actor=actor, target_id=window.id,
                window_id=window.id, occupied=occupied, demanded=demanded,
            )
            return {
                "conflict": True,
                "window_id": window.id,
                "occupied_capacity": occupied,
                "backup_capacity_total": total,
                "demanded_capacity": demanded,
                "draft_saved": True,
                "drafts": self.list_drafts(window.id),
            }

        return {"conflict": False, "window": self.confirm(window.id, actor=actor)}

    # ------------------------------------------------------------------ 变更 -> 作废待复核

    def change_window(self, window_id: int, payload: OutageChangePayload,
                      actor: str = "system"):
        """停用时段变化：旧版本 SUPERSEDED，引用设备的结果/整改单作废待复核。

        新版本以 CONFIRMED 重新落库（沿用同一 window_group_id）。
        """
        old = self.window_repo.lock_row(window_id)
        if old is None:
            raise ServiceError("OUTAGE_WINDOW_NOT_FOUND", 404, window_id=window_id)
        if payload.end_at <= payload.start_at:
            raise ServiceError(
                "OUTAGE_WINDOW_INVALID_RANGE", 400,
                start_at=payload.start_at.isoformat(),
                end_at=payload.end_at.isoformat(),
            )

        old.outage_status = "SUPERSEDED"
        self.db.flush()

        new_version = self.window_repo.latest_group_version(old.window_group_id) + 1
        new_window = self.window_repo.add(
            window_group_id=old.window_group_id,
            version=new_version,
            device_id=old.device_id,
            owner_id=old.owner_id,
            start_at=payload.start_at,
            end_at=payload.end_at,
            reason=payload.reason or old.reason,
            outage_status="DRAFT",
            write_stage="PERSIST_WINDOW",
            created_at=datetime.utcnow(),
        )
        self.db.flush()

        voided = self._void_references([old.device_id], new_window.id, actor)

        self.audit.log(
            "DeviceOutageWindow", 5, actor=actor, target_id=new_window.id,
            window_id=old.id, new_window_id=new_window.id,
        )
        self.db.commit()
        return {
            "superseded_window_id": old.id,
            "new_window": create_outage_window_dto(new_window),
            "voided": voided,
        }

    def _void_references(self, device_ids: list[int], window_id: int,
                         actor: str) -> dict:
        results = self.result_repo.list_by_devices(device_ids)
        # 已经处于作废待复核的不重复计数；但仍刷新 voided_by_window_id。
        active_results = [r for r in results if r.review_status in ("ACTIVE", "RECONFIRMED")]
        result_ids = [r.id for r in results]
        self.result_repo.mark_void_pending(result_ids=result_ids, window_id=window_id)
        for r in results:
            self.audit.log(
                "InspectionResult", 2, actor=actor, target_id=r.id,
                result_id=r.id, device_id=r.device_id,
            )

        tickets = self.ticket_repo.list_by_result_ids(result_ids)
        ticket_ids = [t.id for t in tickets]
        self.ticket_repo.mark_void_pending(ticket_ids=ticket_ids, window_id=window_id)
        for t in tickets:
            self.audit.log(
                "HazardTicket", 2, actor=actor, target_id=t.id,
                ticket_id=t.id,
            )
        return {
            "result_ids": result_ids,
            "ticket_ids": ticket_ids,
            "newly_voided_results": len(active_results),
        }

    # ------------------------------------------------------------------ 手续 & 复役

    def register_procedure(self, window_id: int, payload: OutageProcedurePayload,
                           actor: str = "system"):
        window = self.window_repo.get(window_id)
        if window is None:
            raise ServiceError("OUTAGE_WINDOW_NOT_FOUND", 404, window_id=window_id)
        if payload.procedure_type not in ProcedureType:
            raise ServiceError("VALIDATION_FAILED", 400,
                               detail=f"未知手续类型 {payload.procedure_type}")
        row = self.procedure_repo.add(
            device_id=window.device_id,
            window_id=window.id,
            procedure_type=payload.procedure_type,
            completed=1,
            doc_url=payload.doc_url,
            created_at=datetime.utcnow(),
        )
        self.audit.log(
            "DeviceOutageWindow", 6, actor=actor, target_id=window.device_id,
            device_id=window.device_id, procedure_type=payload.procedure_type,
        )
        self.db.commit()
        return create_procedure_dto(row)

    def list_procedures(self, window_id: int):
        window = self.window_repo.get(window_id)
        if window is None:
            raise ServiceError("OUTAGE_WINDOW_NOT_FOUND", 404, window_id=window_id)
        return [
            create_procedure_dto(row)
            for row in self.procedure_repo.list_by_device_window(
                window.device_id, window.id
            )
        ]

    def restore_device(self, device_id: int, actor: str = "system"):
        """复役：手续没补齐的设备不能回到正常。"""
        device = self.device_repo.get(device_id)
        if device is None:
            raise ServiceError("NOT_FOUND", 404, resource="消防设备",
                               entity_id=device_id)
        if device.status != "OUT_OF_SERVICE":
            raise ServiceError("DEVICE_NOT_OUT_OF_SERVICE", 409,
                               device_code=device.device_code)

        # 取该设备最近一次确认的停用窗口，核对全部必备手续。
        windows = [
            w for w in self.window_repo.list_by_device(device_id)
            if w.outage_status in ("CONFIRMED", "SUPERSEDED")
        ]
        window = windows[0] if windows else None
        done_types: set[str] = set()
        if window is not None:
            done_types = {
                p.procedure_type
                for p in self.procedure_repo.list_by_device_window(device_id, window.id)
                if p.completed
            }
        missing = [p for p in ProcedureType if p not in done_types]
        if missing:
            raise ServiceError(
                "RESTORE_PROCEDURE_INCOMPLETE", 409,
                device_code=device.device_code, missing="、".join(missing),
            )

        self.device_repo.update_status(device_id, "NORMAL")
        self.audit.log(
            "FireDevice", 5, actor=actor, target_id=device_id,
            device_code=device.device_code, procedures="、".join(sorted(done_types)),
        )
        # 复役后排队的待补检可以重新排入（仅记录补排关系，不删原关系）。
        pending = self.assignment_repo.list_pending()
        device_pending = [a for a in pending if a.planned_device_id == device_id]
        for p in device_pending:
            self.assignment_repo.add(
                task_id=p.task_id,
                building_id=p.building_id,
                device_type=p.device_type,
                planned_device_id=p.planned_device_id,
                actual_device_id=device_id,
                assignment_status="RESCHEDULED",
                window_id=p.window_id,
                origin_assignment_id=p.origin_assignment_id or p.id,
                seats=p.seats,
            )
            self.audit.log(
                "InspectionTask", 6, actor=actor, target_id=p.task_id,
                task_id=p.task_id,
                assignment_id=p.id, device_id=device_id,
            )
        self.db.commit()
        return {
            "device_id": device_id,
            "device_code": device.device_code,
            "status": "NORMAL",
            "rescheduled": len(device_pending),
        }

    # ------------------------------------------------------------------ 内部工具

    def _maybe_fail(self, force_fail_stage: str | None, stage: str, window_id: int):
        if force_fail_stage and force_fail_stage == stage:
            raise RuntimeError(f"injected write failure at stage={stage}")

    def _persist_failure(self, window_id: int, stage: str | None,
                         reason: str, actor: str) -> str:
        """失败后在独立事务里保存断点阶段，保证 resume 能定位。

        前置 confirm 已 rollback：阶段边界与逐条提交的名额已落库，
        write_stage 仍指向失败阶段，resume 重跑该阶段（幂等）。
        """
        from src.models.device_outage_window import DeviceOutageWindow

        db = self.db
        row = db.get(DeviceOutageWindow, window_id)
        failed_stage = stage or row.write_stage
        row.last_error = reason[:255]
        db.commit()
        self.audit.log(
            "DeviceOutageWindow", 3, actor=actor, target_id=window_id,
            window_id=window_id, stage=failed_stage, reason=row.last_error,
        )
        db.commit()
        return failed_stage

    def _occupied_for(self, building_id: int, device_type: str,
                      *, exclude_device_ids: list[int], start_at, end_at) -> int:
        """同栋同类型备用设备在重叠时段已占用名额（含其它确认窗口）。"""
        candidates = self.device_repo.list_backup_candidates(
            building_id=building_id, device_type=device_type,
            exclude_device_ids=exclude_device_ids,
        )
        total = 0
        for cand in candidates:
            total += self._occupied_seats_on_device(
                cand.id, start_at, end_at, exclude_window_id=None
            )
        return total

    def _occupied_seats_on_device(self, device_id: int, start_at, end_at,
                                  *, exclude_window_id: int | None) -> int:
        from src.models.capacity_holding import CapacityHolding
        from src.models.device_outage_window import DeviceOutageWindow

        stmt = (
            select(CapacityHolding.seats)
            .join(DeviceOutageWindow,
                  DeviceOutageWindow.id == CapacityHolding.window_id)
            .where(
                CapacityHolding.backup_device_id == device_id,
                DeviceOutageWindow.outage_status == "CONFIRMED",
                DeviceOutageWindow.start_at <= end_at,
                DeviceOutageWindow.end_at >= start_at,
            )
        )
        if exclude_window_id is not None:
            stmt = stmt.where(CapacityHolding.window_id != exclude_window_id)
        return int(sum(self.db.execute(stmt).scalars().all() or [0]))

    def _overlapping_outage_device_ids(self, *, building_id: int, device_type: str,
                                       start_at, end_at,
                                       exclude_window_id: int) -> list[int]:
        from src.models.device_outage_window import DeviceOutageWindow
        from src.models.fire_device import FireDevice

        stmt = (
            select(DeviceOutageWindow.device_id)
            .join(FireDevice, FireDevice.id == DeviceOutageWindow.device_id)
            .where(
                DeviceOutageWindow.outage_status == "CONFIRMED",
                FireDevice.building_id == building_id,
                FireDevice.device_type == device_type,
                DeviceOutageWindow.start_at <= end_at,
                DeviceOutageWindow.end_at >= start_at,
                DeviceOutageWindow.id != exclude_window_id,
            )
        )
        return list(self.db.execute(stmt).scalars().all())

    def _demanded_for(self, building_id: int, device_type: str, device_id: int,
                      start_at, end_at) -> int:
        originals = self.assignment_repo.list_originals_for_window(
            building_id=building_id,
            device_type=device_type,
            device_ids=[device_id],
            plan_start=start_at,
            plan_end=end_at,
        )
        return sum(a.seats for a in originals)

    def _device_code(self, device_id: int) -> str:
        device = self.device_repo.get(device_id)
        return device.device_code if device else str(device_id)
