const prisma = require('../../config/database');

async function getAlertConfig(tenantId) {
  const tenant = await prisma.tenant.findUnique({ where: { id: Number(tenantId) } });
  if (!tenant) throw { status: 404, message: 'Tenant no encontrado' };
  const config = tenant.configJson || {};
  return config.alerts || {
    paymentReminder: { enabled: true, daysBefore: [5, 3, 1], channels: ['EMAIL', 'PUSH'] },
    contractExpiry: { enabled: true, daysBefore: [90, 60, 30], channels: ['EMAIL'] },
    utilityDue: { enabled: true, daysBefore: [5, 3, 1], channels: ['EMAIL'] },
    pqrsNoResponse: { enabled: true, daysAfter: 3, channels: ['PUSH'] },
  };
}

async function updateAlertConfig(tenantId, alertConfig) {
  const tenant = await prisma.tenant.findUnique({ where: { id: Number(tenantId) } });
  if (!tenant) throw { status: 404, message: 'Tenant no encontrado' };
  const currentConfig = tenant.configJson || {};
  currentConfig.alerts = alertConfig;
  await prisma.tenant.update({
    where: { id: Number(tenantId) },
    data: { configJson: currentConfig },
  });
  return currentConfig.alerts;
}

async function getTenantInfo(tenantId) {
  const tenant = await prisma.tenant.findUnique({ where: { id: Number(tenantId) } });
  if (!tenant) throw { status: 404, message: 'Tenant no encontrado' };
  return tenant;
}

async function updateTenantInfo(tenantId, data) {
  const updateData = {};
  if (data.name !== undefined) updateData.name = data.name;
  if (data.logo !== undefined) updateData.logo = data.logo;
  if (data.configJson !== undefined) updateData.configJson = data.configJson;
  const tenant = await prisma.tenant.update({
    where: { id: Number(tenantId) },
    data: updateData,
  });
  return tenant;
}

module.exports = { getAlertConfig, updateAlertConfig, getTenantInfo, updateTenantInfo };
