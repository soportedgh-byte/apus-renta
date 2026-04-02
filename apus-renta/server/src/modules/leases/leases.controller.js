const leasesService = require('./leases.service');
const { success, error, paginated } = require('../../utils/response');

async function list(req, res) {
  try {
    const { page, limit, status, propertyId } = req.query;
    const tenantId = req.user.tenantId;
    const result = await leasesService.list(tenantId, {
      page,
      limit,
      status,
      propertyId,
      userRole: req.user.role,
      userId: req.user.id,
    });
    return paginated(res, result.data, result.page, result.limit, result.total);
  } catch (err) {
    console.error('Leases.list error:', err);
    return error(res, err.message || 'Error al listar contratos', err.status || 500);
  }
}

async function getById(req, res) {
  try {
    const lease = await leasesService.getById(req.params.id, req.user.tenantId);
    return success(res, lease, 'Contrato obtenido exitosamente');
  } catch (err) {
    console.error('Leases.getById error:', err);
    return error(res, err.message || 'Error al obtener contrato', err.status || 500);
  }
}

async function create(req, res) {
  try {
    const lease = await leasesService.create(req.body, req.user.tenantId);
    return success(res, lease, 'Contrato creado exitosamente', 201);
  } catch (err) {
    console.error('Leases.create error:', err);
    return error(res, err.message || 'Error al crear contrato', err.status || 500);
  }
}

async function update(req, res) {
  try {
    const lease = await leasesService.update(req.params.id, req.body, req.user.tenantId);
    return success(res, lease, 'Contrato actualizado exitosamente');
  } catch (err) {
    console.error('Leases.update error:', err);
    return error(res, err.message || 'Error al actualizar contrato', err.status || 500);
  }
}

async function updateStatus(req, res) {
  try {
    const { status } = req.body;
    const lease = await leasesService.updateStatus(req.params.id, status, req.user.tenantId);
    return success(res, lease, 'Estado del contrato actualizado exitosamente');
  } catch (err) {
    console.error('Leases.updateStatus error:', err);
    return error(res, err.message || 'Error al actualizar estado del contrato', err.status || 500);
  }
}

async function sendToSign(req, res) {
  try {
    const result = await leasesService.sendToSign(req.params.id, req.user.tenantId);
    return success(res, result, result.message);
  } catch (err) {
    console.error('Leases.sendToSign error:', err);
    return error(res, err.message || 'Error al enviar contrato a firma', err.status || 500);
  }
}

async function remove(req, res) {
  try {
    const result = await leasesService.remove(req.params.id, req.user.tenantId);
    return success(res, result, result.message);
  } catch (err) {
    console.error('Leases.remove error:', err);
    return error(res, err.message || 'Error al eliminar contrato', err.status || 500);
  }
}

module.exports = {
  list,
  getById,
  create,
  update,
  updateStatus,
  sendToSign,
  remove,
};
