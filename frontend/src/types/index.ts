export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'inspector' | 'manager' | 'safety_officer' | 'mine_manager' | 'operator' | 'viewer';
  is_active: boolean | number;
  mine_id?: number | null;
  created_at?: string;
  updated_at?: string | null;
}

export interface Mine {
  id: number;
  name: string;
  location: string;
  type: string;
  status: string;
  state?: string;
  district?: string;
  owner_company?: string;
  capacity_tonnes_per_day?: number;
  total_workers?: number;
  license_number: string;
  license_expiry?: string;
  emergency_contact?: string;
  manager_id?: number;
  manager_name?: string;
  sections?: Section[];
  section_count?: number;
  active_hazards_count?: number;
  active_alerts_count?: number;
  created_at?: string;
  updated_at?: string;
}

export interface Section {
  id: number;
  mine_id: number;
  name: string;
  type: string;
  depth_meters?: number | null;
  status: string;
  max_workers?: number;
  created_at?: string;
  updated_at?: string;
}

export interface Inspection {
  id: number;
  mine_id: number;
  mine_name?: string;
  section_id?: number | null;
  section_name?: string;
  inspector_id?: number;
  inspector_name?: string;
  type: string;
  status: string;
  scheduled_date: string;
  completed_date?: string | null;
  findings?: string | null;
  recommendations?: string | null;
  severity?: string | null;
  risk_level?: string | null;
  evidence_attached?: boolean | number;
  follow_up_required?: boolean;
  follow_up_date?: string | null;
  created_at?: string;
  updated_at?: string | null;
}

export interface Hazard {
  id: number;
  mine_id: number;
  mine_name?: string;
  section_id?: number | null;
  section_name?: string;
  reported_by?: number;
  reporter_name?: string;
  hazard_type?: string;
  type?: string;
  severity: string;
  status: string;
  title?: string;
  description: string;
  location_detail?: string;
  location_description?: string;
  mitigation_measures?: string;
  reported_date?: string;
  resolved_date?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface Incident {
  id: number;
  mine_id: number;
  mine_name?: string;
  section_id?: number | null;
  section_name?: string;
  reported_by?: number;
  reporter_name?: string;
  incident_type?: string;
  type?: string;
  severity: string;
  status: string;
  title?: string;
  description: string;
  location_detail?: string;
  location_description?: string;
  date_occurred: string;
  date_reported?: string;
  casualties?: number;
  injuries?: number;
  injuries_count?: number;
  fatalities_count?: number;
  root_cause?: string | null;
  corrective_actions?: string;
  investigation_notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Equipment {
  id: number;
  mine_id: number;
  mine_name?: string;
  section_id?: number | null;
  section_name?: string;
  name: string;
  type: string;
  model?: string;
  serial_number: string;
  manufacturer?: string;
  status: string;
  purchase_date?: string;
  installation_date?: string | null;
  last_maintenance_date?: string | null;
  next_maintenance_date?: string | null;
  next_maintenance_due?: string | null;
  maintenance_interval_days?: number;
  created_at?: string;
  updated_at?: string;
}

export interface MaintenanceActivity {
  id: number;
  equipment_id: number;
  equipment_name?: string;
  performed_by: number;
  performer_name?: string;
  type: string;
  status: string;
  description: string;
  scheduled_date?: string;
  date_performed?: string;
  completed_date?: string | null;
  next_due_date?: string | null;
  cost?: number | null;
  parts_replaced?: string | null;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface TrainingRecord {
  id: number;
  mine_id: number;
  mine_name?: string;
  user_id?: number;
  user_name?: string;
  worker_name?: string;
  worker_id_number?: string;
  training_type?: string;
  course_name?: string;
  type?: string;
  status: string;
  trainer_name?: string;
  instructor?: string;
  description?: string;
  scheduled_date?: string;
  date_completed?: string;
  completed_date?: string | null;
  valid_until?: string | null;
  expiry_date?: string | null;
  score?: number | null;
  passing_score?: number;
  certificate_number?: string | null;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ComplianceRule {
  id: number;
  rule_code?: string;
  code?: string;
  title?: string;
  description: string;
  category: string;
  threshold_value?: number | null;
  threshold_unit?: string | null;
  check_frequency?: string;
  check_frequency_days?: number;
  severity: string;
  is_active: boolean | number;
  created_by?: number;
  created_by_name?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ComplianceAlert {
  id: number;
  rule_id: number;
  rule_code?: string;
  rule_title?: string;
  mine_id: number;
  mine_name?: string;
  section_id?: number | null;
  section_name?: string;
  triggered_by_record_type?: string;
  triggered_by_record_id?: number;
  status: string;
  severity: string;
  message: string;
  details?: string;
  assigned_to?: number | null;
  assigned_to_name?: string;
  acknowledged_by?: number | null;
  resolved_by?: number | null;
  acknowledged_at?: string | null;
  resolved_at?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface CorrectiveAction {
  id: number;
  alert_id: number;
  mine_id?: number;
  mine_name?: string;
  assigned_to?: number | null;
  assignee_name?: string;
  assigned_by?: number | null;
  title?: string;
  description: string;
  priority: string;
  status: string;
  due_date?: string | null;
  completed_date?: string | null;
  evidence_notes?: string | null;
  notes?: string;
  created_at?: string;
  updated_at?: string | null;
}

export interface AuditLogEntry {
  id: number;
  user_id?: number | null;
  username?: string;
  user_name?: string;
  full_name?: string;
  role?: string;
  action: string;
  entity_type?: string;
  entity_id?: number | null;
  resource_type?: string;
  resource_id?: number;
  old_values?: any;
  new_values?: any;
  details?: string;
  ip_address?: string | null;
  timestamp?: string;
  created_at?: string;
}

export interface KnowledgeDocument {
  id: number;
  title: string;
  content?: string;
  category?: string;
  source?: string;
  document_type?: string;
  file_path?: string;
  revision_date?: string | null;
  version?: string;
  is_active?: boolean | number;
  uploaded_by?: number;
  uploader_name?: string;
  ingested_at?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AssistantMessage {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: any[];
  created_at?: string;
}

export interface DashboardStats {
  total_mines: number;
  active_mines: number;
  total_workers: number;
  open_hazards: number;
  open_alerts: number;
  overdue_inspections: number;
  active_hazards: number;
  pending_actions: number;
  expiring_training: number;
  pending_inspections: number;
  active_incidents: number;
  compliance_rate: number;
  equipment_operational_rate: number;
  recent_alerts: ComplianceAlert[];
  upcoming_inspections: Inspection[];
  compliance_by_category: {
    category: string;
    compliant: number;
    non_compliant: number;
    total: number;
  }[];
}

export interface ApiResponse<T> {
  data: T;
  message: string;
  total?: number;
  page?: number;
  per_page?: number;
}
