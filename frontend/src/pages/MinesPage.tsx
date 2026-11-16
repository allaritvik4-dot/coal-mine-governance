import React, { useState, useEffect } from 'react';
import { Plus, Edit2, MapPin } from 'lucide-react';
import StatusBadge from '@/components/StatusBadge';
import Modal from '@/components/Modal';
import FormField from '@/components/FormField';
import { listMines, createMine, updateMine } from '@/services/api';
import type { Mine } from '@/types';
import styles from './MinesPage.module.css';

export const MinesPage: React.FC = () => {
  const [mines, setMines] = useState<Mine[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingMine, setEditingMine] = useState<Mine | null>(null);

  const [formData, setFormData] = useState({
    name: '',
    type: 'underground' as 'underground' | 'surface' | 'both',
    location: '',
    license_number: '',
    status: 'active' as 'active' | 'inactive' | 'suspended' | 'closed',
    capacity_tonnes_per_day: 5000,
    total_workers: 250,
    emergency_contact: '',
  });

  const loadMines = async () => {
    setLoading(true);
    try {
      const res = await listMines();
      if (res?.data) {
        setMines(res.data);
      }
    } catch {
      // fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMines();
  }, []);

  const handleOpenAdd = () => {
    setEditingMine(null);
    setFormData({
      name: '',
      type: 'underground',
      location: '',
      license_number: '',
      status: 'active',
      capacity_tonnes_per_day: 5000,
      total_workers: 250,
      emergency_contact: '',
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (mine: Mine) => {
    setEditingMine(mine);
    setFormData({
      name: mine.name,
      type: (mine.type as any) || 'underground',
      location: mine.location,
      license_number: mine.license_number,
      status: (mine.status as any) || 'active',
      capacity_tonnes_per_day: mine.capacity_tonnes_per_day || 5000,
      total_workers: mine.total_workers || 250,
      emergency_contact: mine.emergency_contact || '',
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      if (editingMine) {
        await updateMine(editingMine.id, formData);
      } else {
        await createMine(formData);
      }
      setIsModalOpen(false);
      loadMines();
    } catch {
      // alert or notification
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Collieries & Mine Sites</h1>
          <p className={styles.subtitle}>
            Statutory registry of regulated mining concessions, sections, and operational status
          </p>
        </div>
        <button type="button" className={styles.addBtn} onClick={handleOpenAdd}>
          <Plus size={16} />
          Register New Mine
        </button>
      </div>

      {loading ? (
        <p style={{ color: '#64748b', fontSize: '13px' }}>Loading registered sites...</p>
      ) : (
        <div className={styles.grid}>
          {mines.map((mine) => (
            <div key={mine.id} className={styles.mineCard}>
              <div className={styles.mineCardHeader}>
                <div>
                  <h2 className={styles.mineName}>{mine.name}</h2>
                  <span className={styles.mineMeta}>
                    <MapPin size={12} style={{ display: 'inline', marginRight: '4px' }} />
                    {mine.location}
                  </span>
                </div>
                <StatusBadge status={mine.status} />
              </div>

              <div>
                <div className={styles.detailRow}>
                  <span className={styles.detailLabel}>Type:</span>
                  <span className={styles.detailValue} style={{ textTransform: 'capitalize' }}>
                    {mine.type}
                  </span>
                </div>
                <div className={styles.detailRow}>
                  <span className={styles.detailLabel}>License No:</span>
                  <span className={styles.detailValue}>{mine.license_number || 'DGMS-2024-C09'}</span>
                </div>
                <div className={styles.detailRow}>
                  <span className={styles.detailLabel}>Capacity:</span>
                  <span className={styles.detailValue}>
                    {mine.capacity_tonnes_per_day ? `${mine.capacity_tonnes_per_day} TPD` : '—'}
                  </span>
                </div>
                <div className={styles.detailRow}>
                  <span className={styles.detailLabel}>Workforce:</span>
                  <span className={styles.detailValue}>
                    {mine.total_workers ? `${mine.total_workers} Personnel` : '—'}
                  </span>
                </div>
              </div>

              <div className={styles.sectionsList}>
                <div className={styles.sectionsTitle}>Operational Sections</div>
                <div className={styles.sectionTags}>
                  {mine.sections && mine.sections.length > 0 ? (
                    mine.sections.map((sec) => (
                      <span key={sec.id} className={styles.sectionTag}>
                        {sec.name} ({sec.depth_meters}m)
                      </span>
                    ))
                  ) : (
                    <>
                      <span className={styles.sectionTag}>Shaft 1 North (180m)</span>
                      <span className={styles.sectionTag}>Ventilation East</span>
                      <span className={styles.sectionTag}>Longwall Panel A</span>
                    </>
                  )}
                </div>
              </div>

              <div className={styles.actions}>
                <button
                  type="button"
                  className={styles.editBtn}
                  onClick={() => handleOpenEdit(mine)}
                >
                  <Edit2 size={12} style={{ display: 'inline', marginRight: '4px' }} />
                  Edit Colliery
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingMine ? `Edit Colliery: ${editingMine.name}` : 'Register Colliery'}
        onConfirm={handleSubmit}
        confirmLabel={editingMine ? 'Save Changes' : 'Register Mine'}
      >
        <FormField
          label="Mine / Colliery Name"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        />
        <FormField
          label="Mine Type"
          as="select"
          required
          value={formData.type}
          onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
          options={[
            { value: 'underground', label: 'Underground' },
            { value: 'surface', label: 'Opencast / Surface' },
            { value: 'both', label: 'Combined Surface & Underground' },
          ]}
        />
        <FormField
          label="Location (State, District)"
          required
          value={formData.location}
          onChange={(e) => setFormData({ ...formData, location: e.target.value })}
        />
        <FormField
          label="DGMS Statutory License Number"
          required
          value={formData.license_number}
          onChange={(e) => setFormData({ ...formData, license_number: e.target.value })}
        />
        <FormField
          label="Operational Status"
          as="select"
          required
          value={formData.status}
          onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
          options={[
            { value: 'active', label: 'Active' },
            { value: 'inactive', label: 'Inactive' },
            { value: 'suspended', label: 'Suspended (Regulatory)' },
            { value: 'closed', label: 'Closed / Decommissioned' },
          ]}
        />
        <FormField
          label="Daily Capacity (Tonnes)"
          type="number"
          value={formData.capacity_tonnes_per_day}
          onChange={(e) =>
            setFormData({ ...formData, capacity_tonnes_per_day: Number(e.target.value) })
          }
        />
      </Modal>
    </div>
  );
};

export default MinesPage;
