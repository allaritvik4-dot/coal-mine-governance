import React, { useState, useEffect } from 'react';
import FormField from '@/components/FormField';
import StatusBadge from '@/components/StatusBadge';
import { getMe, changePassword, register } from '@/services/api';
import type { User } from '@/types';
import styles from './SettingsPage.module.css';

export const SettingsPage: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);

  // Change password state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordMsg, setPasswordMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // User management state (Admin only)
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    role: 'safety_officer',
  });
  const [adminMsg, setAdminMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const u = await getMe();
        setUser(u);
      } catch {
        // fallback
        const stored = localStorage.getItem('user');
        if (stored) {
          try {
            setUser(JSON.parse(stored));
          } catch {
            // ignore
          }
        }
      }
    };
    fetchUser();
  }, []);

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordMsg(null);

    if (newPassword !== confirmPassword) {
      setPasswordMsg({ type: 'error', text: 'New passwords do not match.' });
      return;
    }

    try {
      await changePassword({ current_password: currentPassword, new_password: newPassword });
      setPasswordMsg({ type: 'success', text: 'Password successfully updated.' });
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setPasswordMsg({
        type: 'error',
        text: err.response?.data?.message || 'Failed to update password.',
      });
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setAdminMsg(null);

    try {
      await register(newUser);
      setAdminMsg({ type: 'success', text: `User account '${newUser.username}' created successfully.` });
      setNewUser({
        username: '',
        email: '',
        full_name: '',
        password: '',
        role: 'safety_officer',
      });
    } catch (err: any) {
      setAdminMsg({
        type: 'error',
        text: err.response?.data?.message || 'Failed to create user account.',
      });
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>System Settings & User Profile</h1>
        <p className={styles.subtitle}>
          User authorization profile, security credential management, and role administration
        </p>
      </div>

      {/* User Profile Summary */}
      <div className={styles.card}>
        <h2 className={styles.cardTitle}>Current User Profile</h2>
        {user ? (
          <div>
            <div className={styles.profileRow}>
              <span className={styles.profileLabel}>Full Name:</span>
              <span className={styles.profileValue}>{user.full_name}</span>
            </div>
            <div className={styles.profileRow}>
              <span className={styles.profileLabel}>Username:</span>
              <span className={styles.profileValue}>{user.username}</span>
            </div>
            <div className={styles.profileRow}>
              <span className={styles.profileLabel}>Official Email:</span>
              <span className={styles.profileValue}>{user.email}</span>
            </div>
            <div className={styles.profileRow}>
              <span className={styles.profileLabel}>Regulatory Role:</span>
              <span className={styles.profileValue}>
                <StatusBadge status={user.role} />
              </span>
            </div>
            <div className={styles.profileRow}>
              <span className={styles.profileLabel}>Account Status:</span>
              <span className={styles.profileValue}>
                <StatusBadge status={user.is_active ? 'active' : 'inactive'} />
              </span>
            </div>
          </div>
        ) : (
          <p style={{ color: '#64748b', fontSize: '13px' }}>Loading profile...</p>
        )}
      </div>

      {/* Change Password */}
      <div className={styles.card}>
        <h2 className={styles.cardTitle}>Change Access Password</h2>
        {passwordMsg && (
          <div className={passwordMsg.type === 'success' ? styles.successMsg : styles.errorMsg}>
            {passwordMsg.text}
          </div>
        )}
        <form onSubmit={handleChangePassword}>
          <FormField
            label="Current Password"
            type="password"
            required
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
          />
          <FormField
            label="New Password"
            type="password"
            required
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            helper="Minimum 8 characters with at least one number and special character."
          />
          <FormField
            label="Confirm New Password"
            type="password"
            required
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
          <button type="submit" className={styles.submitBtn}>
            Update Password
          </button>
        </form>
      </div>

      {/* Admin User Management */}
      {user?.role === 'admin' && (
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>User Provisioning & Role Assignment (Admin Only)</h2>
          {adminMsg && (
            <div className={adminMsg.type === 'success' ? styles.successMsg : styles.errorMsg}>
              {adminMsg.text}
            </div>
          )}
          <form onSubmit={handleCreateUser}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <FormField
                label="Login Username"
                required
                value={newUser.username}
                onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
              />
              <FormField
                label="Full Name & Designation"
                required
                value={newUser.full_name}
                onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
              />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <FormField
                label="Corporate Email"
                type="email"
                required
                value={newUser.email}
                onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
              />
              <FormField
                label="Temporary Password"
                type="password"
                required
                value={newUser.password}
                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
              />
            </div>
            <FormField
              label="Statutory Role"
              as="select"
              required
              value={newUser.role}
              onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
              options={[
                { value: 'admin', label: 'System Administrator' },
                { value: 'mine_manager', label: 'Colliery Mine Manager' },
                { value: 'safety_officer', label: 'Statutory Safety Officer' },
                { value: 'inspector', label: 'DGMS / Regulatory Inspector' },
                { value: 'viewer', label: 'Auditor / Viewer (Read-only)' },
              ]}
            />
            <button type="submit" className={styles.submitBtn}>
              Provision User Account
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default SettingsPage;
