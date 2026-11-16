import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Search,
  Shield,
  AlertTriangle,
  FileWarning,
  Wrench,
  GraduationCap,
  CheckSquare,
  MessageSquare,
  BarChart3,
  ClipboardList,
  Settings,
  LogOut,
  Cpu,
  ChevronDown,
  Menu,
  X,
} from 'lucide-react';
import { getMe, listMines } from '@/services/api';
import type { User, Mine } from '@/types';
import FloatingAiAssistant from '@/components/FloatingAiAssistant';
import styles from './Layout.module.css';

interface LayoutProps {
  children: React.ReactNode;
}

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/mines', icon: Search, label: 'Mines' },
  { to: '/inspections', icon: Shield, label: 'Inspections' },
  { to: '/hazards', icon: AlertTriangle, label: 'Hazards' },
  { to: '/incidents', icon: FileWarning, label: 'Incidents' },
  { to: '/equipment', icon: Wrench, label: 'Equipment' },
  { to: '/training', icon: GraduationCap, label: 'Training' },
  { to: '/compliance', icon: CheckSquare, label: 'Compliance' },
  { to: '/ai-model', icon: Cpu, label: 'AI Safety Model' },
  { to: '/assistant', icon: MessageSquare, label: 'Assistant' },
  { to: '/reports', icon: BarChart3, label: 'Reports' },
  { to: '/audit-log', icon: ClipboardList, label: 'Audit Log' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState<User | null>(null);
  const [mines, setMines] = useState<Mine[]>([]);
  const [selectedMineId, setSelectedMineId] = useState<string>(
    localStorage.getItem('selectedMineId') || ''
  );
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const userData = await getMe();
        setUser(userData);
        const minesRes = await listMines();
        setMines(minesRes.data);
        if (!selectedMineId && minesRes.data.length > 0) {
          const defaultId = String(minesRes.data[0].id);
          setSelectedMineId(defaultId);
          localStorage.setItem('selectedMineId', defaultId);
        }
      } catch {
        // handled by interceptor
      }
    };
    fetchData();
  }, []);

  const handleMineChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const id = e.target.value;
    setSelectedMineId(id);
    localStorage.setItem('selectedMineId', id);
    window.dispatchEvent(new Event('mineChanged'));
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('selectedMineId');
    navigate('/login');
  };

  return (
    <div className={styles.layout}>
      <aside className={`${styles.sidebar} ${sidebarOpen ? styles.open : styles.closed}`}>
        <div className={styles.sidebarHeader}>
          <h1 className={styles.logo}>Coal Mine Governance</h1>
          <button
            className={styles.toggleBtn}
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>
        <nav className={styles.nav}>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `${styles.navItem} ${isActive ? styles.navItemActive : ''}`
              }
            >
              <item.icon size={18} />
              {sidebarOpen && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>
        <div className={styles.sidebarFooter}>
          <button className={styles.logoutBtn} onClick={handleLogout}>
            <LogOut size={18} />
            {sidebarOpen && <span>Logout</span>}
          </button>
        </div>
      </aside>

      <div className={styles.main}>
        <header className={styles.topbar}>
          <button
            className={styles.menuBtn}
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="Toggle sidebar"
          >
            <Menu size={20} />
          </button>
          <div className={styles.topbarContent}>
            <div className={styles.mineSelector}>
              <label htmlFor="mine-select">Mine:</label>
              <select
                id="mine-select"
                value={selectedMineId}
                onChange={handleMineChange}
                className={styles.mineSelect}
              >
                <option value="">All Mines</option>
                {mines.map((mine) => (
                  <option key={mine.id} value={mine.id}>
                    {mine.name}
                  </option>
                ))}
              </select>
              <ChevronDown size={14} className={styles.selectIcon} />
            </div>
            {user && (
              <div className={styles.userInfo}>
                <span className={styles.userName}>{user.full_name}</span>
                <span className={styles.userRole}>{user.role.replace('_', ' ')}</span>
              </div>
            )}
          </div>
        </header>
        <main className={styles.content}>
          {children}
          <FloatingAiAssistant />
        </main>
      </div>
    </div>
  );
};

export default Layout;
