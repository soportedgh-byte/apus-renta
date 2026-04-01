const service = require('./properties.service');
const { success, error, paginated } = require('../../utils/response');

async function list(req, res) {
  try {
    const result = await service.list(req.user.tenantId, req.query);
    return paginated(res, result.properties, result.page, result.limit, result.total);
  } catch (err) {
    console.error('Properties.list error:', err);
    return error(res, err.message || 'Error al listar propiedades', err.status || 500);
  }
}

async function getById(req, res) {
  try {
    const data = await service.getById(req.params.id, req.user.tenantId);
    return success(res, data);
  } catch (err) {
    console.error('Properties.getById error:', err);
    return error(res, err.message, err.status || 500);
  }
}

async function create(req, res) {
  try {
    const data = await service.create(req.body, req.user.tenantId, req.files || []);
    return success(res, data, 'Propiedad creada', 201);
  } catch (err) {
    console.error('Properties.create error:', err);
    return error(res, err.message, err.status || 500);
  }
}

async function update(req, res) {
  try {
    const data = await service.update(req.params.id, req.body, req.user.tenantId, req.files || []);
    return success(res, data, 'Propiedad actualizada');
  } catch (err) {
    console.error('Properties.update error:', err);
    return error(res, err.message, err.status || 500);
  }
}

async function remove(req, res) {
  try {
    const data = await service.remove(req.params.id, req.user.tenantId);
    return success(res, data);
  } catch (err) {
    console.error('Properties.remove error:', err);
    return error(res, err.message, err.status || 500);
  }
}

async function updateStatus(req, res) {
  try {
    const data = await service.updateStatus(req.params.id, req.body.status, req.user.tenantId);
    return success(res, data, 'Estado actualizado');
  } catch (err) {
    console.error('Properties.updateStatus error:', err);
    return error(res, err.message, err.status || 500);
  }
}

module.exports = { list, getById, create, update, remove, updateStatus };
