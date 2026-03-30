import React, { useState, useEffect, useCallback } from 'react';
import {
  Plus, Filter, Eye, MessageSquare, Paperclip, FileText,
  AlertCircle, AlertTriangle, HelpCircle, Lightbulb, Upload, X,
} from 'lucide-react';
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
  PETICION: { color: '#2E86C1', bg: 'bg-blue-100 text-blue-800', label: 'Peticion', icon: HelpCircle },
  QUEJA: { color: '#E74C3C', bg: 'bg-red-100 text-red-800', label: 'Queja', icon: AlertCircle },
  RECLAMO: { color: '#E67E22', bg: 'bg-orange-100 text-orange-800', label: 'Reclamo', icon: AlertTriangle },
  SUGERENCIA: { color: '#27AE60', bg: 'bg-green-100 text-green-800', label: 'Sugerencia', icon: Lightbulb },
};

const TYPE_OPTIONS = [
  { value: '', label: 'Todos' },
  { value: 'PETICION', label: 'Peticion' },
  { value: 'QUEJA', label: 'Queja' },
  { value: 'RECLAMO', label: 'Reclamo' },
  { value: 'SUGERENCIA', label: 'Sugerencia' },
];

const STATUS_OPTIONS = [
  { value: '', label: 'Todos' },
  { value: 'RADICADA', label: 'Radicada' },
  { value: 'EN_PROCESO', label: 'En Proceso' },
  { value: 'RESUELTA', label: 'Resuelta' },
  { value: 'CERRADA', label: 'Cerrada' },
];

function TypeBadge({ type }) {
  const cfg = TYPE_CONFIG[type] || TYPE_CONFIG.PETICION;
  const Icon = cfg.icon;
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${cfg.bg}`}>
      <Icon className="w-3 h-3" />
      {cfg.label}
    </span>
  );
}

export default function PQRSPage() {
  const { user } = useAuth();
  const [pqrs, setPqrs] = useState([]);
  const [properties, setProperties] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState({ type: '', status: '', propertyId: '' });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedPqrs, setSelectedPqrs] = useState(null);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    propertyId: '',
    type: 'PETICION',
    subject: '',
    description: '',
    attachments: [],
  });

  const [manageForm, setManageForm] = useState({
    status: '',
    resolution: '',
    assignedTo: '',
  });

  const isArrendatario = user?.role === 'ARRENDATARIO';
  const canManage = user?.role === 'PROPIETARIO' || user?.role === 'ENCARGADO' || user?.role === 'ADMIN';

  const fetchProperties = useCallback(async () => {
    try {
      const { data } = await api.get('/properties', { params: { limit: 200 } });
      const list = data.data?.items || data.data || [];
      setProperties(Array.isArray(list) ? list : []);
    } catch {
      setProperties([]);
    }
  }, []);

  const fetchUsers = useCallback(async () => {
    if (!canManage) return;
    try {
      const { data } = await api.get('/users', { params: { limit: 200 } });
      const list = data.data?.items || data.data || [];
      setUsers(Array.isArray(list) ? list : []);
    } catch {
      setUsers([]);
    }
  }, [canManage]);

  const fetchPqrs = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, limit: 10 };
      if (filters.type) params.type = filters.type;
      if (filters.status) params.status = filters.status;
      if (filters.propertyId) params.propertyId = filters.propertyId;
      const { data } = await api.get('/pqrs', { params });
      const items = data.data?.items || data.data || [];
      setPqrs(Array.isArray(items) ? items : []);
      setTotalPages(data.data?.totalPages || data.totalPages || 1);
    } catch {
      setPqrs([]);
    } finally {
      setLoading(false);
    }
  }, [page, filters]);

  useEffect(() => { fetchProperties(); fetchUsers(); }, [fetchProperties, fetchUsers]);
  useEffect(() => { fetchPqrs(); }, [fetchPqrs]);

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const handleFormChange = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleAttachments = (e) => {
    const files = Array.from(e.target.files || []);
    setForm((prev) => ({ ...prev, attachments: [...prev.attachments, ...files] }));
  };

  const removeAttachment = (index) => {
    setForm((prev) => ({
      ...prev,
      attachments: prev.attachments.filter((_, i) => i !== index),
    }));
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const formData = new FormData();
      formData.append('propertyId', form.propertyId);
      formData.append('type', form.type);
      formData.append('subject', form.subject);
      formData.append('description', form.description);
      form.attachments.forEach((file) => {
        formData.append('attachments', file);
      });
      await api.post('/pqrs', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setShowCreateModal(false);
      setForm({ propertyId: '', type: 'PETICION', subject: '', description: '', attachments: [] });
      fetchPqrs();
    } catch {
      // Error handled by interceptor
    } finally {
      setSaving(false);
    }
  };

  const openDetail = (item) => {
    setSelectedPqrs(item);
    setManageForm({
      status: item.status || '',
      resolution: item.resolution || '',
      assignedTo: item.assignedTo?._id || item.assignedTo?.id || item.assignedTo || '',
    });
    setShowDetailModal(true);
  };

  const handleManageSave = async () => {
    if (!selectedPqrs) return;
    setSaving(true);
    try {
      await api.put(`/pqrs/${selectedPqrs._id || selectedPqrs.id}`, {
        status: manageForm.status,
        resolution: manageForm.resolution,
        assignedTo: manageForm.assignedTo || undefined,
      });
      setShowDetailModal(false);
      fetchPqrs();
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

  const userOptions = users.map((u) => ({
    value: u._id || u.id,
    label: `${u.firstName || ''} ${u.lastName || ''}`.trim() || u.email,
  }));

  const columns = [
    {
      key: 'ticketNumber',
      label: '#ID',
      render: (val, row) => (
        <span className="font-mono text-xs text-[#1B4F72]">
          {val || row._id?.slice(-6) || row.id?.toString().slice(-6) || '-'}
        </span>
      ),
    },
    {
      key: 'type',
      label: 'Tipo',
      render: (val) => <TypeBadge type={val} />,
    },
    {
      key: 'subject',
      label: 'Asunto',
      render: (val) => (
        <span className="max-w-[200px] truncate block" title={val}>
          {val || '-'}
        </span>
      ),
    },
    {
      key: 'property',
      label: 'Propiedad',
      render: (_, row) => row.property?.name || row.propertyName || '-',
    },
    {
      key: 'status',
      label: 'Estado',
      render: (val) => <StatusBadge status={val} />,
    },
    {
      key: 'createdAt',
      label: 'Fecha',
      render: (val) => val ? new Date(val).toLocaleDateString('es-CO') : '-',
    },
    {
      key: 'actions',
      label: 'Acciones',
      render: (_, row) => (
        <button
          onClick={() => openDetail(row)}
          className="p-1.5 rounded-lg hover:bg-gray-100 text-[#2E86C1] transition-colors"
          title="Ver detalle"
        >
          <Eye className="w-4 h-4" />
        </button>
      ),
    },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-[#2C3E50]">PQRS</h2>
        {isArrendatario && (
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="w-4 h-4" />
            Nueva Solicitud
          </Button>
        )}
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Filter className="w-4 h-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-600">Filtros</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
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
          <Select
            label="Propiedad"
            value={filters.propertyId}
            onChange={(e) => handleFilterChange('propertyId', e.target.value)}
            options={[{ value: '', label: 'Todas' }, ...propertyOptions]}
          />
        </div>
      </Card>

      {/* Table */}
      <Table
        columns={columns}
        data={pqrs}
        loading={loading}
        emptyMessage="No hay solicitudes PQRS registradas"
        page={page}
        totalPages={totalPages}
        onPageChange={setPage}
      />

      {/* CREATE MODAL */}
      <Modal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} title="Nueva Solicitud PQRS" size="lg">
        <form onSubmit={handleCreate} className="space-y-4">
          <Select
            label="Propiedad *"
            value={form.propertyId}
            onChange={(e) => handleFormChange('propertyId', e.target.value)}
            options={propertyOptions}
            required
          />
          <Select
            label="Tipo *"
            value={form.type}
            onChange={(e) => handleFormChange('type', e.target.value)}
            options={[
              { value: 'PETICION', label: 'Peticion' },
              { value: 'QUEJA', label: 'Queja' },
              { value: 'RECLAMO', label: 'Reclamo' },
              { value: 'SUGERENCIA', label: 'Sugerencia' },
            ]}
            required
          />
          <Input
            label="Asunto *"
            value={form.subject}
            onChange={(e) => handleFormChange('subject', e.target.value)}
            placeholder="Breve descripcion del asunto"
            required
          />
          <div>
            <label className="block text-sm font-medium text-[#2C3E50] mb-1">Descripcion *</label>
            <textarea
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-[#2C3E50] placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#2E86C1] focus:border-transparent min-h-[120px] resize-y"
              value={form.description}
              onChange={(e) => handleFormChange('description', e.target.value)}
              placeholder="Describa en detalle su solicitud..."
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[#2C3E50] mb-1">Adjuntos (opcional)</label>
            <label className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 cursor-pointer hover:bg-gray-50 text-sm text-gray-600 transition-colors w-fit">
              <Upload className="w-4 h-4" />
              Agregar archivos
              <input type="file" className="hidden" multiple accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" onChange={handleAttachments} />
            </label>
            {form.attachments.length > 0 && (
              <div className="mt-2 space-y-1">
                {form.attachments.map((file, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-sm text-gray-600 bg-gray-50 rounded-lg px-3 py-1.5">
                    <Paperclip className="w-3 h-3" />
                    <span className="truncate flex-1">{file.name}</span>
                    <button type="button" onClick={() => removeAttachment(idx)} className="text-gray-400 hover:text-red-500">
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <Button variant="secondary" type="button" onClick={() => setShowCreateModal(false)}>
              Cancelar
            </Button>
            <Button type="submit" loading={saving}>
              Enviar Solicitud
            </Button>
          </div>
        </form>
      </Modal>

      {/* DETAIL / MANAGE MODAL */}
      <Modal
        isOpen={showDetailModal}
        onClose={() => setShowDetailModal(false)}
        title={`PQRS - ${selectedPqrs?.ticketNumber || selectedPqrs?._id?.slice(-6) || ''}`}
        size="lg"
      >
        {selectedPqrs && (
          <div className="space-y-5">
            {/* Info Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-xs text-gray-500 block mb-1">Tipo</span>
                <TypeBadge type={selectedPqrs.type} />
              </div>
              <div>
                <span className="text-xs text-gray-500 block mb-1">Estado</span>
                <StatusBadge status={selectedPqrs.status} />
              </div>
              <div>
                <span className="text-xs text-gray-500 block mb-1">Propiedad</span>
                <span className="text-sm text-[#2C3E50]">
                  {selectedPqrs.property?.name || selectedPqrs.propertyName || '-'}
                </span>
              </div>
              <div>
                <span className="text-xs text-gray-500 block mb-1">Fecha de creacion</span>
                <span className="text-sm text-[#2C3E50]">
                  {selectedPqrs.createdAt ? new Date(selectedPqrs.createdAt).toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric' }) : '-'}
                </span>
              </div>
            </div>

            {/* Subject & Description */}
            <div>
              <span className="text-xs text-gray-500 block mb-1">Asunto</span>
              <p className="text-sm font-medium text-[#2C3E50]">{selectedPqrs.subject}</p>
            </div>
            <div>
              <span className="text-xs text-gray-500 block mb-1">Descripcion</span>
              <p className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 rounded-lg p-3">
                {selectedPqrs.description}
              </p>
            </div>

            {/* Attachments */}
            {selectedPqrs.attachments?.length > 0 && (
              <div>
                <span className="text-xs text-gray-500 block mb-2">Adjuntos</span>
                <div className="space-y-1">
                  {selectedPqrs.attachments.map((att, idx) => (
                    <a
                      key={idx}
                      href={att.url || att}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-sm text-[#2E86C1] hover:underline bg-blue-50 rounded-lg px-3 py-1.5"
                    >
                      <FileText className="w-3.5 h-3.5" />
                      {att.name || att.filename || `Adjunto ${idx + 1}`}
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Resolution (if exists) */}
            {selectedPqrs.resolution && (
              <div>
                <span className="text-xs text-gray-500 block mb-1">Resolucion</span>
                <p className="text-sm text-gray-700 whitespace-pre-wrap bg-green-50 rounded-lg p-3 border border-green-200">
                  {selectedPqrs.resolution}
                </p>
              </div>
            )}

            {/* Manage Section (PROPIETARIO/ENCARGADO) */}
            {canManage && (
              <div className="border-t border-gray-200 pt-4 space-y-4">
                <h4 className="text-sm font-semibold text-[#2C3E50] flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Gestionar Solicitud
                </h4>
                <Select
                  label="Cambiar Estado"
                  value={manageForm.status}
                  onChange={(e) => setManageForm((prev) => ({ ...prev, status: e.target.value }))}
                  options={[
                    { value: 'RADICADA', label: 'Radicada' },
                    { value: 'EN_PROCESO', label: 'En Proceso' },
                    { value: 'RESUELTA', label: 'Resuelta' },
                    { value: 'CERRADA', label: 'Cerrada' },
                  ]}
                />
                <div>
                  <label className="block text-sm font-medium text-[#2C3E50] mb-1">Resolucion</label>
                  <textarea
                    className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-[#2C3E50] placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#2E86C1] focus:border-transparent min-h-[80px] resize-y"
                    value={manageForm.resolution}
                    onChange={(e) => setManageForm((prev) => ({ ...prev, resolution: e.target.value }))}
                    placeholder="Escriba la resolucion..."
                  />
                </div>
                <Select
                  label="Asignar a"
                  value={manageForm.assignedTo}
                  onChange={(e) => setManageForm((prev) => ({ ...prev, assignedTo: e.target.value }))}
                  options={userOptions}
                />
                <div className="flex justify-end">
                  <Button onClick={handleManageSave} loading={saving}>
                    Guardar Cambios
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
