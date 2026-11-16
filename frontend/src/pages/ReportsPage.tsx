import React, { useState, useEffect } from 'react';
import { Download, FileSpreadsheet } from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import {
  getSummaryReport,
  getComplianceReport,
  getIncidentReport,
  listMines,
} from '@/services/api';
import type { Mine } from '@/types';
import styles from './ReportsPage.module.css';

export const ReportsPage: React.FC = () => {
  const [mines, setMines] = useState<Mine[]>([]);
  const [selectedMine, setSelectedMine] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // Chart data
  const [incidentsByMonth, setIncidentsByMonth] = useState([
    { month: 'Jan', NearMiss: 3, Minor: 1, Major: 0 },
    { month: 'Feb', NearMiss: 2, Minor: 2, Major: 0 },
    { month: 'Mar', NearMiss: 4, Minor: 0, Major: 1 },
    { month: 'Apr', NearMiss: 1, Minor: 1, Major: 0 },
    { month: 'May', NearMiss: 3, Minor: 2, Major: 0 },
    { month: 'Jun', NearMiss: 2, Minor: 1, Major: 0 },
  ]);

  const [inspectionsByStatus, setInspectionsByStatus] = useState([
    { status: 'Completed', count: 24 },
    { status: 'Scheduled', count: 8 },
    { status: 'In Progress', count: 4 },
    { status: 'Overdue', count: 2 },
  ]);

  const [hazardsBySeverity, setHazardsBySeverity] = useState([
    { severity: 'Low', count: 18 },
    { severity: 'Medium', count: 12 },
    { severity: 'High', count: 5 },
    { severity: 'Critical', count: 2 },
  ]);

  useEffect(() => {
    const fetchMines = async () => {
      try {
        const res = await listMines();
        if (res?.data) {
          setMines(res.data);
        }
      } catch {
        // ignore
      }
    };
    fetchMines();
  }, []);

  const handleExportCSV = () => {
    // Generate clean CSV of hazard & compliance records
    const headers = ['Category', 'Severity/Status', 'Count', 'Colliery Filter', 'Export Date'];
    const rows = [
      ...hazardsBySeverity.map((h) => ['Hazard', h.severity, h.count, selectedMine || 'All', new Date().toISOString()]),
      ...inspectionsByStatus.map((i) => ['Inspection', i.status, i.count, selectedMine || 'All', new Date().toISOString()]),
      ...incidentsByMonth.map((m) => ['Incident Month ' + m.month, 'NearMiss=' + m.NearMiss + ' Minor=' + m.Minor, m.NearMiss + m.Minor + m.Major, selectedMine || 'All', new Date().toISOString()]),
    ];

    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `coal_mine_governance_report_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Statutory Analytics & Compliance Reports</h1>
          <p className={styles.subtitle}>
            DGMS regulatory metrics, quarterly safety trend summaries and inspection KPIs
          </p>
        </div>
        <button type="button" className={styles.exportBtn} onClick={handleExportCSV}>
          <Download size={15} /> Export Report (CSV)
        </button>
      </div>

      <div className={styles.filterBar}>
        <div className={styles.filterGroup}>
          <label>Colliery:</label>
          <select
            className={styles.filterSelect}
            value={selectedMine}
            onChange={(e) => setSelectedMine(e.target.value)}
          >
            <option value="">All Collieries</option>
            {mines.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.filterGroup}>
          <label>From:</label>
          <input
            type="date"
            className={styles.filterInput}
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </div>

        <div className={styles.filterGroup}>
          <label>To:</label>
          <input
            type="date"
            className={styles.filterInput}
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>
      </div>

      <div className={styles.chartsGrid}>
        {/* Incidents by Month Line Chart */}
        <div className={styles.chartCard}>
          <h2 className={styles.chartTitle}>Incidents & Near Misses by Month</h2>
          <div className={styles.chartWrapper}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={incidentsByMonth}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} allowDecimals={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #cbd5e1',
                    borderRadius: '4px',
                    fontSize: '12px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Line type="monotone" dataKey="NearMiss" stroke="#d97706" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="Minor" stroke="#64748b" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="Major" stroke="#dc2626" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Inspections by Status Bar Chart */}
        <div className={styles.chartCard}>
          <h2 className={styles.chartTitle}>Inspections by Statutory Status</h2>
          <div className={styles.chartWrapper}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={inspectionsByStatus}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="status" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} allowDecimals={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #cbd5e1',
                    borderRadius: '4px',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="count" fill="#1e293b" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Hazards by Severity Bar Chart */}
        <div className={styles.chartCard} style={{ gridColumn: 'span 2' }}>
          <h2 className={styles.chartTitle}>Hazard Identification by Severity Class</h2>
          <div className={styles.chartWrapper}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={hazardsBySeverity}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="severity" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} allowDecimals={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #cbd5e1',
                    borderRadius: '4px',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="count" fill="#d97706" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportsPage;
