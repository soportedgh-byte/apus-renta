const prisma = require('../../config/database');

/**
 * Lista contratos filtrados por tenant con paginacion.
 */
async function list(tenantId, { page = 1, limit = 10, status, propertyId, userRole, userId }) {
  const skip = (page - 1) * limit;

  const where = { tenantId: Number(tenantId) };

  if (status) {
    where.status = status;
  }

  if (propertyId) {
    where.propertyId = Number(propertyId);
  }

  // Si el usuario es ARRENDATARIO, solo ve sus propios contratos
  if (userRole === 'ARRENDATARIO') {
    const tenantPerson = await prisma.tenantPerson.findFirst({
      where: { userId: Number(userId), tenantId: Number(tenantId) },
    });
    if (tenantPerson) {
      where.tenantPersonId = tenantPerson.id;
    } else {
      return { data: [], total: 0, page, limit };
    }
  }

  const [data, total] = await Promise.all([
    prisma.lease.findMany({
      where,
      skip,
      take: Number(limit),
      orderBy: { createdAt: 'desc' },
      include: {
        property: true,
        tenantPerson: {
          include: { user: { select: { id: true, firstName: true, lastName: true, email: true } } },
        },
      },
    }),
    prisma.lease.count({ where }),
  ]);

  return { data, total, page: Number(page), limit: Number(limit) };
}

/**
 * Obtiene un contrato por ID con relaciones completas.
 */
async function getById(id, tenantId) {
  const lease = await prisma.lease.findFirst({
    where: { id: Number(id), tenantId: Number(tenantId) },
    include: {
      property: true,
      tenantPerson: {
        include: { user: { select: { id: true, firstName: true, lastName: true, email: true, phone: true } } },
      },
      payments: {
        orderBy: { createdAt: 'desc' },
      },
    },
  });

  if (!lease) {
    throw { status: 404, message: 'Contrato no encontrado' };
  }

  return lease;
}

/**
 * Crea un nuevo contrato en estado BORRADOR.
 */
async function create(data, tenantId) {
  const { propertyId, tenantPersonId, startDate, endDate, monthlyRent, deposit, terms } = data;

  // Verificar que la propiedad pertenece al tenant
  const property = await prisma.property.findFirst({
    where: { id: Number(propertyId), tenantId: Number(tenantId) },
  });
  if (!property) {
    throw { status: 404, message: 'Propiedad no encontrada o no pertenece a su organizacion' };
  }

  // Verificar que el arrendatario existe
  const tenantPerson = await prisma.tenantPerson.findFirst({
    where: { id: Number(tenantPersonId), tenantId: Number(tenantId) },
  });
  if (!tenantPerson) {
    throw { status: 404, message: 'Arrendatario no encontrado o no pertenece a su organizacion' };
  }

  const lease = await prisma.lease.create({
    data: {
      propertyId: Number(propertyId),
      tenantPersonId: Number(tenantPersonId),
      tenantId: Number(tenantId),
      startDate: new Date(startDate),
      endDate: new Date(endDate),
      monthlyRent: parseFloat(monthlyRent),
      deposit: deposit ? parseFloat(deposit) : null,
      terms: terms || null,
      status: 'BORRADOR',
    },
    include: {
      property: true,
      tenantPerson: {
        include: { user: { select: { id: true, firstName: true, lastName: true, email: true } } },
      },
    },
  });

  return lease;
}

/**
 * Actualiza campos de un contrato existente.
 */
async function update(id, data, tenantId) {
  const existing = await prisma.lease.findFirst({
    where: { id: Number(id), tenantId: Number(tenantId) },
  });
  if (!existing) {
    throw { status: 404, message: 'Contrato no encontrado' };
  }

  const updateData = {};
  if (data.propertyId !== undefined) updateData.propertyId = Number(data.propertyId);
  if (data.tenantPersonId !== undefined) updateData.tenantPersonId = Number(data.tenantPersonId);
  if (data.startDate !== undefined) updateData.startDate = new Date(data.startDate);
  if (data.endDate !== undefined) updateData.endDate = new Date(data.endDate);
  if (data.monthlyRent !== undefined) updateData.monthlyRent = parseFloat(data.monthlyRent);
  if (data.deposit !== undefined) updateData.deposit = parseFloat(data.deposit);
  if (data.terms !== undefined) updateData.terms = data.terms;

  const lease = await prisma.lease.update({
    where: { id: Number(id) },
    data: updateData,
    include: {
      property: true,
      tenantPerson: {
        include: { user: { select: { id: true, firstName: true, lastName: true, email: true } } },
      },
    },
  });

  return lease;
}

/**
 * Actualiza el estado de un contrato y sincroniza el estado de la propiedad.
 */
async function updateStatus(id, status, tenantId) {
  const lease = await prisma.lease.findFirst({
    where: { id: Number(id), tenantId: Number(tenantId) },
  });
  if (!lease) {
    throw { status: 404, message: 'Contrato no encontrado' };
  }

  const validStatuses = ['BORRADOR', 'ACTIVO', 'TERMINADO', 'VENCIDO', 'CANCELADO'];
  if (!validStatuses.includes(status)) {
    throw { status: 400, message: 'Estado no valido' };
  }

  const updated = await prisma.lease.update({
    where: { id: Number(id) },
    data: { status },
    include: { property: true },
  });

  // Sincronizar estado de la propiedad
  if (status === 'ACTIVO') {
    await prisma.property.update({
      where: { id: lease.propertyId },
      data: { status: 'OCUPADO' },
    });
  } else if (status === 'TERMINADO' || status === 'VENCIDO') {
    await prisma.property.update({
      where: { id: lease.propertyId },
      data: { status: 'DISPONIBLE' },
    });
  }

  return updated;
}

/**
 * Placeholder para integracion con ZapSign.
 */
async function sendToSign(id, tenantId) {
  const lease = await prisma.lease.findFirst({
    where: { id: Number(id), tenantId: Number(tenantId) },
  });
  if (!lease) {
    throw { status: 404, message: 'Contrato no encontrado' };
  }

  const updated = await prisma.lease.update({
    where: { id: Number(id) },
    data: { zapsignStatus: 'ENVIADO' },
  });

  return {
    lease: updated,
    message: 'Contrato enviado a firma electronica. Integracion con ZapSign pendiente de configuracion.',
  };
}

/**
 * Elimina un contrato solo si esta en estado BORRADOR.
 */
async function remove(id, tenantId) {
  const lease = await prisma.lease.findFirst({
    where: { id: Number(id), tenantId: Number(tenantId) },
  });
  if (!lease) {
    throw { status: 404, message: 'Contrato no encontrado' };
  }

  if (lease.status !== 'BORRADOR') {
    throw { status: 400, message: 'Solo se pueden eliminar contratos en estado BORRADOR' };
  }

  await prisma.lease.delete({ where: { id: Number(id) } });

  return { message: 'Contrato eliminado exitosamente' };
}

module.exports = {
  list,
  getById,
  create,
  update,
  updateStatus,
  sendToSign,
  remove,
};
