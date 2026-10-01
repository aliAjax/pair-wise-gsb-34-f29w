# 消防设施巡检维保平台

面向园区和物业公司的消防设备巡检、隐患整改、**停机保养与巡检排期联动**、维保计划和合规台账系统。

## 快速启动

```bash
cp .env.example .env && docker compose up -d
```

启动后：

- 前端：<http://localhost:20103>
- 后端健康检查：<http://localhost:21103/health>
- 接口文档（Swagger）：<http://localhost:21103/docs>

## 核心业务：停机保养 × 巡检排期

负责人提交消防设备停用时段后，系统按下述规则联动巡检任务与合规单据（这是本项目的主线，端到端贯通数据库 → 后端 → 前端）：

1. **同段巡检改用备用设备**：停用确认时，同楼栋、同设备类型的正常设备按各自 `capacity`（备用容量名额）承接与停用时段重叠的巡检排期。
2. **容量不足排队转待补检**：备用名额用完后，剩余排期按队列顺序置为 `PENDING_RECHECK`（待补检），记录队列位置；设备复役后可再生成 `RESCHEDULED`（已补排）。
3. **原任务关系保留**：任务与计划设备的 `ORIGINAL` 关系永不删除；停用期间新增 `BACKUP` / `PENDING_RECHECK` 派生关系，通过 `origin_assignment_id` 关联回原排期。
4. **两个负责人同时确认重叠时段**：停用窗口行级锁（PostgreSQL `SELECT … FOR UPDATE`）串行化；后到者通过「并发确认」入口看到当前**已占用数量**，容量不足时其提交**保留为草稿**（`outage_draft`，带乐观锁版本），窗口不被确认。
5. **写入失败后恢复（断点续跑）**：确认流程分为 `PERSIST_WINDOW → HOLD_CAPACITY（内含 REALLOCATE_TASKS）→ MARK_DEVICE_OUTAGE → COMPLETED` 四个阶段，逐条排期提交。失败时返回 `resume_key` 与停留阶段；调用恢复接口续跑。容量占用按 `(window_id, assignment_id)` 唯一约束判重，**已占名额不重复、不丢失**。
6. **停用时段一变化即作废待复核**：调整停用时段后旧版本置 `SUPERSEDED`，引用这些设备的**巡检结果**与**隐患整改单**一律置 `VOID_PENDING`（作废待复核），复核后可 `RECONFIRMED` / `REJECTED`；再次变更会重新作废。
7. **复役前手续校验**：设备必须登记齐 `MAINTENANCE_REPORT`（保养完工报告）、`ACCEPTANCE_CHECK`（验收检测）、`SAFETY_SIGN_OFF`（安全责任人签收）三项手续，否则复役接口返回 `RESTORE_PROCEDURE_INCOMPLETE`，设备不能回到正常。

### 主要接口（前缀 `/api/outage-window`）

| 方法 & 路径 | 说明 |
|---|---|
| `POST /api/outage-window` | 提交停用时段（草稿，返回占用快照） |
| `POST /outage-window/{id}/confirm` | 确认停用（触发备用切换 / 待补检 / 设备停用） |
| `POST /outage-window/{id}/confirm-guard?owner_id=` | 并发确认：容量不足时后到者看占用数量并保留草稿 |
| `POST /outage-window/{id}/resume?resume_key=` | 写入失败后断点续跑 |
| `POST /outage-window/{id}/change` | 停用时段变更（旧版作废 + 结果/隐患单作废待复核） |
| `GET  /outage-window/{id}/holdings` | 已占备用容量名额 |
| `GET  /outage-window/{id}/assignments` | 该窗口的备用/待补检排期 |
| `GET  /outage-window/{id}/drafts` | 后到者保留的草稿 |
| `POST /outage-window/{id}/procedure` | 登记复役手续 |
| `POST /outage-window/device/{deviceId}/restore` | 复役（校验手续 + 补排待补检） |
| `GET  /inspection-task/assignments` | 全部任务-设备排期（含保留的 ORIGINAL） |
| `POST /inspection-result/{id}/review`、`POST /hazard-ticket/{id}/review` | 作废单据复核 |

### 请求头与角色（RBAC）

本地演示通过 `x-user-id`、`x-role` 头传递身份，角色：`INSPECTOR`（巡检员）/`MAINTAINER`（维保商）/`SUPERVISOR`（物业主管）/`AUDITOR`（审计员，只读）/`ADMIN`。停用确认、复役等写操作对审计员返回 `RBAC_DENIED`。

## 本地开发方式

- 前端：`cd frontend && npm install && npm run dev`（端口 20103，统一请求 `/api`，由 Vite/Nginx 反代）
- 后端：`cd backend && pip install -r requirements.txt && uvicorn src.main:app --reload --port 8000`
- 不依赖 Docker/PostgreSQL 也可跑测试：

```bash
cd backend
DATABASE_URL="sqlite:///:memory:" python -m pytest tests/ -q
```

后端测试共 **23 个用例**，覆盖：备用切换、容量不足排队、原关系保留、并发冲突保留草稿、幂等重复确认、写入失败恢复（名额不重复不丢失）、变更作废结果/隐患单、复核、手续未齐禁止复役、复役补排、RBAC、参数校验。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 18 + TypeScript + Vite + Material UI + Zustand |
| 后端 | FastAPI + Python 3.11 + SQLAlchemy 2.0 |
| 数据库 | PostgreSQL 15（测试使用 SQLite 内存库） |
| 部署 | Docker Compose（frontend / backend / db） |

## 项目目录结构

```text
frontend/src/
├── api/                  # http.ts 统一封装 + 按实体分文件（含 OutageWindow.ts）
├── stores/               # zustand，按实体分文件（含 OutageWindowStore.ts）
├── types/                # DeviceOutageWindow / TaskDeviceAssignment / 复核状态等
├── constants/            # 枚举、错误码、错误消息、日志模板、状态文案
├── constructors/         # 默认对象 / 表单 / 响应构造器（含 OutageWindowConstructor）
├── components/common/    # StatusBadge / OutageCapacityBar / ReviewFlag / ChecklistPanel ...
├── hooks/                # useOutageScheduling / useChecklistProgress / useHazardFlow / usePagination
├── pages/                # Dashboard / Devices / Outage / Tasks / Hazards / Reports
├── router/ utils/ mocks/
backend/src/
├── routes/ controllers/ services/ models/ repositories/
├── middlewares/          # auth / rbac / audit_log / error_handler
├── constants/            # 枚举 + error_codes + error_messages + log_templates
├── constructors/ types/ utils/ config/
database/init.sql         # 全部表（含 device_outage_window、capacity_holding 等）
backend/tests/            # pytest：6 组业务规则 + HTTP API 端到端
```

## 环境变量说明

| 变量 | 说明 | 默认值 |
|---|---|---|
| `COMPOSE_PROJECT_NAME` | Compose 项目名与容器名前缀 | `fire-inspect` |
| `FRONTEND_PORT` | 前端宿主机端口 | `20103` |
| `BACKEND_PORT` | 后端宿主机端口 | `21103` |
| `DB_PORT` | PostgreSQL 宿主机端口 | `54320` |
| `DB_NAME / DB_USER / DB_PASSWORD` | 数据库名 / 用户 / 密码 | `app_db / app_user / app_password` |
| `JWT_SECRET` | JWT 密钥 | `local-dev-secret` |
| `DATABASE_URL` | 覆盖数据库连接（测试用 `sqlite://`） | 指向 compose 中的 PostgreSQL |

## Docker 部署说明

- 根 Compose 不写 `version`，顶层 `name: fire-inspect`；容器名均带 `${COMPOSE_PROJECT_NAME:-fire-inspect}` 前缀。
- 前端端口 `${FRONTEND_PORT:-20103}:80`，后端 `${BACKEND_PORT:-21103}:8000`，容器内部后端监听 8000。
- 前端只请求 `/api`，Nginx `location /api/` 反代到 `http://backend:8000/api/`，SPA 使用 `try_files $uri $uri/ /index.html;`。
- 数据库使用命名卷 `db_data`（不绑定挂载，中文目录名也不受影响），配置 healthcheck；后端 `depends_on: condition: service_healthy`，后端自身也有 `/health` healthcheck，前端再依赖后端健康。
- 常见问题：端口占用改 `.env`；重置数据 `docker compose down -v`；`docker compose config --quiet` 可校验编排文件。

## 枚举 / 常量出现位置清单

> 新增枚举值需同步：前后端常量、类型、构造器、日志模板、错误消息、筛选器、展示组件。

| 枚举 | 后端常量 | 前端常量 | 类型 / 模型 | 关联面 |
|---|---|---|---|---|
| `DeviceType`（灭火器/消火栓/烟感/喷淋/疏散指示灯） | `constants/device_type.py` | `constants/DeviceType.ts` | `models/fire_device.py`、`types/FireDevice.ts` | 备用设备筛选、容量统计、台账页、停用页下拉 |
| `DeviceStatus`（NORMAL/OUT_OF_SERVICE/RESTORED） | `constants/device_status.py` | `constants/DeviceStatus.ts` | FireDevice `status` | 停用确认、复役、台账筛选、StatusBadge |
| `OutageStatus`（DRAFT/CONFIRMED/SUPERSEDED） | `constants/outage_status.py` | `constants/OutageStatus.ts` | `device_outage_window` | 草稿保留、行锁确认、变更作旧 |
| `AssignmentStatus`（ORIGINAL/BACKUP/PENDING_RECHECK/RESCHEDULED/DONE） | `constants/assignment_status.py` | `constants/AssignmentStatus.ts` | `task_device_assignment` | 排期去向、队列、原关系保留、任务页/停用页 |
| `ReviewStatus`（ACTIVE/VOID_PENDING/RECONFIRMED/REJECTED） | `constants/review_status.py` | `constants/ReviewStatus.ts` | InspectionResult / HazardTicket `review_status` | 变更作废、复核接口、ReviewFlag、隐患页 |
| `ProcedureType`（三种复役手续）+ `WriteStage`（四阶段） | `constants/procedure_type.py`、`constants/write_stage.py` | `constants/ProcedureType.ts` | `outage_procedure`、窗口 `write_stage` | 复役拦截、断点续跑、恢复按钮 |
| `InspectionStatus`（PLANNED/IN_PROGRESS/SUBMITTED/REVIEWED/OVERDUE） | `constants/inspection_status.py` | `constants/InspectionStatus.ts` | InspectionTask | 任务页、构造器、日志 |
| `HazardSeverity`（LOW/MEDIUM/HIGH/CRITICAL） | `constants/hazard_severity.py` | `constants/HazardSeverity.ts` | HazardTicket | HazardSeverityTag、隐患页、总览 |

错误码 / 错误消息：后端 `constants/error_codes.py`、`constants/error_messages.py` ↔ 前端 `constants/errorCodes.ts`、`errorMessages.ts`。
日志模板：后端 `constants/log_templates.py` ↔ 前端 `constants/logTemplates.ts`，所有写操作经 `AuditService` 落库到 `audit_log`。

## 为什么会牵一发动全身

- 设备状态、停用状态、排期状态、复核状态、手续、写入阶段等枚举在前后端各有一份，且被类型、工厂构造器、日志模板、错误消息、筛选器与展示组件共同引用。
- 容量名额、停用窗口、任务排期、作废复核分布在 model / repository / service / controller / route / store / api / page / 共享组件多层，一个规则调整（如“什么算容量不足”）会同时触达 `OutageWindowService`、`capacity_holding`、`OutageCapacityBar`、错误码、测试与 README。
- `utils/formatters` 混合日期、状态、风险等级、容量百分比，被多个页面依赖；全局配置散落在 `.env.example`、`docker-compose.yml`、`config/settings.py`、请求封装 `api/http.ts` 中，新增配置须多处同步。

## License

MIT
