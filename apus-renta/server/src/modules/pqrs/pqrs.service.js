const prisma = require('../../config/database');

/**
 * Lista PQRS con filtros, paginacion y filtro por rol.
 */
async function list(tenantId, userId, role, { page = 1, limit = 10, status, type, propertyId }) {
  const where = { tenantId: Number(tenantId) };

  // Los arrendatarios solo ven sus propias PQRS
  if (role === 'ARRENDATARIO') {
    where.userId = Number(userId);
  }

  if (status) where.status = status;
  if (type) where.type = type;
  if (propertyId) where.propertyId = Number(propertyId);

  const skip = (page - 1) * limit;

  const [data, total] = await Promise.all([
    prisma.pQRS.findMany({
      where,
      include: {
        user: { select: { id: true, firstName: true, lastName: true, email: true } },
        property: { select: { id: true, name: true, address: true } },
        assignedUser: { select: { id: true, firstName: true, lastName: true, email: true } },
      },
      skip,
      take: Number(limit),
      orderBy: { createdAt: 'desc' },
    }),
    prisma.pQRS.count({ where }),
  ]);

  return { data, total, page: Number(page), limit: Number(limit) };
}

/**
 * Obtener una PQRS por ID.
 */
async function getById(id) {
  const pqrs = await prisma.pQRS.findUnique({
    where: { id: Number(id) },
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

  const pqrs = await prisma.pQRS.create({
    data: {
      propertyId: Number(data.propertyId),
      userId: Number(userId),
      tenantId: Number(tenantId),
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
  const existing = await prisma.pQRS.findFirst({
    where: { id: Number(id), tenantId: Number(tenantId) },
  });

  if (!existing) {
    throw { status: 404, message: 'PQRS no encontrada' };
  }

  const updateData = {};
  if (data.status) updateData.status = data.status;
  if (data.resolution !== undefined) updateData.resolution = data.resolution;

  const pqrs = await prisma.pQRS.update({
    where: { id: Number(id) },
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
  const existing = await prisma.pQRS.findFirst({
    where: { id: Number(id), tenantId: Number(tenantId) },
  });

  if (!existing) {
    throw { status: 404, message: 'PQRS no encontrada' };
  }

  const pqrs = await prisma.pQRS.update({
    where: { id: Number(id) },
    data: { assignedTo: Number(assignedTo) },
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
  const existing = await prisma.pQRS.findFirst({
    where: { id: Number(id), tenantId: Number(tenantId) },
  });

  if (!existing) {
    throw { status: 404, message: 'PQRS no encontrada' };
  }

  await prisma.pQRS.delete({ where: { id: Number(id) } });

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
