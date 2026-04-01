const alertsService = require('./alerts.service');
const { success, error, paginated } = require('../../utils/response');

async function list(req, res) {
  try {
    const tenantId = req.user.tenantId;
    const { page, limit, type, status } = req.query;
    const result = await alertsService.list(tenantId, { page, limit, type, status });
    return paginated(res, result.data, result.page, result.limit, result.total);
  } catch (err) {
    console.error('Alerts.list error:', err);
    return error(res, err.message || 'Error al listar alertas', err.status || 500);
  }
}

async function getConfig(req, res) {
  try {
    const config = await alertsService.getConfig(req.user.tenantId);
    return success(res, config, 'Configuracion de alertas obtenida');
  } catch (err) {
    console.error('Alerts.getConfig error:', err);
    return error(res, err.message || 'Error al obtener configuracion', err.status || 500);
  }
}

async function updateConfig(req, res) {
  try {
    const config = await alertsService.updateConfig(req.user.tenantId, req.body);
    return success(res, config, 'Configuracion de alertas actualizada');
  } catch (err) {
    console.error('Alerts.updateConfig error:', err);
    return error(res, err.message || 'Error al actualizar configuracion', err.status || 500);
  }
}

async function sendTest(req, res) {
  try {
    const { channel } = req.body;
    const alert = await alertsService.sendTest(req.user.tenantId, channel);
    return success(res, alert, 'Alerta de prueba enviada', 201);
  } catch (err) {
    console.error('Alerts.sendTest error:', err);
    return error(res, err.message || 'Error al enviar alerta de prueba', err.status || 500);
  }
}

module.exports = {
  list,
  getConfig,
  updateConfig,
  sendTest,
};
