const service = require('./settings.service');
const { success, error } = require('../../utils/response');

async function getAlertConfig(req, res) {
  try {
    const data = await service.getAlertConfig(req.user.tenantId);
    return success(res, data);
  } catch (err) {
    console.error('Settings.getAlertConfig error:', err);
    return error(res, err.message, err.status || 500);
  }
}

async function updateAlertConfig(req, res) {
  try {
    const data = await service.updateAlertConfig(req.user.tenantId, req.body);
    return success(res, data, 'Configuracion de alertas actualizada');
  } catch (err) {
    console.error('Settings.updateAlertConfig error:', err);
    return error(res, err.message, err.status || 500);
  }
}

async function getTenantInfo(req, res) {
  try {
    const data = await service.getTenantInfo(req.user.tenantId);
    return success(res, data);
  } catch (err) {
    console.error('Settings.getTenantInfo error:', err);
    return error(res, err.message, err.status || 500);
  }
}

async function updateTenantInfo(req, res) {
  try {
    const data = await service.updateTenantInfo(req.user.tenantId, req.body || {}, req.file || null);
    return success(res, data, 'Informacion del tenant actualizada');
  } catch (err) {
    console.error('Settings.updateTenantInfo error:', err);
    return error(res, err.message, err.status || 500);
  }
}

module.exports = { getAlertConfig, updateAlertConfig, getTenantInfo, updateTenantInfo };
