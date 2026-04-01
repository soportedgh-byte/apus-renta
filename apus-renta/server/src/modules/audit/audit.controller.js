const auditService = require('./audit.service');
const { success, error, paginated } = require('../../utils/response');

async function list(req, res) {
  try {
    const { page, limit, userId, action, entity, startDate, endDate } = req.query;
    const data = await auditService.list(req.user.tenantId, {
      page: page || 1,
      limit: limit || 20,
      userId,
      action,
      entity,
      startDate,
      endDate,
    });
    return paginated(res, data.logs, data.page, data.limit, data.total);
  } catch (err) {
    console.error('Audit.list error:', err);
    return error(res, err.message || 'Error al obtener logs de auditoria', err.status || 500);
  }
}

async function getStats(req, res) {
  try {
    const data = await auditService.getStats(req.user.tenantId);
    return success(res, data, 'Estadisticas de auditoria obtenidas exitosamente');
  } catch (err) {
    console.error('Audit.getStats error:', err);
    return error(res, err.message || 'Error al obtener estadisticas de auditoria', err.status || 500);
  }
}

module.exports = {
  list,
  getStats,
};
