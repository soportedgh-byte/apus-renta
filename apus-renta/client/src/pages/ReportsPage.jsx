import React, { useState, useEffect, useCallback } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts';
import { Download, Filter, TrendingUp, Home, CreditCard, Calendar } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Table from '../components/ui/Table';
import StatusBadge from '../components/ui/StatusBadge';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';

const CHART_COLORS = ['#1B4F72', '#2E86C1', '#27AE60', '#F39C12', '#E74C3C', '#8E44AD', '#16A085', '#D35400'];
const PIE_COLORS = { OCUPADO: '#27AE60', DISPONIBLE: '#2E86C1', MANTENIMIENTO: '#F39C12' };

function TabButton({ active, onClick, icon: Icon, children }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
        active
          ? 'bg-white text-[#1B4F72] shadow-sm'
          : 'text-gray-600 hover:text-[#1B4F72]'
      }`}
    >
      <Icon className="w-4 h-4" />
      {children}
    </button>
  );
}

export default function ReportsPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('ingresos');
  const [loading, setLoading] = useState(false);

  // Ingresos state
  const [incomeData, setIncomeData] = useState({ chart: [], summary: [] });
  const [incomeDates, setIncomeDates] = useState({
    startDate: new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
  });

  // Ocupacion state
  const [occupancyData, setOccupancyData] = useState({ pie: [], table: [] });

  // Pagos state
  const [paymentsData, setPaymentsData] = useState([]);
  const [paymentsPage, setPaymentsPage] = useState(1);
  const [paymentsTotalPages, setPaymentsTotalPages] = useState(1);
  const [paymentsFilters, setPaymentsFilters] = useState({
    startDate: '',
    endDate: '',
    status: '',
    propertyId: '',
  });
  const [paymentsTotals, setPaymentsTotals] = useState({ total: 0, count: 0 });
  const [properties, setProperties] = useState([]);

  const fetchProperties = useCallback(async () => {
    try {
      const { data } = await api.get('/properties', { params: { limit: 200 } });
      const list = data.data?.items || data.data || [];
      setProperties(Array.isArray(list) ? list : []);
    } catch {
      setProperties([]);
    }
  }, []);

  useEffect(() => { fetchProperties(); }, [fetchProperties]);

  // INGRESOS
  const fetchIncome = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/reports/income', {
        params: { startDate: incomeDates.startDate, endDate: incomeDates.endDate },
      });
      const result = data.data || data;
      setIncomeData({
        chart: result.chart || result.monthly || [],
        summary: result.summary || result.byProperty || [],
      });
    } catch {
      setIncomeData({ chart: [], summary: [] });
    } finally {
      setLoading(false);
    }
  }, [incomeDates]);

  // OCUPACION
  const fetchOccupancy = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/reports/occupancy');
      const result = data.data || data;
      const pieData = [];
      const tableData = result.properties || result.table || result || [];

      if (Array.isArray(tableData)) {
        const counts = { OCUPADO: 0, DISPONIBLE: 0, MANTENIMIENTO: 0 };
        tableData.forEach((p) => {
          const s = (p.status || '').toUpperCase();
          if (counts[s] !== undefined) counts[s]++;
        });
        Object.entries(counts).forEach(([name, value]) => {
          if (value > 0) pieData.push({ name, value });
        });
      }

      setOccupancyData({ pie: result.pie || pieData, table: Array.isArray(tableData) ? tableData : [] });
    } catch {
      setOccupancyData({ pie: [], table: [] });
    } finally {
      setLoading(false);
    }
  }, []);

  // PAGOS
  const fetchPayments = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page: paymentsPage, limit: 15 };
      if (paymentsFilters.startDate) params.startDate = paymentsFilters.startDate;
      if (paymentsFilters.endDate) params.endDate = paymentsFilters.endDate;
      if (paymentsFilters.status) params.status = paymentsFilters.status;
      if (paymentsFilters.propertyId) params.propertyId = paymentsFilters.propertyId;
      const { data } = await api.get('/reports/payments', { params });
      const result = data.data || data;
      const items = result.items || result.payments || [];
      setPaymentsData(Array.isArray(items) ? items : []);
      setPaymentsTotalPages(result.totalPages || 1);
      setPaymentsTotals({
        total: result.totals?.total || result.total || 0,
        count: result.totals?.count || result.count || items.length,
      });
    } catch {
      setPaymentsData([]);
    } finally {
      setLoading(false);
    }
  }, [paymentsPage, paymentsFilters]);

  useEffect(() => {
    if (activeTab === 'ingresos') fetchIncome();
    else if (activeTab === 'ocupacion') fetchOccupancy();
    else if (activeTab === 'pagos') fetchPayments();
  }, [activeTab, fetchIncome, fetchOccupancy, fetchPayments]);

  const handleExport = async (type) => {
    try {
      const response = await api.get(`/reports/export/${type}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      window.open(url, '_blank');
    } catch {
      // Error handled by interceptor
    }
  };

  const propertyOptions = properties.map((p) => ({
    value: p._id || p.id,
    label: p.name || p.address || `Propiedad ${p._id || p.id}`,
  }));

  const incomeColumns = [
    { key: 'propertyName', label: 'Propiedad', render: (val, row) => val || row.property?.name || '-' },
    { key: 'totalReceived', label: 'Total Recibido', render: (val) => val != null ? `$${Number(val).toLocaleString('es-CO')}` : '$0' },
    { key: 'expected', label: 'Esperado', render: (val) => val != null ? `$${Number(val).toLocaleString('es-CO')}` : '$0' },
    {
      key: 'difference',
      label: 'Diferencia',
      render: (val, row) => {
        const diff = val ?? ((row.totalReceived || 0) - (row.expected || 0));
        const color = diff >= 0 ? '#27AE60' : '#E74C3C';
        return <span style={{ color, fontWeight: 600 }}>${Number(diff).toLocaleString('es-CO')}</span>;
      },
    },
  ];

  const occupancyColumns = [
    { key: 'propertyName', label: 'Propiedad', render: (val, row) => val || row.name || '-' },
    { key: 'status', label: 'Estado', render: (val) => <StatusBadge status={val} /> },
    { key: 'currentTenant', label: 'Arrendatario Actual', render: (val, row) => val || row.tenant?.name || '-' },
    { key: 'leaseEndDate', label: 'Fin de Contrato', render: (val) => val ? new Date(val).toLocaleDateString('es-CO') : '-' },
  ];

  const paymentsColumns = [
    { key: 'date', label: 'Fecha', render: (val, row) => (val || row.createdAt) ? new Date(val || row.createdAt).toLocaleDateString('es-CO') : '-' },
    { key: 'propertyName', label: 'Propiedad', render: (val, row) => val || row.property?.name || '-' },
    { key: 'tenantName', label: 'Arrendatario', render: (val, row) => val || row.tenant?.name || '-' },
    { key: 'amount', label: 'Monto', render: (val) => val != null ? `$${Number(val).toLocaleString('es-CO')}` : '$0' },
    { key: 'status', label: 'Estado', render: (val) => <StatusBadge status={val} /> },
    { key: 'method', label: 'Metodo', render: (val) => val || '-' },
  ];

  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
      <div className="bg-white shadow-lg rounded-lg p-3 border border-gray-200">
        <p className="text-sm font-medium text-[#2C3E50] mb-1">{label}</p>
        {payload.map((entry, idx) => (
          <p key={idx} className="text-xs" style={{ color: entry.color }}>
            {entry.name}: ${Number(entry.value).toLocaleString('es-CO')}
          </p>
        ))}
      </div>
    );
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-[#2C3E50] mb-6">Reportes</h2>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 rounded-lg p-1 w-fit">
        <TabButton active={activeTab === 'ingresos'} onClick={() => setActiveTab('ingresos')} icon={TrendingUp}>
          Ingresos
        </TabButton>
        <TabButton active={activeTab === 'ocupacion'} onClick={() => setActiveTab('ocupacion')} icon={Home}>
          Ocupacion
        </TabButton>
        <TabButton active={activeTab === 'pagos'} onClick={() => setActiveTab('pagos')} icon={CreditCard}>
          Pagos
        </TabButton>
      </div>

      {/* INGRESOS TAB */}
      {activeTab === 'ingresos' && (
        <div className="space-y-6">
          <Card>
            <div className="flex flex-wrap items-end gap-4 mb-6">
              <Input
                label="Fecha Inicio"
                type="date"
                value={incomeDates.startDate}
                onChange={(e) => setIncomeDates((p) => ({ ...p, startDate: e.target.value }))}
                className="w-48"
              />
              <Input
                label="Fecha Fin"
                type="date"
                value={incomeDates.endDate}
                onChange={(e) => setIncomeDates((p) => ({ ...p, endDate: e.target.value }))}
                className="w-48"
              />
              <Button variant="outline" onClick={() => handleExport('income')}>
                <Download className="w-4 h-4" />
                Exportar PDF
              </Button>
            </div>

            {loading ? (
              <div className="flex justify-center py-12">
                <div className="w-6 h-6 border-2 border-[#2E86C1] border-t-transparent rounded-full animate-spin" />
              </div>
            ) : incomeData.chart.length > 0 ? (
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={incomeData.chart}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#6B7280" />
                  <YAxis tick={{ fontSize: 12 }} stroke="#6B7280" tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  {incomeData.chart[0] && Object.keys(incomeData.chart[0])
                    .filter((k) => k !== 'month' && k !== 'period')
                    .map((key, idx) => (
                      <Bar
                        key={key}
                        dataKey={key}
                        stackId="income"
                        fill={CHART_COLORS[idx % CHART_COLORS.length]}
                        radius={idx === 0 ? [0, 0, 4, 4] : [4, 4, 0, 0]}
                      />
                    ))}
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-8">No hay datos de ingresos para el periodo seleccionado</p>
            )}
          </Card>

          {incomeData.summary.length > 0 && (
            <Table
              columns={incomeColumns}
              data={incomeData.summary}
              emptyMessage="Sin datos de resumen"
            />
          )}
        </div>
      )}

      {/* OCUPACION TAB */}
      {activeTab === 'ocupacion' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card title="Distribucion de Ocupacion">
              {loading ? (
                <div className="flex justify-center py-12">
                  <div className="w-6 h-6 border-2 border-[#2E86C1] border-t-transparent rounded-full animate-spin" />
                </div>
              ) : occupancyData.pie.length > 0 ? (
                <div>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={occupancyData.pie}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={4}
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {occupancyData.pie.map((entry, idx) => (
                          <Cell
                            key={idx}
                            fill={PIE_COLORS[entry.name] || CHART_COLORS[idx % CHART_COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => [value, 'Propiedades']} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="flex justify-center gap-6 mt-2">
                    {occupancyData.pie.map((entry, idx) => (
                      <span key={idx} className="flex items-center gap-1.5 text-xs text-gray-600">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: PIE_COLORS[entry.name] || CHART_COLORS[idx] }}
                        />
                        {entry.name} ({entry.value})
                      </span>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">No hay datos de ocupacion</p>
              )}
            </Card>

            <Card title="Resumen por Propiedad">
              {occupancyData.pie.map((entry, idx) => (
                <div key={idx} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                  <span className="flex items-center gap-2 text-sm">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: PIE_COLORS[entry.name] || CHART_COLORS[idx] }}
                    />
                    {entry.name}
                  </span>
                  <span className="text-lg font-bold text-[#2C3E50]">{entry.value}</span>
                </div>
              ))}
            </Card>
          </div>

          <Table
            columns={occupancyColumns}
            data={occupancyData.table}
            loading={loading}
            emptyMessage="No hay datos de propiedades"
          />
        </div>
      )}

      {/* PAGOS TAB */}
      {activeTab === 'pagos' && (
        <div className="space-y-6">
          <Card>
            <div className="flex items-center gap-2 mb-3">
              <Filter className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-600">Filtros</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Input
                label="Fecha Inicio"
                type="date"
                value={paymentsFilters.startDate}
                onChange={(e) => { setPaymentsFilters((p) => ({ ...p, startDate: e.target.value })); setPaymentsPage(1); }}
              />
              <Input
                label="Fecha Fin"
                type="date"
                value={paymentsFilters.endDate}
                onChange={(e) => { setPaymentsFilters((p) => ({ ...p, endDate: e.target.value })); setPaymentsPage(1); }}
              />
              <Select
                label="Estado"
                value={paymentsFilters.status}
                onChange={(e) => { setPaymentsFilters((p) => ({ ...p, status: e.target.value })); setPaymentsPage(1); }}
                options={[
                  { value: '', label: 'Todos' },
                  { value: 'PAGADO', label: 'Pagado' },
                  { value: 'PENDIENTE', label: 'Pendiente' },
                  { value: 'VENCIDO', label: 'Vencido' },
                  { value: 'MORA', label: 'En Mora' },
                ]}
              />
              <Select
                label="Propiedad"
                value={paymentsFilters.propertyId}
                onChange={(e) => { setPaymentsFilters((p) => ({ ...p, propertyId: e.target.value })); setPaymentsPage(1); }}
                options={[{ value: '', label: 'Todas' }, ...propertyOptions]}
              />
            </div>
            <div className="flex justify-end mt-4">
              <Button variant="outline" onClick={() => handleExport('payments')}>
                <Download className="w-4 h-4" />
                Exportar
              </Button>
            </div>
          </Card>

          {/* Totals Row */}
          {paymentsTotals.total > 0 && (
            <div className="grid grid-cols-2 gap-4">
              <Card className="!p-4">
                <span className="text-xs text-gray-500 block">Total Pagos</span>
                <span className="text-2xl font-bold text-[#1B4F72]">
                  ${Number(paymentsTotals.total).toLocaleString('es-CO')}
                </span>
              </Card>
              <Card className="!p-4">
                <span className="text-xs text-gray-500 block">Cantidad de Pagos</span>
                <span className="text-2xl font-bold text-[#2E86C1]">{paymentsTotals.count}</span>
              </Card>
            </div>
          )}

          <Table
            columns={paymentsColumns}
            data={paymentsData}
            loading={loading}
            emptyMessage="No hay pagos para los filtros seleccionados"
            page={paymentsPage}
            totalPages={paymentsTotalPages}
            onPageChange={setPaymentsPage}
          />
        </div>
      )}
    </div>
  );
}
