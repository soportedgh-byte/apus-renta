const pqrsService = require('./pqrs.service');
const { success, error, paginated } = require('../../utils/response');

async function list(req, res) {
  try {
    const { tenantId, page, limit, status, type, propertyId } = req.query;
    const { id: userId, role } = req.user;
    const result = await pqrsService.list(tenantId, userId, role, { page, limit, status, type, propertyId });
    return paginated(res, result.data, result.page, result.limit, result.total);
  } catch (err) {
    return error(res, err.message || 'Error al listar PQRS', err.status || 500);
  }
}

async function getById(req, res) {
  try {
    const pqrs = await pqrsService.getById(req.params.id);
    return success(res, pqrs, 'PQRS obtenida');
  } catch (err) {
    return error(res, err.message || 'Error al obtener PQRS', err.status || 500);
  }
}

async function create(req, res) {
  try {
    const pqrs = await pqrsService.create(req.body, req.user.id, req.user.tenantId, req.files);
    return success(res, pqrs, 'PQRS creada exitosamente', 201);
  } catch (err) {
    return error(res, err.message || 'Error al crear PQRS', err.status || 500);
  }
}

async function update(req, res) {
  try {
    const pqrs = await pqrsService.update(req.params.id, req.body, req.user.tenantId);
    return success(res, pqrs, 'PQRS actualizada exitosamente');
  } catch (err) {
    return error(res, err.message || 'Error al actualizar PQRS', err.status || 500);
  }
}

async function assign(req, res) {
  try {
    const { assignedTo } = req.body;
    const pqrs = await pqrsService.assign(req.params.id, assignedTo, req.user.tenantId);
    return success(res, pqrs, 'PQRS asignada exitosamente');
  } catch (err) {
    return error(res, err.message || 'Error al asignar PQRS', err.status || 500);
  }
}

async function remove(req, res) {
  try {
    const result = await pqrsService.remove(req.params.id, req.user.tenantId);
    return success(res, result, 'PQRS eliminada exitosamente');
  } catch (err) {
    return error(res, err.message || 'Error al eliminar PQRS', err.status || 500);
  }
}

module.exports = {
  list,
  getById,
  create,
  update,
  assign,
  remove,
};
