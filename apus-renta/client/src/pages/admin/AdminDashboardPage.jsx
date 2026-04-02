import React, { useState, useEffect } from 'react';
import { Users, UserCheck, UserX, DollarSign } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import api from '../../services/api';

const PLAN_COLORS = {
  FREE: '#9CA3AF',
  BASIC: '#2E86C1',
  PRO: '#27AE60',
  ENTERPRISE: '#8E44AD',
};

const PLAN_BADGE = {
  FREE: 'bg-gray-100 text-gray-700',
  BASIC: 'bg-blue-100 text-blue-700',
  PRO: 'bg-green-100 text-green-700',
  ENTERPRISE: 'bg-purple-100 text-purple-700',
};

const STATUS_BADGE = {
  ACTIVE: 'bg-green-100 text-green-700',
  SUSPENDED: 'bg-yellow-100 text-yellow-700',
  INACTIVE: 'bg-red-100 text-red-700',
};

function formatCOP(value) {
  if (value == null) return '$0';
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

function formatDate(dateStr) {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleDateString('es-CO', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export default function AdminDashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true);
        const res = await api.get('/superadmin/dashboard');
        setData(res.data.data || res.data);
      } catch (err) {
        setError(err.response?.data?.message || 'Error al cargar el dashboard');
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-[#2E86C1] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-xl">
        <p className="font-medium">Error</p>
        <p className="text-sm mt-1">{error}</p>
      </div>
    );
  }

  const stats = data?.stats || {};
  const tenants = data?.recentTenants || [];
  const planDistribution = data?.planDistribution || [];

  const pieData = planDistribution.map((item) => ({
    name: item.plan || item.name,
    value: item.count || item.value || 0,
  }));

  const kpis = [
    {
      label: 'Total Clientes',
      value: stats.totalTenants ?? 0,
      icon: Users,
      color: '#1B4F72',
      bg: '#D6EAF8',
    },
    {
      label: 'Activos',
      value: stats.activeTenants ?? 0,
      icon: UserCheck,
      color: '#27AE60',
      bg: '#D5F5E3',
    },
    {
      label: 'Suspendidos',
      value: stats.suspendedTenants ?? 0,
      icon: UserX,
      color: '#F39C12',
      bg: '#FEF9E7',
    },
    {
      label: 'Ingresos Estimados',
      value: formatCOP(stats.estimatedRevenue),
      icon: DollarSign,
      color: '#2E86C1',
      bg: '#D6EAF8',
      isCurrency: true,
    },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#2C3E50]">Admin Dashboard</h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div
              key={kpi.label}
              className="bg-white rounded-xl border border-gray-200 p-5 flex items-center gap-4"
            >
              <div
                className="w-12 h-12 rounded-xl flex items-center justify-center shrink-0"
                style={{ backgroundColor: kpi.bg }}
              >
                <Icon className="w-6 h-6" style={{ color: kpi.color }} />
              </div>
              <div>
                <p className="text-sm text-gray-500">{kpi.label}</p>
                <p className="text-xl font-bold" style={{ color: kpi.color }}>
                  {kpi.isCurrency ? kpi.value : kpi.value.toLocaleString('es-CO')}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Chart + Table */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pie Chart */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 lg:col-span-1">
          <h2 className="text-lg font-semibold text-[#2C3E50] mb-4">
            Distribucion por Plan
          </h2>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {pieData.map((entry) => (
                    <Cell
                      key={entry.name}
                      fill={PLAN_COLORS[entry.name] || '#9CA3AF'}
                    />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-sm text-center py-10">Sin datos</p>
          )}
        </div>

        {/* Recent Tenants Table */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 lg:col-span-2 overflow-x-auto">
          <h2 className="text-lg font-semibold text-[#2C3E50] mb-4">
            Clientes Recientes
          </h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b border-gray-100">
                <th className="pb-3 font-medium">Nombre</th>
                <th className="pb-3 font-medium">Propietario</th>
                <th className="pb-3 font-medium">Plan</th>
                <th className="pb-3 font-medium">Estado</th>
                <th className="pb-3 font-medium">Propiedades</th>
                <th className="pb-3 font-medium">Usuarios</th>
                <th className="pb-3 font-medium">Fecha</th>
              </tr>
            </thead>
            <tbody>
              {tenants.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center text-gray-400 py-8">
                    No hay clientes recientes
                  </td>
                </tr>
              ) : (
                tenants.map((t) => (
                  <tr
                    key={t.id || t._id}
                    className="border-b border-gray-50 hover:bg-gray-50"
                  >
                    <td className="py-3 font-medium text-[#2C3E50]">{t.name}</td>
                    <td className="py-3 text-gray-600">{t.ownerName || t.ownerEmail || '-'}</td>
                    <td className="py-3">
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          PLAN_BADGE[t.plan] || PLAN_BADGE.FREE
                        }`}
                      >
                        {t.plan}
                      </span>
                    </td>
                    <td className="py-3">
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          STATUS_BADGE[t.status] || 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {t.status}
                      </span>
                    </td>
                    <td className="py-3 text-gray-600">{t.propertyCount ?? t.properties ?? 0}</td>
                    <td className="py-3 text-gray-600">{t.userCount ?? t.users ?? 0}</td>
                    <td className="py-3 text-gray-500">{formatDate(t.createdAt)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
