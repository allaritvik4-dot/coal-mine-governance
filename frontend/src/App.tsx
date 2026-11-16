import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import ProtectedRoute from '@/components/ProtectedRoute';
import LoginPage from '@/pages/LoginPage';
import DashboardPage from '@/pages/DashboardPage';
import MinesPage from '@/pages/MinesPage';
import InspectionsPage from '@/pages/InspectionsPage';
import HazardsPage from '@/pages/HazardsPage';
import IncidentsPage from '@/pages/IncidentsPage';
import EquipmentPage from '@/pages/EquipmentPage';
import TrainingPage from '@/pages/TrainingPage';
import CompliancePage from '@/pages/CompliancePage';
import AssistantPage from '@/pages/AssistantPage';
import ReportsPage from '@/pages/ReportsPage';
import AuditLogPage from '@/pages/AuditLogPage';
import PrivacyPage from '@/pages/PrivacyPage';
import TermsPage from '@/pages/TermsPage';
import SettingsPage from '@/pages/SettingsPage';
import ModelDiagnosticsPage from '@/pages/ModelDiagnosticsPage';

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/privacy" element={<PrivacyPage />} />
      <Route path="/terms" element={<TermsPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Layout>
              <DashboardPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/mines"
        element={
          <ProtectedRoute>
            <Layout>
              <MinesPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/inspections"
        element={
          <ProtectedRoute>
            <Layout>
              <InspectionsPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/hazards"
        element={
          <ProtectedRoute>
            <Layout>
              <HazardsPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/incidents"
        element={
          <ProtectedRoute>
            <Layout>
              <IncidentsPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/equipment"
        element={
          <ProtectedRoute>
            <Layout>
              <EquipmentPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/training"
        element={
          <ProtectedRoute>
            <Layout>
              <TrainingPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/compliance"
        element={
          <ProtectedRoute>
            <Layout>
              <CompliancePage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/ai-model"
        element={
          <ProtectedRoute>
            <Layout>
              <ModelDiagnosticsPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/assistant"
        element={
          <ProtectedRoute>
            <Layout>
              <AssistantPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/reports"
        element={
          <ProtectedRoute>
            <Layout>
              <ReportsPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/audit-log"
        element={
          <ProtectedRoute>
            <Layout>
              <AuditLogPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <Layout>
              <SettingsPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
