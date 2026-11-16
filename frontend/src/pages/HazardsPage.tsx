import React, { useState, useEffect, useMemo } from 'react';
import { Plus, Edit2, ShieldAlert, CheckCircle } from 'lucide-react';
import DataTable, { Column } from '@/components/DataTable';
import StatusBadge from '@/components/StatusBadge';
import Modal from '@/components/Modal';
import FormField from '@/components/FormField';
import {
  listHazards,
  createHazard,
  updateHazard,
  updateHazardStatus,
  listMines,
} from '@/services/api';
import type { Hazard, Mine } from '@/types';
import styles from './HazardsPage.module.css';

export const HazardsPage: React.FC = () => {
  const [hazards, setHazards] = useState<Hazard[]>([]);
  const [mines, setMines] = useState<Mine[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [filterMine, setFilterMine] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  // Add / Edit Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingHazard, setEditingHazard] = useState<Hazard | null>(null);
  const [formData, setFormData] = useState({
    mine_id: 1,
    title: '',
    type: 'gas' as any,
    severity: 'medium' as any,
    status: 'reported' as any,
    description: '',
    location_description: '',
    mitigation_measures: '',
  });

  // Status Modal
  const [isStatusModalOpen, setIsStatusModalOpen] = useState(false);
  const [selectedHazard, setSelectedHazard] = useState<Hazard | null>(null);
  const [newStatus, setNewStatus] = useState('mitigating');
  const [mitigationNotes, setMitigationNotes] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [hazRes, minesRes] = await Promise.allSettled([
        listHazards(),
        listMines(),
      ]);
      if (hazRes.status === 'fulfilled' && hazRes.value?.data) {
        setHazards(hazRes.value.data);
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

  const filteredHazards = useMemo(() => {
    return hazards.filter((h) => {
      if (filterMine && String(h.mine_id) !== filterMine) return false;
      if (filterSeverity && h.severity !== filterSeverity) return false;
      if (filterStatus && h.status !== filterStatus) return false;
      return true;
    });
  }, [hazards, filterMine, filterSeverity, filterStatus]);

  const handleOpenAdd = () => {
    setEditingHazard(null);
    setFormData({
      mine_id: mines[0]?.id || 1,
      title: '',
      type: 'gas',
      severity: 'medium',
      status: 'reported',
      description: '',
      location_description: '',
      mitigation_measures: '',
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (h: Hazard) => {
    setEditingHazard(h);
    setFormData({
      mine_id: h.mine_id,
      title: h.title ?? '',
      type: h.type ?? h.hazard_type ?? '',
      severity: h.severity,
      status: h.status,
      description: h.description,
      location_description: h.location_description ?? '',
      mitigation_measures: h.mitigation_measures || '',
    });
    setIsModalOpen(true);
  };

  const handleOpenStatusModal = (h: Hazard) => {
    setSelectedHazard(h);
    setNewStatus(h.status === 'reported' ? 'mitigating' : 'resolved');
    setMitigationNotes(h.mitigation_measures || '');
    setIsStatusModalOpen(true);
  };

  const handleSaveHazard = async () => {
    try {
      if (editingHazard) {
        await updateHazard(editingHazard.id, formData);
      } else {
        await createHazard(formData);
      }
      setIsModalOpen(false);
      loadData();
    } catch {
      // ignore
    }
  };

  const handleStatusSubmit = async () => {
    if (!selectedHazard) return;
    try {
      await updateHazardStatus(selectedHazard.id, newStatus, mitigationNotes);
      setIsStatusModalOpen(false);
      loadData();
    } catch {
      // ignore
    }
  };

  const columns: Column<Hazard>[] = [
    {
      key: 'id',
      header: 'ID',
      width: '60px',
      render: (h) => `#${h.id}`,
    },
    {
      key: 'title',
      header: 'Hazard Title',
      render: (h) => (
        <div>
          <span style={{ fontWeight: 600 }}>{h.title}</span>
          <div style={{ fontSize: '11px', color: '#64748b' }}>{h.location_description}</div>
        </div>
      ),
    },
    {
      key: 'type',
      header: 'Category',
      render: (h) => <span style={{ textTransform: 'capitalize' }}>{h.type}</span>,
    },
    {
      key: 'mine_name',
      header: 'Colliery',
      render: (h) => h.mine_name || `Mine #${h.mine_id}`,
    },
    {
      key: 'severity',
      header: 'Severity',
      render: (h) => <StatusBadge status={h.severity} />,
    },
    {
      key: 'status',
      header: 'Status',
      render: (h) => <StatusBadge status={h.status} />,
    },
    {
      key: 'actions',
      header: 'Actions',
      sortable: false,
      render: (h) => (
        <div>
          <button
            type="button"
            className={styles.actionBtn}
            onClick={() => handleOpenEdit(h)}
            title="Edit"
          >
            <Edit2 size={12} />
          </button>
          <button
            type="button"
            className={`${styles.actionBtn} ${h.status === 'resolved' ? '' : styles.resolveBtn}`}
            onClick={() => handleOpenStatusModal(h)}
            title="Change Status"
          >
            {h.status === 'resolved' ? <CheckCircle size={12} /> : <ShieldAlert size={12} />} Update
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Underground & Surface Hazards</h1>
          <p className={styles.subtitle}>
            Proactive tracking of methane buildup, roof spalling, water seepage, and electrical risks
          </p>
        </div>
        <button type="button" className={styles.addBtn} onClick={handleOpenAdd}>
          <Plus size={16} />
          Report Hazard
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
          <label>Severity:</label>
          <select
            className={styles.filterSelect}
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
          >
            <option value="">All Severities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
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
            <option value="reported">Reported</option>
            <option value="assessed">Assessed</option>
            <option value="mitigating">Mitigating</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={filteredHazards}
        pageSize={10}
        emptyMessage="No hazards found matching current filters."
      />

      {/* Add / Edit Hazard Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingHazard ? `Edit Hazard #${editingHazard.id}` : 'Report Mine Hazard'}
        onConfirm={handleSaveHazard}
        confirmLabel="Save Hazard"
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
          label="Hazard Short Description"
          required
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          placeholder="e.g. Elevated Methane Level at Face 3B"
        />
        <FormField
          label="Hazard Classification"
          as="select"
          required
          value={formData.type}
          onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
          options={[
            { value: 'gas', label: 'Inflammable/Toxic Gas (CH4, CO)' },
            { value: 'structural', label: 'Roof/Side Strata Instability' },
            { value: 'water', label: 'Inundation / Water Inrush' },
            { value: 'electrical', label: 'Flameproof Electrical Defect' },
            { value: 'mechanical', label: 'Conveyor / Haulage Malfunction' },
            { value: 'chemical', label: 'Dust & Chemical Exposure' },
            { value: 'other', label: 'Other Operational Hazard' },
          ]}
        />
        <FormField
          label="Severity Rating"
          as="select"
          required
          value={formData.severity}
          onChange={(e) => setFormData({ ...formData, severity: e.target.value as any })}
          options={[
            { value: 'low', label: 'Low - Advisory' },
            { value: 'medium', label: 'Medium - Operational Attention' },
            { value: 'high', label: 'High - Immediate Control Required' },
            { value: 'critical', label: 'Critical - Evacuate & Isolate' },
          ]}
        />
        <FormField
          label="Exact Location in Mine"
          required
          value={formData.location_description}
          onChange={(e) => setFormData({ ...formData, location_description: e.target.value })}
          placeholder="e.g. Panel 4, Dip heading 12, Level 2"
        />
        <FormField
          label="Detailed Observations"
          as="textarea"
          required
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
        />
        <FormField
          label="Action Taken / Mitigation Measures"
          as="textarea"
          value={formData.mitigation_measures}
          onChange={(e) => setFormData({ ...formData, mitigation_measures: e.target.value })}
        />
      </Modal>

      {/* Status Update Modal */}
      <Modal
        isOpen={isStatusModalOpen}
        onClose={() => setIsStatusModalOpen(false)}
        title={`Update Hazard Status #${selectedHazard?.id}`}
        onConfirm={handleStatusSubmit}
        confirmLabel="Update Status"
      >
        <FormField
          label="New Status"
          as="select"
          required
          value={newStatus}
          onChange={(e) => setNewStatus(e.target.value)}
          options={[
            { value: 'reported', label: 'Reported / Under Review' },
            { value: 'assessed', label: 'Assessed by Safety Officer' },
            { value: 'mitigating', label: 'Mitigating Measures Deployed' },
            { value: 'resolved', label: 'Resolved & Safe Sign-off' },
          ]}
        />
        <FormField
          label="Mitigation / Resolution Notes"
          as="textarea"
          value={mitigationNotes}
          onChange={(e) => setMitigationNotes(e.target.value)}
          helper="Document air velocity checks, auxiliary fans started, rock bolts installed, etc."
        />
      </Modal>
    </div>
  );
};

export default HazardsPage;
