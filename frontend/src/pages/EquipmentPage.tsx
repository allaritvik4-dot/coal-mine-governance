import React, { useState, useEffect, useMemo } from 'react';
import { Plus, Edit2, Wrench, AlertTriangle } from 'lucide-react';
import DataTable, { Column } from '@/components/DataTable';
import StatusBadge from '@/components/StatusBadge';
import Modal from '@/components/Modal';
import FormField from '@/components/FormField';
import {
  listEquipment,
  createEquipment,
  updateEquipment,
  getMaintenanceDue,
  createMaintenance,
  listMaintenance,
  listMines,
} from '@/services/api';
import type { Equipment, Mine, MaintenanceActivity } from '@/types';
import styles from './EquipmentPage.module.css';

export const EquipmentPage: React.FC = () => {
  const [equipmentList, setEquipmentList] = useState<Equipment[]>([]);
  const [dueList, setDueList] = useState<Equipment[]>([]);
  const [mines, setMines] = useState<Mine[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [filterMine, setFilterMine] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  // Modals
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingEquipment, setEditingEquipment] = useState<Equipment | null>(null);

  const [isMaintenanceModalOpen, setIsMaintenanceModalOpen] = useState(false);
  const [maintainingEquipment, setMaintainingEquipment] = useState<Equipment | null>(null);
  const [maintenanceHistory, setMaintenanceHistory] = useState<MaintenanceActivity[]>([]);

  const [formData, setFormData] = useState({
    mine_id: 1,
    name: '',
    type: 'ventilation_fan' as any,
    serial_number: '',
    manufacturer: '',
    installation_date: new Date().toISOString().split('T')[0],
    last_maintenance_date: '',
    next_maintenance_due: '',
    status: 'operational' as any,
  });

  const [maintenanceFormData, setMaintenanceFormData] = useState({
    type: 'preventive' as any,
    description: '',
    date_performed: new Date().toISOString().split('T')[0],
    next_due_date: '',
    cost: 5000,
    parts_replaced: '',
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [eqRes, dueRes, minesRes] = await Promise.allSettled([
        listEquipment(),
        getMaintenanceDue(),
        listMines(),
      ]);
      if (eqRes.status === 'fulfilled' && eqRes.value?.data) {
        setEquipmentList(eqRes.value.data);
      }
      if (dueRes.status === 'fulfilled' && dueRes.value) {
        setDueList(Array.isArray(dueRes.value) ? dueRes.value : (dueRes.value as any)?.data || []);
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

  const filteredEquipment = useMemo(() => {
    return equipmentList.filter((e) => {
      if (filterMine && String(e.mine_id) !== filterMine) return false;
      if (filterStatus && e.status !== filterStatus) return false;
      return true;
    });
  }, [equipmentList, filterMine, filterStatus]);

  const handleOpenAdd = () => {
    setEditingEquipment(null);
    setFormData({
      mine_id: mines[0]?.id || 1,
      name: '',
      type: 'ventilation_fan',
      serial_number: '',
      manufacturer: '',
      installation_date: new Date().toISOString().split('T')[0],
      last_maintenance_date: '',
      next_maintenance_due: '',
      status: 'operational',
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (eq: Equipment) => {
    setEditingEquipment(eq);
    setFormData({
      mine_id: eq.mine_id,
      name: eq.name,
      type: eq.type,
      serial_number: eq.serial_number || '',
      manufacturer: eq.manufacturer || '',
      installation_date: eq.installation_date ? eq.installation_date.split('T')[0] : '',
      last_maintenance_date: eq.last_maintenance_date ? eq.last_maintenance_date.split('T')[0] : '',
      next_maintenance_due: eq.next_maintenance_due ? eq.next_maintenance_due.split('T')[0] : '',
      status: eq.status,
    });
    setIsModalOpen(true);
  };

  const handleOpenMaintenance = async (eq: Equipment) => {
    setMaintainingEquipment(eq);
    setMaintenanceFormData({
      type: 'preventive',
      description: '',
      date_performed: new Date().toISOString().split('T')[0],
      next_due_date: '',
      cost: 5000,
      parts_replaced: '',
    });
    try {
      const res = await listMaintenance({ equipment_id: eq.id });
      if (res?.data) {
        setMaintenanceHistory(res.data);
      }
    } catch {
      setMaintenanceHistory([]);
    }
    setIsMaintenanceModalOpen(true);
  };

  const handleSaveEquipment = async () => {
    try {
      if (editingEquipment) {
        await updateEquipment(editingEquipment.id, formData);
      } else {
        await createEquipment(formData);
      }
      setIsModalOpen(false);
      loadData();
    } catch {
      // ignore
    }
  };

  const handleSaveMaintenance = async () => {
    if (!maintainingEquipment) return;
    try {
      await createMaintenance({
        equipment_id: maintainingEquipment.id,
        ...maintenanceFormData,
      });
      setIsMaintenanceModalOpen(false);
      loadData();
    } catch {
      // ignore
    }
  };

  const columns: Column<Equipment>[] = [
    {
      key: 'name',
      header: 'Equipment Name',
      render: (e) => (
        <div>
          <span style={{ fontWeight: 600 }}>{e.name}</span>
          <div style={{ fontSize: '11px', color: '#64748b' }}>
            SN: {e.serial_number || 'N/A'} &bull; {e.manufacturer || 'OEM'}
          </div>
        </div>
      ),
    },
    {
      key: 'type',
      header: 'Category',
      render: (e) => <span style={{ textTransform: 'capitalize' }}>{e.type.replace('_', ' ')}</span>,
    },
    {
      key: 'mine_name',
      header: 'Colliery',
      render: (e) => e.mine_name || `Mine #${e.mine_id}`,
    },
    {
      key: 'status',
      header: 'Operational Status',
      render: (e) => <StatusBadge status={e.status} />,
    },
    {
      key: 'last_maintenance_date',
      header: 'Last Service',
      render: (e) => (e.last_maintenance_date ? e.last_maintenance_date.split('T')[0] : '—'),
    },
    {
      key: 'next_maintenance_due',
      header: 'Next Due',
      render: (e) => {
        const isOverdue = e.next_maintenance_due && new Date(e.next_maintenance_due) < new Date();
        return (
          <span style={{ color: isOverdue ? '#dc2626' : 'inherit', fontWeight: isOverdue ? 700 : 400 }}>
            {e.next_maintenance_due ? e.next_maintenance_due.split('T')[0] : '—'}
            {isOverdue && ' (Overdue)'}
          </span>
        );
      },
    },
    {
      key: 'actions',
      header: 'Actions',
      sortable: false,
      render: (e) => (
        <div>
          <button
            type="button"
            className={styles.actionBtn}
            onClick={() => handleOpenEdit(e)}
            title="Edit Equipment"
          >
            <Edit2 size={12} />
          </button>
          <button
            type="button"
            className={styles.actionBtn}
            onClick={() => handleOpenMaintenance(e)}
            title="Log Service / View Maintenance"
          >
            <Wrench size={12} /> Log Service
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Heavy Machinery & Ventilation Equipment</h1>
          <p className={styles.subtitle}>
            DGMS Flameproof & Intrinsically Safe machinery registry, maintenance scheduling and testing records
          </p>
        </div>
        <button type="button" className={styles.addBtn} onClick={handleOpenAdd}>
          <Plus size={16} />
          Register Equipment
        </button>
      </div>

      {/* Due Warning Banner */}
      {dueList.length > 0 && (
        <div className={styles.dueBanner}>
          <AlertTriangle size={20} />
          <div>
            <span className={styles.dueTitle}>Mandatory Maintenance Overdue</span>
            <span>
              {dueList.length} machinery unit(s) require immediate inspection or statutory overhaul.
            </span>
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
            <option value="operational">Operational</option>
            <option value="needs_maintenance">Needs Maintenance</option>
            <option value="under_repair">Under Repair</option>
            <option value="decommissioned">Decommissioned</option>
          </select>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={filteredEquipment}
        pageSize={10}
        emptyMessage="No equipment records found."
      />

      {/* Add / Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingEquipment ? `Edit Equipment: ${editingEquipment.name}` : 'Register Equipment'}
        onConfirm={handleSaveEquipment}
        confirmLabel="Save Equipment"
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
          label="Equipment Name / Tag"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="e.g. Main Surface Exhauster Fan #1"
        />
        <FormField
          label="Category"
          as="select"
          required
          value={formData.type}
          onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
          options={[
            { value: 'ventilation_fan', label: 'Main / Auxiliary Ventilation Fan' },
            { value: 'continuous_miner', label: 'Continuous Miner' },
            { value: 'shuttle_car', label: 'Shuttle Car / Hauler' },
            { value: 'roof_bolter', label: 'Roof Bolter Rig' },
            { value: 'conveyor', label: 'Belt Conveyor Drive Head' },
            { value: 'substation', label: 'Flameproof Mining Substation' },
            { value: 'methanometer', label: 'Fixed Environmental Gas Sensor' },
          ]}
        />
        <FormField
          label="Serial Number / Approval No."
          required
          value={formData.serial_number}
          onChange={(e) => setFormData({ ...formData, serial_number: e.target.value })}
        />
        <FormField
          label="Manufacturer / OEM"
          value={formData.manufacturer}
          onChange={(e) => setFormData({ ...formData, manufacturer: e.target.value })}
        />
        <FormField
          label="Next Statutory Maintenance Due"
          type="date"
          value={formData.next_maintenance_due}
          onChange={(e) => setFormData({ ...formData, next_maintenance_due: e.target.value })}
        />
        <FormField
          label="Current Status"
          as="select"
          value={formData.status}
          onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
          options={[
            { value: 'operational', label: 'Operational & Certified' },
            { value: 'needs_maintenance', label: 'Needs Maintenance' },
            { value: 'under_repair', label: 'Under Repair' },
            { value: 'decommissioned', label: 'Decommissioned' },
          ]}
        />
      </Modal>

      {/* Maintenance Activity Modal */}
      <Modal
        isOpen={isMaintenanceModalOpen}
        onClose={() => setIsMaintenanceModalOpen(false)}
        title={`Maintenance & Service Log: ${maintainingEquipment?.name}`}
        onConfirm={handleSaveMaintenance}
        confirmLabel="Record Maintenance Activity"
        maxWidth="680px"
      >
        <div style={{ marginBottom: '16px' }}>
          <h3 style={{ fontSize: '13px', textTransform: 'uppercase', color: '#475569', marginBottom: '8px' }}>
            Log New Service
          </h3>
          <FormField
            label="Maintenance Type"
            as="select"
            required
            value={maintenanceFormData.type}
            onChange={(e) => setMaintenanceFormData({ ...maintenanceFormData, type: e.target.value as any })}
            options={[
              { value: 'preventive', label: 'Preventive Routine Overhaul' },
              { value: 'corrective', label: 'Corrective Repair' },
              { value: 'emergency', label: 'Emergency Breakdown Intervention' },
            ]}
          />
          <FormField
            label="Work Summary & Checks Performed"
            as="textarea"
            required
            value={maintenanceFormData.description}
            onChange={(e) => setMaintenanceFormData({ ...maintenanceFormData, description: e.target.value })}
            placeholder="Replaced motor bearings, FLP enclosure inspection, insulation resistance test..."
          />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <FormField
              label="Date Performed"
              type="date"
              required
              value={maintenanceFormData.date_performed}
              onChange={(e) => setMaintenanceFormData({ ...maintenanceFormData, date_performed: e.target.value })}
            />
            <FormField
              label="Next Due Date"
              type="date"
              value={maintenanceFormData.next_due_date}
              onChange={(e) => setMaintenanceFormData({ ...maintenanceFormData, next_due_date: e.target.value })}
            />
          </div>
          <FormField
            label="Parts Replaced"
            value={maintenanceFormData.parts_replaced}
            onChange={(e) => setMaintenanceFormData({ ...maintenanceFormData, parts_replaced: e.target.value })}
            placeholder="Filter elements, seals, coupling pins"
          />
        </div>

        {maintenanceHistory.length > 0 && (
          <div>
            <h3 style={{ fontSize: '13px', textTransform: 'uppercase', color: '#475569', marginBottom: '8px' }}>
              Service History
            </h3>
            <div style={{ maxHeight: '160px', overflowY: 'auto', border: '1px solid #e2e8f0', borderRadius: '4px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '11px' }}>
                <thead>
                  <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0', textAlign: 'left' }}>
                    <th style={{ padding: '6px' }}>Date</th>
                    <th style={{ padding: '6px' }}>Type</th>
                    <th style={{ padding: '6px' }}>Summary</th>
                    <th style={{ padding: '6px' }}>Parts</th>
                  </tr>
                </thead>
                <tbody>
                  {maintenanceHistory.map((m) => (
                    <tr key={m.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '6px' }}>{m.date_performed ? m.date_performed.split('T')[0] : '—'}</td>
                      <td style={{ padding: '6px', textTransform: 'capitalize' }}>{m.type}</td>
                      <td style={{ padding: '6px' }}>{m.description}</td>
                      <td style={{ padding: '6px' }}>{m.parts_replaced || 'None'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default EquipmentPage;
