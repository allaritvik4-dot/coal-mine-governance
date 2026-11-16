import React, { useState, useEffect, useMemo } from 'react';
import { Plus, Edit2, AlertTriangle, GraduationCap } from 'lucide-react';
import DataTable, { Column } from '@/components/DataTable';
import StatusBadge from '@/components/StatusBadge';
import Modal from '@/components/Modal';
import FormField from '@/components/FormField';
import {
  listTraining,
  createTraining,
  updateTraining,
  getExpiringTraining,
  listMines,
} from '@/services/api';
import type { TrainingRecord, Mine } from '@/types';
import styles from './TrainingPage.module.css';

export const TrainingPage: React.FC = () => {
  const [records, setRecords] = useState<TrainingRecord[]>([]);
  const [expiringList, setExpiringList] = useState<TrainingRecord[]>([]);
  const [mines, setMines] = useState<Mine[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [filterMine, setFilterMine] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  // Modals
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState<TrainingRecord | null>(null);

  const [formData, setFormData] = useState({
    mine_id: 1,
    worker_name: '',
    worker_id_number: '',
    training_type: 'vocational_refresher' as any,
    description: '',
    trainer_name: '',
    date_completed: new Date().toISOString().split('T')[0],
    valid_until: '',
    certificate_number: '',
    status: 'valid' as any,
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [trRes, expRes, minesRes] = await Promise.allSettled([
        listTraining(),
        getExpiringTraining({ days: 30 }),
        listMines(),
      ]);
      if (trRes.status === 'fulfilled' && trRes.value?.data) {
        setRecords(trRes.value.data);
      }
      if (expRes.status === 'fulfilled' && expRes.value) {
        setExpiringList(Array.isArray(expRes.value) ? expRes.value : (expRes.value as any)?.data || []);
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

  const filteredRecords = useMemo(() => {
    return records.filter((r) => {
      if (filterMine && String(r.mine_id) !== filterMine) return false;
      if (filterStatus && r.status !== filterStatus) return false;
      return true;
    });
  }, [records, filterMine, filterStatus]);

  const handleOpenAdd = () => {
    setEditingRecord(null);
    setFormData({
      mine_id: mines[0]?.id || 1,
      worker_name: '',
      worker_id_number: '',
      training_type: 'vocational_refresher',
      description: '',
      trainer_name: '',
      date_completed: new Date().toISOString().split('T')[0],
      valid_until: '',
      certificate_number: '',
      status: 'valid',
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (r: TrainingRecord) => {
    setEditingRecord(r);
    setFormData({
      mine_id: r.mine_id,
      worker_name: r.worker_name ?? '',
      worker_id_number: r.worker_id_number ?? '',
      training_type: r.training_type ?? '',
      description: r.description || '',
      trainer_name: r.trainer_name || '',
      date_completed: r.date_completed ? r.date_completed.split('T')[0] : '',
      valid_until: r.valid_until ? r.valid_until.split('T')[0] : '',
      certificate_number: r.certificate_number || '',
      status: r.status,
    });
    setIsModalOpen(true);
  };

  const handleSave = async () => {
    try {
      if (editingRecord) {
        await updateTraining(editingRecord.id, formData);
      } else {
        await createTraining(formData);
      }
      setIsModalOpen(false);
      loadData();
    } catch {
      // ignore
    }
  };

  const columns: Column<TrainingRecord>[] = [
    {
      key: 'worker_name',
      header: 'Worker Name',
      render: (r) => (
        <div>
          <span style={{ fontWeight: 600 }}>{r.worker_name}</span>
          <div style={{ fontSize: '11px', color: '#64748b' }}>Badge ID: {r.worker_id_number}</div>
        </div>
      ),
    },
    {
      key: 'training_type',
      header: 'Statutory Course',
      render: (r) => <span style={{ textTransform: 'capitalize' }}>{(r.training_type ?? '').replace(/_/g, ' ')}</span>,
    },
    {
      key: 'mine_name',
      header: 'Colliery',
      render: (r) => r.mine_name || `Mine #${r.mine_id}`,
    },
    {
      key: 'certificate_number',
      header: 'Certificate No.',
      render: (r) => r.certificate_number || 'DGMS-CERT',
    },
    {
      key: 'valid_until',
      header: 'Validity Expiry',
      render: (r) => {
        const isExp = r.valid_until && new Date(r.valid_until) < new Date();
        return (
          <span style={{ color: isExp ? '#dc2626' : 'inherit', fontWeight: isExp ? 700 : 400 }}>
            {r.valid_until ? r.valid_until.split('T')[0] : '—'}
          </span>
        );
      },
    },
    {
      key: 'status',
      header: 'Certification Status',
      render: (r) => <StatusBadge status={r.status} />,
    },
    {
      key: 'actions',
      header: 'Actions',
      sortable: false,
      render: (r) => (
        <div>
          <button
            type="button"
            className={styles.actionBtn}
            onClick={() => handleOpenEdit(r)}
            title="Edit Record"
          >
            <Edit2 size={12} />
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Mine Safety Training & Certifications</h1>
          <p className={styles.subtitle}>
            DGMS Vocational Training Rules (VTR) mandatory worker qualifications, refresher compliance and certificates
          </p>
        </div>
        <button type="button" className={styles.addBtn} onClick={handleOpenAdd}>
          <Plus size={16} />
          Add Training Record
        </button>
      </div>

      {expiringList.length > 0 && (
        <div className={styles.warningBanner}>
          <AlertTriangle size={20} />
          <div>
            <strong>Expiring Certifications Warning:</strong>{' '}
            {expiringList.length} miners have safety qualifications expiring within 30 days. Statutory retraining is required prior to underground deployment.
          </div>
        </div>
      )}

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
            <option value="valid">Valid</option>
            <option value="expiring_soon">Expiring Soon</option>
            <option value="expired">Expired</option>
          </select>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={filteredRecords}
        pageSize={10}
        emptyMessage="No training records match."
      />

      {/* Add / Edit Record Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingRecord ? `Edit Training Record #${editingRecord.id}` : 'Register Training Record'}
        onConfirm={handleSave}
        confirmLabel="Save Record"
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
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <FormField
            label="Worker Full Name"
            required
            value={formData.worker_name}
            onChange={(e) => setFormData({ ...formData, worker_name: e.target.value })}
          />
          <FormField
            label="Worker Badge / Employee ID"
            required
            value={formData.worker_id_number}
            onChange={(e) => setFormData({ ...formData, worker_id_number: e.target.value })}
          />
        </div>
        <FormField
          label="Course Type"
          as="select"
          required
          value={formData.training_type}
          onChange={(e) => setFormData({ ...formData, training_type: e.target.value as any })}
          options={[
            { value: 'vocational_refresher', label: 'VTR Annual Refresher' },
            { value: 'gas_testing', label: 'Methane & Toxic Gas Detection Certification' },
            { value: 'first_aid', label: 'St. John Ambulance First Aid & Triage' },
            { value: 'strata_control', label: 'Strata Control & Roof Support Mechanics' },
            { value: 'rescue_brigade', label: 'Mine Rescue Apparatus & Emergency Procedures' },
            { value: 'blasting_safety', label: 'Shot-firer / Blasting Safety Regulations' },
          ]}
        />
        <FormField
          label="Accredited Trainer / Institution"
          value={formData.trainer_name}
          onChange={(e) => setFormData({ ...formData, trainer_name: e.target.value })}
          placeholder="e.g. DGMS Vocational Training Institute"
        />
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <FormField
            label="Date Completed"
            type="date"
            required
            value={formData.date_completed}
            onChange={(e) => setFormData({ ...formData, date_completed: e.target.value })}
          />
          <FormField
            label="Valid Until"
            type="date"
            required
            value={formData.valid_until}
            onChange={(e) => setFormData({ ...formData, valid_until: e.target.value })}
          />
        </div>
        <FormField
          label="Certificate / Hallmarking Number"
          value={formData.certificate_number}
          onChange={(e) => setFormData({ ...formData, certificate_number: e.target.value })}
        />
        <FormField
          label="Status"
          as="select"
          value={formData.status}
          onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
          options={[
            { value: 'valid', label: 'Valid / Certified' },
            { value: 'expiring_soon', label: 'Expiring Soon (< 30 days)' },
            { value: 'expired', label: 'Expired (Renewal Overdue)' },
          ]}
        />
      </Modal>
    </div>
  );
};

export default TrainingPage;
