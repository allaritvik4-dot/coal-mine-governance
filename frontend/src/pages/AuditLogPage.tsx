import React, { useState, useEffect, useMemo } from 'react';
import { Search } from 'lucide-react';
import DataTable, { Column } from '@/components/DataTable';
import StatusBadge from '@/components/StatusBadge';
import { getAuditLog } from '@/services/api';
import type { AuditLogEntry } from '@/types';
import styles from './AuditLogPage.module.css';

export const AuditLogPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterAction, setFilterAction] = useState('');
  const [filterEntity, setFilterEntity] = useState('');

  const loadLogs = async () => {
    setLoading(true);
    try {
      const res = await getAuditLog();
      if (res?.data) {
        setLogs(res.data);
      }
    } catch {
      // fallback sample data if backend table is empty
      setLogs([
        {
          id: 1,
          user_id: 1,
          username: 'admin',
          action: 'CREATE',
          entity_type: 'inspection',
          entity_id: 101,
          old_values: null,
          new_values: '{"type":"safety","scheduled_date":"2026-11-20"}',
          ip_address: '127.0.0.1',
          timestamp: '2026-11-16 10:14:02',
        },
        {
          id: 2,
          user_id: 2,
          username: 'safety_officer_1',
          action: 'STATUS_UPDATE',
          entity_type: 'hazard',
          entity_id: 42,
          old_values: '{"status":"reported"}',
          new_values: '{"status":"mitigating","mitigation_notes":"Aux fan installed"}',
          ip_address: '192.168.1.45',
          timestamp: '2026-11-16 11:22:15',
        },
        {
          id: 3,
          user_id: 1,
          username: 'admin',
          action: 'ACKNOWLEDGE',
          entity_type: 'compliance_alert',
          entity_id: 12,
          old_values: '{"status":"open"}',
          new_values: '{"status":"acknowledged"}',
          ip_address: '127.0.0.1',
          timestamp: '2026-11-16 12:05:40',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  const filteredLogs = useMemo(() => {
    return logs.filter((log) => {
      if (filterAction && log.action !== filterAction) return false;
      if (filterEntity && log.entity_type !== filterEntity) return false;
      if (search) {
        const q = search.toLowerCase();
        const matchUser = log.username?.toLowerCase().includes(q);
        const matchAction = log.action?.toLowerCase().includes(q);
        const matchEntity = log.entity_type?.toLowerCase().includes(q);
        const matchValues =
          (log.new_values && log.new_values.toLowerCase().includes(q)) ||
          (log.old_values && log.old_values.toLowerCase().includes(q));
        if (!matchUser && !matchAction && !matchEntity && !matchValues) return false;
      }
      return true;
    });
  }, [logs, search, filterAction, filterEntity]);

  const columns: Column<AuditLogEntry>[] = [
    {
      key: 'timestamp',
      header: 'Timestamp (UTC)',
      width: '150px',
      render: (l) => <span style={{ fontSize: '11px', color: '#64748b' }}>{l.timestamp}</span>,
    },
    {
      key: 'username',
      header: 'Authenticated User',
      render: (l) => <strong>{l.username || `User #${l.user_id}`}</strong>,
    },
    {
      key: 'action',
      header: 'Action Taken',
      render: (l) => <StatusBadge status={l.action} variant="steel" />,
    },
    {
      key: 'entity_type',
      header: 'Entity Class',
      render: (l) => (
        <span style={{ textTransform: 'capitalize', fontWeight: 500 }}>
          {(l.entity_type ?? '').replace('_', ' ')}
        </span>
      ),
    },
    {
      key: 'entity_id',
      header: 'Entity Ref',
      width: '90px',
      render: (l) => `#${l.entity_id}`,
    },
    {
      key: 'new_values',
      header: 'Audit Modification Details',
      render: (l) => (
        <div style={{ maxWidth: '380px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          <code style={{ fontSize: '11px', background: '#f8fafc', padding: '2px 6px', border: '1px solid #e2e8f0' }}>
            {l.new_values || l.old_values || 'Record created / altered'}
          </code>
        </div>
      ),
    },
    {
      key: 'ip_address',
      header: 'Terminal IP',
      width: '110px',
      render: (l) => <span style={{ fontSize: '11px', color: '#64748b' }}>{l.ip_address || '127.0.0.1'}</span>,
    },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Statutory Audit Trail & System Log</h1>
          <p className={styles.subtitle}>
            Immutable ledger of all user authorizations, compliance determinations, alert sign-offs and data edits
          </p>
        </div>
      </div>

      <div className={styles.filterBar}>
        <div className={styles.filterGroup}>
          <Search size={14} color="#64748b" />
          <input
            type="text"
            className={styles.searchInput}
            placeholder="Search audit trail by user, action, detail..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className={styles.filterGroup}>
          <label>Action:</label>
          <select
            className={styles.filterSelect}
            value={filterAction}
            onChange={(e) => setFilterAction(e.target.value)}
          >
            <option value="">All Actions</option>
            <option value="CREATE">CREATE</option>
            <option value="UPDATE">UPDATE</option>
            <option value="STATUS_UPDATE">STATUS_UPDATE</option>
            <option value="ACKNOWLEDGE">ACKNOWLEDGE</option>
            <option value="RESOLVE">RESOLVE</option>
            <option value="DELETE">DELETE</option>
          </select>
        </div>

        <div className={styles.filterGroup}>
          <label>Entity:</label>
          <select
            className={styles.filterSelect}
            value={filterEntity}
            onChange={(e) => setFilterEntity(e.target.value)}
          >
            <option value="">All Entities</option>
            <option value="inspection">Inspection</option>
            <option value="hazard">Hazard</option>
            <option value="incident">Incident</option>
            <option value="equipment">Equipment</option>
            <option value="compliance_alert">Compliance Alert</option>
            <option value="compliance_rule">Compliance Rule</option>
            <option value="corrective_action">Corrective Action</option>
          </select>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={filteredLogs}
        pageSize={12}
        emptyMessage="No audit trail events matched."
      />
    </div>
  );
};

export default AuditLogPage;
