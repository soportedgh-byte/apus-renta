const prisma = require('../../config/database');

/**
 * Lista servicios publicos con filtros y paginacion.
 */
async function list(tenantId, { page = 1, limit = 10, propertyId, type, status, period, role, userId }) {
  const where = { tenantId: Number(tenantId) };

  if (propertyId) where.propertyId = Number(propertyId);
  if (type) where.type = type;
  if (status) where.status = status;
  if (period) where.period = period;

  // If ARRENDATARIO, filter to only their property
  if (role === 'ARRENDATARIO' && userId) {
    const user = await prisma.user.findUnique({
      where: { id: Number(userId) },
      include: { tenantPerson: { include: { leases: { where: { status: 'ACTIVO' }, take: 1 } } } },
    });
    const lease = user?.tenantPerson?.leases?.[0];
    if (lease) {
      where.propertyId = lease.propertyId;
    }
  }

  const skip = (page - 1) * limit;

  const [data, total] = await Promise.all([
    prisma.utilityBill.findMany({
      where,
      include: { property: true },
      skip,
      take: Number(limit),
      orderBy: { createdAt: 'desc' },
    }),
    prisma.utilityBill.count({ where }),
  ]);

  return { data, total, page: Number(page), limit: Number(limit) };
}

/**
 * Resumen tipo semaforo de servicios publicos por propiedad y tipo.
 */
async function getSummary(tenantId) {
  const now = new Date();

  // Obtener todas las propiedades del tenant
  const properties = await prisma.property.findMany({
    where: { tenantId: Number(tenantId) },
    select: { id: true, name: true },
  });

  const utilityTypes = ['AGUA', 'LUZ', 'GAS'];

  // Obtener el ultimo registro de cada combinacion propiedad-tipo
  const matrix = [];

  for (const property of properties) {
    const row = {
      propertyId: property.id,
      propertyName: property.name,
      utilities: {},
    };

    for (const type of utilityTypes) {
      const latest = await prisma.utilityBill.findFirst({
        where: {
          tenantId: Number(tenantId),
          propertyId: property.id,
          type,
        },
        orderBy: { createdAt: 'desc' },
      });

      if (!latest) {
        row.utilities[type] = { status: null, color: 'gray', amount: null };
        continue;
      }

      let color;
      if (latest.status === 'PAGADO') {
        color = 'green';
      } else if (latest.status === 'VENCIDO' || (latest.status === 'PENDIENTE' && latest.dueDate <= now)) {
        color = 'red';
      } else if (latest.status === 'PENDIENTE' && latest.dueDate > now) {
        color = 'yellow';
      } else {
        color = 'gray';
      }

      row.utilities[type] = {
        id: latest.id,
        status: latest.status,
        color,
        amount: latest.amount,
        period: latest.period,
        dueDate: latest.dueDate,
      };
    }

    matrix.push(row);
  }

  return matrix;
}

/**
 * Obtener un servicio publico por ID.
 */
async function getById(id) {
  const utility = await prisma.utilityBill.findUnique({
    where: { id: Number(id) },
    include: { property: true },
  });

  if (!utility) {
    throw { status: 404, message: 'Servicio publico no encontrado' };
  }

  return utility;
}

/**
 * Crear un nuevo registro de servicio publico.
 */
async function create(data, tenantId, file) {
  const createData = {
    propertyId: Number(data.propertyId),
    tenantId: Number(tenantId),
    type: data.type,
    amount: parseFloat(data.amount),
    period: data.period,
    dueDate: new Date(data.dueDate),
    status: 'PENDIENTE',
  };

  if (file) {
    createData.receiptUrl = `/uploads/utilities/${file.filename}`;
  }

  const utility = await prisma.utilityBill.create({
    data: createData,
    include: { property: true },
  });

  return utility;
}

/**
 * Actualizar un servicio publico.
 */
async function update(id, data) {
  const existing = await prisma.utilityBill.findUnique({ where: { id: Number(id) } });
  if (!existing) {
    throw { status: 404, message: 'Servicio publico no encontrado' };
  }

  const updateData = {};
  if (data.amount !== undefined) updateData.amount = parseFloat(data.amount);
  if (data.status !== undefined) updateData.status = data.status;

  const utility = await prisma.utilityBill.update({
    where: { id: Number(id) },
    data: updateData,
    include: { property: true },
  });

  return utility;
}

/**
 * Actualizar solo el estado de un servicio publico.
 */
async function updateStatus(id, status) {
  const existing = await prisma.utilityBill.findUnique({ where: { id: Number(id) } });
  if (!existing) {
    throw { status: 404, message: 'Servicio publico no encontrado' };
  }

  const utility = await prisma.utilityBill.update({
    where: { id: Number(id) },
    data: { status },
    include: { property: true },
  });

  return utility;
}

module.exports = {
  list,
  getSummary,
  getById,
  create,
  update,
  updateStatus,
};
