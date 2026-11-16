import React from 'react';
import styles from './StatusBadge.module.css';

interface StatusBadgeProps {
  status: string;
  variant?: 'green' | 'amber' | 'red' | 'steel' | 'blue';
  label?: string;
}

const getVariant = (status: string): 'green' | 'amber' | 'red' | 'steel' | 'blue' => {
  const s = status.toLowerCase();
  if (['completed', 'safe', 'valid', 'resolved', 'low', 'active', 'operational'].includes(s)) {
    return 'green';
  }
  if (['pending', 'in_progress', 'under_review', 'investigating', 'needs_maintenance', 'expiring_soon', 'medium', 'moderate', 'open', 'acknowledged'].includes(s)) {
    return 'amber';
  }
  if (['critical', 'overdue', 'expired', 'high', 'fatal', 'major', 'urgent', 'escalated'].includes(s)) {
    return 'red';
  }
  if (['underground', 'opencast', 'both', 'extraction'].includes(s)) {
    return 'blue';
  }
  return 'steel';
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, variant, label }) => {
  const chosenVariant = variant || getVariant(status);
  const displayLabel = label || status.replace(/_/g, ' ');

  return (
    <span className={`${styles.badge} ${styles[chosenVariant]}`}>
      {displayLabel}
    </span>
  );
};

export default StatusBadge;
