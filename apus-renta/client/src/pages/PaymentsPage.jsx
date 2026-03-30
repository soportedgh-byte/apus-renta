import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Plus,
  Eye,
  CheckCircle,
  XCircle,
  Download,
  Search,
  Loader2,
  Upload,
  FileText,
  Image as ImageIcon,
  AlertTriangle,
  X,
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

const PAYMENT_STATUS_OPTIONS = [
  { value: '', label: 'Todos los estados' },
  { value: 'PENDIENTE', label: 'Pendiente' },
  { value: 'APROBADO', label: 'Aprobado' },
  { value: 'RECHAZADO', label: 'Rechazado' },
];

const PAYMENT_METHODS = [
  { value: 'NEQUI', label: 'Nequi' },
  { value: 'BANCOLOMBIA', label: 'Bancolombia' },
  { value: 'DAVIVIENDA', label: 'Davivienda' },
  { value: 'EFECTIVO', label: 'Efectivo' },
  { value: 'TRANSFERENCIA', label: 'Transferencia' },
  { value: 'OTRO', label: 'Otro' },
];

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
  leaseId: '',
  amount: '',
  paymentDate: '',
  method: '',
  reference: '',
  notes: '',
};

export default function PaymentsPage() {
  const { user } = useAuth();
  const isPropietario = user?.role === 'PROPIETARIO';
  const isArrendatario = user?.role === 'ARRENDATARIO';

  // --- Data ---
  const [payments, setPayments] = useState([]);
  const [properties, setProperties] = useState([]);
  const [leases, setLeases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // --- Filters ---
  const [filterStatus, setFilterStatus] = useState('');
  const [filterProperty, setFilterProperty] = useState('');
  const [filterStartDate, setFilterStartDate] = useState('');
  const [filterEndDate, setFilterEndDate] = useState('');

  // --- Modals ---
  const [showForm, setShowForm] = useState(false);
  const [showDetail, setShowDetail] = useState(false);
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);

  // --- Form ---
  const [form, setForm] = useState(INITIAL_FORM);
  const [formErrors, setFormErrors] = useState({});
  const [saving, setSaving] = useState(false);
  const [supportFile, setSupportFile] = useState(null);
  const [supportPreview, setSupportPreview] = useState(null);
  const fileInputRef = useRef(null);

  // --- Detail ---
  const [selectedPayment, setSelectedPayment] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // --- Approve/Reject ---
  const [actionTarget, setActionTarget] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [actionSaving, setActionSaving] = useState(false);

  // --- Toast ---
  const [toast, setToast] = useState(null);

  const showToast = useCallback((message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  }, []);

  // ====== Fetch data ======

  const fetchPayments = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, limit: 10 };
      if (filterStatus) params.status = filterStatus;
      if (filterProperty) params.propertyId = filterProperty;
      if (filterStartDate) params.startDate = filterStartDate;
      if (filterEndDate) params.endDate = filterEndDate;
      const { data } = await api.get('/payments', { params });
      const result = data.data || data;
      setPayments(Array.isArray(result) ? result : result.payments || result.items || []);
      setTotalPages(result.totalPages || result.pages || Math.ceil((result.total || 0) / 10) || 1);
    } catch (err) {
      showToast(err.response?.data?.message || 'Error al cargar pagos', 'error');
    } finally {
      setLoading(false);
    }
  }, [page, filterStatus, filterProperty, filterStartDate, filterEndDate, showToast]);

  const fetchProperties = useCallback(async () => {
    try {
      const { data } = await api.get('/properties', { params: { limit: 200 } });
      const result = data.data || data;
      setProperties(Array.isArray(result) ? result : result.properties || result.items || []);
    } catch {
      /* silent */
    }
  }, []);

  const fetchLeases = useCallback(async () => {
    try {
      const params = { status: 'ACTIVO', limit: 200 };
      const { data } = await api.get('/leases', { params });
      const result = data.data || data;
      const list = Array.isArray(result) ? result : result.leases || result.items || [];
      setLeases(list);

      // Auto-select lease if tenant has only one
      if (isArrendatario && list.length === 1) {
        setForm((prev) => ({
          ...prev,
          leaseId: list[0].id || list[0]._id,
          amount: list[0].monthlyRent || '',
        }));
      }
    } catch {
      /* silent */
    }
  }, [isArrendatario]);

  useEffect(() => {
    fetchPayments();
  }, [fetchPayments]);

  useEffect(() => {
    fetchProperties();
    fetchLeases();
  }, [fetchProperties, fetchLeases]);

  // Reset page on filter change
  useEffect(() => {
    setPage(1);
  }, [filterStatus, filterProperty, filterStartDate, filterEndDate]);

  // ====== Helpers ======

  const propertyOptions = properties.map((p) => ({
    value: p.id || p._id,
    label: p.name || p.title || `${p.type} - ${p.address}`,
  }));

  const filterPropertyOptions = [{ value: '', label: 'Todas las propiedades' }, ...propertyOptions];

  const leaseOptions = leases.map((l) => ({
    value: l.id || l._id,
    label: `${l.property?.name || l.propertyName || 'Contrato'} - ${formatCurrency(l.monthlyRent)}/mes`,
  }));

  // ====== File handling ======

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSupportFile(file);

    // Preview for images
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (ev) => setSupportPreview(ev.target.result);
      reader.readAsDataURL(file);
    } else {
      setSupportPreview(null);
    }
  };

  const clearFile = () => {
    setSupportFile(null);
    setSupportPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // ====== Form handlers ======

  const openCreate = () => {
    setForm(INITIAL_FORM);
    setSupportFile(null);
    setSupportPreview(null);
    setFormErrors({});

    // Auto-fill if single lease
    if (leases.length === 1) {
      setForm((prev) => ({
        ...prev,
        leaseId: leases[0].id || leases[0]._id,
        amount: leases[0].monthlyRent || '',
      }));
    }

    setShowForm(true);
  };

  const handleLeaseChange = (leaseId) => {
    const lease = leases.find((l) => (l.id || l._id) === leaseId);
    setForm((prev) => ({
      ...prev,
      leaseId,
      amount: lease?.monthlyRent || prev.amount,
    }));
    if (formErrors.leaseId) {
      setFormErrors((prev) => {
        const next = { ...prev };
        delete next.leaseId;
        return next;
      });
    }
  };

  const validateForm = () => {
    const errors = {};
    if (!form.leaseId) errors.leaseId = 'Seleccione un contrato';
    if (!form.amount || Number(form.amount) <= 0) errors.amount = 'Monto requerido';
    if (!form.paymentDate) errors.paymentDate = 'Fecha de pago requerida';
    if (!form.method) errors.method = 'Seleccione un metodo de pago';
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    setSaving(true);
    try {
      const formData = new FormData();
      formData.append('leaseId', form.leaseId);
      formData.append('amount', Number(form.amount));
      formData.append('paymentDate', form.paymentDate);
      formData.append('method', form.method);
      if (form.reference) formData.append('reference', form.reference);
      if (form.notes) formData.append('notes', form.notes);
      if (supportFile) formData.append('support', supportFile);

      await api.post('/payments', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      showToast('Pago registrado exitosamente');
      setShowForm(false);
      clearFile();
      fetchPayments();
    } catch (err) {
      showToast(err.response?.data?.message || 'Error al registrar pago', 'error');
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

  const openDetail = async (payment) => {
    setSelectedPayment(payment);
    setShowDetail(true);
    setDetailLoading(true);
    try {
      const paymentId = payment.id || payment._id;
      const { data } = await api.get(`/payments/${paymentId}`);
      setSelectedPayment(data.data || data);
    } catch {
      /* keep existing data */
    } finally {
      setDetailLoading(false);
    }
  };

  // ====== Approve/Reject ======

  const openApprove = async (payment) => {
    setActionTarget(payment);
    setShowApproveModal(true);
    // Fetch full detail for support preview
    try {
      const paymentId = payment.id || payment._id;
      const { data } = await api.get(`/payments/${paymentId}`);
      setActionTarget(data.data || data);
    } catch {
      /* keep existing */
    }
  };

  const handleApprove = async () => {
    setActionSaving(true);
    try {
      const paymentId = actionTarget.id || actionTarget._id;
      await api.patch(`/payments/${paymentId}/approve`);
      showToast('Pago aprobado exitosamente');
      setShowApproveModal(false);
      fetchPayments();
    } catch (err) {
      showToast(err.response?.data?.message || 'Error al aprobar pago', 'error');
    } finally {
      setActionSaving(false);
    }
  };

  const openReject = async (payment) => {
    setActionTarget(payment);
    setRejectionReason('');
    setShowRejectModal(true);
    try {
      const paymentId = payment.id || payment._id;
      const { data } = await api.get(`/payments/${paymentId}`);
      setActionTarget(data.data || data);
    } catch {
      /* keep existing */
    }
  };

  const handleReject = async () => {
    if (!rejectionReason.trim()) return;
    setActionSaving(true);
    try {
      const paymentId = actionTarget.id || actionTarget._id;
      await api.patch(`/payments/${paymentId}/reject`, {
        rejectionReason: rejectionReason.trim(),
      });
      showToast('Pago rechazado');
      setShowRejectModal(false);
      fetchPayments();
    } catch (err) {
      showToast(err.response?.data?.message || 'Error al rechazar pago', 'error');
    } finally {
      setActionSaving(false);
    }
  };

  // ====== Receipt download ======

  const downloadReceipt = (payment) => {
    const paymentId = payment.id || payment._id;
    const token = localStorage.getItem('token');
    window.open(`/api/v1/payments/${paymentId}/receipt/download?token=${token}`, '_blank');
  };

  // ====== Support image URL helper ======

  const getSupportUrl = (payment) => {
    if (!payment) return null;
    return payment.supportUrl || payment.supportFile || payment.support || null;
  };

  // ====== Table columns ======

  const columns = [
    {
      key: 'property',
      label: 'Propiedad',
      render: (_, row) =>
        row.property?.name ||
        row.lease?.property?.name ||
        row.propertyName ||
        row.lease?.propertyName ||
        '—',
    },
    {
      key: 'tenant',
      label: 'Inquilino',
      render: (_, row) => {
        const t = row.tenant || row.tenantPerson || row.lease?.tenant;
        if (!t) return row.tenantName || '—';
        return `${t.firstName || ''} ${t.lastName || ''}`.trim() || t.fullName || t.email || '—';
      },
    },
    {
      key: 'amount',
      label: 'Monto',
      render: (val) => (
        <span className="font-medium text-[#1B4F72]">{formatCurrency(val)}</span>
      ),
    },
    {
      key: 'paymentDate',
      label: 'Fecha',
      render: (val, row) => formatDate(val || row.date),
    },
    {
      key: 'method',
      label: 'Metodo',
      render: (val, row) => val || row.paymentMethod || '—',
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
        const isPending = status === 'PENDIENTE';
        const isApproved = status === 'APROBADO';

        return (
          <div className="flex items-center gap-1">
            <button
              onClick={() => openDetail(row)}
              className="p-1.5 rounded-lg hover:bg-[#D6EAF8] text-[#2E86C1] transition-colors"
              title="Ver detalles"
            >
              <Eye className="w-4 h-4" />
            </button>

            {isPropietario && isPending && (
              <>
                <button
                  onClick={() => openApprove(row)}
                  className="p-1.5 rounded-lg hover:bg-green-100 text-green-600 transition-colors"
                  title="Aprobar"
                >
                  <CheckCircle className="w-4 h-4" />
                </button>
                <button
                  onClick={() => openReject(row)}
                  className="p-1.5 rounded-lg hover:bg-red-100 text-red-600 transition-colors"
                  title="Rechazar"
                >
                  <XCircle className="w-4 h-4" />
                </button>
              </>
            )}

            {isApproved && (
              <button
                onClick={() => downloadReceipt(row)}
                className="p-1.5 rounded-lg hover:bg-[#D6EAF8] text-[#1B4F72] transition-colors"
                title="Descargar recibo"
              >
                <Download className="w-4 h-4" />
              </button>
            )}
          </div>
        );
      },
    },
  ];

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
        <h2 className="text-2xl font-bold text-[#2C3E50]">Pagos</h2>
        {isArrendatario && (
          <Button onClick={openCreate}>
            <Plus className="w-4 h-4" />
            Registrar Pago
          </Button>
        )}
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-col sm:flex-row gap-4 flex-wrap">
          <Select
            label="Estado"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            options={PAYMENT_STATUS_OPTIONS.slice(1)}
            className="sm:w-48"
          />
          <Select
            label="Propiedad"
            value={filterProperty}
            onChange={(e) => setFilterProperty(e.target.value)}
            options={filterPropertyOptions.slice(1)}
            className="sm:w-56"
          />
          <Input
            label="Fecha desde"
            type="date"
            value={filterStartDate}
            onChange={(e) => setFilterStartDate(e.target.value)}
            className="sm:w-44"
          />
          <Input
            label="Fecha hasta"
            type="date"
            value={filterEndDate}
            onChange={(e) => setFilterEndDate(e.target.value)}
            className="sm:w-44"
          />
        </div>
      </Card>

      {/* Table */}
      <Table
        columns={columns}
        data={payments}
        loading={loading}
        emptyMessage="No se encontraron pagos"
        page={page}
        totalPages={totalPages}
        onPageChange={setPage}
      />

      {/* ====== Create Payment Modal (ARRENDATARIO) ====== */}
      <Modal
        isOpen={showForm}
        onClose={() => {
          setShowForm(false);
          clearFile();
        }}
        title="Registrar Pago"
        size="lg"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Select
            label="Contrato *"
            value={form.leaseId}
            onChange={(e) => handleLeaseChange(e.target.value)}
            options={leaseOptions}
            error={formErrors.leaseId}
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Monto (COP) *"
              type="number"
              min="0"
              value={form.amount}
              onChange={(e) => handleFieldChange('amount', e.target.value)}
              error={formErrors.amount}
            />
            <Input
              label="Fecha de Pago *"
              type="date"
              value={form.paymentDate}
              onChange={(e) => handleFieldChange('paymentDate', e.target.value)}
              error={formErrors.paymentDate}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Select
              label="Metodo de Pago *"
              value={form.method}
              onChange={(e) => handleFieldChange('method', e.target.value)}
              options={PAYMENT_METHODS}
              error={formErrors.method}
            />
            <Input
              label="Referencia"
              value={form.reference}
              onChange={(e) => handleFieldChange('reference', e.target.value)}
              placeholder="No. de transaccion"
            />
          </div>

          {/* File upload */}
          <div className="w-full">
            <label className="block text-sm font-medium text-[#2C3E50] mb-1">
              Soporte de pago
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-[#2E86C1] transition-colors">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*,.pdf"
                onChange={handleFileChange}
                className="hidden"
                id="support-file"
              />

              {supportFile ? (
                <div className="space-y-2">
                  {supportPreview && (
                    <img
                      src={supportPreview}
                      alt="Preview"
                      className="mx-auto max-h-32 rounded-lg object-contain"
                    />
                  )}
                  <div className="flex items-center justify-center gap-2 text-sm text-[#2C3E50]">
                    {supportFile.type.startsWith('image/') ? (
                      <ImageIcon className="w-4 h-4 text-[#2E86C1]" />
                    ) : (
                      <FileText className="w-4 h-4 text-[#2E86C1]" />
                    )}
                    <span>{supportFile.name}</span>
                    <button
                      type="button"
                      onClick={clearFile}
                      className="p-0.5 rounded hover:bg-red-100 text-red-500"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ) : (
                <label
                  htmlFor="support-file"
                  className="cursor-pointer space-y-1 block"
                >
                  <Upload className="w-8 h-8 mx-auto text-gray-400" />
                  <p className="text-sm text-gray-500">
                    Clic para subir imagen o PDF del soporte
                  </p>
                  <p className="text-xs text-gray-400">
                    JPG, PNG o PDF
                  </p>
                </label>
              )}
            </div>
          </div>

          <div className="w-full">
            <label className="block text-sm font-medium text-[#2C3E50] mb-1">Notas</label>
            <textarea
              rows={3}
              value={form.notes}
              onChange={(e) => handleFieldChange('notes', e.target.value)}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-[#2C3E50] focus:outline-none focus:ring-2 focus:ring-[#2E86C1] focus:border-transparent resize-y"
              placeholder="Notas adicionales..."
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button
              variant="secondary"
              type="button"
              onClick={() => {
                setShowForm(false);
                clearFile();
              }}
            >
              Cancelar
            </Button>
            <Button type="submit" loading={saving}>
              Registrar Pago
            </Button>
          </div>
        </form>
      </Modal>

      {/* ====== Detail Modal ====== */}
      <Modal
        isOpen={showDetail}
        onClose={() => setShowDetail(false)}
        title="Detalle del Pago"
        size="lg"
      >
        {detailLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-[#2E86C1]" />
          </div>
        ) : selectedPayment ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Propiedad</p>
                <p className="text-sm font-medium text-[#2C3E50]">
                  {selectedPayment.property?.name ||
                    selectedPayment.lease?.property?.name ||
                    selectedPayment.propertyName ||
                    '—'}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Inquilino</p>
                <p className="text-sm font-medium text-[#2C3E50]">
                  {(() => {
                    const t =
                      selectedPayment.tenant ||
                      selectedPayment.tenantPerson ||
                      selectedPayment.lease?.tenant;
                    if (!t) return selectedPayment.tenantName || '—';
                    return (
                      `${t.firstName || ''} ${t.lastName || ''}`.trim() ||
                      t.fullName ||
                      '—'
                    );
                  })()}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Monto</p>
                <p className="text-sm font-semibold text-[#1B4F72]">
                  {formatCurrency(selectedPayment.amount)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Fecha de Pago</p>
                <p className="text-sm text-[#2C3E50]">
                  {formatDate(selectedPayment.paymentDate || selectedPayment.date)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Metodo</p>
                <p className="text-sm text-[#2C3E50]">
                  {selectedPayment.method || selectedPayment.paymentMethod || '—'}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Referencia</p>
                <p className="text-sm text-[#2C3E50]">{selectedPayment.reference || '—'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Estado</p>
                <StatusBadge status={selectedPayment.status} />
              </div>
              {selectedPayment.rejectionReason && (
                <div className="sm:col-span-2">
                  <p className="text-xs text-gray-500 uppercase tracking-wider">Razon de Rechazo</p>
                  <p className="text-sm text-[#E74C3C]">{selectedPayment.rejectionReason}</p>
                </div>
              )}
            </div>

            {selectedPayment.notes && (
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Notas</p>
                <p className="text-sm text-[#2C3E50] bg-gray-50 rounded-lg p-3">
                  {selectedPayment.notes}
                </p>
              </div>
            )}

            {/* Support image */}
            {getSupportUrl(selectedPayment) && (
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">
                  Soporte de Pago
                </p>
                <div className="rounded-lg border border-gray-200 overflow-hidden">
                  <img
                    src={getSupportUrl(selectedPayment)}
                    alt="Soporte de pago"
                    className="w-full max-h-64 object-contain bg-gray-50"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                  <div className="hidden items-center justify-center gap-2 p-4 text-gray-500 text-sm">
                    <FileText className="w-5 h-5" />
                    <a
                      href={getSupportUrl(selectedPayment)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#2E86C1] underline"
                    >
                      Ver archivo adjunto
                    </a>
                  </div>
                </div>
              </div>
            )}

            {/* Receipt download */}
            {(selectedPayment.status || '').toUpperCase() === 'APROBADO' && (
              <div className="pt-2">
                <Button
                  variant="outline"
                  onClick={() => downloadReceipt(selectedPayment)}
                >
                  <Download className="w-4 h-4" />
                  Descargar Recibo
                </Button>
              </div>
            )}
          </div>
        ) : null}
      </Modal>

      {/* ====== Approve Modal ====== */}
      <Modal
        isOpen={showApproveModal}
        onClose={() => setShowApproveModal(false)}
        title="Aprobar Pago"
        size="lg"
      >
        {actionTarget && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Inquilino</p>
                <p className="text-sm font-medium text-[#2C3E50]">
                  {(() => {
                    const t =
                      actionTarget.tenant ||
                      actionTarget.tenantPerson ||
                      actionTarget.lease?.tenant;
                    if (!t) return actionTarget.tenantName || '—';
                    return (
                      `${t.firstName || ''} ${t.lastName || ''}`.trim() ||
                      t.fullName ||
                      '—'
                    );
                  })()}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Monto</p>
                <p className="text-sm font-semibold text-[#1B4F72]">
                  {formatCurrency(actionTarget.amount)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Fecha</p>
                <p className="text-sm text-[#2C3E50]">
                  {formatDate(actionTarget.paymentDate || actionTarget.date)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Metodo</p>
                <p className="text-sm text-[#2C3E50]">
                  {actionTarget.method || actionTarget.paymentMethod || '—'}
                </p>
              </div>
            </div>

            {getSupportUrl(actionTarget) && (
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">
                  Soporte de Pago
                </p>
                <img
                  src={getSupportUrl(actionTarget)}
                  alt="Soporte"
                  className="w-full max-h-48 object-contain rounded-lg border border-gray-200 bg-gray-50"
                />
              </div>
            )}

            <div className="flex justify-end gap-3 pt-2">
              <Button variant="secondary" onClick={() => setShowApproveModal(false)}>
                Cancelar
              </Button>
              <Button variant="success" onClick={handleApprove} loading={actionSaving}>
                <CheckCircle className="w-4 h-4" />
                Confirmar Aprobacion
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* ====== Reject Modal ====== */}
      <Modal
        isOpen={showRejectModal}
        onClose={() => setShowRejectModal(false)}
        title="Rechazar Pago"
        size="lg"
      >
        {actionTarget && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Inquilino</p>
                <p className="text-sm font-medium text-[#2C3E50]">
                  {(() => {
                    const t =
                      actionTarget.tenant ||
                      actionTarget.tenantPerson ||
                      actionTarget.lease?.tenant;
                    if (!t) return actionTarget.tenantName || '—';
                    return (
                      `${t.firstName || ''} ${t.lastName || ''}`.trim() ||
                      t.fullName ||
                      '—'
                    );
                  })()}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Monto</p>
                <p className="text-sm font-semibold text-[#1B4F72]">
                  {formatCurrency(actionTarget.amount)}
                </p>
              </div>
            </div>

            {getSupportUrl(actionTarget) && (
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">
                  Soporte de Pago
                </p>
                <img
                  src={getSupportUrl(actionTarget)}
                  alt="Soporte"
                  className="w-full max-h-48 object-contain rounded-lg border border-gray-200 bg-gray-50"
                />
              </div>
            )}

            <div className="w-full">
              <label className="block text-sm font-medium text-[#2C3E50] mb-1">
                Razon del rechazo *
              </label>
              <textarea
                rows={3}
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-[#2C3E50] focus:outline-none focus:ring-2 focus:ring-[#2E86C1] focus:border-transparent resize-y"
                placeholder="Ingrese la razon del rechazo..."
              />
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <Button variant="secondary" onClick={() => setShowRejectModal(false)}>
                Cancelar
              </Button>
              <Button
                variant="danger"
                onClick={handleReject}
                loading={actionSaving}
                disabled={!rejectionReason.trim()}
              >
                <XCircle className="w-4 h-4" />
                Confirmar Rechazo
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
