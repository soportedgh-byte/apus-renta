import React, { useState, useEffect, useCallback } from 'react';
import {
  Plus,
  Search,
  Eye,
  Pencil,
  Trash2,
  User,
  Loader2,
  Phone,
  Mail,
  FileText,
  AlertCircle,
  Users,
  ChevronDown,
  ChevronUp,
  DollarSign,
  Calendar,
  Home,
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

const DOCUMENT_TYPES = [
  { value: 'CC', label: 'Cedula de Ciudadania' },
  { value: 'CE', label: 'Cedula de Extranjeria' },
  { value: 'PASAPORTE', label: 'Pasaporte' },
  { value: 'NIT', label: 'NIT' },
];

const INITIAL_FORM = {
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  documentType: '',
  documentNumber: '',
  phone: '',
  emergencyContactName: '',
  emergencyContactPhone: '',
  notes: '',
};

const ITEMS_PER_PAGE = 10;

export default function TenantsPage() {
  const { user } = useAuth();
  const canManage = user?.role === 'PROPIETARIO';

  // --- State ---
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');

  // Modal state
  const [showFormModal, setShowFormModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleting, setDeleting] = useState(null);
  const [viewing, setViewing] = useState(null);
  const [formData, setFormData] = useState(INITIAL_FORM);
  const [formErrors, setFormErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  // Detail data
  const [detailLoading, setDetailLoading] = useState(false);
  const [tenantDetail, setTenantDetail] = useState(null);

  // --- Fetch ---
  const fetchTenants = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        page,
        limit: ITEMS_PER_PAGE,
      };
      if (search) params.search = search;

      const { data } = await api.get('/tenants', { params });
      const result = data.data || data;
      setTenants(result.tenants || result.items || result.docs || result || []);
      setTotalPages(result.totalPages || Math.ceil((result.total || 0) / ITEMS_PER_PAGE) || 1);
    } catch (err) {
      console.error('Error fetching tenants:', err);
      setTenants([]);
    } finally {
      setLoading(false);
    }
  }, [page, search]);

  useEffect(() => {
    fetchTenants();
  }, [fetchTenants]);

  useEffect(() => {
    setPage(1);
  }, [search]);

  // --- Fetch detail ---
  const fetchTenantDetail = async (tenant) => {
    setViewing(tenant);
    setShowDetailModal(true);
    setDetailLoading(true);
    try {
      const { data } = await api.get(`/tenants/${tenant._id || tenant.id}`);
      setTenantDetail(data.data || data);
    } catch (err) {
      console.error('Error fetching tenant detail:', err);
      setTenantDetail(tenant);
    } finally {
      setDetailLoading(false);
    }
  };

  // --- Validation ---
  const validate = () => {
    const errors = {};
    if (!formData.firstName.trim()) errors.firstName = 'El nombre es requerido';
    if (!formData.lastName.trim()) errors.lastName = 'El apellido es requerido';
    if (!formData.email.trim()) {
      errors.email = 'El email es requerido';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Email invalido';
    }
    if (!editing && !formData.password) {
      errors.password = 'La contrasena es requerida';
    } else if (!editing && formData.password.length < 6) {
      errors.password = 'Minimo 6 caracteres';
    }
    if (!formData.documentType) errors.documentType = 'El tipo de documento es requerido';
    if (!formData.documentNumber.trim()) errors.documentNumber = 'El numero de documento es requerido';
    if (!formData.phone.trim()) errors.phone = 'El telefono es requerido';
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // --- Handlers ---
  const handleOpenCreate = () => {
    setEditing(null);
    setFormData(INITIAL_FORM);
    setFormErrors({});
    setShowFormModal(true);
  };

  const handleOpenEdit = (tenant) => {
    setEditing(tenant);
    setFormData({
      firstName: tenant.firstName || '',
      lastName: tenant.lastName || '',
      email: tenant.email || '',
      password: '',
      documentType: tenant.documentType || '',
      documentNumber: tenant.documentNumber || '',
      phone: tenant.phone || '',
      emergencyContactName: tenant.emergencyContactName || '',
      emergencyContactPhone: tenant.emergencyContactPhone || '',
      notes: tenant.notes || '',
    });
    setFormErrors({});
    setShowFormModal(true);
  };

  const handleOpenDelete = (tenant) => {
    setDeleting(tenant);
    setShowDeleteModal(true);
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (formErrors[name]) {
      setFormErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setSubmitting(true);
    try {
      const payload = { ...formData };
      // Don't send empty password on edit
      if (editing && !payload.password) {
        delete payload.password;
      }
      // Remove empty optional fields
      if (!payload.emergencyContactName) delete payload.emergencyContactName;
      if (!payload.emergencyContactPhone) delete payload.emergencyContactPhone;
      if (!payload.notes) delete payload.notes;

      if (editing) {
        await api.put(`/tenants/${editing._id || editing.id}`, payload);
      } else {
        await api.post('/tenants', payload);
      }
      setShowFormModal(false);
      fetchTenants();
    } catch (err) {
      const msg = err.response?.data?.message || err.response?.data?.error || 'Error al guardar';
      setFormErrors({ _general: msg });
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleting) return;
    setSubmitting(true);
    try {
      await api.delete(`/tenants/${deleting._id || deleting.id}`);
      setShowDeleteModal(false);
      setDeleting(null);
      fetchTenants();
    } catch (err) {
      console.error('Error deleting tenant:', err);
    } finally {
      setSubmitting(false);
    }
  };

  // --- Format helpers ---
  const getFullName = (tenant) => `${tenant.firstName || ''} ${tenant.lastName || ''}`.trim();

  const getDocLabel = (type) => {
    const found = DOCUMENT_TYPES.find((d) => d.value === type);
    return found ? found.label : type;
  };

  const formatCurrency = (value) => {
    if (!value) return '$0';
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(value);
  };

  // --- Table columns ---
  const columns = [
    {
      key: 'name',
      label: 'Nombre',
      render: (_, row) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-[#D6EAF8] flex items-center justify-center flex-shrink-0">
            <User className="w-4 h-4 text-[#1B4F72]" />
          </div>
          <div>
            <p className="font-medium text-[#2C3E50]">{getFullName(row)}</p>
            <p className="text-xs text-gray-400">{row.email}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'document',
      label: 'Documento',
      render: (_, row) => (
        <span className="text-sm text-[#2C3E50]">
          {row.documentType} {row.documentNumber}
        </span>
      ),
    },
    {
      key: 'phone',
      label: 'Telefono',
      render: (_, row) => (
        <span className="text-sm text-[#2C3E50]">{row.phone || '-'}</span>
      ),
    },
    {
      key: 'property',
      label: 'Propiedad Actual',
      render: (_, row) => {
        const propName = row.currentProperty?.name || row.propertyName;
        return propName ? (
          <span className="text-sm text-[#2C3E50]">{propName}</span>
        ) : (
          <span className="text-sm text-gray-400 italic">Sin asignar</span>
        );
      },
    },
    {
      key: 'leaseStatus',
      label: 'Estado Contrato',
      render: (_, row) => {
        const status = row.currentLease?.status || row.leaseStatus;
        return status ? <StatusBadge status={status} /> : (
          <span className="text-sm text-gray-400">-</span>
        );
      },
    },
    {
      key: 'actions',
      label: 'Acciones',
      render: (_, row) => (
        <div className="flex items-center gap-1">
          <button
            onClick={() => fetchTenantDetail(row)}
            className="p-1.5 rounded-lg hover:bg-[#D6EAF8] text-[#2E86C1] transition-colors"
            title="Ver detalle"
          >
            <Eye className="w-4 h-4" />
          </button>
          {canManage && (
            <>
              <button
                onClick={() => handleOpenEdit(row)}
                className="p-1.5 rounded-lg hover:bg-[#D6EAF8] text-[#2E86C1] transition-colors"
                title="Editar"
              >
                <Pencil className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleOpenDelete(row)}
                className="p-1.5 rounded-lg hover:bg-red-50 text-[#E74C3C] transition-colors"
                title="Eliminar"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </>
          )}
        </div>
      ),
    },
  ];

  // --- Detail view helper ---
  const renderDetail = () => {
    if (detailLoading) {
      return (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-[#2E86C1]" />
        </div>
      );
    }

    const t = tenantDetail || viewing;
    if (!t) return null;

    const lease = t.currentLease || t.lease;
    const payments = t.payments || t.paymentHistory || [];

    return (
      <div className="space-y-6">
        {/* Personal info */}
        <div>
          <h4 className="text-sm font-semibold text-[#1B4F72] uppercase tracking-wider mb-3">
            Informacion Personal
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <InfoRow icon={User} label="Nombre" value={getFullName(t)} />
            <InfoRow icon={Mail} label="Email" value={t.email} />
            <InfoRow icon={FileText} label="Documento" value={`${getDocLabel(t.documentType)} - ${t.documentNumber}`} />
            <InfoRow icon={Phone} label="Telefono" value={t.phone} />
            {t.emergencyContactName && (
              <InfoRow icon={AlertCircle} label="Contacto emergencia" value={`${t.emergencyContactName} - ${t.emergencyContactPhone || ''}`} />
            )}
          </div>
          {t.notes && (
            <div className="mt-3 p-3 bg-gray-50 rounded-lg text-sm text-gray-600">
              <span className="font-medium text-[#2C3E50]">Notas: </span>{t.notes}
            </div>
          )}
        </div>

        {/* Lease info */}
        {lease && (
          <div>
            <h4 className="text-sm font-semibold text-[#1B4F72] uppercase tracking-wider mb-3">
              Contrato Actual
            </h4>
            <div className="bg-[#D6EAF8]/30 rounded-lg p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Propiedad</span>
                <span className="text-sm font-medium text-[#2C3E50]">{lease.property?.name || lease.propertyName || '-'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Estado</span>
                <StatusBadge status={lease.status} />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Canon mensual</span>
                <span className="text-sm font-medium text-[#2C3E50]">{formatCurrency(lease.monthlyRent)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Inicio</span>
                <span className="text-sm text-[#2C3E50]">{lease.startDate ? new Date(lease.startDate).toLocaleDateString('es-CO') : '-'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Fin</span>
                <span className="text-sm text-[#2C3E50]">{lease.endDate ? new Date(lease.endDate).toLocaleDateString('es-CO') : '-'}</span>
              </div>
            </div>
          </div>
        )}

        {/* Payment history summary */}
        {payments.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-[#1B4F72] uppercase tracking-wider mb-3">
              Historial de Pagos (ultimos)
            </h4>
            <div className="divide-y divide-gray-100 border border-gray-100 rounded-lg overflow-hidden">
              {payments.slice(0, 5).map((payment, idx) => (
                <div key={payment._id || payment.id || idx} className="flex items-center justify-between px-4 py-3 bg-white hover:bg-gray-50 transition-colors">
                  <div>
                    <p className="text-sm font-medium text-[#2C3E50]">
                      {payment.concept || payment.description || `Pago #${idx + 1}`}
                    </p>
                    <p className="text-xs text-gray-400">
                      {payment.date ? new Date(payment.date).toLocaleDateString('es-CO') : '-'}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-[#2C3E50]">{formatCurrency(payment.amount)}</p>
                    <StatusBadge status={payment.status} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {!lease && payments.length === 0 && (
          <div className="text-center py-6 text-gray-400 text-sm">
            Este inquilino no tiene contrato ni pagos registrados.
          </div>
        )}
      </div>
    );
  };

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <h2 className="text-2xl font-bold text-[#2C3E50]">Inquilinos</h2>
        {canManage && (
          <Button onClick={handleOpenCreate}>
            <Plus className="w-4 h-4" />
            Nuevo Inquilino
          </Button>
        )}
      </div>

      {/* Search */}
      <div className="mb-6 max-w-md">
        <Input
          placeholder="Buscar por nombre, email o documento..."
          icon={Search}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Empty state */}
      {!loading && tenants.length === 0 ? (
        <Card className="text-center py-16">
          <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-[#2C3E50] mb-2">No se encontraron inquilinos</h3>
          <p className="text-gray-500 mb-6">
            {search
              ? 'Intenta ajustar la busqueda.'
              : 'Comienza agregando tu primer inquilino.'}
          </p>
          {canManage && !search && (
            <Button onClick={handleOpenCreate}>
              <Plus className="w-4 h-4" />
              Nuevo Inquilino
            </Button>
          )}
        </Card>
      ) : (
        <Table
          columns={columns}
          data={tenants}
          loading={loading}
          emptyMessage="No hay inquilinos registrados"
          page={page}
          totalPages={totalPages}
          onPageChange={setPage}
        />
      )}

      {/* Create/Edit Modal */}
      <Modal
        isOpen={showFormModal}
        onClose={() => setShowFormModal(false)}
        title={editing ? 'Editar Inquilino' : 'Nuevo Inquilino'}
        size="xl"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {formErrors._general && (
            <div className="bg-red-50 text-[#E74C3C] px-4 py-3 rounded-lg text-sm">
              {formErrors._general}
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Nombre *"
              name="firstName"
              value={formData.firstName}
              onChange={handleFormChange}
              error={formErrors.firstName}
              placeholder="Nombre"
            />
            <Input
              label="Apellido *"
              name="lastName"
              value={formData.lastName}
              onChange={handleFormChange}
              error={formErrors.lastName}
              placeholder="Apellido"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Email *"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleFormChange}
              error={formErrors.email}
              placeholder="correo@ejemplo.com"
            />
            {!editing && (
              <Input
                label="Contrasena *"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleFormChange}
                error={formErrors.password}
                placeholder="Minimo 6 caracteres"
              />
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Select
              label="Tipo de Documento *"
              name="documentType"
              value={formData.documentType}
              onChange={handleFormChange}
              options={DOCUMENT_TYPES}
              error={formErrors.documentType}
            />
            <Input
              label="Numero de Documento *"
              name="documentNumber"
              value={formData.documentNumber}
              onChange={handleFormChange}
              error={formErrors.documentNumber}
              placeholder="Ej: 1234567890"
            />
          </div>

          <Input
            label="Telefono *"
            name="phone"
            value={formData.phone}
            onChange={handleFormChange}
            error={formErrors.phone}
            placeholder="Ej: 3001234567"
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Contacto de Emergencia"
              name="emergencyContactName"
              value={formData.emergencyContactName}
              onChange={handleFormChange}
              placeholder="Nombre del contacto"
            />
            <Input
              label="Telefono Emergencia"
              name="emergencyContactPhone"
              value={formData.emergencyContactPhone}
              onChange={handleFormChange}
              placeholder="Ej: 3007654321"
            />
          </div>

          <div className="w-full">
            <label className="block text-sm font-medium text-[#2C3E50] mb-1">Notas</label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleFormChange}
              rows={3}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-[#2C3E50] placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#2E86C1] focus:border-transparent resize-none"
              placeholder="Notas adicionales..."
            />
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setShowFormModal(false)}
            >
              Cancelar
            </Button>
            <Button type="submit" loading={submitting}>
              {editing ? 'Guardar Cambios' : 'Crear Inquilino'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Detail Modal */}
      <Modal
        isOpen={showDetailModal}
        onClose={() => { setShowDetailModal(false); setTenantDetail(null); }}
        title={viewing ? getFullName(viewing) : 'Detalle Inquilino'}
        size="lg"
      >
        {renderDetail()}
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Eliminar Inquilino"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Estas seguro de que deseas eliminar al inquilino{' '}
            <span className="font-semibold text-[#2C3E50]">
              {deleting ? getFullName(deleting) : ''}
            </span>?
            Esta accion no se puede deshacer.
          </p>
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
            <Button
              variant="secondary"
              onClick={() => setShowDeleteModal(false)}
            >
              Cancelar
            </Button>
            <Button
              variant="danger"
              loading={submitting}
              onClick={handleDelete}
            >
              Eliminar
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

// --- Small helper component ---
function InfoRow({ icon: Icon, label, value }) {
  return (
    <div className="flex items-start gap-2 text-sm">
      <Icon className="w-4 h-4 text-[#2E86C1] mt-0.5 flex-shrink-0" />
      <div>
        <span className="text-gray-500">{label}:</span>{' '}
        <span className="text-[#2C3E50] font-medium">{value || '-'}</span>
      </div>
    </div>
  );
}
