
import React, { useState, useEffect, useMemo } from 'react';
import { Plus, Eye, Edit2 } from 'lucide-react';
import DataTable, { Column } from '@/components/DataTable';
import StatusBadge from '@/components/StatusBadge';
import Modal from '@/components/Modal';
import FormField from '@/components/FormField';
import {
  listIncidents,
  createIncident,
  updateIncident,
  listMines,
} from '@/services/api';
import type { Incident, Mine } from '@/types';
import styles from './IncidentsPage.module.css';

export const IncidentsPage: React.FC = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [mines, setMines] = useState<Mine[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [filterMine, setFilterMine] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  // Modals
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingIncident, setEditingIncident] = useState<Incident | null>(null);
  const [viewingIncident, setViewingIncident] = useState<Incident | null>(null);

  const [formData, setFormData] = useState({
    mine_id: 1,
    title: '',
    type: 'injury' as any,
    severity: 'minor' as any,
    status: 'reported' as any,
    description: '',
    location_description: '',
    injuries_count: 0,
    fatalities_count: 0,
    root_cause: '',
    date_occurred: new Date().toISOString().split('T')[0],
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [incRes, minesRes] = await Promise.allSettled([
        listIncidents(),
        listMines(),
      ]);
      if (incRes.status === 'fulfilled' && incRes.value?.data) {
        setIncidents(incRes.value.data);
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

  const filteredIncidents = useMemo(() => {
    return incidents.filter((i) => {
      if (filterMine && String(i.mine_id) !== filterMine) return false;
      if (filterSeverity && i.severity !== filterSeverity) return false;
      if (filterStatus && i.status !== filterStatus) return false;
      return true;
    });
  }, [incidents, filterMine, filterSeverity, filterStatus]);

  const handleOpenAdd = () => {
    setEditingIncident(null);
    setFormData({
      mine_id: mines[0]?.id || 1,
      title: '',
      type: 'injury',
      severity: 'minor',
      status: 'reported',
      description: '',
      location_description: '',
      injuries_count: 0,
      fatalities_count: 0,
      root_cause: '',
      date_occurred: new Date().toISOString().split('T')[0],
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (i: Incident) => {
    setEditingIncident(i);
    setFormData({
      mine_id: i.mine_id,
      title: i.title ?? '',
      type: i.type ?? i.incident_type ?? '',
      severity: i.severity,
      status: i.status,
      description: i.description,
      location_description: i.location_description ?? '',
      injuries_count: i.injuries_count || i.injuries || 0,
      fatalities_count: i.fatalities_count || i.casualties || 0,
      root_cause: i.root_cause || '',
      date_occurred: i.date_occurred ? i.date_occurred.split('T')[0] : '',
    });
    setIsModalOpen(true);
  };

  const handleSave = async () => {
    try {
      if (editingIncident) {
        await updateIncident(editingIncident.id, formData);
      } else {
        await createIncident(formData);
      }
      setIsModalOpen(false);
      loadData();
    } catch {
      // ignore
    }
  };

  const columns: Column<Incident>[] = [
    {
      key: 'id',
      header: 'ID',
      width: '60px',
      render: (i) => `#${i.id}`,
    },
    {
      key: 'title',
      header: 'Incident',
      render: (i) => (
        <div>
          <span style={{ fontWeight: 600 }}>{i.title}</span>
          <div style={{ fontSize: '11px', color: '#64748b' }}>{i.location_description}</div>
        </div>
      ),
    },
    {
      key: 'type',
      header: 'Classification',
      render: (i) => <span style={{ textTransform: 'capitalize' }}>{(i.type ?? i.incident_type ?? '').replace('_', ' ')}</span>,
    },
    {
      key: 'mine_name',
      header: 'Colliery',
      render: (i) => i.mine_name || `Mine #${i.mine_id}`,
    },
    {
      key: 'severity',
      header: 'Severity',
      render: (i) => <StatusBadge status={i.severity} />,
    },
    {
      key: 'status',
      header: 'Status',
      render: (i) => <StatusBadge status={i.status} />,
    },
    {
      key: 'date_occurred',
      header: 'Date',
      render: (i) => (i.date_occurred ? i.date_occurred.split('T')[0] : '—'),
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
            onClick={() => setViewingIncident(i)}
            title="View Details"
          >
            <Eye size={12} />
          </button>
          <button
            type="button"
            className={styles.actionBtn}
            onClick={() => handleOpenEdit(i)}
            title="Edit"
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
          <h1 className={styles.title}>Statutory Incident Log</h1>
          <p className={styles.subtitle}>
            DGMS Form IV-A/B recordable accidents, near misses, and structural failures
          </p>
        </div>
        <button type="button" className={styles.addBtn} onClick={handleOpenAdd}>
          <Plus size={16} />
          Record Incident
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
            <option value="minor">Minor</option>
            <option value="moderate">Moderate</option>
            <option value="major">Major</option>
            <option value="critical">Critical</option>
            <option value="fatal">Fatal</option>
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
            <option value="investigating">Investigating</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={filteredIncidents}
        pageSize={10}
        emptyMessage="No incidents recorded."
      />

      {/* Add / Edit Incident Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingIncident ? `Edit Incident Record #${editingIncident.id}` : 'Record Safety Incident'}
        onConfirm={handleSave}
        confirmLabel="Save Incident Record"
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
          label="Incident Title"
          required
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          placeholder="e.g. Continuous Miner Hydraulic Rupture"
        />
        <FormField
          label="Classification"
          as="select"
          required
          value={formData.type}
          onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
          options={[
            { value: 'near_miss', label: 'Near Miss / Dangerous Occurrence' },
            { value: 'injury', label: 'Reportable Injury' },
            { value: 'property_damage', label: 'Equipment / Property Damage' },
            { value: 'collapse', label: 'Roof / Side Wall Fall' },
            { value: 'fire', label: 'Underground Spontaneous Heating / Fire' },
            { value: 'environmental', label: 'Toxic Spill / Tailings Breach' },
            { value: 'fatal', label: 'Fatal Accident' },
          ]}
        />
        <FormField
          label="Severity"
          as="select"
          required
          value={formData.severity}
          onChange={(e) => setFormData({ ...formData, severity: e.target.value as any })}
          options={[
            { value: 'minor', label: 'Minor / First Aid' },
            { value: 'moderate', label: 'Moderate / Lost Time Injury' },
            { value: 'major', label: 'Major / Serious Bodily Injury' },
            { value: 'critical', label: 'Critical / Structural Threat' },
            { value: 'fatal', label: 'Fatal' },
          ]}
        />
        <FormField
          label="Date & Time of Occurrence"
          type="date"
          required
          value={formData.date_occurred}
          onChange={(e) => setFormData({ ...formData, date_occurred: e.target.value })}
        />
        <FormField
          label="Location in Mine"
          required
          value={formData.location_description}
          onChange={(e) => setFormData({ ...formData, location_description: e.target.value })}
        />
        <FormField
          label="Factual Summary of Occurrence"
          as="textarea"
          required
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
        />
        <FormField
          label="Root Cause Analysis (if determined)"
          as="textarea"
          value={formData.root_cause}
          onChange={(e) => setFormData({ ...formData, root_cause: e.target.value })}
        />
      </Modal>

      {/* View Details Modal */}
      <Modal
        isOpen={!!viewingIncident}
        onClose={() => setViewingIncident(null)}
        title={`Incident Record #${viewingIncident?.id}`}
        cancelLabel="Close"
      >
        {viewingIncident && (
          <div>
            <div className={styles.detailRow}>
              <span className={styles.detailLabel}>Title:</span>
              <span className={styles.detailVal}><strong>{viewingIncident.title}</strong></span>
            </div>
            <div className={styles.detailRow}>
              <span className={styles.detailLabel}>Colliery:</span>
              <span className={styles.detailVal}>{viewingIncident.mine_name || `Mine #${viewingIncident.mine_id}`}</span>
            </div>
            <div className={styles.detailRow}>
              <span className={styles.detailLabel}>Classification:</span>
              <span className={styles.detailVal} style={{ textTransform: 'capitalize' }}>
                {(viewingIncident.type ?? viewingIncident.incident_type ?? '').replace('_', ' ')}
              </span>
            </div>
            <div className={styles.detailRow}>
              <span className={styles.detailLabel}>Severity:</span>
              <span className={styles.detailVal}><StatusBadge status={viewingIncident.severity} /></span>
            </div>
            <div className={styles.detailRow}>
              <span className={styles.detailLabel}>Status:</span>
              <span className={styles.detailVal}><StatusBadge status={viewingIncident.status} /></span>
            </div>
            <div className={styles.detailRow}>
              <span className={styles.detailLabel}>Date Occurred:</span>
              <span className={styles.detailVal}>{viewingIncident.date_occurred || '—'}</span>
            </div>
            <div className={styles.detailRow}>
              <span className={styles.detailLabel}>Casualties / Injuries:</span>
              <span className={styles.detailVal}>
                {viewingIncident.fatalities_count || 0} Fatalities, {viewingIncident.injuries_count || 0} Injuries
              </span>
            </div>
            <div className={styles.detailRow}>
              <span className={styles.detailLabel}>Location Detail:</span>
              <span className={styles.detailVal}>{viewingIncident.location_description}</span>
            </div>
            <div style={{ marginTop: '16px' }}>
              <strong>Description:</strong>
              <p style={{ marginTop: '6px', lineHeight: 1.5 }}>{viewingIncident.description}</p>
            </div>
            {viewingIncident.root_cause && (
              <div style={{ marginTop: '16px', background: '#f8fafc', padding: '12px', border: '1px solid #e2e8f0', borderRadius: '4px' }}>
                <strong>Statutory Root Cause Finding:</strong>
                <p style={{ marginTop: '6px', lineHeight: 1.5 }}>{viewingIncident.root_cause}</p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default IncidentsPage;
