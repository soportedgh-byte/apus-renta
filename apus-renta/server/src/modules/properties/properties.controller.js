const propertiesService = require('./properties.service');
const { success, error, paginated } = require('../../utils/response');

async function list(req, res) {
  try {
    const tenantId = req.user.tenantId;
    const { page, limit, status, type, search } = req.query;
    const result = await propertiesService.list(tenantId, { page, limit, status, type, search });
    return paginated(res, result.properties, result.page, result.limit, result.total);
  } catch (err) {
    return error(res, err.message || 'Error al listar propiedades', err.status || 500);
  }
}

async function getById(req, res) {
  try {
    const property = await propertiesService.getById(req.params.id, req.user.tenantId);
    return success(res, property, 'Propiedad obtenida exitosamente');
  } catch (err) {
    return error(res, err.message || 'Error al obtener propiedad', err.status || 500);
  }
}

async function create(req, res) {
  try {
    const property = await propertiesService.create(req.body, req.user.tenantId, req.files || []);
    return success(res, property, 'Propiedad creada exitosamente', 201);
  } catch (err) {
    return error(res, err.message || 'Error al crear propiedad', err.status || 500);
  }
}

async function update(req, res) {
  try {
    const property = await propertiesService.update(req.params.id, req.body, req.user.tenantId, req.files || []);
    return success(res, property, 'Propiedad actualizada exitosamente');
  } catch (err) {
    return error(res, err.message || 'Error al actualizar propiedad', err.status || 500);
  }
}

async function remove(req, res) {
  try {
    const result = await propertiesService.delete(req.params.id, req.user.tenantId);
    const message = result.softDeleted
      ? 'Propiedad marcada como en mantenimiento (tiene contratos activos)'
      : 'Propiedad eliminada exitosamente';
    return success(res, result, message);
  } catch (err) {
    return error(res, err.message || 'Error al eliminar propiedad', err.status || 500);
  }
}

async function updateStatus(req, res) {
  try {
    const { status: newStatus } = req.body;
    const property = await propertiesService.updateStatus(req.params.id, newStatus, req.user.tenantId);
    return success(res, property, 'Estado de propiedad actualizado exitosamente');
  } catch (err) {
    return error(res, err.message || 'Error al actualizar estado de propiedad', err.status || 500);
  }
}

module.exports = {
  list,
  getById,
  create,
  update,
  delete: remove,
  updateStatus,
};
