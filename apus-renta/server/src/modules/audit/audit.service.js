const prisma = require('../../config/database');

/**
 * Listar logs de auditoria con filtros y paginacion.
 */
async function list(tenantId, { page = 1, limit = 20, userId, action, entity, startDate, endDate } = {}) {
  const where = { tenantId: Number(tenantId) };

  if (userId) where.userId = Number(userId);
  if (action) where.action = action;
  if (entity) where.entity = entity;
  if (startDate || endDate) {
    where.createdAt = {};
    if (startDate) where.createdAt.gte = new Date(startDate);
    if (endDate) where.createdAt.lte = new Date(endDate);
  }

  const skip = (Number(page) - 1) * Number(limit);
  const take = Number(limit);

  const [logs, total] = await Promise.all([
    prisma.auditLog.findMany({
      where,
      include: {
        user: {
          select: { id: true, firstName: true, lastName: true, email: true, role: true },
        },
      },
      orderBy: { createdAt: 'desc' },
      skip,
      take,
    }),
    prisma.auditLog.count({ where }),
  ]);

  return { logs, total, page: Number(page), limit: take };
}

/**
 * Estadisticas de auditoria.
 */
async function getStats(tenantId) {
  // Count by action
  const byAction = await prisma.auditLog.groupBy({
    by: ['action'],
    _count: { id: true },
    where: { tenantId: Number(tenantId) },
    orderBy: { _count: { id: 'desc' } },
  });

  // Count by entity
  const byEntity = await prisma.auditLog.groupBy({
    by: ['entity'],
    _count: { id: true },
    where: { tenantId: Number(tenantId) },
    orderBy: { _count: { id: 'desc' } },
  });

  // Most active users
  const byUser = await prisma.auditLog.groupBy({
    by: ['userId'],
    _count: { id: true },
    where: { tenantId: Number(tenantId) },
    orderBy: { _count: { id: 'desc' } },
    take: 10,
  });

  // Enrich user info
  const userIds = byUser.map((u) => u.userId);
  const users = await prisma.user.findMany({
    where: { id: { in: userIds } },
    select: { id: true, firstName: true, lastName: true, email: true },
  });
  const userMap = Object.fromEntries(users.map((u) => [u.id, u]));

  const mostActiveUsers = byUser.map((u) => ({
    userId: u.userId,
    user: userMap[u.userId] || null,
    count: u._count.id,
  }));

  // Recent critical actions (CREATE, DELETE, UPDATE on sensitive entities)
  const criticalActions = await prisma.auditLog.findMany({
    where: {
      tenantId: Number(tenantId),
      action: { in: ['DELETE', 'UPDATE_STATUS', 'APPROVE', 'REJECT'] },
    },
    include: {
      user: { select: { id: true, firstName: true, lastName: true, email: true } },
    },
    orderBy: { createdAt: 'desc' },
    take: 20,
  });

  return {
    byAction: byAction.map((a) => ({ action: a.action, count: a._count.id })),
    byEntity: byEntity.map((e) => ({ entity: e.entity, count: e._count.id })),
    mostActiveUsers,
    criticalActions,
  };
}

/**
 * Crear una entrada de log de auditoria.
 * Llamado desde otros modulos para registrar acciones.
 */
async function log({ tenantId, userId, action, entity, entityId, details, ipAddress, userAgent }) {
  return prisma.auditLog.create({
    data: {
      tenantId: Number(tenantId),
      userId: Number(userId),
      action,
      entity,
      entityId: entityId ? Number(entityId) : 0,
      details: details || undefined,
      ipAddress: ipAddress || null,
      userAgent: userAgent ? String(userAgent).substring(0, 500) : null,
    },
  });
}

module.exports = {
  list,
  getStats,
  log,
};
