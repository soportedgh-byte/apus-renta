const prisma = require('../../config/database');

/**
 * Lista alertas con filtros y paginacion.
 */
async function list(tenantId, { page = 1, limit = 10, type, status }) {
  const where = { tenantId: Number(tenantId) };

  if (type) where.type = type;
  if (status) where.status = status;

  const skip = (page - 1) * limit;

  const [data, total] = await Promise.all([
    prisma.alert.findMany({
      where,
      skip,
      take: Number(limit),
      orderBy: { createdAt: 'desc' },
    }),
    prisma.alert.count({ where }),
  ]);

  return { data, total, page: Number(page), limit: Number(limit) };
}

/**
 * Obtener configuracion de alertas del tenant desde configJson.
 */
async function getConfig(tenantId) {
  const tenant = await prisma.tenant.findUnique({
    where: { id: Number(tenantId) },
    select: { configJson: true },
  });

  if (!tenant) {
    throw { status: 404, message: 'Tenant no encontrado' };
  }

  const config = tenant.configJson ? (typeof tenant.configJson === 'string' ? JSON.parse(tenant.configJson) : tenant.configJson) : {};

  return config.alerts || {
    emailEnabled: false,
    whatsappEnabled: false,
    leaseExpiryDays: [30, 60, 90],
    paymentReminder: true,
    utilityReminder: true,
    pqrsReminder: true,
  };
}

/**
 * Actualizar configuracion de alertas del tenant.
 */
async function updateConfig(tenantId, alertConfig) {
  const tenant = await prisma.tenant.findUnique({
    where: { id: Number(tenantId) },
    select: { configJson: true },
  });

  if (!tenant) {
    throw { status: 404, message: 'Tenant no encontrado' };
  }

  const config = tenant.configJson ? (typeof tenant.configJson === 'string' ? JSON.parse(tenant.configJson) : tenant.configJson) : {};
  config.alerts = alertConfig;

  await prisma.tenant.update({
    where: { id: Number(tenantId) },
    data: { configJson: config },
  });

  return config.alerts;
}

/**
 * Enviar una alerta de prueba (placeholder para email/whatsapp).
 */
async function sendTest(tenantId, channel) {
  const alert = await prisma.alert.create({
    data: {
      tenantId: Number(tenantId),
      type: 'TEST',
      title: 'Alerta de prueba',
      message: `Esta es una alerta de prueba enviada por el canal: ${channel || 'sistema'}`,
      channel: channel || 'EMAIL',
      status: 'ENVIADA',
    },
  });

  // TODO: Integracion real con servicio de email/whatsapp
  console.log(`[ALERT TEST] Tenant ${tenantId} - Canal: ${channel} - Alerta creada con ID: ${alert.id}`);

  return alert;
}

module.exports = {
  list,
  getConfig,
  updateConfig,
  sendTest,
};
