-- 消防设施巡检维保平台初始化结构
-- 应用启动时 SQLAlchemy 也会 createAll；此文件保证数据库容器初始化后结构一致。

CREATE TABLE IF NOT EXISTS building (
  id SERIAL PRIMARY KEY,
  name VARCHAR(64) NOT NULL,
  campus VARCHAR(64) NOT NULL,
  floor_count INTEGER NOT NULL DEFAULT 1,
  fire_grade VARCHAR(32) NOT NULL DEFAULT '二级',
  manager_id INTEGER,
  address_code VARCHAR(32)
);

CREATE TABLE IF NOT EXISTS fire_device (
  id SERIAL PRIMARY KEY,
  building_id INTEGER NOT NULL,
  device_code VARCHAR(64) NOT NULL UNIQUE,
  device_type VARCHAR(32) NOT NULL,
  floor VARCHAR(16) NOT NULL,
  location_desc VARCHAR(128) NOT NULL,
  install_date TIMESTAMP,
  status VARCHAR(32) NOT NULL DEFAULT 'NORMAL',
  next_maintenance_at TIMESTAMP,
  reuse_paperwork VARCHAR(128) NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_fire_device_building ON fire_device(building_id);
CREATE INDEX IF NOT EXISTS idx_fire_device_status ON fire_device(status);

CREATE TABLE IF NOT EXISTS inspection_task (
  id SERIAL PRIMARY KEY,
  building_id INTEGER NOT NULL,
  inspector_id INTEGER,
  plan_date TIMESTAMP NOT NULL,
  task_type VARCHAR(32) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'PLANNED',
  checklist_version VARCHAR(16) NOT NULL DEFAULT 'v1',
  finished_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_inspection_task_building ON inspection_task(building_id);
CREATE INDEX IF NOT EXISTS idx_inspection_task_status ON inspection_task(status);
CREATE INDEX IF NOT EXISTS idx_inspection_task_plan ON inspection_task(plan_date);

CREATE TABLE IF NOT EXISTS inspection_result (
  id SERIAL PRIMARY KEY,
  task_id INTEGER NOT NULL,
  device_id INTEGER NOT NULL,
  item_code VARCHAR(64) NOT NULL,
  result_status VARCHAR(32) NOT NULL DEFAULT 'NORMAL',
  measured_value VARCHAR(128),
  photo_url VARCHAR(256),
  note VARCHAR(256),
  review_flag VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
  voided_at TIMESTAMP,
  voided_by_outage_id INTEGER
);
CREATE INDEX IF NOT EXISTS idx_result_task ON inspection_result(task_id);
CREATE INDEX IF NOT EXISTS idx_result_device ON inspection_result(device_id);
CREATE INDEX IF NOT EXISTS idx_result_review ON inspection_result(review_flag);

CREATE TABLE IF NOT EXISTS hazard_ticket (
  id SERIAL PRIMARY KEY,
  result_id INTEGER NOT NULL,
  device_id INTEGER NOT NULL,
  severity VARCHAR(16) NOT NULL DEFAULT 'MEDIUM',
  owner_id INTEGER,
  deadline TIMESTAMP,
  rectify_status VARCHAR(32) NOT NULL DEFAULT 'OPEN',
  rectify_note VARCHAR(256),
  closed_at TIMESTAMP,
  voided_at TIMESTAMP,
  voided_by_outage_id INTEGER
);
CREATE INDEX IF NOT EXISTS idx_ticket_device ON hazard_ticket(device_id);
CREATE INDEX IF NOT EXISTS idx_ticket_result ON hazard_ticket(result_id);
CREATE INDEX IF NOT EXISTS idx_ticket_status ON hazard_ticket(rectify_status);

CREATE TABLE IF NOT EXISTS outage_batch (
  id SERIAL PRIMARY KEY,
  submitted_by INTEGER NOT NULL,
  submitted_at TIMESTAMP NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'PARTIAL_FAILED',
  note VARCHAR(256),
  fail_device_codes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS device_outage (
  id SERIAL PRIMARY KEY,
  batch_id INTEGER,
  device_id INTEGER NOT NULL,
  start_at TIMESTAMP NOT NULL,
  end_at TIMESTAMP NOT NULL,
  reason VARCHAR(256),
  status VARCHAR(32) NOT NULL DEFAULT 'DRAFT',
  version INTEGER NOT NULL DEFAULT 1,
  confirmed_by INTEGER,
  created_at TIMESTAMP NOT NULL,
  confirmed_at TIMESTAMP,
  occupied_count INTEGER NOT NULL DEFAULT 0,
  conflict_outage_ids VARCHAR(128) NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_outage_batch ON device_outage(batch_id);
CREATE INDEX IF NOT EXISTS idx_outage_device ON device_outage(device_id);
CREATE INDEX IF NOT EXISTS idx_outage_status ON device_outage(status);

CREATE TABLE IF NOT EXISTS task_reroute (
  id SERIAL PRIMARY KEY,
  task_id INTEGER NOT NULL,
  outage_id INTEGER,
  device_id INTEGER NOT NULL,
  backup_device_id INTEGER,
  relation VARCHAR(16) NOT NULL DEFAULT 'ORIGINAL',
  note VARCHAR(256),
  UNIQUE (task_id, outage_id, device_id, relation)
);
CREATE INDEX IF NOT EXISTS idx_reroute_task ON task_reroute(task_id);
CREATE INDEX IF NOT EXISTS idx_reroute_outage ON task_reroute(outage_id);
CREATE INDEX IF NOT EXISTS idx_reroute_backup ON task_reroute(backup_device_id);

CREATE TABLE IF NOT EXISTS audit_log (
  id SERIAL PRIMARY KEY,
  actor VARCHAR(64) NOT NULL,
  action VARCHAR(128) NOT NULL,
  target_type VARCHAR(64) NOT NULL,
  target_id VARCHAR(64),
  detail VARCHAR(512),
  created_at TIMESTAMP NOT NULL
);
