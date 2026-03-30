const prisma = require('../../config/database');

/**
 * Lista PQRS con filtros, paginacion y filtro por rol.
 */
async function list(tenantId, userId, role, { page = 1, limit = 10, status, type, propertyId }) {
  const where = { tenantId };

  // Los arrendatarios solo ven sus propias PQRS
  if (role === 'ARRENDATARIO') {
    where.userId = userId;
  }

  if (status) where.status = status;
  if (type) where.type = type;
  if (propertyId) where.propertyId = parseInt(propertyId);

  const skip = (page - 1) * limit;

  const [data, total] = await Promise.all([
    prisma.pqrs.findMany({
      where,
      include: {
        user: { select: { id: true, firstName: true, lastName: true, email: true } },
        property: { select: { id: true, name: true, address: true } },
        assignedUser: { select: { id: true, firstName: true, lastName: true, email: true } },
      },
      skip,
      take: parseInt(limit),
      orderBy: { createdAt: 'desc' },
    }),
    prisma.pqrs.count({ where }),
  ]);

  return { data, total, page: parseInt(page), limit: parseInt(limit) };
}

/**
 * Obtener una PQRS por ID.
 */
async function getById(id) {
  const pqrs = await prisma.pqrs.findUnique({
    where: { id: parseInt(id) },
    include: {
      user: { select: { id: true, firstName: true, lastName: true, email: true } },
      property: { select: { id: true, name: true, address: true } },
      assignedUser: { select: { id: true, firstName: true, lastName: true, email: true } },
    },
  });

  if (!pqrs) {
    throw { status: 404, message: 'PQRS no encontrada' };
  }

  return pqrs;
}

/**
 * Crear una nueva PQRS.
 */
async function create(data, userId, tenantId, files) {
  const attachments = [];
  if (files && files.length > 0) {
    for (const file of files) {
      attachments.push(`/uploads/pqrs/${file.filename}`);
    }
  }

  const pqrs = await prisma.pqrs.create({
    data: {
      propertyId: parseInt(data.propertyId),
      userId,
      tenantId: parseInt(tenantId),
      type: data.type,
      subject: data.subject,
      description: data.description,
      status: 'RADICADA',
      attachments: JSON.stringify(attachments),
    },
    include: {
      user: { select: { id: true, firstName: true, lastName: true, email: true } },
      property: { select: { id: true, name: true, address: true } },
    },
  });

  return pqrs;
}

/**
 * Actualizar estado y resolucion de una PQRS.
 */
async function update(id, data, tenantId) {
  const existing = await prisma.pqrs.findFirst({
    where: { id: parseInt(id), tenantId: parseInt(tenantId) },
  });

  if (!existing) {
    throw { status: 404, message: 'PQRS no encontrada' };
  }

  const updateData = {};
  if (data.status) updateData.status = data.status;
  if (data.resolution !== undefined) updateData.resolution = data.resolution;

  const pqrs = await prisma.pqrs.update({
    where: { id: parseInt(id) },
    data: updateData,
    include: {
      user: { select: { id: true, firstName: true, lastName: true, email: true } },
      property: { select: { id: true, name: true, address: true } },
      assignedUser: { select: { id: true, firstName: true, lastName: true, email: true } },
    },
  });

  return pqrs;
}

/**
 * Asignar una PQRS a un usuario.
 */
async function assign(id, assignedTo, tenantId) {
  const existing = await prisma.pqrs.findFirst({
    where: { id: parseInt(id), tenantId: parseInt(tenantId) },
  });

  if (!existing) {
    throw { status: 404, message: 'PQRS no encontrada' };
  }

  const pqrs = await prisma.pqrs.update({
    where: { id: parseInt(id) },
    data: { assignedTo: parseInt(assignedTo) },
    include: {
      user: { select: { id: true, firstName: true, lastName: true, email: true } },
      property: { select: { id: true, name: true, address: true } },
      assignedUser: { select: { id: true, firstName: true, lastName: true, email: true } },
    },
  });

  return pqrs;
}

/**
 * Eliminar una PQRS (hard delete).
 */
async function remove(id, tenantId) {
  const existing = await prisma.pqrs.findFirst({
    where: { id: parseInt(id), tenantId: parseInt(tenantId) },
  });

  if (!existing) {
    throw { status: 404, message: 'PQRS no encontrada' };
  }

  await prisma.pqrs.delete({ where: { id: parseInt(id) } });

  return { message: 'PQRS eliminada exitosamente' };
}

module.exports = {
  list,
  getById,
  create,
  update,
  assign,
  remove,
};
