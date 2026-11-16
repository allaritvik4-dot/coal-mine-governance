import React, { useState, useEffect, useMemo } from 'react';
import { Plus, CheckCircle, Edit2 } from 'lucide-react';
import DataTable, { Column } from '@/components/DataTable';
import StatusBadge from '@/components/StatusBadge';
import Modal from '@/components/Modal';
import FormField from '@/components/FormField';
import {
  listInspections,
  createInspection,
  updateInspection,
  completeInspection,
  listMines,
} from '@/services/api';
import type { Inspection, Mine } from '@/types';
import styles from './InspectionsPage.module.css';

export const InspectionsPage: React.FC = () => {
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [mines, setMines] = useState<Mine[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [filterMine, setFilterMine] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterDate, setFilterDate] = useState('');

  // Add/Edit Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingInspection, setEditingInspection] = useState<Inspection | null>(null);
  const [formData, setFormData] = useState({
    mine_id: 1,
    type: 'safety' as any,
    scheduled_date: '',
    findings: '',
    recommendations: '',
    severity: 'low' as any,
  });

  // Complete Modal
  const [isCompleteModalOpen, setIsCompleteModalOpen] = useState(false);
  const [completingInspection, setCompletingInspection] = useState<Inspection | null>(null);
  const [completeData, setCompleteData] = useState({
    findings: '',
    recommendations: '',
    severity: 'medium',
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [inspRes, minesRes] = await Promise.allSettled([
        listInspections(),
        listMines(),
      ]);
      if (inspRes.status === 'fulfilled' && inspRes.value?.data) {
        setInspections(inspRes.value.data);
      }
      if (minesRes.status === 'fulfilled' && minesRes.value?.data) {
        setMines(minesRes.value.data);
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

  const filteredInspections = useMemo(() => {
    return inspections.filter((insp) => {
      if (filterMine && String(insp.mine_id) !== filterMine) return false;
      if (filterStatus && insp.status !== filterStatus) return false;
      if (filterDate && insp.scheduled_date && !insp.scheduled_date.startsWith(filterDate))
        return false;
      return true;
    });
  }, [inspections, filterMine, filterStatus, filterDate]);

  const handleOpenAdd = () => {
    setEditingInspection(null);
    setFormData({
      mine_id: mines[0]?.id || 1,
      type: 'safety',
      scheduled_date: new Date().toISOString().split('T')[0],
      findings: '',
      recommendations: '',
      severity: 'low',
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (insp: Inspection) => {
    setEditingInspection(insp);
    setFormData({
      mine_id: insp.mine_id,
      type: insp.type,
      scheduled_date: insp.scheduled_date ? insp.scheduled_date.split('T')[0] : '',
      findings: insp.findings || '',
      recommendations: insp.recommendations || '',
      severity: insp.severity || 'low',
    });
    setIsModalOpen(true);
  };

  const handleOpenComplete = (insp: Inspection) => {
    setCompletingInspection(insp);
    setCompleteData({
      findings: insp.findings || '',
      recommendations: insp.recommendations || '',
      severity: insp.severity || 'medium',
    });
    setIsCompleteModalOpen(true);
  };

  const handleSaveInspection = async () => {
    try {
      if (editingInspection) {
        await updateInspection(editingInspection.id, formData);
      } else {
        await createInspection(formData);
      }
      setIsModalOpen(false);
      loadData();
    } catch {
      // ignore
    }
  };

  const handleCompleteSubmit = async () => {
    if (!completingInspection) return;
    try {
      await completeInspection(completingInspection.id, completeData);
      setIsCompleteModalOpen(false);
      loadData();
    } catch {
      // ignore
    }
  };

  const columns: Column<Inspection>[] = [
    {
      key: 'id',
      header: 'ID',
      width: '60px',
      render: (i) => `#${i.id}`,
    },
    {
      key: 'type',
      header: 'Type',
      render: (i) => <span style={{ textTransform: 'capitalize', fontWeight: 600 }}>{i.type}</span>,
    },
    {
      key: 'mine_name',
      header: 'Mine Site',
      render: (i) => i.mine_name || `Mine #${i.mine_id}`,
    },
    {
      key: 'scheduled_date',
      header: 'Scheduled',
      render: (i) => (i.scheduled_date ? i.scheduled_date.split('T')[0] : '—'),
    },
    {
      key: 'status',
      header: 'Status',
      render: (i) => <StatusBadge status={i.status} />,
    },
    {
      key: 'severity',
      header: 'Risk Level',
      render: (i) => <StatusBadge status={i.severity || 'low'} />,
    },
    {
      key: 'findings',
      header: 'Findings Summary',
      render: (i) => (
        <span
          style={{
            maxWidth: '220px',
            display: 'inline-block',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {i.findings || 'Pending inspection'}
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      sortable: false,
      render: (i) => (
        <div>
          <button
            type="button"
            className={styles.actionBtn}
            onClick={() => handleOpenEdit(i)}
            title="Edit"
          >
            <Edit2 size={12} />
          </button>
          {i.status !== 'completed' && (
            <button
              type="button"
              className={`${styles.actionBtn} ${styles.completeBtn}`}
              onClick={() => handleOpenComplete(i)}
              title="Record Completion"
            >
              <CheckCircle size={12} /> Complete
            </button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Safety & Regulatory Inspections</h1>
          <p className={styles.subtitle}>
            Statutory DGMS and internal mine safety compliance audits and walkthroughs
          </p>
        </div>
        <button type="button" className={styles.addBtn} onClick={handleOpenAdd}>
          <Plus size={16} />
          Schedule Inspection
        </button>
      </div>

      <div className={styles.filterBar}>
        <div className={styles.filterGroup}>
          <label>Mine:</label>
          <select
            className={styles.filterSelect}
            value={filterMine}
            onChange={(e) => setFilterMine(e.target.value)}
          >
            <option value="">All Mines</option>
            {mines.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.filterGroup}>
          <label>Status:</label>
          <select
            className={styles.filterSelect}
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="">All Statuses</option>
            <option value="scheduled">Scheduled</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>

        <div className={styles.filterGroup}>
          <label>Date:</label>
          <input
            type="date"
            className={styles.filterInput}
            value={filterDate}
            onChange={(e) => setFilterDate(e.target.value)}
          />
        </div>
      </div>

      <DataTable
        columns={columns}
        data={filteredInspections}
        pageSize={10}
        emptyMessage="No inspections match criteria."
      />

      {/* Add / Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingInspection ? `Edit Inspection #${editingInspection.id}` : 'Schedule Inspection'}
        onConfirm={handleSaveInspection}
        confirmLabel="Save Inspection"
      >
        <FormField
          label="Colliery"
          as="select"
          required
          value={formData.mine_id}
          onChange={(e) => setFormData({ ...formData, mine_id: Number(e.target.value) })}
        >
          {mines.map((m) => (
            <option key={m.id} value={m.id}>
              {m.name}
            </option>
          ))}
        </FormField>
        <FormField
          label="Inspection Type"
          as="select"
          required
          value={formData.type}
          onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
          options={[
            { value: 'routine', label: 'Routine DGMS Inspection' },
            { value: 'safety', label: 'Mine Safety & Ventilation Audit' },
            { value: 'environmental', label: 'Environmental & Dust Monitoring' },
            { value: 'equipment', label: 'Heavy Machinery & Electrical Check' },
            { value: 'special', label: 'Special Structural Investigation' },
          ]}
        />
        <FormField
          label="Scheduled Date"
          type="date"
          required
          value={formData.scheduled_date}
          onChange={(e) => setFormData({ ...formData, scheduled_date: e.target.value })}
        />
        <FormField
          label="Risk Assessment"
          as="select"
          value={formData.severity}
          onChange={(e) => setFormData({ ...formData, severity: e.target.value as any })}
          options={[
            { value: 'low', label: 'Low Risk' },
            { value: 'medium', label: 'Medium Risk' },
            { value: 'high', label: 'High Risk' },
            { value: 'critical', label: 'Critical Risk' },
          ]}
        />
        <FormField
          label="Preliminary Findings / Scope"
          as="textarea"
          value={formData.findings}
          onChange={(e) => setFormData({ ...formData, findings: e.target.value })}
        />
      </Modal>

      {/* Complete Inspection Modal */}
      <Modal
        isOpen={isCompleteModalOpen}
        onClose={() => setIsCompleteModalOpen(false)}
        title={`Sign-off Inspection #${completingInspection?.id}`}
        onConfirm={handleCompleteSubmit}
        confirmLabel="Finalize & Complete"
      >
        <FormField
          label="Observed Findings"
          as="textarea"
          required
          value={completeData.findings}
          onChange={(e) => setCompleteData({ ...completeData, findings: e.target.value })}
          helper="Detail ventilation velocity, gas readings, roof bolt torque, or observed defects."
        />
        <FormField
          label="Inspector Recommendations"
          as="textarea"
          required
          value={completeData.recommendations}
          onChange={(e) => setCompleteData({ ...completeData, recommendations: e.target.value })}
        />
        <FormField
          label="Final Severity Rating"
          as="select"
          value={completeData.severity}
          onChange={(e) => setCompleteData({ ...completeData, severity: e.target.value })}
          options={[
            { value: 'low', label: 'Low / Compliant' },
            { value: 'medium', label: 'Medium / Notice Issued' },
            { value: 'high', label: 'High / Corrective Order' },
            { value: 'critical', label: 'Critical / Immediate Halt' },
          ]}
        />
      </Modal>
    </div>
  );
};

export default InspectionsPage;
