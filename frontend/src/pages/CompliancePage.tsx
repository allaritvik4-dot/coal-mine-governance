import React, { useState, useEffect, useMemo } from 'react';
import { Plus, Play, CheckCircle, AlertCircle, Edit2, ShieldAlert } from 'lucide-react';
import DataTable, { Column } from '@/components/DataTable';
import StatusBadge from '@/components/StatusBadge';
import Modal from '@/components/Modal';
import FormField from '@/components/FormField';
import {
  getRules,
  createRule,
  updateRule,
  getAlerts,
  acknowledgeAlert,
  resolveAlert,
  runChecks,
  createCorrectiveAction,
  listMines,
} from '@/services/api';
import type { ComplianceRule, ComplianceAlert, Mine } from '@/types';
import styles from './CompliancePage.module.css';

export const CompliancePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'alerts' | 'rules'>('alerts');
  const [rules, setRules] = useState<ComplianceRule[]>([]);
  const [alerts, setAlerts] = useState<ComplianceAlert[]>([]);
  const [mines, setMines] = useState<Mine[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters for alerts
  const [alertSeverity, setAlertSeverity] = useState('');
  const [alertStatus, setAlertStatus] = useState('');

  // Rule Modal
  const [isRuleModalOpen, setIsRuleModalOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<ComplianceRule | null>(null);
  const [ruleFormData, setRuleFormData] = useState<{
    rule_code: string;
    description: string;
    category: string;
    threshold_value: number | null;
    threshold_unit: string;
    check_frequency: string;
    severity: any;
    is_active: boolean;
  }>({
    rule_code: '',
    description: '',
    category: 'ventilation',
    threshold_value: 0.5,
    threshold_unit: '% CH4',
    check_frequency: 'daily',
    severity: 'critical' as any,
    is_active: true,
  });

  // Action / Resolve Modal
  const [isActionModalOpen, setIsActionModalOpen] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<ComplianceAlert | null>(null);
  const [actionDescription, setActionDescription] = useState('');
  const [actionPriority, setActionPriority] = useState('high');
  const [dueDate, setDueDate] = useState('');

  const [isResolveModalOpen, setIsResolveModalOpen] = useState(false);
  const [resolveNotes, setResolveNotes] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [rRes, aRes, mRes] = await Promise.allSettled([
        getRules(),
        getAlerts(),
        listMines(),
      ]);
      if (rRes.status === 'fulfilled' && rRes.value?.data) {
        setRules(rRes.value.data);
      }
      if (aRes.status === 'fulfilled' && aRes.value?.data) {
        setAlerts(aRes.value.data);
      }
      if (mRes.status === 'fulfilled' && mRes.value?.data) {
        setMines(mRes.value.data);
      }
    } catch {
      // fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredAlerts = useMemo(() => {
    return alerts.filter((a) => {
      if (alertSeverity && a.severity !== alertSeverity) return false;
      if (alertStatus && a.status !== alertStatus) return false;
      return true;
    });
  }, [alerts, alertSeverity, alertStatus]);

  const handleRunChecks = async () => {
    try {
      await runChecks();
      loadData();
    } catch {
      // ignore
    }
  };

  const handleOpenAddRule = () => {
    setEditingRule(null);
    setRuleFormData({
      rule_code: '',
      description: '',
      category: 'ventilation',
      threshold_value: 0.5,
      threshold_unit: '% CH4',
      check_frequency: 'daily',
      severity: 'critical',
      is_active: true,
    });
    setIsRuleModalOpen(true);
  };

  const handleOpenEditRule = (r: ComplianceRule) => {
    setEditingRule(r);
    setRuleFormData({
      rule_code: r.rule_code ?? '',
      description: r.description,
      category: r.category,
      threshold_value: r.threshold_value ?? null,
      threshold_unit: r.threshold_unit ?? '',
      check_frequency: r.check_frequency ?? '',
      severity: r.severity,
      is_active: Boolean(r.is_active),
    });
    setIsRuleModalOpen(true);
  };

  const handleSaveRule = async () => {
    try {
      if (editingRule) {
        await updateRule(editingRule.id, ruleFormData);
      } else {
        await createRule(ruleFormData);
      }
      setIsRuleModalOpen(false);
      loadData();
    } catch {
      // ignore
    }
  };

  const handleAcknowledge = async (id: number) => {
    try {
      await acknowledgeAlert(id);
      loadData();
    } catch {
      // ignore
    }
  };

  const handleOpenResolve = (a: ComplianceAlert) => {
    setSelectedAlert(a);
    setResolveNotes('');
    setIsResolveModalOpen(true);
  };

  const handleResolveSubmit = async () => {
    if (!selectedAlert) return;
    try {
      await resolveAlert(selectedAlert.id, resolveNotes);
      setIsResolveModalOpen(false);
      loadData();
    } catch {
      // ignore
    }
  };

  const handleOpenCreateAction = (a: ComplianceAlert) => {
    setSelectedAlert(a);
    setActionDescription(`Corrective intervention for Alert #${a.id}: ${a.message}`);
    setActionPriority(a.severity === 'critical' ? 'urgent' : 'high');
    const d = new Date();
    d.setDate(d.getDate() + 3);
    setDueDate(d.toISOString().split('T')[0]);
    setIsActionModalOpen(true);
  };

  const handleCreateActionSubmit = async () => {
    if (!selectedAlert) return;
    try {
      await createCorrectiveAction({
        alert_id: selectedAlert.id,
        mine_id: selectedAlert.mine_id,
        description: actionDescription,
        priority: actionPriority as any,
        due_date: dueDate,
        status: 'assigned',
      });
      setIsActionModalOpen(false);
      loadData();
    } catch {
      // ignore
    }
  };

  const alertColumns: Column<ComplianceAlert>[] = [
    {
      key: 'id',
      header: 'Alert ID',
      width: '70px',
      render: (a) => `#${a.id}`,
    },
    {
      key: 'rule_code',
      header: 'Rule Code',
      render: (a) => <strong>{a.rule_code || `RULE-${a.rule_id}`}</strong>,
    },
    {
      key: 'mine_name',
      header: 'Mine / Section',
      render: (a) => (
        <div>
          <div>{a.mine_name || `Mine #${a.mine_id}`}</div>
          <div style={{ fontSize: '11px', color: '#64748b' }}>{a.section_name || 'All Sections'}</div>
        </div>
      ),
    },
    {
      key: 'message',
      header: 'Statutory Violation Notice',
      render: (a) => (
        <span style={{ maxWidth: '280px', display: 'inline-block' }}>{a.message}</span>
      ),
    },
    {
      key: 'severity',
      header: 'Severity',
      render: (a) => <StatusBadge status={a.severity} />,
    },
    {
      key: 'status',
      header: 'Alert Status',
      render: (a) => <StatusBadge status={a.status} />,
    },
    {
      key: 'actions',
      header: 'Response Actions',
      sortable: false,
      render: (a) => (
        <div style={{ display: 'flex', gap: '4px' }}>
          {a.status === 'open' && (
            <button
              type="button"
              className={`${styles.actionBtn} ${styles.actionBtnWarn}`}
              onClick={() => handleAcknowledge(a.id)}
            >
              Acknowledge
            </button>
          )}
          {a.status !== 'resolved' && (
            <>
              <button
                type="button"
                className={styles.actionBtn}
                onClick={() => handleOpenCreateAction(a)}
              >
                Assign Action
              </button>
              <button
                type="button"
                className={`${styles.actionBtn} ${styles.actionBtnSuccess}`}
                onClick={() => handleOpenResolve(a)}
              >
                Resolve
              </button>
            </>
          )}
        </div>
      ),
    },
  ];

  const ruleColumns: Column<ComplianceRule>[] = [
    {
      key: 'rule_code',
      header: 'Statutory Code',
      width: '120px',
      render: (r) => <strong>{r.rule_code}</strong>,
    },
    {
      key: 'description',
      header: 'Regulatory Description',
      render: (r) => (
        <div>
          <div>{r.description}</div>
          <div style={{ fontSize: '11px', color: '#64748b' }}>
            Threshold: {r.threshold_value} {r.threshold_unit} &bull; Check: {r.check_frequency}
          </div>
        </div>
      ),
    },
    {
      key: 'category',
      header: 'Category',
      render: (r) => <span style={{ textTransform: 'capitalize' }}>{r.category}</span>,
    },
    {
      key: 'severity',
      header: 'Severity',
      render: (r) => <StatusBadge status={r.severity} />,
    },
    {
      key: 'is_active',
      header: 'Status',
      render: (r) => (
        <StatusBadge status={r.is_active ? 'active' : 'inactive'} />
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      sortable: false,
      render: (r) => (
        <button
          type="button"
          className={styles.actionBtn}
          onClick={() => handleOpenEditRule(r)}
        >
          <Edit2 size={12} /> Edit
        </button>
      ),
    },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Statutory Rules & Compliance Monitoring</h1>
          <p className={styles.subtitle}>
            DGMS safety criteria automated rule evaluations, proactive threshold alerts, and corrective action workflows
          </p>
        </div>
        <div className={styles.headerActions}>
          <button type="button" className={styles.runBtn} onClick={handleRunChecks}>
            <Play size={14} /> Run Rules Evaluation
          </button>
          {activeTab === 'rules' && (
            <button type="button" className={styles.addBtn} onClick={handleOpenAddRule}>
              <Plus size={16} /> Add Compliance Rule
            </button>
          )}
        </div>
      </div>

      <div className={styles.tabs}>
        <button
          type="button"
          className={`${styles.tab} ${activeTab === 'alerts' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('alerts')}
        >
          Compliance Alerts ({alerts.filter((a) => a.status !== 'resolved').length} Open)
        </button>
        <button
          type="button"
          className={`${styles.tab} ${activeTab === 'rules' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('rules')}
        >
          Regulatory Rules Directory ({rules.length})
        </button>
      </div>

      {activeTab === 'alerts' && (
        <>
          <div className={styles.filterBar}>
            <div className={styles.filterGroup}>
              <label>Severity:</label>
              <select
                className={styles.filterSelect}
                value={alertSeverity}
                onChange={(e) => setAlertSeverity(e.target.value)}
              >
                <option value="">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
            <div className={styles.filterGroup}>
              <label>Status:</label>
              <select
                className={styles.filterSelect}
                value={alertStatus}
                onChange={(e) => setAlertStatus(e.target.value)}
              >
                <option value="">All Statuses</option>
                <option value="open">Open</option>
                <option value="acknowledged">Acknowledged</option>
                <option value="resolved">Resolved</option>
              </select>
            </div>
          </div>

          <DataTable
            columns={alertColumns}
            data={filteredAlerts}
            pageSize={10}
            emptyMessage="No compliance alerts found."
          />
        </>
      )}

      {activeTab === 'rules' && (
        <DataTable
          columns={ruleColumns}
          data={rules}
          pageSize={10}
          emptyMessage="No rules registered."
        />
      )}

      {/* Add / Edit Rule Modal */}
      <Modal
        isOpen={isRuleModalOpen}
        onClose={() => setIsRuleModalOpen(false)}
        title={editingRule ? `Edit Rule: ${editingRule.rule_code}` : 'New Compliance Rule'}
        onConfirm={handleSaveRule}
        confirmLabel="Save Rule"
      >
        <FormField
          label="Rule Identifier / DGMS Regulation No."
          required
          value={ruleFormData.rule_code}
          onChange={(e) => setRuleFormData({ ...ruleFormData, rule_code: e.target.value })}
          placeholder="CMR-124-METHANE"
        />
        <FormField
          label="Statutory Rule Description"
          as="textarea"
          required
          value={ruleFormData.description}
          onChange={(e) => setRuleFormData({ ...ruleFormData, description: e.target.value })}
        />
        <FormField
          label="Rule Category"
          as="select"
          required
          value={ruleFormData.category}
          onChange={(e) => setRuleFormData({ ...ruleFormData, category: e.target.value })}
          options={[
            { value: 'ventilation', label: 'Mine Ventilation & Air Flow' },
            { value: 'gas_monitoring', label: 'Toxic & Inflammable Gases' },
            { value: 'roof_support', label: 'Strata & Roof Support' },
            { value: 'equipment', label: 'Machinery & Flameproof Enclosures' },
            { value: 'fire_safety', label: 'Fire & Spontaneous Heating' },
            { value: 'training', label: 'Worker Vocational Training' },
          ]}
        />
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <FormField
            label="Threshold Limit"
            type="number"
            step="0.01"
            value={ruleFormData.threshold_value ?? ''}
            onChange={(e) => setRuleFormData({ ...ruleFormData, threshold_value: Number(e.target.value) })}
          />
          <FormField
            label="Unit of Measure"
            value={ruleFormData.threshold_unit}
            onChange={(e) => setRuleFormData({ ...ruleFormData, threshold_unit: e.target.value })}
            placeholder="e.g. % CH4, m3/min, lux"
          />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <FormField
            label="Evaluation Frequency"
            as="select"
            value={ruleFormData.check_frequency}
            onChange={(e) => setRuleFormData({ ...ruleFormData, check_frequency: e.target.value })}
            options={[
              { value: 'continuous', label: 'Continuous Real-time' },
              { value: 'shift', label: 'Every Shift' },
              { value: 'daily', label: 'Daily' },
              { value: 'weekly', label: 'Weekly' },
              { value: 'monthly', label: 'Monthly' },
            ]}
          />
          <FormField
            label="Breach Severity"
            as="select"
            value={ruleFormData.severity}
            onChange={(e) => setRuleFormData({ ...ruleFormData, severity: e.target.value as any })}
            options={[
              { value: 'low', label: 'Low - Warning' },
              { value: 'medium', label: 'Medium - Corrective Notice' },
              { value: 'high', label: 'High - Immediate Hazard' },
              { value: 'critical', label: 'Critical - Stop Work Order' },
            ]}
          />
        </div>
      </Modal>

      {/* Assign Corrective Action Modal */}
      <Modal
        isOpen={isActionModalOpen}
        onClose={() => setIsActionModalOpen(false)}
        title={`Assign Corrective Action (Alert #${selectedAlert?.id})`}
        onConfirm={handleCreateActionSubmit}
        confirmLabel="Assign Action"
      >
        <FormField
          label="Action Directives & Scope"
          as="textarea"
          required
          value={actionDescription}
          onChange={(e) => setActionDescription(e.target.value)}
        />
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <FormField
            label="Priority Level"
            as="select"
            value={actionPriority}
            onChange={(e) => setActionPriority(e.target.value)}
            options={[
              { value: 'low', label: 'Low' },
              { value: 'medium', label: 'Medium' },
              { value: 'high', label: 'High' },
              { value: 'urgent', label: 'Urgent' },
            ]}
          />
          <FormField
            label="Statutory Due Date"
            type="date"
            required
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
          />
        </div>
      </Modal>

      {/* Resolve Alert Modal */}
      <Modal
        isOpen={isResolveModalOpen}
        onClose={() => setIsResolveModalOpen(false)}
        title={`Sign-off Alert #${selectedAlert?.id}`}
        onConfirm={handleResolveSubmit}
        confirmLabel="Mark Resolved"
      >
        <FormField
          label="Verification & Safe-Closure Notes"
          as="textarea"
          required
          value={resolveNotes}
          onChange={(e) => setResolveNotes(e.target.value)}
          placeholder="State the corrective measures completed and verified by the Colliery Manager or Safety Officer."
        />
      </Modal>
    </div>
  );
};

export default CompliancePage;
