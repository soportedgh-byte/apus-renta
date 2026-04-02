import React, { useState, useEffect, useCallback } from 'react';
import {
  Building2,
  Plus,
  Search,
  Pencil,
  Trash2,
  BedDouble,
  Bath,
  Maximize,
  ChevronLeft,
  ChevronRight,
  Loader2,
  X,
  Upload,
  DollarSign,
  MapPin,
  ImageOff,
} from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';
import StatusBadge from '../components/ui/StatusBadge';
import Modal from '../components/ui/Modal';

const PROPERTY_TYPES = [
  { value: 'CASA', label: 'Casa' },
  { value: 'APARTAMENTO', label: 'Apartamento' },
  { value: 'LOCAL', label: 'Local' },
  { value: 'OFICINA', label: 'Oficina' },
  { value: 'BODEGA', label: 'Bodega' },
];

const PROPERTY_STATUS = [
  { value: 'DISPONIBLE', label: 'Disponible' },
  { value: 'OCUPADO', label: 'Ocupado' },
  { value: 'MANTENIMIENTO', label: 'Mantenimiento' },
];

const INITIAL_FORM = {
  name: '',
  type: '',
  address: '',
  city: '',
  area: '',
  bedrooms: '',
  bathrooms: '',
  monthlyRent: '',
  description: '',
};

const ITEMS_PER_PAGE = 9;

export default function PropertiesPage() {
  const { user } = useAuth();
  const canManage = ['PROPIETARIO', 'ENCARGADO'].includes(user?.role);

  // --- State ---
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  // Modal state
  const [showFormModal, setShowFormModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleting, setDeleting] = useState(null);
  const [formData, setFormData] = useState(INITIAL_FORM);
  const [formErrors, setFormErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  // Photo state
  const [photoFiles, setPhotoFiles] = useState([]);
  const [photoPreviews, setPhotoPreviews] = useState([]);

  // Carousel state per card
  const [carouselIndexes, setCarouselIndexes] = useState({});

  // --- Fetch ---
  const fetchProperties = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        page,
        limit: ITEMS_PER_PAGE,
      };
      if (search) params.search = search;
      if (filterType) params.type = filterType;
      if (filterStatus) params.status = filterStatus;

      const { data } = await api.get('/properties', { params });
      const result = data.data || data;
      setProperties(result.properties || result.items || result.docs || result || []);
      setTotalPages(result.totalPages || Math.ceil((result.total || 0) / ITEMS_PER_PAGE) || 1);
    } catch (err) {
      console.error('Error fetching properties:', err);
      setProperties([]);
    } finally {
      setLoading(false);
    }
  }, [page, search, filterType, filterStatus]);

  useEffect(() => {
    fetchProperties();
  }, [fetchProperties]);

  // Reset page when filters change
  useEffect(() => {
    setPage(1);
  }, [search, filterType, filterStatus]);

  // --- Validation ---
  const validate = () => {
    const errors = {};
    if (!formData.name.trim()) errors.name = 'El nombre es requerido';
    if (!formData.type) errors.type = 'El tipo es requerido';
    if (!formData.address.trim()) errors.address = 'La direccion es requerida';
    if (!formData.city.trim()) errors.city = 'La ciudad es requerida';
    if (!formData.monthlyRent || Number(formData.monthlyRent) <= 0) {
      errors.monthlyRent = 'El canon mensual debe ser mayor a 0';
    }
    if (formData.area && Number(formData.area) <= 0) {
      errors.area = 'El area debe ser mayor a 0';
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // --- Handlers ---
  const handleOpenCreate = () => {
    setEditing(null);
    setFormData(INITIAL_FORM);
    setFormErrors({});
    setPhotoFiles([]);
    setPhotoPreviews([]);
    setShowFormModal(true);
  };

  const handleOpenEdit = (property) => {
    setEditing(property);
    setFormData({
      name: property.name || '',
      type: property.type || '',
      address: property.address || '',
      city: property.city || '',
      area: property.area || '',
      bedrooms: property.bedrooms || '',
      bathrooms: property.bathrooms || '',
      monthlyRent: property.monthlyRent || '',
      description: property.description || '',
    });
    setFormErrors({});
    setPhotoFiles([]);
    setPhotoPreviews(property.photos || []);
    setShowFormModal(true);
  };

  const handleOpenDelete = (property) => {
    setDeleting(property);
    setShowDeleteModal(true);
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (formErrors[name]) {
      setFormErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handlePhotoChange = (e) => {
    const files = Array.from(e.target.files);
    setPhotoFiles((prev) => [...prev, ...files]);

    files.forEach((file) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreviews((prev) => [...prev, reader.result]);
      };
      reader.readAsDataURL(file);
    });
  };

  const handleRemovePhoto = (index) => {
    setPhotoPreviews((prev) => prev.filter((_, i) => i !== index));
    setPhotoFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setSubmitting(true);
    try {
      const payload = new FormData();
      Object.entries(formData).forEach(([key, value]) => {
        if (value !== '' && value !== undefined) {
          payload.append(key, value);
        }
      });
      photoFiles.forEach((file) => {
        payload.append('photos', file);
      });

      if (editing) {
        await api.put(`/properties/${editing._id || editing.id}`, payload, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      } else {
        await api.post('/properties', payload, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }
      setShowFormModal(false);
      fetchProperties();
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
      await api.delete(`/properties/${deleting._id || deleting.id}`);
      setShowDeleteModal(false);
      setDeleting(null);
      fetchProperties();
    } catch (err) {
      console.error('Error deleting property:', err);
    } finally {
      setSubmitting(false);
    }
  };

  // Carousel helpers
  const getCarouselIndex = (id) => carouselIndexes[id] || 0;
  const setCarouselIndex = (id, idx) => {
    setCarouselIndexes((prev) => ({ ...prev, [id]: idx }));
  };

  // --- Render helpers ---
  const formatCurrency = (value) => {
    if (!value) return '$0';
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(value);
  };

  const normalizePhotoUrl = (photo) => {
    if (!photo) return '';
    if (photo.startsWith('http') || photo.startsWith('data:') || photo.startsWith('/')) return photo;
    return `/${photo}`;
  };

  const renderPropertyCard = (property) => {
    const rawPhotos = property.photos || [];
    const photos = rawPhotos.map(normalizePhotoUrl);
    const id = property._id || property.id;
    const currentIndex = getCarouselIndex(id);

    return (
      <div
        key={id}
        className="bg-white rounded-xl shadow-md overflow-hidden border border-gray-100 hover:shadow-lg transition-shadow group"
      >
        {/* Photo / Placeholder */}
        <div className="relative h-48 bg-gray-100 overflow-hidden">
          {photos.length > 0 ? (
            <>
              <img
                src={photos[currentIndex]}
                alt={property.name}
                className="w-full h-full object-cover"
              />
              {photos.length > 1 && (
                <>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setCarouselIndex(id, currentIndex === 0 ? photos.length - 1 : currentIndex - 1);
                    }}
                    className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/40 hover:bg-black/60 text-white rounded-full p-1 transition-colors"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setCarouselIndex(id, currentIndex === photos.length - 1 ? 0 : currentIndex + 1);
                    }}
                    className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/40 hover:bg-black/60 text-white rounded-full p-1 transition-colors"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                  <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1">
                    {photos.map((_, i) => (
                      <span
                        key={i}
                        className={`block w-1.5 h-1.5 rounded-full ${i === currentIndex ? 'bg-white' : 'bg-white/50'}`}
                      />
                    ))}
                  </div>
                </>
              )}
            </>
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Building2 className="w-16 h-16 text-gray-300" />
            </div>
          )}

          {/* Type badge overlay */}
          <div className="absolute top-3 left-3">
            <StatusBadge type={property.type} />
          </div>
        </div>

        {/* Info */}
        <div className="p-4">
          <div className="flex items-start justify-between mb-1">
            <h3 className="text-base font-semibold text-[#2C3E50] truncate flex-1">
              {property.name}
            </h3>
            <StatusBadge status={property.status} />
          </div>

          <p className="text-sm text-gray-500 flex items-center gap-1 mb-3 truncate">
            <MapPin className="w-3.5 h-3.5 flex-shrink-0" />
            {property.address}{property.city ? `, ${property.city}` : ''}
          </p>

          {/* Details row */}
          <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
            {property.area && (
              <span className="flex items-center gap-1">
                <Maximize className="w-3.5 h-3.5" />
                {property.area} m2
              </span>
            )}
            {property.bedrooms != null && property.bedrooms !== '' && (
              <span className="flex items-center gap-1">
                <BedDouble className="w-3.5 h-3.5" />
                {property.bedrooms}
              </span>
            )}
            {property.bathrooms != null && property.bathrooms !== '' && (
              <span className="flex items-center gap-1">
                <Bath className="w-3.5 h-3.5" />
                {property.bathrooms}
              </span>
            )}
          </div>

          {/* Rent + Actions */}
          <div className="flex items-center justify-between pt-3 border-t border-gray-100">
            <span className="text-lg font-bold text-[#1B4F72]">
              {formatCurrency(property.monthlyRent)}
              <span className="text-xs font-normal text-gray-400"> /mes</span>
            </span>

            {canManage && (
              <div className="flex items-center gap-1">
                <button
                  onClick={() => handleOpenEdit(property)}
                  className="p-1.5 rounded-lg hover:bg-[#D6EAF8] text-[#2E86C1] transition-colors"
                  title="Editar"
                >
                  <Pencil className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleOpenDelete(property)}
                  className="p-1.5 rounded-lg hover:bg-red-50 text-[#E74C3C] transition-colors"
                  title="Eliminar"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <h2 className="text-2xl font-bold text-[#2C3E50]">Propiedades</h2>
        {canManage && (
          <Button onClick={handleOpenCreate}>
            <Plus className="w-4 h-4" />
            Nueva Propiedad
          </Button>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="flex-1">
          <Input
            placeholder="Buscar por nombre o direccion..."
            icon={Search}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="w-full sm:w-48">
          <Select
            options={PROPERTY_TYPES}
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          />
        </div>
        <div className="w-full sm:w-48">
          <Select
            options={PROPERTY_STATUS}
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          />
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-[#2E86C1]" />
        </div>
      ) : properties.length === 0 ? (
        <Card className="text-center py-16">
          <Building2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-[#2C3E50] mb-2">No se encontraron propiedades</h3>
          <p className="text-gray-500 mb-6">
            {search || filterType || filterStatus
              ? 'Intenta ajustar los filtros de busqueda.'
              : 'Comienza agregando tu primera propiedad.'}
          </p>
          {canManage && !search && !filterType && !filterStatus && (
            <Button onClick={handleOpenCreate}>
              <Plus className="w-4 h-4" />
              Nueva Propiedad
            </Button>
          )}
        </Card>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {properties.map(renderPropertyCard)}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6 bg-white rounded-xl shadow-sm px-4 py-3 border border-gray-100">
              <span className="text-sm text-gray-600">
                Pagina {page} de {totalPages}
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="p-1.5 rounded-lg hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (page <= 3) {
                    pageNum = i + 1;
                  } else if (page >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = page - 2 + i;
                  }
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setPage(pageNum)}
                      className={`w-8 h-8 rounded-lg text-sm font-medium transition-colors ${
                        page === pageNum
                          ? 'bg-[#1B4F72] text-white'
                          : 'hover:bg-gray-100 text-gray-600'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  className="p-1.5 rounded-lg hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Create/Edit Modal */}
      <Modal
        isOpen={showFormModal}
        onClose={() => setShowFormModal(false)}
        title={editing ? 'Editar Propiedad' : 'Nueva Propiedad'}
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
              name="name"
              value={formData.name}
              onChange={handleFormChange}
              error={formErrors.name}
              placeholder="Ej: Apartamento Centro"
            />
            <Select
              label="Tipo *"
              name="type"
              value={formData.type}
              onChange={handleFormChange}
              options={PROPERTY_TYPES}
              error={formErrors.type}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Direccion *"
              name="address"
              value={formData.address}
              onChange={handleFormChange}
              error={formErrors.address}
              placeholder="Ej: Calle 50 #30-20"
            />
            <Input
              label="Ciudad *"
              name="city"
              value={formData.city}
              onChange={handleFormChange}
              error={formErrors.city}
              placeholder="Ej: Medellin"
            />
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Input
              label="Area (m2)"
              name="area"
              type="number"
              value={formData.area}
              onChange={handleFormChange}
              error={formErrors.area}
              min="0"
            />
            <Input
              label="Habitaciones"
              name="bedrooms"
              type="number"
              value={formData.bedrooms}
              onChange={handleFormChange}
              min="0"
            />
            <Input
              label="Banos"
              name="bathrooms"
              type="number"
              value={formData.bathrooms}
              onChange={handleFormChange}
              min="0"
            />
            <Input
              label="Canon mensual *"
              name="monthlyRent"
              type="number"
              value={formData.monthlyRent}
              onChange={handleFormChange}
              error={formErrors.monthlyRent}
              min="0"
            />
          </div>

          <div className="w-full">
            <label className="block text-sm font-medium text-[#2C3E50] mb-1">Descripcion</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleFormChange}
              rows={3}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-[#2C3E50] placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#2E86C1] focus:border-transparent resize-none"
              placeholder="Descripcion de la propiedad..."
            />
          </div>

          {/* Photo upload */}
          <div className="w-full">
            <label className="block text-sm font-medium text-[#2C3E50] mb-1">Fotos</label>
            <div className="flex flex-wrap gap-3">
              {photoPreviews.map((preview, idx) => (
                <div key={idx} className="relative w-20 h-20 rounded-lg overflow-hidden border border-gray-200 group">
                  <img
                    src={preview}
                    alt={`preview-${idx}`}
                    className="w-full h-full object-cover"
                  />
                  <button
                    type="button"
                    onClick={() => handleRemovePhoto(idx)}
                    className="absolute top-0.5 right-0.5 bg-black/50 hover:bg-black/70 text-white rounded-full p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
              <label className="w-20 h-20 rounded-lg border-2 border-dashed border-gray-300 hover:border-[#2E86C1] flex items-center justify-center cursor-pointer transition-colors">
                <Upload className="w-5 h-5 text-gray-400" />
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handlePhotoChange}
                  className="hidden"
                />
              </label>
            </div>
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
              {editing ? 'Guardar Cambios' : 'Crear Propiedad'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Eliminar Propiedad"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Estas seguro de que deseas eliminar la propiedad{' '}
            <span className="font-semibold text-[#2C3E50]">{deleting?.name}</span>?
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
