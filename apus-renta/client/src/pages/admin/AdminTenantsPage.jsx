import React, { useState, useEffect, useCallback } from 'react';
import {
  Plus,
  Search,
  Eye,
  Pencil,
  XCircle,
  X,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
} from 'lucide-react';
import api from '../../services/api';

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

const PLANS = ['FREE', 'BASIC', 'PRO', 'ENTERPRISE'];
const STATUSES = ['ACTIVE', 'SUSPENDED', 'INACTIVE'];

function formatDate(dateStr) {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleDateString('es-CO', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

// ─── Modal Wrapper ───
function Modal({ open, onClose, title, children, maxWidth = 'max-w-lg' }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div
        className={`relative bg-white rounded-xl shadow-xl w-full ${maxWidth} mx-4 max-h-[90vh] overflow-y-auto`}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-[#2C3E50]">{title}</h2>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-gray-100">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        <div className="px-6 py-4">{children}</div>
      </div>
    </div>
  );
}

// ─── Create / Edit Modal ───
function TenantFormModal({ open, onClose, tenant, onSaved }) {
  const isEdit = !!tenant;
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    firstName: '',
    lastName: '',
    plan: 'FREE',
    maxProperties: 5,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (tenant) {
      setForm({
        name: tenant.name || '',
        email: tenant.ownerEmail || '',
        password: '',
        firstName: tenant.ownerFirstName || tenant.firstName || '',
        lastName: tenant.ownerLastName || tenant.lastName || '',
        plan: tenant.plan || 'FREE',
        maxProperties: tenant.maxProperties ?? 5,
      });
    } else {
      setForm({
        name: '',
        email: '',
        password: '',
        firstName: '',
        lastName: '',
        plan: 'FREE',
        maxProperties: 5,
      });
    }
    setError(null);
  }, [tenant, open]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: name === 'maxProperties' ? Number(value) : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const payload = { ...form };
      if (isEdit) {
        delete payload.password;
        await api.put(`/admin/tenants/${tenant.id || tenant._id}`, payload);
      } else {
        await api.post('/admin/tenants', payload);
      }
      onSaved();
      onClose();
    } catch (err) {
      setError(err.response?.data?.message || 'Error al guardar');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? 'Editar Cliente' : 'Nuevo Cliente'}>
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg text-sm">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Nombre de Organizacion</label>
          <input
            name="name"
            value={form.name}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#2E86C1] focus:border-[#2E86C1] outline-none"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
            <input
              name="firstName"
              value={form.firstName}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#2E86C1] focus:border-[#2E86C1] outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Apellido</label>
            <input
              name="lastName"
              value={form.lastName}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#2E86C1] focus:border-[#2E86C1] outline-none"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email del Propietario</label>
          <input
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#2E86C1] focus:border-[#2E86C1] outline-none"
          />
        </div>

        {!isEdit && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Contrasena</label>
            <input
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              required
              minLength={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#2E86C1] focus:border-[#2E86C1] outline-none"
            />
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Plan</label>
            <select
              name="plan"
              value={form.plan}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#2E86C1] focus:border-[#2E86C1] outline-none"
            >
              {PLANS.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Max Propiedades</label>
            <input
              name="maxProperties"
              type="number"
              min={1}
              value={form.maxProperties}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#2E86C1] focus:border-[#2E86C1] outline-none"
            />
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={saving}
            className="px-4 py-2 text-sm font-medium text-white bg-[#1B4F72] rounded-lg hover:bg-[#1B4F72]/90 disabled:opacity-50"
          >
            {saving ? 'Guardando...' : isEdit ? 'Actualizar' : 'Crear'}
          </button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Detail Modal ───
function TenantDetailModal({ open, onClose, tenantId }) {
  const [tenant, setTenant] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!tenantId || !open) return;
    const fetchDetail = async () => {
      setLoading(true);
      try {
        const [tenantRes, statsRes] = await Promise.all([
          api.get(`/admin/tenants/${tenantId}`),
          api.get(`/admin/tenants/${tenantId}/stats`).catch(() => ({ data: { data: {} } })),
        ]);
        setTenant(tenantRes.data.data || tenantRes.data);
        setStats(statsRes.data.data || statsRes.data);
      } catch {
        setTenant(null);
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [tenantId, open]);

  return (
    <Modal open={open} onClose={onClose} title="Detalle del Cliente" maxWidth="max-w-xl">
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="w-6 h-6 border-4 border-[#2E86C1] border-t-transparent rounded-full animate-spin" />
        </div>
      ) : tenant ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Organizacion</p>
              <p className="font-medium text-[#2C3E50]">{tenant.name}</p>
            </div>
            <div>
              <p className="text-gray-500">Plan</p>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${PLAN_BADGE[tenant.plan] || PLAN_BADGE.FREE}`}>
                {tenant.plan}
              </span>
            </div>
            <div>
              <p className="text-gray-500">Propietario</p>
              <p className="font-medium text-[#2C3E50]">
                {tenant.ownerFirstName || ''} {tenant.ownerLastName || ''}
              </p>
            </div>
            <div>
              <p className="text-gray-500">Email</p>
              <p className="font-medium text-[#2C3E50]">{tenant.ownerEmail}</p>
            </div>
            <div>
              <p className="text-gray-500">Estado</p>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_BADGE[tenant.status] || 'bg-gray-100 text-gray-700'}`}>
                {tenant.status}
              </span>
            </div>
            <div>
              <p className="text-gray-500">Fecha de Creacion</p>
              <p className="font-medium text-[#2C3E50]">{formatDate(tenant.createdAt)}</p>
            </div>
          </div>

          {stats && (
            <>
              <hr className="border-gray-200" />
              <h3 className="font-semibold text-[#2C3E50]">Estadisticas</h3>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="bg-gray-50 p-3 rounded-lg text-center">
                  <p className="text-gray-500">Propiedades</p>
                  <p className="text-xl font-bold text-[#1B4F72]">{stats.properties ?? 0}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg text-center">
                  <p className="text-gray-500">Usuarios</p>
                  <p className="text-xl font-bold text-[#2E86C1]">{stats.users ?? 0}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg text-center">
                  <p className="text-gray-500">Contratos</p>
                  <p className="text-xl font-bold text-[#27AE60]">{stats.leases ?? 0}</p>
                </div>
              </div>
            </>
          )}
        </div>
      ) : (
        <p className="text-gray-400 text-center py-8">No se pudo cargar la informacion</p>
      )}
    </Modal>
  );
}

// ─── Delete Confirmation ───
function DeleteConfirmModal({ open, onClose, tenant, onConfirm }) {
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await api.put(`/admin/tenants/${tenant.id || tenant._id}`, { status: 'INACTIVE' });
      onConfirm();
      onClose();
    } catch {
      // silent
    } finally {
      setDeleting(false);
    }
  };

  if (!open || !tenant) return null;

  return (
    <Modal open={open} onClose={onClose} title="Desactivar Cliente" maxWidth="max-w-sm">
      <div className="text-center space-y-4">
        <div className="mx-auto w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
          <AlertTriangle className="w-6 h-6 text-[#E74C3C]" />
        </div>
        <p className="text-sm text-gray-600">
          Estas seguro de desactivar a <strong>{tenant.name}</strong>? El cliente no podra acceder al sistema.
        </p>
        <div className="flex justify-center gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            Cancelar
          </button>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="px-4 py-2 text-sm font-medium text-white bg-[#E74C3C] rounded-lg hover:bg-[#E74C3C]/90 disabled:opacity-50"
          >
            {deleting ? 'Desactivando...' : 'Desactivar'}
          </button>
        </div>
      </div>
    </Modal>
  );
}

// ─── Main Page ───
export default function AdminTenantsPage() {
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [search, setSearch] = useState('');
  const [filterPlan, setFilterPlan] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const limit = 10;

  // Modals
  const [formOpen, setFormOpen] = useState(false);
  const [editTenant, setEditTenant] = useState(null);
  const [detailId, setDetailId] = useState(null);
  const [deleteTenant, setDeleteTenant] = useState(null);

  const fetchTenants = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { page, limit };
      if (search) params.search = search;
      if (filterPlan) params.plan = filterPlan;
      if (filterStatus) params.status = filterStatus;

      const res = await api.get('/admin/tenants', { params });
      const result = res.data.data || res.data;
      setTenants(result.tenants || result.rows || result || []);
      setTotalPages(result.totalPages || Math.ceil((result.total || 0) / limit) || 1);
    } catch (err) {
      setError(err.response?.data?.message || 'Error al cargar clientes');
    } finally {
      setLoading(false);
    }
  }, [page, search, filterPlan, filterStatus]);

  useEffect(() => {
    fetchTenants();
  }, [fetchTenants]);

  const handleEdit = (tenant) => {
    setEditTenant(tenant);
    setFormOpen(true);
  };

  const handleCreate = () => {
    setEditTenant(null);
    setFormOpen(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-[#2C3E50]">Clientes</h1>
        <button
          onClick={handleCreate}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-[#1B4F72] rounded-lg hover:bg-[#1B4F72]/90"
        >
          <Plus className="w-4 h-4" />
          Nuevo Cliente
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Buscar por nombre o email..."
            className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#2E86C1] focus:border-[#2E86C1] outline-none"
          />
        </div>
        <select
          value={filterPlan}
          onChange={(e) => { setFilterPlan(e.target.value); setPage(1); }}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#2E86C1] focus:border-[#2E86C1] outline-none"
        >
          <option value="">Todos los Planes</option>
          {PLANS.map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
        <select
          value={filterStatus}
          onChange={(e) => { setFilterStatus(e.target.value); setPage(1); }}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#2E86C1] focus:border-[#2E86C1] outline-none"
        >
          <option value="">Todos los Estados</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-x-auto">
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="w-6 h-6 border-4 border-[#2E86C1] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b border-gray-100">
                <th className="px-5 py-3 font-medium">Nombre</th>
                <th className="px-5 py-3 font-medium">Propietario</th>
                <th className="px-5 py-3 font-medium">Plan</th>
                <th className="px-5 py-3 font-medium">Estado</th>
                <th className="px-5 py-3 font-medium">Propiedades</th>
                <th className="px-5 py-3 font-medium">Fecha</th>
                <th className="px-5 py-3 font-medium">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {tenants.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center text-gray-400 py-10">
                    No se encontraron clientes
                  </td>
                </tr>
              ) : (
                tenants.map((t) => (
                  <tr key={t.id || t._id} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="px-5 py-3 font-medium text-[#2C3E50]">{t.name}</td>
                    <td className="px-5 py-3 text-gray-600">{t.ownerEmail || '-'}</td>
                    <td className="px-5 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${PLAN_BADGE[t.plan] || PLAN_BADGE.FREE}`}>
                        {t.plan}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_BADGE[t.status] || 'bg-gray-100 text-gray-700'}`}>
                        {t.status}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-gray-600">{t.propertyCount ?? t.properties ?? 0}</td>
                    <td className="px-5 py-3 text-gray-500">{formatDate(t.createdAt)}</td>
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => setDetailId(t.id || t._id)}
                          title="Ver"
                          className="p-1.5 rounded-lg hover:bg-[#D6EAF8] text-gray-500 hover:text-[#1B4F72]"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleEdit(t)}
                          title="Editar"
                          className="p-1.5 rounded-lg hover:bg-[#D6EAF8] text-gray-500 hover:text-[#1B4F72]"
                        >
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => setDeleteTenant(t)}
                          title="Desactivar"
                          className="p-1.5 rounded-lg hover:bg-red-50 text-gray-500 hover:text-[#E74C3C]"
                        >
                          <XCircle className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500">
            Pagina {page} de {totalPages}
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Modals */}
      <TenantFormModal
        open={formOpen}
        onClose={() => { setFormOpen(false); setEditTenant(null); }}
        tenant={editTenant}
        onSaved={fetchTenants}
      />
      <TenantDetailModal
        open={!!detailId}
        onClose={() => setDetailId(null)}
        tenantId={detailId}
      />
      <DeleteConfirmModal
        open={!!deleteTenant}
        onClose={() => setDeleteTenant(null)}
        tenant={deleteTenant}
        onConfirm={fetchTenants}
      />
    </div>
  );
}
