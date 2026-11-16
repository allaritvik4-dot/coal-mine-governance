import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import styles from './StatCard.module.css';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: string;
    direction: 'up' | 'down' | 'neutral';
  };
  description?: string;
  statusVariant?: 'slate' | 'amber' | 'red' | 'green';
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  icon: Icon,
  trend,
  description,
}) => {
  return (
    <div className={styles.card}>
      <div className={styles.topRow}>
        <span className={styles.label}>{label}</span>
        <div className={styles.iconWrapper}>
          <Icon size={18} />
        </div>
      </div>
      <div className={styles.valueRow}>
        <span className={styles.value}>{value}</span>
        {trend && (
          <div
            className={`${styles.trend} ${
              trend.direction === 'up'
                ? styles.trendUp
                : trend.direction === 'down'
                ? styles.trendDown
                : styles.trendNeutral
            }`}
          >
            {trend.direction === 'up' && <TrendingUp size={14} />}
            {trend.direction === 'down' && <TrendingDown size={14} />}
            {trend.direction === 'neutral' && <Minus size={14} />}
            <span>{trend.value}</span>
          </div>
        )}
      </div>
      {description && <div className={styles.description}>{description}</div>}
    </div>
  );
};

export default StatCard;
