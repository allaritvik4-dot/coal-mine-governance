import axios from 'axios';
import type {
  User,
  Mine,
  Section,
  Inspection,
  Hazard,
  Incident,
  Equipment,
  MaintenanceActivity,
  TrainingRecord,
  ComplianceRule,
  ComplianceAlert,
  CorrectiveAction,
  AuditLogEntry,
  KnowledgeDocument,
  AssistantMessage,
  DashboardStats,
  ApiResponse,
} from '@/types';

const api = axios.create({
  baseURL: '/api',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ── Auth ──────────────────────────────────────────────────────────────

export const authApi = {
  login: (username: string, password: string) =>
    api.post<ApiResponse<{ token: string; user: User }>>('/auth/login', { username, password }),

  register: (data: { username: string; email: string; password: string; full_name: string; role?: string }) =>
    api.post<ApiResponse<User>>('/auth/register', data),

  getMe: () =>
    api.get<ApiResponse<User>>('/auth/me'),

  changePassword: (data: { current_password: string; new_password: string }) =>
    api.put<ApiResponse<null>>('/auth/change-password', data),
};

// ── Mines ─────────────────────────────────────────────────────────────

export const minesApi = {
  list: (params?: Record<string, string | number>) =>
    api.get<ApiResponse<Mine[]>>('/mines', { params }),

  get: (id: number) =>
    api.get<ApiResponse<Mine>>(`/mines/${id}`),

  create: (data: Partial<Mine>) =>
    api.post<ApiResponse<Mine>>('/mines', data),

  update: (id: number, data: Partial<Mine>) =>
    api.put<ApiResponse<Mine>>(`/mines/${id}`, data),

  getDashboard: () =>
    api.get<ApiResponse<DashboardStats>>('/mines/dashboard'),
};

// ── Inspections ───────────────────────────────────────────────────────

export const inspectionsApi = {
  list: (params?: Record<string, string | number>) =>
    api.get<ApiResponse<Inspection[]>>('/inspections', { params }),

  get: (id: number) =>
    api.get<ApiResponse<Inspection>>(`/inspections/${id}`),

  create: (data: Partial<Inspection>) =>
    api.post<ApiResponse<Inspection>>('/inspections', data),

  update: (id: number, data: Partial<Inspection>) =>
    api.put<ApiResponse<Inspection>>(`/inspections/${id}`, data),

  complete: (id: number, data: { findings: string; recommendations: string; severity: string }) =>
    api.put<ApiResponse<Inspection>>(`/inspections/${id}/complete`, data),
};

// ── Hazards ───────────────────────────────────────────────────────────

export const hazardsApi = {
  list: (params?: Record<string, string | number>) =>
    api.get<ApiResponse<Hazard[]>>('/hazards', { params }),

  get: (id: number) =>
    api.get<ApiResponse<Hazard>>(`/hazards/${id}`),

  create: (data: Partial<Hazard>) =>
    api.post<ApiResponse<Hazard>>('/hazards', data),

  update: (id: number, data: Partial<Hazard>) =>
    api.put<ApiResponse<Hazard>>(`/hazards/${id}`, data),

  updateStatus: (id: number, status: string, mitigation_measures?: string) =>
    api.put<ApiResponse<Hazard>>(`/hazards/${id}/status`, { status, mitigation_measures }),
};

// ── Incidents ─────────────────────────────────────────────────────────

export const incidentsApi = {
  list: (params?: Record<string, string | number>) =>
    api.get<ApiResponse<Incident[]>>('/incidents', { params }),

  get: (id: number) =>
    api.get<ApiResponse<Incident>>(`/incidents/${id}`),

  create: (data: Partial<Incident>) =>
    api.post<ApiResponse<Incident>>('/incidents', data),

  update: (id: number, data: Partial<Incident>) =>
    api.put<ApiResponse<Incident>>(`/incidents/${id}`, data),
};

// ── Equipment ─────────────────────────────────────────────────────────

export const equipmentApi = {
  list: (params?: Record<string, string | number>) =>
    api.get<ApiResponse<Equipment[]>>('/equipment', { params }),

  get: (id: number) =>
    api.get<ApiResponse<Equipment>>(`/equipment/${id}`),

  create: (data: Partial<Equipment>) =>
    api.post<ApiResponse<Equipment>>('/equipment', data),

  update: (id: number, data: Partial<Equipment>) =>
    api.put<ApiResponse<Equipment>>(`/equipment/${id}`, data),

  getMaintenanceDue: (params?: Record<string, string | number>) =>
    api.get<ApiResponse<Equipment[]>>('/equipment/maintenance-due', { params }),
};

// ── Maintenance ───────────────────────────────────────────────────────

export const maintenanceApi = {
  list: (params?: Record<string, string | number>) =>
    api.get<ApiResponse<MaintenanceActivity[]>>('/maintenance', { params }),

  create: (data: Partial<MaintenanceActivity>) =>
    api.post<ApiResponse<MaintenanceActivity>>('/maintenance', data),

  update: (id: number, data: Partial<MaintenanceActivity>) =>
    api.put<ApiResponse<MaintenanceActivity>>(`/maintenance/${id}`, data),
};

// ── Training ──────────────────────────────────────────────────────────

export const trainingApi = {
  list: (params?: Record<string, string | number>) =>
    api.get<ApiResponse<TrainingRecord[]>>('/training', { params }),

  get: (id: number) =>
    api.get<ApiResponse<TrainingRecord>>(`/training/${id}`),

  create: (data: Partial<TrainingRecord>) =>
    api.post<ApiResponse<TrainingRecord>>('/training', data),

  update: (id: number, data: Partial<TrainingRecord>) =>
    api.put<ApiResponse<TrainingRecord>>(`/training/${id}`, data),

  getExpiring: (params?: Record<string, string | number>) =>
    api.get<ApiResponse<TrainingRecord[]>>('/training/expiring', { params }),
};

// ── Compliance ────────────────────────────────────────────────────────

export const complianceApi = {
  getRules: (params?: Record<string, string | number>) =>
    api.get<ApiResponse<ComplianceRule[]>>('/compliance/rules', { params }),

  createRule: (data: Partial<ComplianceRule>) =>
    api.post<ApiResponse<ComplianceRule>>('/compliance/rules', data),

  updateRule: (id: number, data: Partial<ComplianceRule>) =>
    api.put<ApiResponse<ComplianceRule>>(`/compliance/rules/${id}`, data),

  getAlerts: (params?: Record<string, string | number>) =>
    api.get<ApiResponse<ComplianceAlert[]>>('/compliance/alerts', { params }),

  acknowledgeAlert: (id: number) =>
    api.put<ApiResponse<ComplianceAlert>>(`/compliance/alerts/${id}/acknowledge`),

  resolveAlert: (id: number, notes?: string) =>
    api.put<ApiResponse<ComplianceAlert>>(`/compliance/alerts/${id}/resolve`, { notes }),

  runChecks: (mine_id?: number) =>
    api.post<ApiResponse<ComplianceAlert[]>>('/compliance/run-checks', { mine_id }),

  getCorrectiveActions: (params?: Record<string, string | number>) =>
    api.get<ApiResponse<CorrectiveAction[]>>('/compliance/corrective-actions', { params }),

  createCorrectiveAction: (data: Partial<CorrectiveAction>) =>
    api.post<ApiResponse<CorrectiveAction>>('/compliance/corrective-actions', data),

  updateCorrectiveAction: (id: number, data: Partial<CorrectiveAction>) =>
    api.put<ApiResponse<CorrectiveAction>>(`/compliance/corrective-actions/${id}`, data),
};

// ── Assistant ─────────────────────────────────────────────────────────

export const assistantApi = {
  ask: (question: string, conversation_id?: string) =>
    api.post<ApiResponse<AssistantMessage>>('/assistant/ask', { question, conversation_id }),

  getDocuments: (params?: Record<string, string | number>) =>
    api.get<ApiResponse<KnowledgeDocument[]>>('/assistant/documents', { params }),

  ingestDocument: (data: { title: string; content: string; category: string; source: string }) =>
    api.post<ApiResponse<KnowledgeDocument>>('/assistant/documents', data),
};

// ── Reports ───────────────────────────────────────────────────────────

export const reportsApi = {
  getSummary: (params?: Record<string, string | number>) =>
    api.get<ApiResponse<Record<string, unknown>>>('/reports/summary', { params }),

  getComplianceReport: (params?: Record<string, string | number>) =>
    api.get<ApiResponse<Record<string, unknown>>>('/reports/compliance', { params }),

  getIncidentReport: (params?: Record<string, string | number>) =>
    api.get<ApiResponse<Record<string, unknown>>>('/reports/incidents', { params }),

  getAuditLog: (params?: Record<string, string | number>) =>
    api.get<ApiResponse<AuditLogEntry[]>>('/reports/audit-log', { params }),
};

// ── Direct Function Exports ──────────────────────────────────────────

export const login = async (username: string, password: string) => (await authApi.login(username, password)).data.data;
export const register = async (data: any) => (await authApi.register(data)).data.data;
export const getMe = async () => (await authApi.getMe()).data.data;
export const changePassword = async (data: any) => (await authApi.changePassword(data)).data.data;

export const listMines = async (params?: any) => (await minesApi.list(params)).data;
export const getMine = async (id: number) => (await minesApi.get(id)).data.data;
export const createMine = async (data: any) => (await minesApi.create(data)).data.data;
export const updateMine = async (id: number, data: any) => (await minesApi.update(id, data)).data.data;
export const getMineDashboard = async (id?: number) => (await minesApi.getDashboard()).data.data;

export const listInspections = async (params?: any) => (await inspectionsApi.list(params)).data;
export const getInspection = async (id: number) => (await inspectionsApi.get(id)).data.data;
export const createInspection = async (data: any) => (await inspectionsApi.create(data)).data.data;
export const updateInspection = async (id: number, data: any) => (await inspectionsApi.update(id, data)).data.data;
export const completeInspection = async (id: number, data: any) => (await inspectionsApi.complete(id, data)).data.data;

export const listHazards = async (params?: any) => (await hazardsApi.list(params)).data;
export const getHazard = async (id: number) => (await hazardsApi.get(id)).data.data;
export const createHazard = async (data: any) => (await hazardsApi.create(data)).data.data;
export const updateHazard = async (id: number, data: any) => (await hazardsApi.update(id, data)).data.data;
export const updateHazardStatus = async (id: number, status: string, notes?: string) => (await hazardsApi.updateStatus(id, status, notes)).data.data;

export const listIncidents = async (params?: any) => (await incidentsApi.list(params)).data;
export const getIncident = async (id: number) => (await incidentsApi.get(id)).data.data;
export const createIncident = async (data: any) => (await incidentsApi.create(data)).data.data;
export const updateIncident = async (id: number, data: any) => (await incidentsApi.update(id, data)).data.data;

export const listEquipment = async (params?: any) => (await equipmentApi.list(params)).data;
export const getEquipment = async (id: number) => (await equipmentApi.get(id)).data.data;
export const createEquipment = async (data: any) => (await equipmentApi.create(data)).data.data;
export const updateEquipment = async (id: number, data: any) => (await equipmentApi.update(id, data)).data.data;
export const getMaintenanceDue = async (params?: any) => (await equipmentApi.getMaintenanceDue(params)).data.data;

export const listMaintenance = async (params?: any) => (await maintenanceApi.list(params)).data;
export const createMaintenance = async (data: any) => (await maintenanceApi.create(data)).data.data;
export const updateMaintenance = async (id: number, data: any) => (await maintenanceApi.update(id, data)).data.data;

export const listTraining = async (params?: any) => (await trainingApi.list(params)).data;
export const getTraining = async (id: number) => (await trainingApi.get(id)).data.data;
export const createTraining = async (data: any) => (await trainingApi.create(data)).data.data;
export const updateTraining = async (id: number, data: any) => (await trainingApi.update(id, data)).data.data;
export const getExpiringTraining = async (params?: any) => (await trainingApi.getExpiring(params)).data.data;

export const getRules = async (params?: any) => (await complianceApi.getRules(params)).data;
export const createRule = async (data: any) => (await complianceApi.createRule(data)).data.data;
export const updateRule = async (id: number, data: any) => (await complianceApi.updateRule(id, data)).data.data;
export const getAlerts = async (params?: any) => (await complianceApi.getAlerts(params)).data;
export const acknowledgeAlert = async (id: number) => (await complianceApi.acknowledgeAlert(id)).data.data;
export const resolveAlert = async (id: number, notes?: string) => (await complianceApi.resolveAlert(id, notes)).data.data;
export const runChecks = async (mine_id?: number) => (await complianceApi.runChecks(mine_id)).data.data;
export const getCorrectiveActions = async (params?: any) => (await complianceApi.getCorrectiveActions(params)).data;
export const createCorrectiveAction = async (data: any) => (await complianceApi.createCorrectiveAction(data)).data.data;
export const updateCorrectiveAction = async (id: number, data: any) => (await complianceApi.updateCorrectiveAction(id, data)).data.data;

export const askAssistant = async (question: string, conversation_id?: string) => (await assistantApi.ask(question, conversation_id)).data.data;
export const getDocuments = async (params?: any) => (await assistantApi.getDocuments(params)).data;
export const ingestDocument = async (data: any) => (await assistantApi.ingestDocument(data)).data.data;

export const getSummaryReport = async (params?: any) => (await reportsApi.getSummary(params)).data.data;
export const getComplianceReport = async (params?: any) => (await reportsApi.getComplianceReport(params)).data.data;
export const getIncidentReport = async (params?: any) => (await reportsApi.getIncidentReport(params)).data.data;
export const getAuditLog = async (params?: any) => (await reportsApi.getAuditLog(params)).data;

// ── ML Safety Risk Model ─────────────────────────────────────────────
export const mlApi = {
  getModelInfo: () => api.get<ApiResponse<any>>('/ml/model-info'),
  predict: (description: string) => api.post<ApiResponse<any>>('/ml/predict', { description }),
  retrain: () => api.post<ApiResponse<any>>('/ml/retrain'),
};

export const getModelInfo = async () => (await mlApi.getModelInfo()).data.data;
export const predictHazardRisk = async (description: string) => (await mlApi.predict(description)).data.data;
export const retrainModel = async () => (await mlApi.retrain()).data.data;

export default api;
