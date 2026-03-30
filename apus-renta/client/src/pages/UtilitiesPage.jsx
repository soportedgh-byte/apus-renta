import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Droplets, Zap, Flame, Filter, Eye, Upload, LayoutGrid, List } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Modal from '../components/ui/Modal';
import Table from '../components/ui/Table';
import StatusBadge from '../components/ui/StatusBadge';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';

const TYPE_CONFIG = {
  AGUA: { icon: Droplets, color: '#2E86C1', label: 'Agua', bg: 'bg-blue-50' },
  LUZ: { icon: Zap, color: '#F39C12', label: 'Luz', bg: 'bg-yellow-50' },
  GAS: { icon: Flame, color: '#E67E22', label: 'Gas', bg: 'bg-orange-50' },
};

const STATUS_OPTIONS = [
  { value: '', label: 'Todos' },
  { value: 'PENDIENTE', label: 'Pendiente' },
  { value: 'PAGADO', label: 'Pagado' },
  { value: 'VENCIDO', label: 'Vencido' },
];

const TYPE_OPTIONS = [
  { value: '', label: 'Todos' },
  { value: 'AGUA', label: 'Agua' },
  { value: 'LUZ', label: 'Luz' },
  { value: 'GAS', label: 'Gas' },
];

const MONTHS = [
  { value: '01', label: 'Enero' },
  { value: '02', label: 'Febrero' },
  { value: '03', label: 'Marzo' },
  { value: '04', label: 'Abril' },
  { value: '05', label: 'Mayo' },
  { value: '06', label: 'Junio' },
  { value: '07', label: 'Julio' },
  { value: '08', label: 'Agosto' },
  { value: '09', label: 'Septiembre' },
  { value: '10', label: 'Octubre' },
  { value: '11', label: 'Noviembre' },
  { value: '12', label: 'Diciembre' },
];

function TypeIcon({ type }) {
  const cfg = TYPE_CONFIG[type] || TYPE_CONFIG.AGUA;
  const Icon = cfg.icon;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium ${cfg.bg}`}>
      <Icon className="w-3.5 h-3.5" style={{ color: cfg.color }} />
      <span style={{ color: cfg.color }}>{cfg.label}</span>
    </span>
  );
}

function TrafficLightCell({ status }) {
  const colorMap = {
    PAGADO: '#27AE60',
    PENDIENTE: '#F39C12',
    VENCIDO: '#E74C3C',
  };
  const color = colorMap[status] || '#D5D8DC';
  return (
    <div className="flex items-center justify-center">
      <div
        className="w-5 h-5 rounded-full border-2"
        style={{ backgroundColor: color, borderColor: color === '#D5D8DC' ? '#BDC3C7' : color }}
        title={status || 'Sin datos'}
      />
    </div>
  );
}

export default function UtilitiesPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('registro');
  const [utilities, setUtilities] = useState([]);
  const [properties, setProperties] = useState([]);
  const [summary, setSummary] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filters, setFilters] = useState({ propertyId: '', type: '', status: '', period: '' });
  const [form, setForm] = useState({
    propertyId: '',
    type: 'AGUA',
    amount: '',
    periodMonth: '',
    periodYear: new Date().getFullYear().toString(),
    dueDate: '',
    receipt: null,
  });
  const [saving, setSaving] = useState(false);

  const isPropietario = user?.role === 'PROPIETARIO' || user?.role === 'ADMIN';

  const fetchProperties = useCallback(async () => {
    try {
      const { data } = await api.get('/properties', { params: { limit: 200 } });
      const list = data.data?.items || data.data || [];
      setProperties(Array.isArray(list) ? list : []);
    } catch {
      setProperties([]);
    }
  }, []);

  const fetchUtilities = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, limit: 10 };
      if (filters.propertyId) params.propertyId = filters.propertyId;
      if (filters.type) params.type = filters.type;
      if (filters.status) params.status = filters.status;
      if (filters.period) params.period = filters.period;
      const { data } = await api.get('/utilities', { params });
      const items = data.data?.items || data.data || [];
      setUtilities(Array.isArray(items) ? items : []);
      setTotalPages(data.data?.totalPages || data.totalPages || 1);
    } catch {
      setUtilities([]);
    } finally {
      setLoading(false);
    }
  }, [page, filters]);

  const fetchSummary = useCallback(async () => {
    if (!isPropietario) return;
    setLoading(true);
    try {
      const { data } = await api.get('/utilities/summary');
      setSummary(data.data || data || []);
    } catch {
      setSummary([]);
    } finally {
      setLoading(false);
    }
  }, [isPropietario]);

  useEffect(() => {
    fetchProperties();
  }, [fetchProperties]);

  useEffect(() => {
    if (activeTab === 'registro') {
      fetchUtilities();
    } else if (activeTab === 'resumen') {
      fetchSummary();
    }
  }, [activeTab, fetchUtilities, fetchSummary]);

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const handleFormChange = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleFileChange = (e) => {
    setForm((prev) => ({ ...prev, receipt: e.target.files[0] || null }));
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const formData = new FormData();
      formData.append('propertyId', form.propertyId);
      formData.append('type', form.type);
      formData.append('amount', form.amount);
      formData.append('period', `${form.periodYear}-${form.periodMonth}`);
      formData.append('dueDate', form.dueDate);
      if (form.receipt) {
        formData.append('receipt', form.receipt);
      }
      await api.post('/utilities', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setShowCreateModal(false);
      setForm({ propertyId: '', type: 'AGUA', amount: '', periodMonth: '', periodYear: new Date().getFullYear().toString(), dueDate: '', receipt: null });
      fetchUtilities();
    } catch {
      // Error handled by interceptor
    } finally {
      setSaving(false);
    }
  };

  const propertyOptions = properties.map((p) => ({
    value: p._id || p.id,
    label: p.name || p.address || `Propiedad ${p._id || p.id}`,
  }));

  const columns = [
    {
      key: 'property',
      label: 'Propiedad',
      render: (_, row) => row.property?.name || row.propertyName || '-',
    },
    {
      key: 'type',
      label: 'Tipo',
      render: (val) => <TypeIcon type={val} />,
    },
    {
      key: 'period',
      label: 'Periodo',
      render: (val) => val || '-',
    },
    {
      key: 'amount',
      label: 'Monto',
      render: (val) => val != null ? `$${Number(val).toLocaleString('es-CO')}` : '-',
    },
    {
      key: 'dueDate',
      label: 'Vencimiento',
      render: (val) => val ? new Date(val).toLocaleDateString('es-CO') : '-',
    },
    {
      key: 'status',
      label: 'Estado',
      render: (val) => <StatusBadge status={val} />,
    },
    {
      key: 'actions',
      label: 'Acciones',
      render: (_, row) => (
        <button
          className="p-1.5 rounded-lg hover:bg-gray-100 text-[#2E86C1] transition-colors"
          title="Ver detalle"
        >
          <Eye className="w-4 h-4" />
        </button>
      ),
    },
  ];

  const yearOptions = [];
  const currentYear = new Date().getFullYear();
  for (let y = currentYear - 2; y <= currentYear + 1; y++) {
    yearOptions.push({ value: y.toString(), label: y.toString() });
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-[#2C3E50]">Servicios</h2>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4" />
          Registrar Servicio
        </Button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 rounded-lg p-1 w-fit">
        <button
          onClick={() => setActiveTab('registro')}
          className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'registro'
              ? 'bg-white text-[#1B4F72] shadow-sm'
              : 'text-gray-600 hover:text-[#1B4F72]'
          }`}
        >
          <List className="w-4 h-4" />
          Registro
        </button>
        {isPropietario && (
          <button
            onClick={() => setActiveTab('resumen')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'resumen'
                ? 'bg-white text-[#1B4F72] shadow-sm'
                : 'text-gray-600 hover:text-[#1B4F72]'
            }`}
          >
            <LayoutGrid className="w-4 h-4" />
            Resumen
          </button>
        )}
      </div>

      {/* REGISTRO TAB */}
      {activeTab === 'registro' && (
        <>
          <Card className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <Filter className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-600">Filtros</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Select
                label="Propiedad"
                value={filters.propertyId}
                onChange={(e) => handleFilterChange('propertyId', e.target.value)}
                options={[{ value: '', label: 'Todas' }, ...propertyOptions]}
              />
              <Select
                label="Tipo"
                value={filters.type}
                onChange={(e) => handleFilterChange('type', e.target.value)}
                options={TYPE_OPTIONS}
              />
              <Select
                label="Estado"
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                options={STATUS_OPTIONS}
              />
              <Input
                label="Periodo"
                type="month"
                value={filters.period}
                onChange={(e) => handleFilterChange('period', e.target.value)}
              />
            </div>
          </Card>

          <Table
            columns={columns}
            data={utilities}
            loading={loading}
            emptyMessage="No hay servicios registrados"
            page={page}
            totalPages={totalPages}
            onPageChange={setPage}
          />
        </>
      )}

      {/* RESUMEN TAB */}
      {activeTab === 'resumen' && isPropietario && (
        <Card title="Matriz de Servicios">
          {loading ? (
            <div className="flex justify-center py-12">
              <div className="w-6 h-6 border-2 border-[#2E86C1] border-t-transparent rounded-full animate-spin" />
            </div>
          ) : summary.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No hay datos de resumen disponibles</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-medium text-[#2C3E50]">Propiedad</th>
                    <th className="text-center py-3 px-4 font-medium">
                      <span className="inline-flex items-center gap-1">
                        <Droplets className="w-4 h-4" style={{ color: '#2E86C1' }} /> Agua
                      </span>
                    </th>
                    <th className="text-center py-3 px-4 font-medium">
                      <span className="inline-flex items-center gap-1">
                        <Zap className="w-4 h-4" style={{ color: '#F39C12' }} /> Luz
                      </span>
                    </th>
                    <th className="text-center py-3 px-4 font-medium">
                      <span className="inline-flex items-center gap-1">
                        <Flame className="w-4 h-4" style={{ color: '#E67E22' }} /> Gas
                      </span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {summary.map((row, idx) => (
                    <tr key={row.propertyId || idx} className={`border-b border-gray-100 ${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                      <td className="py-3 px-4 font-medium text-[#2C3E50]">{row.propertyName || '-'}</td>
                      <td className="py-3 px-4"><TrafficLightCell status={row.agua} /></td>
                      <td className="py-3 px-4"><TrafficLightCell status={row.luz} /></td>
                      <td className="py-3 px-4"><TrafficLightCell status={row.gas} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="flex items-center gap-6 mt-4 pt-3 border-t border-gray-200 text-xs text-gray-500">
                <span className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#27AE60' }} /> Pagado
                </span>
                <span className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#F39C12' }} /> Pendiente
                </span>
                <span className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#E74C3C' }} /> Vencido
                </span>
                <span className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#D5D8DC' }} /> Sin datos
                </span>
              </div>
            </div>
          )}
        </Card>
      )}

      {/* CREATE MODAL */}
      <Modal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} title="Registrar Servicio" size="lg">
        <form onSubmit={handleCreate} className="space-y-4">
          <Select
            label="Propiedad *"
            value={form.propertyId}
            onChange={(e) => handleFormChange('propertyId', e.target.value)}
            options={propertyOptions}
            required
          />
          <Select
            label="Tipo de Servicio *"
            value={form.type}
            onChange={(e) => handleFormChange('type', e.target.value)}
            options={[
              { value: 'AGUA', label: 'Agua' },
              { value: 'LUZ', label: 'Luz' },
              { value: 'GAS', label: 'Gas' },
            ]}
            required
          />
          <Input
            label="Monto *"
            type="number"
            min="0"
            step="0.01"
            value={form.amount}
            onChange={(e) => handleFormChange('amount', e.target.value)}
            required
          />
          <div className="grid grid-cols-2 gap-4">
            <Select
              label="Mes *"
              value={form.periodMonth}
              onChange={(e) => handleFormChange('periodMonth', e.target.value)}
              options={MONTHS}
              required
            />
            <Select
              label="Ano *"
              value={form.periodYear}
              onChange={(e) => handleFormChange('periodYear', e.target.value)}
              options={yearOptions}
              required
            />
          </div>
          <Input
            label="Fecha de Vencimiento *"
            type="date"
            value={form.dueDate}
            onChange={(e) => handleFormChange('dueDate', e.target.value)}
            required
          />
          <div>
            <label className="block text-sm font-medium text-[#2C3E50] mb-1">Recibo (opcional)</label>
            <div className="flex items-center gap-2">
              <label className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 cursor-pointer hover:bg-gray-50 text-sm text-gray-600 transition-colors">
                <Upload className="w-4 h-4" />
                {form.receipt ? form.receipt.name : 'Seleccionar archivo'}
                <input type="file" className="hidden" accept=".pdf,.jpg,.jpeg,.png" onChange={handleFileChange} />
              </label>
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <Button variant="secondary" type="button" onClick={() => setShowCreateModal(false)}>
              Cancelar
            </Button>
            <Button type="submit" loading={saving}>
              Registrar
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
