import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/layout/Layout';

// Lazy-load page components
const LoginPage = React.lazy(() => import('./pages/LoginPage'));
const DashboardPage = React.lazy(() => import('./pages/DashboardPage'));
const PropertiesPage = React.lazy(() => import('./pages/PropertiesPage'));
const TenantsPage = React.lazy(() => import('./pages/TenantsPage'));
const LeasesPage = React.lazy(() => import('./pages/LeasesPage'));
const PaymentsPage = React.lazy(() => import('./pages/PaymentsPage'));
const UtilitiesPage = React.lazy(() => import('./pages/UtilitiesPage'));
const PQRSPage = React.lazy(() => import('./pages/PQRSPage'));
const ReportsPage = React.lazy(() => import('./pages/ReportsPage'));
const AuditPage = React.lazy(() => import('./pages/AuditPage'));
const SettingsPage = React.lazy(() => import('./pages/SettingsPage'));
const AdminDashboardPage = React.lazy(() => import('./pages/admin/AdminDashboardPage'));
const AdminTenantsPage = React.lazy(() => import('./pages/admin/AdminTenantsPage'));
const AdminPlansPage = React.lazy(() => import('./pages/admin/AdminPlansPage'));

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="w-8 h-8 border-4 border-[#2E86C1] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function PublicRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="w-8 h-8 border-4 border-[#2E86C1] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

function AppRoutes() {
  return (
    <React.Suspense
      fallback={
        <div className="flex items-center justify-center min-h-screen bg-gray-50">
          <div className="w-8 h-8 border-4 border-[#2E86C1] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <Routes>
        {/* Public */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />

        {/* Protected */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="properties" element={<PropertiesPage />} />
          <Route path="tenants" element={<TenantsPage />} />
          <Route path="leases" element={<LeasesPage />} />
          <Route path="payments" element={<PaymentsPage />} />
          <Route path="utilities" element={<UtilitiesPage />} />
          <Route path="pqrs" element={<PQRSPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="audit" element={<AuditPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="admin" element={<AdminDashboardPage />} />
          <Route path="admin/tenants" element={<AdminTenantsPage />} />
          <Route path="admin/plans" element={<AdminPlansPage />} />
        </Route>

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </React.Suspense>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
