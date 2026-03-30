import React, { useState, useEffect, useCallback } from 'react';
import {
  Plus,
  Eye,
  Pencil,
  Trash2,
  FileSignature,
  RefreshCw,
  Search,
  FileText,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';
import StatusBadge from '../components/ui/StatusBadge';
import Table from '../components/ui/Table';
import Modal from '../components/ui/Modal';

const STATUS_OPTIONS = [
  { value: '', label: 'Todos los estados' },
  { value: 'BORRADOR', label: 'Borrador' },
  { value: 'ACTIVO', label: 'Activo' },
  { value: 'VENCIDO', label: 'Vencido' },
  { value: 'TERMINADO', label: 'Terminado' },
  { value: 'RENOVADO', label: 'Renovado' },
];

const STATUS_TRANSITIONS = {
  BORRADOR: ['ACTIVO', 'TERMINADO'],
  ACTIVO: ['VENCIDO', 'TERMINADO', 'RENOVADO'],
  VENCIDO: ['RENOVADO', 'TERMINADO'],
  RENOVADO: ['ACTIVO', 'TERMINADO'],
};

function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('es-CO', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function formatCurrency(amount) {
  if (amount == null) return '—';
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

const INITIAL_FORM = {
  propertyId: '',
  tenantPersonId: '',
  startDate: '',
  endDate: '',
  monthlyRent: '',
  deposit: '',
  terms: '',
};

export default function LeasesPage() {
  const { user } = useAuth();
  const isPropietario = user?.role === 'PROPIETARIO';

  // --- Data ---
  const [leases, setLeases] = useState([]);
  const [properties, setProperties] = useState([]);
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // --- Filters ---
  const [filterStatus, setFilterStatus] = useState('');
  const [filterProperty, setFilterProperty] = useState('');

  // --- Modals ---
  const [showForm, setShowForm] = useState(false);
  const [showDetail, setShowDetail] = useState(false);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // --- Form ---
  const [form, setForm] = useState(INITIAL_FORM);
  const [editingId, setEditingId] = useState(null);
  const [formErrors, setFormErrors] = useState({});
  const [saving, setSaving] = useState(false);

  // --- Detail ---
  const [selectedLease, setSelectedLease] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [leasePayments, setLeasePayments] = useState([]);

  // --- Status change ---
  const [statusTarget, setStatusTarget] = useState(null);
  const [newStatus, setNewStatus] = useState('');
  const [statusReason, setStatusReason] = useState('');
  const [statusSaving, setStatusSaving] = useState(false);

  // --- Delete ---
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  // --- Toast ---
  const [toast, setToast] = useState(null);

  const showToast = useCallback((message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  }, []);

  // ====== Fetch data ======

  const fetchLeases = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, limit: 10 };
      if (filterStatus) params.status = filterStatus;
      if (filterProperty) params.propertyId = filterProperty;
      const { data } = await api.get('/leases', { params });
      const result = data.data || data;
      setLeases(Array.isArray(result) ? result : result.leases || result.items || []);
      setTotalPages(result.totalPages || result.pages || Math.ceil((result.total || 0) / 10) || 1);
    } catch (err) {
      showToast(err.response?.data?.message || 'Error al cargar contratos', 'error');
    } finally {
      setLoading(false);
    }
  }, [page, filterStatus, filterProperty, showToast]);

  const fetchProperties = useCallback(async () => {
    try {
      const { data } = await api.get('/properties', { params: { limit: 200 } });
      const result = data.data || data;
      const list = Array.isArray(result) ? result : result.properties || result.items || [];
      setProperties(list);
    } catch {
      /* silent */
    }
  }, []);

  const fetchTenants = useCallback(async () => {
    try {
      const { data } = await api.get('/persons', { params: { role: 'ARRENDATARIO', limit: 200 } });
      const result = data.data || data;
      const list = Array.isArray(result) ? result : result.persons || result.items || [];
      setTenants(list);
    } catch {
      /* silent */
    }
  }, []);

  useEffect(() => {
    fetchLeases();
  }, [fetchLeases]);

  useEffect(() => {
    fetchProperties();
    fetchTenants();
  }, [fetchProperties, fetchTenants]);

  // Reset page on filter change
  useEffect(() => {
    setPage(1);
  }, [filterStatus, filterProperty]);

  // ====== Helpers ======

  const propertyOptions = properties.map((p) => ({
    value: p.id || p._id,
    label: p.name || p.title || `${p.type} - ${p.address}`,
  }));

  const tenantOptions = tenants.map((t) => ({
    value: t.id || t._id,
    label: `${t.firstName || ''} ${t.lastName || ''}`.trim() || t.fullName || t.email,
  }));

  const filterPropertyOptions = [{ value: '', label: 'Todas las propiedades' }, ...propertyOptions];

  // ====== Form handlers ======

  const openCreate = () => {
    setForm(INITIAL_FORM);
    setEditingId(null);
    setFormErrors({});
    setShowForm(true);
  };

  const openEdit = (lease) => {
    setForm({
      propertyId: lease.propertyId || lease.property?.id || lease.property?._id || '',
      tenantPersonId: lease.tenantPersonId || lease.tenant?.id || lease.tenant?._id || '',
      startDate: lease.startDate ? lease.startDate.substring(0, 10) : '',
      endDate: lease.endDate ? lease.endDate.substring(0, 10) : '',
      monthlyRent: lease.monthlyRent || '',
      deposit: lease.deposit || '',
      terms: lease.terms || '',
    });
    setEditingId(lease.id || lease._id);
    setFormErrors({});
    setShowForm(true);
  };

  const validateForm = () => {
    const errors = {};
    if (!form.propertyId) errors.propertyId = 'Seleccione una propiedad';
    if (!form.tenantPersonId) errors.tenantPersonId = 'Seleccione un inquilino';
    if (!form.startDate) errors.startDate = 'Fecha de inicio requerida';
    if (!form.endDate) errors.endDate = 'Fecha de fin requerida';
    if (!form.monthlyRent || Number(form.monthlyRent) <= 0) errors.monthlyRent = 'Canon mensual requerido';
    if (form.startDate && form.endDate && new Date(form.endDate) <= new Date(form.startDate)) {
      errors.endDate = 'La fecha fin debe ser posterior a la fecha inicio';
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    setSaving(true);
    try {
      const payload = {
        ...form,
        monthlyRent: Number(form.monthlyRent),
        deposit: form.deposit ? Number(form.deposit) : 0,
      };
      if (editingId) {
        await api.put(`/leases/${editingId}`, payload);
        showToast('Contrato actualizado exitosamente');
      } else {
        await api.post('/leases', payload);
        showToast('Contrato creado exitosamente');
      }
      setShowForm(false);
      fetchLeases();
    } catch (err) {
      showToast(err.response?.data?.message || 'Error al guardar contrato', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleFieldChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    if (formErrors[field]) {
      setFormErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  // ====== Detail ======

  const openDetail = async (lease) => {
    setSelectedLease(lease);
    setShowDetail(true);
    setDetailLoading(true);
    try {
      const leaseId = lease.id || lease._id;
      const [leaseRes, paymentsRes] = await Promise.allSettled([
        api.get(`/leases/${leaseId}`),
        api.get('/payments', { params: { leaseId, limit: 50 } }),
      ]);
      if (leaseRes.status === 'fulfilled') {
        setSelectedLease(leaseRes.value.data.data || leaseRes.value.data);
      }
      if (paymentsRes.status === 'fulfilled') {
        const pResult = paymentsRes.value.data.data || paymentsRes.value.data;
        setLeasePayments(
          Array.isArray(pResult) ? pResult : pResult.payments || pResult.items || []
        );
      }
    } catch {
      /* keep what we have */
    } finally {
      setDetailLoading(false);
    }
  };

  // ====== Status change ======

  const openStatusChange = (lease) => {
    setStatusTarget(lease);
    setNewStatus('');
    setStatusReason('');
    setShowStatusModal(true);
  };

  const handleStatusChange = async () => {
    if (!newStatus) return;
    setStatusSaving(true);
    try {
      const leaseId = statusTarget.id || statusTarget._id;
      await api.patch(`/leases/${leaseId}/status`, {
        status: newStatus,
        reason: statusReason,
      });
      showToast('Estado actualizado exitosamente');
      setShowStatusModal(false);
      fetchLeases();
    } catch (err) {
      showToast(err.response?.data?.message || 'Error al cambiar estado', 'error');
    } finally {
      setStatusSaving(false);
    }
  };

  // ====== Sign ======

  const handleSendToSign = async (lease) => {
    try {
      const leaseId = lease.id || lease._id;
      await api.post(`/leases/${leaseId}/sign`);
      showToast('Contrato enviado a firma exitosamente');
      fetchLeases();
    } catch (err) {
      showToast(err.response?.data?.message || 'Error al enviar a firma', 'error');
    }
  };

  // ====== Delete ======

  const openDelete = (lease) => {
    setDeleteTarget(lease);
    setShowDeleteConfirm(true);
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      const leaseId = deleteTarget.id || deleteTarget._id;
      await api.delete(`/leases/${leaseId}`);
      showToast('Contrato eliminado exitosamente');
      setShowDeleteConfirm(false);
      fetchLeases();
    } catch (err) {
      showToast(err.response?.data?.message || 'Error al eliminar contrato', 'error');
    } finally {
      setDeleting(false);
    }
  };

  // ====== Table columns ======

  const columns = [
    {
      key: 'property',
      label: 'Propiedad',
      render: (_, row) =>
        row.property?.name || row.property?.title || row.propertyName || '—',
    },
    {
      key: 'tenant',
      label: 'Inquilino',
      render: (_, row) => {
        const t = row.tenant || row.tenantPerson;
        if (!t) return row.tenantName || '—';
        return `${t.firstName || ''} ${t.lastName || ''}`.trim() || t.fullName || t.email || '—';
      },
    },
    {
      key: 'startDate',
      label: 'Inicio',
      render: (val) => formatDate(val),
    },
    {
      key: 'endDate',
      label: 'Fin',
      render: (val) => formatDate(val),
    },
    {
      key: 'monthlyRent',
      label: 'Canon Mensual',
      render: (val) => formatCurrency(val),
    },
    {
      key: 'status',
      label: 'Estado',
      render: (val) => <StatusBadge status={val} />,
    },
    {
      key: 'actions',
      label: 'Acciones',
      render: (_, row) => {
        const status = (row.status || '').toUpperCase();
        const isDraft = status === 'BORRADOR';
        return (
          <div className="flex items-center gap-1">
            <button
              onClick={() => openDetail(row)}
              className="p-1.5 rounded-lg hover:bg-[#D6EAF8] text-[#2E86C1] transition-colors"
              title="Ver detalles"
            >
              <Eye className="w-4 h-4" />
            </button>

            {isPropietario && isDraft && (
              <button
                onClick={() => openEdit(row)}
                className="p-1.5 rounded-lg hover:bg-[#D6EAF8] text-[#1B4F72] transition-colors"
                title="Editar"
              >
                <Pencil className="w-4 h-4" />
              </button>
            )}

            {isPropietario && (
              <button
                onClick={() => handleSendToSign(row)}
                className="p-1.5 rounded-lg hover:bg-purple-100 text-purple-600 transition-colors"
                title="Enviar a firma"
              >
                <FileSignature className="w-4 h-4" />
              </button>
            )}

            {isPropietario && STATUS_TRANSITIONS[status] && (
              <button
                onClick={() => openStatusChange(row)}
                className="p-1.5 rounded-lg hover:bg-amber-100 text-amber-600 transition-colors"
                title="Cambiar estado"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            )}

            {isPropietario && isDraft && (
              <button
                onClick={() => openDelete(row)}
                className="p-1.5 rounded-lg hover:bg-red-100 text-red-600 transition-colors"
                title="Eliminar"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        );
      },
    },
  ];

  // ====== Available statuses for status change ======
  const availableStatuses = statusTarget
    ? (STATUS_TRANSITIONS[(statusTarget.status || '').toUpperCase()] || []).map((s) => ({
        value: s,
        label: s.charAt(0) + s.slice(1).toLowerCase(),
      }))
    : [];

  // ====== Render ======

  return (
    <div className="space-y-6">
      {/* Toast */}
      {toast && (
        <div
          className={`fixed top-4 right-4 z-[100] px-4 py-3 rounded-lg shadow-lg text-white text-sm font-medium transition-all ${
            toast.type === 'error' ? 'bg-[#E74C3C]' : 'bg-[#27AE60]'
          }`}
        >
          {toast.message}
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <h2 className="text-2xl font-bold text-[#2C3E50]">Contratos</h2>
        {isPropietario && (
          <Button onClick={openCreate}>
            <Plus className="w-4 h-4" />
            Nuevo Contrato
          </Button>
        )}
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-col sm:flex-row gap-4">
          <Select
            label="Estado"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            options={STATUS_OPTIONS.slice(1)}
            className="sm:w-48"
          />
          <Select
            label="Propiedad"
            value={filterProperty}
            onChange={(e) => setFilterProperty(e.target.value)}
            options={filterPropertyOptions.slice(1)}
            className="sm:w-64"
          />
        </div>
      </Card>

      {/* Table */}
      <Table
        columns={columns}
        data={leases}
        loading={loading}
        emptyMessage="No se encontraron contratos"
        page={page}
        totalPages={totalPages}
        onPageChange={setPage}
      />

      {/* ====== Create/Edit Modal ====== */}
      <Modal
        isOpen={showForm}
        onClose={() => setShowForm(false)}
        title={editingId ? 'Editar Contrato' : 'Nuevo Contrato'}
        size="lg"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Select
            label="Propiedad *"
            value={form.propertyId}
            onChange={(e) => handleFieldChange('propertyId', e.target.value)}
            options={propertyOptions}
            error={formErrors.propertyId}
          />

          <Select
            label="Inquilino *"
            value={form.tenantPersonId}
            onChange={(e) => handleFieldChange('tenantPersonId', e.target.value)}
            options={tenantOptions}
            error={formErrors.tenantPersonId}
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Fecha de Inicio *"
              type="date"
              value={form.startDate}
              onChange={(e) => handleFieldChange('startDate', e.target.value)}
              error={formErrors.startDate}
            />
            <Input
              label="Fecha de Fin *"
              type="date"
              value={form.endDate}
              onChange={(e) => handleFieldChange('endDate', e.target.value)}
              error={formErrors.endDate}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Canon Mensual (COP) *"
              type="number"
              min="0"
              value={form.monthlyRent}
              onChange={(e) => handleFieldChange('monthlyRent', e.target.value)}
              error={formErrors.monthlyRent}
            />
            <Input
              label="Deposito (COP)"
              type="number"
              min="0"
              value={form.deposit}
              onChange={(e) => handleFieldChange('deposit', e.target.value)}
            />
          </div>

          <div className="w-full">
            <label className="block text-sm font-medium text-[#2C3E50] mb-1">
              Terminos y condiciones
            </label>
            <textarea
              rows={4}
              value={form.terms}
              onChange={(e) => handleFieldChange('terms', e.target.value)}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-[#2C3E50] focus:outline-none focus:ring-2 focus:ring-[#2E86C1] focus:border-transparent resize-y"
              placeholder="Ingrese los terminos del contrato..."
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" type="button" onClick={() => setShowForm(false)}>
              Cancelar
            </Button>
            <Button type="submit" loading={saving}>
              {editingId ? 'Actualizar' : 'Crear Contrato'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* ====== Detail Modal ====== */}
      <Modal
        isOpen={showDetail}
        onClose={() => setShowDetail(false)}
        title="Detalle del Contrato"
        size="xl"
      >
        {detailLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-[#2E86C1]" />
          </div>
        ) : selectedLease ? (
          <div className="space-y-6">
            {/* Contract info */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Propiedad</p>
                <p className="text-sm font-medium text-[#2C3E50]">
                  {selectedLease.property?.name || selectedLease.propertyName || '—'}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Inquilino</p>
                <p className="text-sm font-medium text-[#2C3E50]">
                  {(() => {
                    const t = selectedLease.tenant || selectedLease.tenantPerson;
                    if (!t) return selectedLease.tenantName || '—';
                    return `${t.firstName || ''} ${t.lastName || ''}`.trim() || t.fullName || '—';
                  })()}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Fecha Inicio</p>
                <p className="text-sm text-[#2C3E50]">{formatDate(selectedLease.startDate)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Fecha Fin</p>
                <p className="text-sm text-[#2C3E50]">{formatDate(selectedLease.endDate)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Canon Mensual</p>
                <p className="text-sm font-semibold text-[#1B4F72]">
                  {formatCurrency(selectedLease.monthlyRent)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Deposito</p>
                <p className="text-sm text-[#2C3E50]">{formatCurrency(selectedLease.deposit)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Estado</p>
                <StatusBadge status={selectedLease.status} />
              </div>
            </div>

            {/* Terms */}
            {selectedLease.terms && (
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Terminos</p>
                <p className="text-sm text-[#2C3E50] bg-gray-50 rounded-lg p-3 whitespace-pre-wrap">
                  {selectedLease.terms}
                </p>
              </div>
            )}

            {/* Property details */}
            {selectedLease.property && (
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">
                  Detalles de Propiedad
                </p>
                <div className="bg-gray-50 rounded-lg p-3 grid grid-cols-2 gap-2 text-sm">
                  {selectedLease.property.address && (
                    <div>
                      <span className="text-gray-500">Direccion: </span>
                      <span className="text-[#2C3E50]">{selectedLease.property.address}</span>
                    </div>
                  )}
                  {selectedLease.property.city && (
                    <div>
                      <span className="text-gray-500">Ciudad: </span>
                      <span className="text-[#2C3E50]">{selectedLease.property.city}</span>
                    </div>
                  )}
                  {selectedLease.property.type && (
                    <div>
                      <span className="text-gray-500">Tipo: </span>
                      <span className="text-[#2C3E50]">{selectedLease.property.type}</span>
                    </div>
                  )}
                  {selectedLease.property.area && (
                    <div>
                      <span className="text-gray-500">Area: </span>
                      <span className="text-[#2C3E50]">{selectedLease.property.area} m²</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Tenant details */}
            {(selectedLease.tenant || selectedLease.tenantPerson) && (
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">
                  Detalles del Inquilino
                </p>
                <div className="bg-gray-50 rounded-lg p-3 grid grid-cols-2 gap-2 text-sm">
                  {(() => {
                    const t = selectedLease.tenant || selectedLease.tenantPerson;
                    return (
                      <>
                        {t.email && (
                          <div>
                            <span className="text-gray-500">Email: </span>
                            <span className="text-[#2C3E50]">{t.email}</span>
                          </div>
                        )}
                        {t.phone && (
                          <div>
                            <span className="text-gray-500">Telefono: </span>
                            <span className="text-[#2C3E50]">{t.phone}</span>
                          </div>
                        )}
                        {t.documentNumber && (
                          <div>
                            <span className="text-gray-500">Documento: </span>
                            <span className="text-[#2C3E50]">{t.documentNumber}</span>
                          </div>
                        )}
                      </>
                    );
                  })()}
                </div>
              </div>
            )}

            {/* Payment history */}
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">
                Historial de Pagos
              </p>
              {leasePayments.length === 0 ? (
                <p className="text-sm text-gray-400 italic">No hay pagos registrados para este contrato.</p>
              ) : (
                <div className="overflow-x-auto rounded-lg border border-gray-200">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-gray-100 text-[#2C3E50]">
                        <th className="px-3 py-2 text-left font-medium">Fecha</th>
                        <th className="px-3 py-2 text-left font-medium">Monto</th>
                        <th className="px-3 py-2 text-left font-medium">Metodo</th>
                        <th className="px-3 py-2 text-left font-medium">Estado</th>
                      </tr>
                    </thead>
                    <tbody>
                      {leasePayments.map((pay, idx) => (
                        <tr key={pay.id || pay._id || idx} className="border-t border-gray-100">
                          <td className="px-3 py-2">{formatDate(pay.paymentDate || pay.date)}</td>
                          <td className="px-3 py-2">{formatCurrency(pay.amount)}</td>
                          <td className="px-3 py-2">{pay.method || pay.paymentMethod || '—'}</td>
                          <td className="px-3 py-2">
                            <StatusBadge status={pay.status} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        ) : null}
      </Modal>

      {/* ====== Status Change Modal ====== */}
      <Modal
        isOpen={showStatusModal}
        onClose={() => setShowStatusModal(false)}
        title="Cambiar Estado del Contrato"
        size="md"
      >
        {statusTarget && (
          <div className="space-y-4">
            <p className="text-sm text-[#2C3E50]">
              Contrato actual en estado:{' '}
              <StatusBadge status={statusTarget.status} />
            </p>

            <Select
              label="Nuevo estado *"
              value={newStatus}
              onChange={(e) => setNewStatus(e.target.value)}
              options={availableStatuses}
            />

            <div className="w-full">
              <label className="block text-sm font-medium text-[#2C3E50] mb-1">
                Razon del cambio
              </label>
              <textarea
                rows={3}
                value={statusReason}
                onChange={(e) => setStatusReason(e.target.value)}
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-[#2C3E50] focus:outline-none focus:ring-2 focus:ring-[#2E86C1] focus:border-transparent resize-y"
                placeholder="Ingrese la razon del cambio de estado..."
              />
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <Button variant="secondary" onClick={() => setShowStatusModal(false)}>
                Cancelar
              </Button>
              <Button onClick={handleStatusChange} loading={statusSaving} disabled={!newStatus}>
                Cambiar Estado
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* ====== Delete Confirm Modal ====== */}
      <Modal
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        title="Eliminar Contrato"
        size="sm"
      >
        <div className="space-y-4">
          <div className="flex items-center gap-3 text-[#E74C3C]">
            <AlertTriangle className="w-6 h-6 flex-shrink-0" />
            <p className="text-sm">
              Esta seguro de eliminar este contrato? Esta accion no se puede deshacer.
            </p>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" onClick={() => setShowDeleteConfirm(false)}>
              Cancelar
            </Button>
            <Button variant="danger" onClick={handleDelete} loading={deleting}>
              Eliminar
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
