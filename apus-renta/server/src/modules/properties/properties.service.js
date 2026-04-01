const prisma = require('../../config/database');

/**
 * Listar propiedades con filtros y paginacion.
 */
async function list(tenantId, { page = 1, limit = 10, status, type, search } = {}) {
  const skip = (page - 1) * limit;

  const where = { tenantId };

  if (status) {
    where.status = status;
  }

  if (type) {
    where.type = type;
  }

  if (search) {
    where.OR = [
      { name: { contains: search } },
      { address: { contains: search } },
    ];
  }

  const [properties, total] = await Promise.all([
    prisma.property.findMany({
      where,
      skip,
      take: Number(limit),
      include: {
        _count: {
          select: { leases: true },
        },
      },
      orderBy: { createdAt: 'desc' },
    }),
    prisma.property.count({ where }),
  ]);

  return { properties, total, page: Number(page), limit: Number(limit) };
}

/**
 * Obtener propiedad por ID con relaciones.
 */
async function getById(id, tenantId) {
  const property = await prisma.property.findUnique({
    where: { id },
    include: {
      leases: {
        include: {
          tenantPerson: {
            include: { user: true },
          },
        },
      },
      utilityBills: true,
    },
  });

  if (!property) {
    throw { status: 404, message: 'Propiedad no encontrada' };
  }

  if (property.tenantId !== tenantId) {
    throw { status: 403, message: 'No tiene permisos para ver esta propiedad' };
  }

  return property;
}

/**
 * Crear una nueva propiedad.
 */
async function create(data, tenantId, files = []) {
  const photos = files.map((file) => file.path);

  const property = await prisma.property.create({
    data: {
      ...data,
      area: data.area ? parseFloat(data.area) : undefined,
      bedrooms: data.bedrooms ? parseInt(data.bedrooms, 10) : undefined,
      bathrooms: data.bathrooms ? parseInt(data.bathrooms, 10) : undefined,
      monthlyRent: data.monthlyRent ? parseFloat(data.monthlyRent) : undefined,
      photos,
      tenantId,
    },
  });

  return property;
}

/**
 * Actualizar una propiedad existente.
 */
async function update(id, data, tenantId, files = []) {
  const existing = await prisma.property.findFirst({
    where: { id, tenantId },
  });

  if (!existing) {
    throw { status: 404, message: 'Propiedad no encontrada o no tiene permisos' };
  }

  const newPhotos = files.map((file) => file.path);
  const photos = [...(existing.photos || []), ...newPhotos];

  const updateData = { ...data, photos };

  if (updateData.area) updateData.area = parseFloat(updateData.area);
  if (updateData.bedrooms) updateData.bedrooms = parseInt(updateData.bedrooms, 10);
  if (updateData.bathrooms) updateData.bathrooms = parseInt(updateData.bathrooms, 10);
  if (updateData.monthlyRent) updateData.monthlyRent = parseFloat(updateData.monthlyRent);

  // Remover campos que no deben actualizarse directamente
  delete updateData.tenantId;

  const property = await prisma.property.update({
    where: { id },
    data: updateData,
  });

  return property;
}

/**
 * Eliminar una propiedad.
 * Si tiene contratos activos, realiza soft delete cambiando el estado.
 */
async function remove(id, tenantId) {
  const existing = await prisma.property.findFirst({
    where: { id, tenantId },
    include: { _count: { select: { leases: true } } },
  });

  if (!existing) {
    throw { status: 404, message: 'Propiedad no encontrada o no tiene permisos' };
  }

  if (existing._count.leases > 0) {
    // Soft delete: marcar como inactiva si tiene contratos
    const property = await prisma.property.update({
      where: { id },
      data: { status: 'MANTENIMIENTO' },
    });
    return { property, softDeleted: true };
  }

  await prisma.property.delete({ where: { id } });
  return { deleted: true };
}

/**
 * Actualizar solo el estado de una propiedad.
 */
async function updateStatus(id, status, tenantId) {
  const existing = await prisma.property.findFirst({
    where: { id, tenantId },
  });

  if (!existing) {
    throw { status: 404, message: 'Propiedad no encontrada o no tiene permisos' };
  }

  const property = await prisma.property.update({
    where: { id },
    data: { status },
  });

  return property;
}

module.exports = {
  list,
  getById,
  create,
  update,
  delete: remove,
  updateStatus,
};
