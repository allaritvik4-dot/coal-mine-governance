-- Coal Mine Smart Governance & Compliance Monitoring System
-- Database Schema for SQLite

-- ============================================================
-- MINES
-- ============================================================
CREATE TABLE IF NOT EXISTS mines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('underground', 'opencast')),
    location TEXT NOT NULL,
    state TEXT NOT NULL,
    district TEXT NOT NULL,
    license_number TEXT UNIQUE NOT NULL,
    owner_company TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'suspended', 'closed')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mines_state ON mines(state);
CREATE INDEX IF NOT EXISTS idx_mines_status ON mines(status);

-- ============================================================
-- USERS
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'mine_manager', 'safety_officer', 'inspector', 'viewer')),
    email TEXT UNIQUE NOT NULL,
    mine_id INTEGER,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (mine_id) REFERENCES mines(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_mine_id ON users(mine_id);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- ============================================================
-- SECTIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mine_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    depth_meters REAL,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'closed')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mine_id) REFERENCES mines(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sections_mine_id ON sections(mine_id);
CREATE INDEX IF NOT EXISTS idx_sections_status ON sections(status);

-- ============================================================
-- INSPECTIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mine_id INTEGER NOT NULL,
    section_id INTEGER,
    inspector_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    scheduled_date TEXT NOT NULL,
    completed_date TEXT,
    status TEXT NOT NULL DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'in_progress', 'completed', 'overdue', 'cancelled')),
    findings TEXT,
    risk_level TEXT CHECK(risk_level IN ('low', 'medium', 'high', 'critical')),
    evidence_attached INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (mine_id) REFERENCES mines(id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE SET NULL,
    FOREIGN KEY (inspector_id) REFERENCES users(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_inspections_mine_id ON inspections(mine_id);
CREATE INDEX IF NOT EXISTS idx_inspections_inspector_id ON inspections(inspector_id);
CREATE INDEX IF NOT EXISTS idx_inspections_status ON inspections(status);
CREATE INDEX IF NOT EXISTS idx_inspections_scheduled_date ON inspections(scheduled_date);

-- ============================================================
-- HAZARDS
-- ============================================================
CREATE TABLE IF NOT EXISTS hazards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mine_id INTEGER NOT NULL,
    section_id INTEGER,
    reported_by INTEGER NOT NULL,
    hazard_type TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('low', 'medium', 'high', 'critical')),
    location_detail TEXT,
    status TEXT NOT NULL DEFAULT 'reported' CHECK(status IN ('reported', 'under_review', 'mitigated', 'closed')),
    reported_date TEXT NOT NULL,
    resolved_date TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mine_id) REFERENCES mines(id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE SET NULL,
    FOREIGN KEY (reported_by) REFERENCES users(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_hazards_mine_id ON hazards(mine_id);
CREATE INDEX IF NOT EXISTS idx_hazards_severity ON hazards(severity);
CREATE INDEX IF NOT EXISTS idx_hazards_status ON hazards(status);

-- ============================================================
-- INCIDENTS
-- ============================================================
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mine_id INTEGER NOT NULL,
    section_id INTEGER,
    reported_by INTEGER NOT NULL,
    incident_type TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('low', 'medium', 'high', 'critical')),
    casualties INTEGER NOT NULL DEFAULT 0,
    injuries INTEGER NOT NULL DEFAULT 0,
    date_occurred TEXT NOT NULL,
    date_reported TEXT NOT NULL,
    root_cause TEXT,
    status TEXT NOT NULL DEFAULT 'reported' CHECK(status IN ('reported', 'investigating', 'resolved', 'closed')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mine_id) REFERENCES mines(id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE SET NULL,
    FOREIGN KEY (reported_by) REFERENCES users(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_incidents_mine_id ON incidents(mine_id);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_date_occurred ON incidents(date_occurred);

-- ============================================================
-- EQUIPMENT
-- ============================================================
CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mine_id INTEGER NOT NULL,
    section_id INTEGER,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    serial_number TEXT UNIQUE NOT NULL,
    manufacturer TEXT,
    installation_date TEXT,
    last_maintenance_date TEXT,
    next_maintenance_due TEXT,
    status TEXT NOT NULL DEFAULT 'operational' CHECK(status IN ('operational', 'needs_maintenance', 'under_repair', 'decommissioned')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mine_id) REFERENCES mines(id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_equipment_mine_id ON equipment(mine_id);
CREATE INDEX IF NOT EXISTS idx_equipment_status ON equipment(status);
CREATE INDEX IF NOT EXISTS idx_equipment_next_maintenance_due ON equipment(next_maintenance_due);

-- ============================================================
-- MAINTENANCE ACTIVITIES
-- ============================================================
CREATE TABLE IF NOT EXISTS maintenance_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL,
    performed_by INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('preventive', 'corrective', 'emergency')),
    description TEXT NOT NULL,
    date_performed TEXT NOT NULL,
    next_due_date TEXT,
    cost REAL,
    parts_replaced TEXT,
    status TEXT NOT NULL DEFAULT 'completed' CHECK(status IN ('scheduled', 'in_progress', 'completed', 'cancelled')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE,
    FOREIGN KEY (performed_by) REFERENCES users(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_maintenance_equipment_id ON maintenance_activities(equipment_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_date_performed ON maintenance_activities(date_performed);

-- ============================================================
-- TRAINING RECORDS
-- ============================================================
CREATE TABLE IF NOT EXISTS training_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mine_id INTEGER NOT NULL,
    worker_name TEXT NOT NULL,
    worker_id_number TEXT NOT NULL,
    training_type TEXT NOT NULL,
    description TEXT NOT NULL,
    trainer_name TEXT NOT NULL,
    date_completed TEXT NOT NULL,
    valid_until TEXT,
    certificate_number TEXT,
    status TEXT NOT NULL DEFAULT 'valid' CHECK(status IN ('valid', 'expiring_soon', 'expired')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mine_id) REFERENCES mines(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_training_mine_id ON training_records(mine_id);
CREATE INDEX IF NOT EXISTS idx_training_status ON training_records(status);
CREATE INDEX IF NOT EXISTS idx_training_valid_until ON training_records(valid_until);

-- ============================================================
-- COMPLIANCE RULES
-- ============================================================
CREATE TABLE IF NOT EXISTS compliance_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_code TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    threshold_value REAL,
    threshold_unit TEXT,
    check_frequency TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('low', 'medium', 'high', 'critical')),
    is_active INTEGER NOT NULL DEFAULT 1,
    created_by INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_compliance_rules_category ON compliance_rules(category);
CREATE INDEX IF NOT EXISTS idx_compliance_rules_is_active ON compliance_rules(is_active);

-- ============================================================
-- COMPLIANCE ALERTS
-- ============================================================
CREATE TABLE IF NOT EXISTS compliance_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER NOT NULL,
    mine_id INTEGER NOT NULL,
    section_id INTEGER,
    triggered_by_record_type TEXT NOT NULL,
    triggered_by_record_id INTEGER,
    message TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('low', 'medium', 'high', 'critical')),
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'acknowledged', 'resolved', 'escalated')),
    assigned_to INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TEXT,
    resolved_by INTEGER,
    FOREIGN KEY (rule_id) REFERENCES compliance_rules(id) ON DELETE CASCADE,
    FOREIGN KEY (mine_id) REFERENCES mines(id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_alerts_rule_id ON compliance_alerts(rule_id);
CREATE INDEX IF NOT EXISTS idx_alerts_mine_id ON compliance_alerts(mine_id);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON compliance_alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON compliance_alerts(severity);

-- ============================================================
-- CORRECTIVE ACTIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS corrective_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id INTEGER NOT NULL,
    mine_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    assigned_to INTEGER,
    assigned_by INTEGER,
    priority TEXT NOT NULL DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high', 'urgent')),
    status TEXT NOT NULL DEFAULT 'assigned' CHECK(status IN ('assigned', 'in_progress', 'completed', 'overdue', 'cancelled')),
    due_date TEXT,
    completed_date TEXT,
    evidence_notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (alert_id) REFERENCES compliance_alerts(id) ON DELETE CASCADE,
    FOREIGN KEY (mine_id) REFERENCES mines(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_corrective_alert_id ON corrective_actions(alert_id);
CREATE INDEX IF NOT EXISTS idx_corrective_mine_id ON corrective_actions(mine_id);
CREATE INDEX IF NOT EXISTS idx_corrective_status ON corrective_actions(status);
CREATE INDEX IF NOT EXISTS idx_corrective_due_date ON corrective_actions(due_date);

-- ============================================================
-- AUDIT LOG
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    old_values TEXT,
    new_values TEXT,
    ip_address TEXT,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_entity_type ON audit_log(entity_type);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);

-- ============================================================
-- KNOWLEDGE DOCUMENTS
-- ============================================================
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    source TEXT,
    document_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    revision_date TEXT,
    version TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    ingested_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_knowledge_docs_type ON knowledge_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_docs_active ON knowledge_documents(is_active);
