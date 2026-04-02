import React, { useState, useEffect, useCallback } from 'react';
import {
  Building2,
  DollarSign,
  AlertTriangle,
  Bell,
  TrendingUp,
  Calendar,
  CreditCard,
  MessageSquare,
  RefreshCw,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import api from '../../services/api';
import Card from '../../components/ui/Card';
import StatusBadge from '../../components/ui/StatusBadge';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatCurrency(value) {
  if (value == null) return '$0';
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

function formatPercent(value) {
  if (value == null) return '0%';
  return `${Number(value).toFixed(1)}%`;
}

function formatDate(dateStr) {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleDateString('es-CO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

function formatShortMonth(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString('es-CO', { month: 'short' }).replace('.', '');
}

// ---------------------------------------------------------------------------
// Skeleton Loader
// ---------------------------------------------------------------------------

function Skeleton({ className = '' }) {
  return (
    <div
      className={`animate-pulse rounded-lg bg-gray-200 ${className}`}
    />
  );
}

function KpiSkeleton() {
  return (
    <div className="bg-white shadow-md rounded-xl p-6">
      <div className="flex items-center justify-between mb-3">
        <Skeleton className="h-4 w-28" />
        <Skeleton className="h-10 w-10 rounded-lg" />
      </div>
      <Skeleton className="h-8 w-32 mb-1" />
      <Skeleton className="h-3 w-20" />
    </div>
  );
}

function ChartSkeleton() {
  return (
    <div className="bg-white shadow-md rounded-xl p-6">
      <Skeleton className="h-5 w-48 mb-6" />
      <Skeleton className="h-56 w-full" />
    </div>
  );
}

function TableSkeleton({ rows = 3 }) {
  return (
    <div className="bg-white shadow-md rounded-xl p-6">
      <Skeleton className="h-5 w-44 mb-5" />
      <div className="space-y-3">
        {Array.from({ length: rows }).map((_, i) => (
          <Skeleton key={i} className="h-10 w-full" />
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// KPI Card
// ---------------------------------------------------------------------------

const KPI_THEMES = {
  blue: {
    bg: 'bg-[#D6EAF8]',
    icon: 'text-[#1B4F72]',
    value: 'text-[#1B4F72]',
  },
  green: {
    bg: 'bg-green-50',
    icon: 'text-[#27AE60]',
    value: 'text-[#27AE60]',
  },
  red: {
    bg: 'bg-red-50',
    icon: 'text-[#E74C3C]',
    value: 'text-[#E74C3C]',
  },
  warning: {
    bg: 'bg-amber-50',
    icon: 'text-[#F39C12]',
    value: 'text-[#F39C12]',
  },
};

function KpiCard({ title, value, subtitle, icon: Icon, theme = 'blue' }) {
  const t = KPI_THEMES[theme] || KPI_THEMES.blue;
  return (
    <div className="bg-white shadow-md rounded-xl p-6 flex items-start justify-between">
      <div className="min-w-0">
        <p className="text-sm font-medium text-gray-500 truncate">{title}</p>
        <p className={`text-2xl font-bold mt-1 ${t.value}`}>{value}</p>
        {subtitle && (
          <p className="text-xs text-gray-400 mt-1">{subtitle}</p>
        )}
      </div>
      <div
        className={`flex-shrink-0 w-12 h-12 rounded-xl ${t.bg} flex items-center justify-center`}
      >
        <Icon className={`w-6 h-6 ${t.icon}`} />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Custom Recharts Tooltip
// ---------------------------------------------------------------------------

function ChartTooltipContent({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg px-4 py-3 text-sm">
      <p className="font-medium text-[#2C3E50] mb-1">{label}</p>
      {payload.map((entry, i) => (
        <p key={i} style={{ color: entry.color }} className="flex justify-between gap-4">
          <span>{entry.name}:</span>
          <span className="font-semibold">{formatCurrency(entry.value)}</span>
        </p>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboard = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/reports/dashboard');
      setData(res.data.data || res.data);
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setError('No se pudo cargar el dashboard. Intente de nuevo.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  // ------ LOADING STATE ------
  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-7 w-40 mb-2" />
            <Skeleton className="h-4 w-64" />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <KpiSkeleton key={i} />
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartSkeleton />
          <TableSkeleton rows={4} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TableSkeleton rows={3} />
          <TableSkeleton rows={3} />
        </div>
      </div>
    );
  }

  // ------ ERROR STATE ------
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <AlertTriangle className="w-12 h-12 text-[#E74C3C] mb-4" />
        <p className="text-lg font-medium text-[#2C3E50] mb-2">{error}</p>
        <button
          onClick={fetchDashboard}
          className="inline-flex items-center gap-2 text-sm text-[#2E86C1] hover:text-[#1B4F72] font-medium transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Reintentar
        </button>
      </div>
    );
  }

  // ------ SAFE DESTRUCTURE ------
  const {
    occupancyRate = 0,
    monthlyCollection = 0,
    totalDelinquency = 0,
    activeAlerts = 0,
    monthlyIncomeTrend = [],
    properties = [],
    expiringLeases = [],
    recentPayments = [],
    openPqrs = {},
  } = data || {};

  // Prepare chart data
  const chartData = (monthlyIncomeTrend || []).map((item) => ({
    name: formatShortMonth(item.month || item.date),
    Recaudado: item.actual ?? item.collected ?? 0,
    Esperado: item.expected ?? 0,
  }));

  // PQRS summary
  const pqrsEntries = Object.entries(openPqrs || {});
  const totalPqrs = pqrsEntries.reduce((sum, [, count]) => sum + count, 0);

  const PQRS_COLORS = {
    QUEJA: 'bg-red-100 text-red-800',
    PETICION: 'bg-blue-100 text-blue-800',
    RECLAMO: 'bg-amber-100 text-amber-800',
    SUGERENCIA: 'bg-green-100 text-green-800',
  };

  return (
    <div className="space-y-6">
      {/* ---- HEADER ---- */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold text-[#2C3E50]">Dashboard</h2>
          <p className="text-sm text-gray-500">
            Resumen general de su portafolio inmobiliario
          </p>
        </div>
        <button
          onClick={fetchDashboard}
          className="inline-flex items-center gap-2 text-sm text-[#2E86C1] hover:text-[#1B4F72] font-medium transition-colors self-start"
        >
          <RefreshCw className="w-4 h-4" />
          Actualizar
        </button>
      </div>

      {/* ---- ROW 1: KPI CARDS ---- */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Tasa de Ocupacion"
          value={formatPercent(occupancyRate)}
          subtitle="del portafolio"
          icon={Building2}
          theme="blue"
        />
        <KpiCard
          title="Recaudo del Mes"
          value={formatCurrency(monthlyCollection)}
          subtitle="mes actual"
          icon={DollarSign}
          theme="green"
        />
        <KpiCard
          title="Mora Acumulada"
          value={formatCurrency(totalDelinquency)}
          subtitle="pendiente"
          icon={AlertTriangle}
          theme="red"
        />
        <KpiCard
          title="Alertas Activas"
          value={activeAlerts}
          subtitle="requieren atencion"
          icon={Bell}
          theme="warning"
        />
      </div>

      {/* ---- ROW 2: CHART + PROPERTY STATUS ---- */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Income Trend */}
        <Card title="Tendencia de Ingresos (6 meses)">
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRecaudado" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2E86C1" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#2E86C1" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorEsperado" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#D6EAF8" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#D6EAF8" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 12, fill: '#6b7280' }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 12, fill: '#6b7280' }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) =>
                    v >= 1_000_000
                      ? `${(v / 1_000_000).toFixed(1)}M`
                      : v >= 1_000
                      ? `${(v / 1_000).toFixed(0)}K`
                      : v
                  }
                />
                <Tooltip content={<ChartTooltipContent />} />
                <Legend
                  verticalAlign="top"
                  align="right"
                  iconType="line"
                  wrapperStyle={{ fontSize: 12 }}
                />
                <Area
                  type="monotone"
                  dataKey="Esperado"
                  stroke="#93C5FD"
                  strokeWidth={2}
                  strokeDasharray="6 3"
                  fill="url(#colorEsperado)"
                />
                <Area
                  type="monotone"
                  dataKey="Recaudado"
                  stroke="#2E86C1"
                  strokeWidth={2}
                  fill="url(#colorRecaudado)"
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-56 text-gray-400 text-sm">
              No hay datos de ingresos disponibles
            </div>
          )}
        </Card>

        {/* Property Status */}
        <Card title="Estado de Propiedades">
          {properties.length > 0 ? (
            <div className="divide-y divide-gray-100 max-h-[300px] overflow-y-auto">
              {properties.map((prop, idx) => (
                <div
                  key={prop.id || idx}
                  className="flex items-center justify-between py-3 first:pt-0 last:pb-0"
                >
                  <div className="min-w-0 mr-3">
                    <p className="text-sm font-medium text-[#2C3E50] truncate">
                      {prop.name || prop.address || `Propiedad ${idx + 1}`}
                    </p>
                    <p className="text-xs text-gray-400 truncate">
                      {prop.tenantName || prop.tenant || 'Sin inquilino'}
                    </p>
                  </div>
                  <StatusBadge status={prop.status || (prop.tenantName ? 'OCUPADO' : 'DISPONIBLE')} />
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-56 text-gray-400 text-sm">
              No hay propiedades registradas
            </div>
          )}
        </Card>
      </div>

      {/* ---- ROW 3: EXPIRING LEASES + RECENT PAYMENTS ---- */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Expiring Leases */}
        <Card>
          <div className="flex items-center gap-2 mb-4">
            <Calendar className="w-5 h-5 text-[#F39C12]" />
            <h3 className="text-lg font-semibold text-[#2C3E50]">
              Contratos por Vencer
            </h3>
          </div>
          {expiringLeases.length > 0 ? (
            <div className="overflow-x-auto rounded-lg border border-gray-200">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 text-left">
                    <th className="px-4 py-2.5 font-medium text-gray-600">Propiedad</th>
                    <th className="px-4 py-2.5 font-medium text-gray-600">Inquilino</th>
                    <th className="px-4 py-2.5 font-medium text-gray-600">Vencimiento</th>
                  </tr>
                </thead>
                <tbody>
                  {expiringLeases.map((lease, idx) => (
                    <tr
                      key={lease.id || idx}
                      className="border-t border-gray-100 hover:bg-[#D6EAF8]/20 transition-colors"
                    >
                      <td className="px-4 py-2.5 text-[#2C3E50] whitespace-nowrap">
                        {lease.propertyName || lease.property || '-'}
                      </td>
                      <td className="px-4 py-2.5 text-gray-600 whitespace-nowrap">
                        {lease.tenantName || lease.tenant || '-'}
                      </td>
                      <td className="px-4 py-2.5 whitespace-nowrap">
                        <span className="text-[#F39C12] font-medium">
                          {formatDate(lease.endDate || lease.expirationDate)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-gray-400 py-6 text-center">
              No hay contratos proximos a vencer
            </p>
          )}
        </Card>

        {/* Recent Payments */}
        <Card>
          <div className="flex items-center gap-2 mb-4">
            <CreditCard className="w-5 h-5 text-[#27AE60]" />
            <h3 className="text-lg font-semibold text-[#2C3E50]">
              Pagos Recientes
            </h3>
          </div>
          {recentPayments.length > 0 ? (
            <div className="overflow-x-auto rounded-lg border border-gray-200">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 text-left">
                    <th className="px-4 py-2.5 font-medium text-gray-600">Propiedad</th>
                    <th className="px-4 py-2.5 font-medium text-gray-600">Monto</th>
                    <th className="px-4 py-2.5 font-medium text-gray-600">Fecha</th>
                    <th className="px-4 py-2.5 font-medium text-gray-600">Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {recentPayments.slice(0, 5).map((pay, idx) => (
                    <tr
                      key={pay.id || idx}
                      className="border-t border-gray-100 hover:bg-[#D6EAF8]/20 transition-colors"
                    >
                      <td className="px-4 py-2.5 text-[#2C3E50] whitespace-nowrap">
                        {pay.propertyName || pay.property || '-'}
                      </td>
                      <td className="px-4 py-2.5 font-medium text-[#2C3E50] whitespace-nowrap">
                        {formatCurrency(pay.amount)}
                      </td>
                      <td className="px-4 py-2.5 text-gray-600 whitespace-nowrap">
                        {formatDate(pay.date || pay.paymentDate)}
                      </td>
                      <td className="px-4 py-2.5 whitespace-nowrap">
                        <StatusBadge status={pay.status || 'PAGADO'} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-gray-400 py-6 text-center">
              No hay pagos recientes
            </p>
          )}
        </Card>
      </div>

      {/* ---- ROW 4: OPEN PQRS ---- */}
      <Card>
        <div className="flex items-center gap-2 mb-4">
          <MessageSquare className="w-5 h-5 text-[#2E86C1]" />
          <h3 className="text-lg font-semibold text-[#2C3E50]">
            PQRS Abiertas
          </h3>
          {totalPqrs > 0 && (
            <span className="ml-2 px-2 py-0.5 text-xs font-medium rounded-full bg-[#D6EAF8] text-[#1B4F72]">
              {totalPqrs}
            </span>
          )}
        </div>

        {pqrsEntries.length > 0 ? (
          <div className="flex flex-wrap gap-3">
            {pqrsEntries.map(([type, count]) => {
              const key = type.toUpperCase();
              const colorClass = PQRS_COLORS[key] || 'bg-gray-100 text-gray-800';
              return (
                <div
                  key={type}
                  className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg ${colorClass}`}
                >
                  <span className="text-sm font-medium capitalize">
                    {type.toLowerCase().replace(/_/g, ' ')}
                  </span>
                  <span className="text-lg font-bold">{count}</span>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-sm text-gray-400 py-4 text-center">
            No hay PQRS abiertas
          </p>
        )}
      </Card>
    </div>
  );
}
