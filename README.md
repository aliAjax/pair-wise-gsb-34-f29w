# 消防设施巡检维保平台（fire-inspect）

面向园区和物业公司的消防设备巡检、隐患整改、维保计划与合规台账系统。本期重点实现**停机保养与巡检排期冲突联动**：提交消防设备停用时段后，同段巡检自动改用备用设备、容量不足排队转待补检、并发确认保留草稿、写入失败可续传、停用变化级联作废待复核、复役手续不齐不允许回正常。

## 快速启动（首选）

```bash
cp .env.example .env && docker compose up -d
```

启动完成后：

- 前端：<http://localhost:20103>
- 后端健康检查：<http://localhost:21103/health>
- API 文档（本地开发）：<http://localhost:21103/docs>

重置全部数据：

```bash
docker compose down -v && docker compose up -d
```

## 停机保养 × 巡检排期：业务规则

1. **提交停用时段 → 同段巡检改派**
   负责人提交停用后，计划落在停用窗口且引用该设备的巡检任务，优先改派给「同楼栋、同类型、正常且该窗口未停用」的备用设备；`task_reroute` 中同时保留 `ORIGINAL`（原任务关系）与新增的 `BACKUP` 关系，不覆盖旧数据。
2. **容量不足排队转待补检**
   每台备用设备在重叠窗口内容量有限（`BACKUP_SLOT_CAPACITY`，种子数据设为 1 槽）。超出容量的任务转 `PENDING_MAKEUP（待补检）`，在巡检任务页可按状态筛选。
3. **两个负责人同时确认重叠时段**
   后端对设备行加锁（PostgreSQL `SELECT … FOR UPDATE`）后二次检查窗口占用；先到者占名额生效，后到者接口返回**占用数量 `occupied_count`** 与冲突时段，时段只保存为 `DRAFT` 草稿，不抢名额、不改设备状态。提交前还可用 `GET /api/device-outage/occupied` 预览占用。
4. **写入失败后恢复（续传）**
   提交时用 `fail_device_codes` 模拟部分设备写入失败（落 `PENDING` 条目并形成 `PARTIAL_FAILED` 批次）。`POST /api/device-outage/batch/{id}/resume` 只续传 `PENDING` 条目；唯一约束 `(task_id, outage_id, device_id, relation)` 保证已占名额**不重复也不丢失**。
5. **停用时段变化 → 作废待复核**
   确认后的时段被改期（旧版本标记 `SUPERSEDED`，新版本号递增并重算改派）或撤销时，引用这些设备的**巡检结果**置 `VOID_PENDING_REVIEW`、**隐患整改单**置 `VOID_PENDING_REVIEW`（已复验关闭的除外），由主管/审计在任务页或隐患页选择「恢复有效 / 确认作废」。
6. **复役手续闸口**
   停用设备手续为三项：维保报告、安全检测、主管签字。复役时缺任何一项都会返回 `PAPERWORK_INCOMPLETE`，设备挂 `PENDING_REUSE（待复役）`，不能回到 `NORMAL`；手续补齐后方可复役。

演示路径（种子数据已预置冲突场景）：

1. 以「吴维保（维保商）」身份打开「停机保养排期」，选择 `HYD-001 / SMK-001 / SPR-001` 提交，勾选“模拟最后一台写入失败”；
2. 观察 HYD 任务改派 `HYD-002`、SMK 3 个任务中 2 个改派 1 个待补检、SPR 写入失败待续传；
3. 点「续传未生效设备」，SPR-001 生效且其任务排队待补检，HYD/SMK 名额不翻倍；
4. 切到「郑主管」对 `HYD-001` 再提交一个重叠时段 → 看到占用数量并保留草稿；
5. 对已确认停用「变更时段」，到「巡检任务 / 隐患整改」查看作废待复核并恢复/确认；
6. 「消防设备台账」里对停用设备点「申请复役」（手续不齐 → 待复役），补完三项手续后复役成功。

## 访问地址或 CLI 示例

```bash
# 健康检查
curl http://localhost:21103/health

# 查看停用窗口占用数量（后到者决策依据）
curl "http://localhost:21103/api/device-outage/occupied?device_id=1&start_at=2026-10-03T09:00:00Z&end_at=2026-10-03T15:00:00Z"

# 提交停用（fail_device_codes 模拟部分写入失败）
curl -X POST http://localhost:21103/api/device-outage \
  -H 'Content-Type: application/json' -H 'x-user-id: 2' \
  -d '{"items":[{"device_code":"SPR-001","start_at":"2026-10-03T09:00:00Z","end_at":"2026-10-03T15:00:00Z"}],"fail_device_codes":["SPR-001"]}'

# 续传未生效设备（已占名额不重复不丢失）
curl -X POST http://localhost:21103/api/device-outage/batch/1/resume -H 'x-user-id: 2'

# 补齐复役手续 + 复役
curl -X POST http://localhost:21103/api/fire-device/8/paperwork -H 'Content-Type: application/json' \
  -d '{"paperwork_items":["MAINTENANCE_REPORT","SAFETY_CHECK","MANAGER_SIGN_OFF"]}'
curl -X POST http://localhost:21103/api/fire-device/8/reactivate -H 'x-user-id: 3'
```

本地演示身份通过 `x-user-id` 头切换：`1` 巡检员、`2` 维保商、`3` 物业主管、`4` 审计员（前端顶栏可直接切换）。

## 本地开发方式

- 前端：`cd frontend && npm install && npm run dev`（Vite 监听 20103，`/api` 代理到 `127.0.0.1:21103`）
- 后端：

```bash
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
# 本地无 PostgreSQL 时可用 SQLite：
DATABASE_URL="sqlite:///./fire_inspect.db" uvicorn src.main:app --reload --port 21103
```

- 后端测试：

```bash
cd backend && pip install pytest && python -m pytest tests/ -q
```

- 前端构建：`cd frontend && npm run build`

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 18 + TypeScript + Vite + Material UI 5 + Redux Toolkit + react-router-dom 6 |
| 后端 | FastAPI + Python 3.11 + SQLAlchemy 2.0 + Pydantic 2 + python-jose（JWT） |
| 数据库 | PostgreSQL 15（本地测试用 SQLite，内存库 + StaticPool） |
| 部署 | Docker Compose（db / backend / frontend，命名卷 + healthcheck） |

## 项目目录结构

```text
.
├── docker-compose.yml          # 顶层 name: fire-inspect；无 version 字段
├── .env / .env.example
├── database/init.sql           # 全部表结构（device_outage/outage_batch/task_reroute 等）
├── backend/
│   ├── Dockerfile
│   └── src/
│       ├── main.py             # FastAPI、lifespan 播种、中间件链、路由
│       ├── routes/             # 按实体分文件（含 device_outage_routes）
│       ├── controllers/        # 每实体一文件 + base_controller 二次包装异常
│       ├── services/           # 业务编排（reroute/cascade_void/device_outage…）
│       ├── repositories/       # 数据访问层
│       ├── models/             # SQLAlchemy ORM
│       ├── constructors/       # ORM → 响应 DTO 工厂
│       ├── types/              # Pydantic 请求 DTO
│       ├── middlewares/        # auth / rbac / audit / error / rate-limit / request-log
│       ├── constants/          # 枚举、错误码、错误消息、日志模板、状态文案
│       ├── config/             # settings、database 引擎与会话
│       └── utils/              # formatters（日期/状态/风险）、exceptions
└── frontend/
    ├── Dockerfile / nginx.conf
    └── src/
        ├── api/                # 统一 /api 封装 client.ts + 按实体拆分
        ├── stores/             # Redux Toolkit slices（含 SessionStore/DeviceOutageStore）
        ├── pages/              # 6 个页面（新增“停机保养排期”）
        ├── router/             # 路由表 + RoleGuard 路由守卫
        ├── components/         # AppLayout + common 共享组件
        ├── hooks/              # usePagination / useChecklistProgress / useHazardFlow
        ├── constants/          # 枚举、错误码/消息、日志模板、角色、状态文案
        ├── constructors/       # 默认对象/表单/响应构造器
        ├── types/              # 共享 TS 类型
        └── utils/formatters.ts # 日期/状态/风险混合格式化
```

## 环境变量说明

| 变量 | 默认值 | 说明 |
|---|---|---|
| `COMPOSE_PROJECT_NAME` | `fire-inspect` | Compose 项目名与容器名前缀 |
| `FRONTEND_PORT` | `20103` | 前端宿主机端口（容器内 80） |
| `BACKEND_PORT` | `21103` | 后端宿主机端口（容器内 8000） |
| `DB_PORT` | `54320` | PostgreSQL 宿主机映射端口 |
| `DB_NAME / DB_USER / DB_PASSWORD` | `app_db / app_user / app_password` | 数据库凭据 |
| `JWT_SECRET` | `local-dev-secret` | JWT 签名密钥，生产请替换 |
| `DATABASE_URL`（仅后端/本地开发） | 指向 compose 内 PostgreSQL | 可临时覆盖为 `sqlite:///./x.db` |

配置分散经过 `.env.example`、`docker-compose.yml`、`backend/src/config/settings.py`、请求封装与日志模块读取，新增配置需同步多处。

## Docker 部署说明

- 根 Compose 文件不写 `version`，顶层 `name: fire-inspect`；所有服务 `container_name` 带 `${COMPOSE_PROJECT_NAME:-fire-inspect}` 前缀。
- 端口：前端 `${FRONTEND_PORT:-20103}:80`，后端 `${BACKEND_PORT:-21103}:8000`。
- 数据库使用**命名卷 `db_data`**，不绑定挂载到中文路径；`database/init.sql` 只读挂到 `/docker-entrypoint-initdb.d`（应用启动也会 `create_all` + 播种，二者结构一致）。
- db 配置 `pg_isready` healthcheck；backend `depends_on: condition: service_healthy`；frontend 再依赖 backend 健康（backend 用 Python 标准库探活，不依赖 slim 镜像里的 wget）。
- Nginx：`location /api/` 反代 `http://backend:8000/api/`，前端路由统一 `try_files $uri $uri/ /index.html;`；前端代码只请求同源 `/api`，无硬编码 localhost。
- 常见问题：
  - 端口占用：改 `.env` 中端口后 `docker compose up -d`；
  - 要重置种子数据：`docker compose down -v`；
  - 在中文目录名下启动：已避免向中文路径做绑定挂载，命名卷不受影响。

## 枚举/常量出现位置清单

> 新增一个枚举值至少要同步：常量、类型、（后端）标签文案、日志模板、错误消息、格式化、列表筛选、详情展示与种子数据。

### DeviceType（EXTINGUISHER / HYDRANT / SMOKE_DETECTOR / SPRINKLER / EXIT_LIGHT）

- 后端：`backend/src/constants/device_type.py`（枚举 + 中文标签）、`models/fire_device.py`、`repositories/fire_device_repository.py`（备用候选筛选）、`seed.py`、`utils/formatters.py`、`constructors/fire_device_factory.py`
- 前端：`constants/DeviceType.ts`、`types/DeviceType.ts`、`types/FireDevice.ts`、`constructors/FireDeviceConstructor.ts`、`constants/statusText.ts`、`utils/formatters.ts`、`pages/DevicesPage.tsx`（筛选器/展示）、`pages/TasksPage.tsx`（任务类型）、`pages/ReportsPage.tsx`

### InspectionStatus（PLANNED / IN_PROGRESS / SUBMITTED / REVIEWED / OVERDUE / PENDING_MAKEUP）

- 后端：`constants/inspection_status.py`、`models/inspection_task.py`、`services/inspection_task_service.py`（合法状态集）、`services/reroute_service.py`（容量不足置 `PENDING_MAKEUP`）、`seed.py`、`constructors/inspection_task_factory.py`、`services/dashboard_service.py`
- 前端：`constants/InspectionStatus.ts`、`types/InspectionStatus.ts`、`constructors/InspectionTaskConstructor.ts`、`constants/statusText.ts`、`utils/formatters.ts`、`pages/TasksPage.tsx`（筛选/徽标/待补检）、`pages/DashboardPage.tsx`、`pages/ReportsPage.tsx`、`mocks/seedData.ts`

### HazardSeverity（LOW / MEDIUM / HIGH / CRITICAL）

- 后端：`constants/hazard_severity.py`、`models/hazard_ticket.py`、`services/hazard_ticket_service.py`、`seed.py`、`constructors/hazard_ticket_factory.py`、`services/dashboard_service.py`
- 前端：`constants/HazardSeverity.ts`、`types/HazardSeverity.ts`、`constructors/HazardTicketConstructor.ts`、`constants/statusText.ts`、`utils/formatters.ts`（formatRisk）、`components/common/HazardSeverityTag.tsx`、`pages/HazardsPage.tsx`、`pages/DashboardPage.tsx`、`pages/ReportsPage.tsx`

### 本期新增枚举/常量

- DeviceStatus：`NORMAL / OUTAGE / PENDING_REUSE / FAULT`（后端 `constants/device_status.py`，前端 `constants/DeviceStatus.ts`）
- OutageStatus：`DRAFT / CONFIRMED / SUPERSEDED / CANCELLED / PENDING`（后端 `constants/outage_status.py`，前端 `constants/OutageStatus.ts`，同处还定义 `BACKUP_SLOT_CAPACITY`）
- 复役手续：`MAINTENANCE_REPORT / SAFETY_CHECK / MANAGER_SIGN_OFF`（后端 `constants/error_messages.py` 内的清单，前端设备页手续弹窗）
- 任务改派关系：`ORIGINAL / BACKUP / QUEUED`（`models/task_reroute.py` 与 `services/reroute_service.py`）
- 结果复核标志：`ACTIVE / VOID_PENDING_REVIEW / VOID_CONFIRMED`（`models/inspection_result.py`、`types/InspectionResult.ts`）

## 为什么该项目会“牵一发动全身”

- 日志模板集中在 `constants/log_templates.*`，每个实体 ≥4 条，停用联动还新增了 `DeviceOutage` 6 条与改派/排队模板；字段变更必须同步模板与 service 调用处。
- 错误码与错误消息分文件集中定义，service 抛 `ServiceException`、controller 经 `base_controller.call` 二次包装成 HTTP 响应，全局错误中间件只做兜底，无法在一个位置吞掉全部异常。
- 构造器/工厂按实体拆分（停用有 `device_outage_factory.py`、改派有 `task_reroute_factory.py`），页面、store、service 不散写默认结构。
- 枚举在前后端多处重复定义并在本 README 列位置；新增状态要同步常量、类型、日志、错误、格式化、筛选、展示、种子。
- `utils/formatters.*` 混合日期、状态文本、风险等级与复役手续格式化，被页面与服务共同依赖。
- 一个停用动作会横跨：`device_outage → fire_device → task_reroute → inspection_task → inspection_result → hazard_ticket → audit_log`，任何字段调整都会触达 routes/controller/service/repository/model/constructor/constants 与前端 api/types/store/page/component。

## License

MIT
