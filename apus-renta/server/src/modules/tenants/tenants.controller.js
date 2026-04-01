const tenantsService = require('./tenants.service');
const { success, error, paginated } = require('../../utils/response');

async function list(req, res) {
  try {
    const tenantId = req.user.tenantId;
    const { page, limit, search } = req.query;
    const result = await tenantsService.list(tenantId, { page, limit, search });
    return paginated(res, result.tenants, result.page, result.limit, result.total);
  } catch (err) {
    console.error('Tenants.list error:', err);
    return error(res, err.message || 'Error al listar arrendatarios', err.status || 500);
  }
}

async function getById(req, res) {
  try {
    const tenant = await tenantsService.getById(req.params.id, req.user.tenantId);
    return success(res, tenant, 'Arrendatario obtenido exitosamente');
  } catch (err) {
    console.error('Tenants.getById error:', err);
    return error(res, err.message || 'Error al obtener arrendatario', err.status || 500);
  }
}

async function create(req, res) {
  try {
    const tenant = await tenantsService.create(req.body, req.user.tenantId);
    return success(res, tenant, 'Arrendatario creado exitosamente', 201);
  } catch (err) {
    console.error('Tenants.create error:', err);
    return error(res, err.message || 'Error al crear arrendatario', err.status || 500);
  }
}

async function update(req, res) {
  try {
    const tenant = await tenantsService.update(req.params.id, req.body, req.user.tenantId);
    return success(res, tenant, 'Arrendatario actualizado exitosamente');
  } catch (err) {
    console.error('Tenants.update error:', err);
    return error(res, err.message || 'Error al actualizar arrendatario', err.status || 500);
  }
}

async function remove(req, res) {
  try {
    const tenant = await tenantsService.remove(req.params.id, req.user.tenantId);
    return success(res, tenant, 'Arrendatario desactivado exitosamente');
  } catch (err) {
    console.error('Tenants.delete error:', err);
    return error(res, err.message || 'Error al eliminar arrendatario', err.status || 500);
  }
}

async function listAll(req, res) {
  try {
    const users = await require('../../config/database').user.findMany({
      where: { tenantId: Number(req.user.tenantId), role: 'ARRENDATARIO', status: 'ACTIVE' },
      select: { id: true, firstName: true, lastName: true, email: true, tenantPerson: { select: { id: true, documentNumber: true } } },
      orderBy: { firstName: 'asc' },
    });
    return success(res, users);
  } catch (err) {
    console.error('Tenants.listAll error:', err);
    return error(res, err.message, err.status || 500);
  }
}

module.exports = {
  list,
  getById,
  create,
  update,
  delete: remove,
  listAll,
};
