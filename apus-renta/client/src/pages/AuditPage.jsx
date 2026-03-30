import React, { useState, useEffect, useCallback } from 'react';
import { Shield, Filter, Search, Eye, Activity, Users, TrendingUp } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Modal from '../components/ui/Modal';
import Table from '../components/ui/Table';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';

export default function AuditPage() {
  const { user } = useAuth();
  const [logs, setLogs] = useState([]);
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState({ totalActions: 0, activeUsers: 0, topAction: '-' });
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedLog, setSelectedLog] = useState(null);

  const [filters, setFilters] = useState({
    userId: '',
    action: '',
    entity: '',
    startDate: '',
    endDate: '',
  });

  const isPropietario = user?.role === 'PROPIETARIO' || user?.role === 'ADMIN';

  const fetchUsers = useCallback(async () => {
    try {
      const { data } = await api.get('/users', { params: { limit: 200 } });
      const list = data.data?.items || data.data || [];
      setUsers(Array.isArray(list) ? list : []);
    } catch {
      setUsers([]);
    }
  }, []);

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, limit: 15 };
      if (filters.userId) params.userId = filters.userId;
      if (filters.action) params.action = filters.action;
      if (filters.entity) params.entity = filters.entity;
      if (filters.startDate) params.startDate = filters.startDate;
      if (filters.endDate) params.endDate = filters.endDate;
      const { data } = await api.get('/audit', { params });
      const result = data.data || data;
      const items = result.items || result.logs || [];
      setLogs(Array.isArray(items) ? items : []);
      setTotalPages(result.totalPages || 1);

      // Stats
      if (result.stats) {
        setStats(result.stats);
      } else {
        setStats({
          totalActions: result.total || items.length || 0,
          activeUsers: result.activeUsers || new Set(items.map((l) => l.userId || l.user?._id)).size,
          topAction: result.topAction || '-',
        });
      }
    } catch {
      setLogs([]);
    } finally {
      setLoading(false);
    }
  }, [page, filters]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);
  useEffect(() => { fetchLogs(); }, [fetchLogs]);

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const openDetail = (log) => {
    setSelectedLog(log);
    setShowDetailModal(true);
  };

  const formatDetail = (detail) => {
    if (!detail) return '-';
    try {
      if (typeof detail === 'string') {
        const parsed = JSON.parse(detail);
        return JSON.stringify(parsed, null, 2);
      }
      return JSON.stringify(detail, null, 2);
    } catch {
      return String(detail);
    }
  };

  const truncateDetail = (detail) => {
    if (!detail) return '-';
    const str = typeof detail === 'object' ? JSON.stringify(detail) : String(detail);
    return str.length > 80 ? str.slice(0, 80) + '...' : str;
  };

  const userOptions = [
    { value: '', label: 'Todos' },
    ...users.map((u) => ({
      value: u._id || u.id,
      label: `${u.firstName || ''} ${u.lastName || ''}`.trim() || u.email,
    })),
  ];

  const entityOptions = [
    { value: '', label: 'Todas' },
    { value: 'PROPERTY', label: 'Propiedad' },
    { value: 'TENANT', label: 'Arrendatario' },
    { value: 'LEASE', label: 'Contrato' },
    { value: 'PAYMENT', label: 'Pago' },
    { value: 'UTILITY', label: 'Servicio' },
    { value: 'PQRS', label: 'PQRS' },
    { value: 'USER', label: 'Usuario' },
    { value: 'SETTINGS', label: 'Configuracion' },
  ];

  const columns = [
    {
      key: 'createdAt',
      label: 'Fecha/Hora',
      render: (val) => val ? (
        <span className="text-xs">
          {new Date(val).toLocaleDateString('es-CO')}{' '}
          <span className="text-gray-400">{new Date(val).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })}</span>
        </span>
      ) : '-',
    },
    {
      key: 'user',
      label: 'Usuario',
      render: (val, row) => {
        const name = val?.firstName
          ? `${val.firstName} ${val.lastName || ''}`.trim()
          : row.userName || row.userEmail || '-';
        return <span className="text-sm">{name}</span>;
      },
    },
    {
      key: 'action',
      label: 'Accion',
      render: (val) => (
        <span className="inline-flex px-2 py-0.5 bg-[#D6EAF8] text-[#1B4F72] rounded text-xs font-medium">
          {val || '-'}
        </span>
      ),
    },
    {
      key: 'entity',
      label: 'Entidad',
      render: (val) => <span className="text-sm text-gray-700">{val || '-'}</span>,
    },
    {
      key: 'ip',
      label: 'IP',
      render: (val) => <span className="font-mono text-xs text-gray-500">{val || '-'}</span>,
    },
    {
      key: 'detail',
      label: 'Detalle',
      render: (val, row) => {
        const detail = val || row.details || row.metadata;
        return (
          <button
            onClick={() => openDetail(row)}
            className="text-xs text-gray-500 hover:text-[#2E86C1] max-w-[200px] truncate block text-left transition-colors"
            title="Click para ver detalle completo"
          >
            {truncateDetail(detail)}
          </button>
        );
      },
    },
  ];

  if (!isPropietario) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Shield className="w-16 h-16 text-gray-300 mb-4" />
        <h2 className="text-xl font-semibold text-[#2C3E50] mb-2">Acceso Restringido</h2>
        <p className="text-gray-500">Solo los propietarios pueden acceder al registro de auditoria.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <Shield className="w-6 h-6 text-[#1B4F72]" />
        <h2 className="text-2xl font-bold text-[#2C3E50]">Auditoria</h2>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <Card className="!p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-[#D6EAF8]">
              <Activity className="w-5 h-5 text-[#1B4F72]" />
            </div>
            <div>
              <span className="text-xs text-gray-500 block">Total acciones</span>
              <span className="text-xl font-bold text-[#2C3E50]">{stats.totalActions.toLocaleString()}</span>
            </div>
          </div>
        </Card>
        <Card className="!p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-green-100">
              <Users className="w-5 h-5 text-[#27AE60]" />
            </div>
            <div>
              <span className="text-xs text-gray-500 block">Usuarios activos</span>
              <span className="text-xl font-bold text-[#2C3E50]">{stats.activeUsers}</span>
            </div>
          </div>
        </Card>
        <Card className="!p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-100">
              <TrendingUp className="w-5 h-5 text-[#F39C12]" />
            </div>
            <div>
              <span className="text-xs text-gray-500 block">Accion mas frecuente</span>
              <span className="text-sm font-bold text-[#2C3E50]">{stats.topAction}</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Filter className="w-4 h-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-600">Filtros</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <Select
            label="Usuario"
            value={filters.userId}
            onChange={(e) => handleFilterChange('userId', e.target.value)}
            options={userOptions}
          />
          <Input
            label="Accion"
            icon={Search}
            value={filters.action}
            onChange={(e) => handleFilterChange('action', e.target.value)}
            placeholder="Buscar accion..."
          />
          <Select
            label="Entidad"
            value={filters.entity}
            onChange={(e) => handleFilterChange('entity', e.target.value)}
            options={entityOptions}
          />
          <Input
            label="Desde"
            type="date"
            value={filters.startDate}
            onChange={(e) => handleFilterChange('startDate', e.target.value)}
          />
          <Input
            label="Hasta"
            type="date"
            value={filters.endDate}
            onChange={(e) => handleFilterChange('endDate', e.target.value)}
          />
        </div>
      </Card>

      {/* Table */}
      <Table
        columns={columns}
        data={logs}
        loading={loading}
        emptyMessage="No hay registros de auditoria"
        page={page}
        totalPages={totalPages}
        onPageChange={setPage}
      />

      {/* Detail Modal */}
      <Modal
        isOpen={showDetailModal}
        onClose={() => setShowDetailModal(false)}
        title="Detalle de Registro"
        size="lg"
      >
        {selectedLog && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-xs text-gray-500 block mb-1">Fecha/Hora</span>
                <span className="text-sm text-[#2C3E50]">
                  {selectedLog.createdAt
                    ? new Date(selectedLog.createdAt).toLocaleString('es-CO')
                    : '-'}
                </span>
              </div>
              <div>
                <span className="text-xs text-gray-500 block mb-1">Usuario</span>
                <span className="text-sm text-[#2C3E50]">
                  {selectedLog.user?.firstName
                    ? `${selectedLog.user.firstName} ${selectedLog.user.lastName || ''}`
                    : selectedLog.userName || selectedLog.userEmail || '-'}
                </span>
              </div>
              <div>
                <span className="text-xs text-gray-500 block mb-1">Accion</span>
                <span className="inline-flex px-2 py-0.5 bg-[#D6EAF8] text-[#1B4F72] rounded text-xs font-medium">
                  {selectedLog.action || '-'}
                </span>
              </div>
              <div>
                <span className="text-xs text-gray-500 block mb-1">Entidad</span>
                <span className="text-sm text-[#2C3E50]">{selectedLog.entity || '-'}</span>
              </div>
              <div>
                <span className="text-xs text-gray-500 block mb-1">IP</span>
                <span className="font-mono text-sm text-gray-600">{selectedLog.ip || '-'}</span>
              </div>
              <div>
                <span className="text-xs text-gray-500 block mb-1">ID Entidad</span>
                <span className="font-mono text-xs text-gray-500">{selectedLog.entityId || '-'}</span>
              </div>
            </div>
            <div>
              <span className="text-xs text-gray-500 block mb-2">Detalle Completo</span>
              <pre className="bg-gray-900 text-green-400 rounded-lg p-4 text-xs overflow-x-auto max-h-[300px] overflow-y-auto">
                {formatDetail(selectedLog.detail || selectedLog.details || selectedLog.metadata)}
              </pre>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
