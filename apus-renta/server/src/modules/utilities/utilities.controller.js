const utilitiesService = require('./utilities.service');
const { success, error, paginated } = require('../../utils/response');

async function list(req, res) {
  try {
    const tenantId = req.user.tenantId;
    const { page, limit, propertyId, type, status, period } = req.query;
    const result = await utilitiesService.list(tenantId, { page, limit, propertyId, type, status, period });
    return paginated(res, result.data, result.page, result.limit, result.total);
  } catch (err) {
    console.error('Utilities.list error:', err);
    return error(res, err.message || 'Error al listar servicios publicos', err.status || 500);
  }
}

async function getSummary(req, res) {
  try {
    const tenantId = req.user.tenantId;
    const result = await utilitiesService.getSummary(tenantId);
    return success(res, result, 'Resumen de servicios publicos obtenido');
  } catch (err) {
    console.error('Utilities.getSummary error:', err);
    return error(res, err.message || 'Error al obtener resumen', err.status || 500);
  }
}

async function getById(req, res) {
  try {
    const utility = await utilitiesService.getById(req.params.id);
    return success(res, utility, 'Servicio publico obtenido');
  } catch (err) {
    console.error('Utilities.getById error:', err);
    return error(res, err.message || 'Error al obtener servicio publico', err.status || 500);
  }
}

async function create(req, res) {
  try {
    const body = { ...req.body, tenantId: req.user.tenantId };
    const utility = await utilitiesService.create(body, req.file);
    return success(res, utility, 'Servicio publico creado exitosamente', 201);
  } catch (err) {
    console.error('Utilities.create error:', err);
    return error(res, err.message || 'Error al crear servicio publico', err.status || 500);
  }
}

async function update(req, res) {
  try {
    const utility = await utilitiesService.update(req.params.id, req.body);
    return success(res, utility, 'Servicio publico actualizado exitosamente');
  } catch (err) {
    console.error('Utilities.update error:', err);
    return error(res, err.message || 'Error al actualizar servicio publico', err.status || 500);
  }
}

async function updateStatus(req, res) {
  try {
    const { status } = req.body;
    const utility = await utilitiesService.updateStatus(req.params.id, status);
    return success(res, utility, 'Estado actualizado exitosamente');
  } catch (err) {
    console.error('Utilities.updateStatus error:', err);
    return error(res, err.message || 'Error al actualizar estado', err.status || 500);
  }
}

module.exports = {
  list,
  getSummary,
  getById,
  create,
  update,
  updateStatus,
};
