-- fire-inspect 初始化结构（PostgreSQL 15）
-- 应用启动时 SQLAlchemy create_all 也会幂等建表，此文件用于容器初始化与审计。

CREATE TABLE IF NOT EXISTS building (
  id SERIAL PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  campus VARCHAR(128) NOT NULL DEFAULT '',
  floor_count INTEGER NOT NULL DEFAULT 1,
  fire_grade VARCHAR(32) NOT NULL DEFAULT 'SECOND',
  manager_id INTEGER,
  address_code VARCHAR(64) NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS fire_device (
  id SERIAL PRIMARY KEY,
  building_id INTEGER NOT NULL,
  device_code VARCHAR(64) NOT NULL UNIQUE,
  device_type VARCHAR(32) NOT NULL,
  floor VARCHAR(16) NOT NULL DEFAULT '1',
  location_desc VARCHAR(255) NOT NULL DEFAULT '',
  install_date DATE,
  status VARCHAR(32) NOT NULL DEFAULT 'NORMAL',
  next_maintenance_at TIMESTAMP,
  capacity INTEGER NOT NULL DEFAULT 3
);
CREATE INDEX IF NOT EXISTS idx_device_building ON fire_device(building_id);
CREATE INDEX IF NOT EXISTS idx_device_status_type ON fire_device(status, device_type);

CREATE TABLE IF NOT EXISTS inspection_task (
  id SERIAL PRIMARY KEY,
  building_id INTEGER NOT NULL,
  inspector_id INTEGER,
  plan_date TIMESTAMP NOT NULL,
  task_type VARCHAR(32) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'PLANNED',
  checklist_version VARCHAR(32) NOT NULL DEFAULT 'v1',
  finished_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_task_plan ON inspection_task(plan_date);

CREATE TABLE IF NOT EXISTS inspection_result (
  id SERIAL PRIMARY KEY,
  task_id INTEGER NOT NULL,
  device_id INTEGER NOT NULL,
  item_code VARCHAR(64) NOT NULL,
  result_status VARCHAR(32) NOT NULL DEFAULT 'NORMAL',
  measured_value VARCHAR(64) NOT NULL DEFAULT '',
  photo_url VARCHAR(255),
  note TEXT,
  review_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
  voided_by_window_id INTEGER,
  reviewed_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_result_device ON inspection_result(device_id);
CREATE INDEX IF NOT EXISTS idx_result_review ON inspection_result(review_status);

CREATE TABLE IF NOT EXISTS hazard_ticket (
  id SERIAL PRIMARY KEY,
  result_id INTEGER NOT NULL,
  severity VARCHAR(32) NOT NULL DEFAULT 'MEDIUM',
  owner_id INTEGER,
  deadline TIMESTAMP,
  rectify_status VARCHAR(32) NOT NULL DEFAULT 'OPEN',
  rectify_note TEXT,
  closed_at TIMESTAMP,
  review_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
  voided_by_window_id INTEGER,
  reviewed_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ticket_review ON hazard_ticket(review_status);

-- 设备停用时段
CREATE TABLE IF NOT EXISTS device_outage_window (
  id SERIAL PRIMARY KEY,
  window_group_id INTEGER NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,
  device_id INTEGER NOT NULL,
  owner_id INTEGER NOT NULL,
  start_at TIMESTAMP NOT NULL,
  end_at TIMESTAMP NOT NULL,
  reason VARCHAR(255) NOT NULL DEFAULT '',
  outage_status VARCHAR(32) NOT NULL DEFAULT 'DRAFT',
  occupied_capacity INTEGER NOT NULL DEFAULT 0,
  demanded_capacity INTEGER NOT NULL DEFAULT 0,
  write_stage VARCHAR(64) NOT NULL DEFAULT 'PERSIST_WINDOW',
  resume_key VARCHAR(64),
  last_error VARCHAR(255),
  created_at TIMESTAMP,
  confirmed_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_window_device ON device_outage_window(device_id);
CREATE INDEX IF NOT EXISTS idx_window_status_range
  ON device_outage_window(outage_status, start_at, end_at);

-- 容量占用（恢复时按 window_id + assignment_id 判重）
CREATE TABLE IF NOT EXISTS capacity_holding (
  id SERIAL PRIMARY KEY,
  window_id INTEGER NOT NULL,
  backup_device_id INTEGER NOT NULL,
  assignment_id INTEGER NOT NULL,
  seats INTEGER NOT NULL DEFAULT 1,
  created_at TIMESTAMP,
  CONSTRAINT uq_holding_window_assignment UNIQUE (window_id, assignment_id)
);
CREATE INDEX IF NOT EXISTS idx_holding_window ON capacity_holding(window_id);
CREATE INDEX IF NOT EXISTS idx_holding_backup ON capacity_holding(backup_device_id);

-- 任务-设备排期（ORIGINAL 关系永不删除）
CREATE TABLE IF NOT EXISTS task_device_assignment (
  id SERIAL PRIMARY KEY,
  task_id INTEGER NOT NULL,
  building_id INTEGER NOT NULL,
  device_type VARCHAR(32) NOT NULL,
  planned_device_id INTEGER NOT NULL,
  actual_device_id INTEGER,
  assignment_status VARCHAR(32) NOT NULL DEFAULT 'ORIGINAL',
  window_id INTEGER,
  origin_assignment_id INTEGER,
  queue_position INTEGER,
  seats INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_assignment_window ON task_device_assignment(window_id);
CREATE INDEX IF NOT EXISTS idx_assignment_status ON task_device_assignment(assignment_status);

-- 停用草稿（后到负责人保留）
CREATE TABLE IF NOT EXISTS outage_draft (
  id SERIAL PRIMARY KEY,
  window_id INTEGER NOT NULL,
  owner_id INTEGER NOT NULL,
  payload VARCHAR(2000) NOT NULL DEFAULT '{}',
  observed_occupied INTEGER NOT NULL DEFAULT 0,
  lock_version INTEGER NOT NULL DEFAULT 1,
  updated_at TIMESTAMP,
  CONSTRAINT uq_draft_window_owner UNIQUE (window_id, owner_id)
);

-- 复役手续
CREATE TABLE IF NOT EXISTS outage_procedure (
  id SERIAL PRIMARY KEY,
  device_id INTEGER NOT NULL,
  window_id INTEGER NOT NULL,
  procedure_type VARCHAR(32) NOT NULL,
  completed INTEGER NOT NULL DEFAULT 0,
  doc_url VARCHAR(255),
  created_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_procedure_device ON outage_procedure(device_id, window_id);

CREATE TABLE IF NOT EXISTS audit_log (
  id SERIAL PRIMARY KEY,
  actor VARCHAR(64) NOT NULL DEFAULT 'system',
  action VARCHAR(128) NOT NULL,
  target_type VARCHAR(64) NOT NULL,
  target_id VARCHAR(64) NOT NULL DEFAULT '',
  detail TEXT,
  created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at);
