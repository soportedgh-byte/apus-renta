const service = require('./admin.service');
const { success, error, paginated } = require('../../utils/response');

async function getDashboard(req, res) {
  try {
    const data = await service.getDashboard();
    return success(res, data);
  } catch (err) {
    console.error('Admin.getDashboard error:', err);
    return error(res, err.message, err.status || 500);
  }
}

async function listTenants(req, res) {
  try {
    const result = await service.listTenants(req.query);
    return paginated(res, result.tenants, result.page, result.limit, result.total);
  } catch (err) {
    console.error('Admin.listTenants error:', err);
    return error(res, err.message, err.status || 500);
  }
}

async function createTenant(req, res) {
  try {
    const data = await service.createTenant(req.body);
    return success(res, data, 'Tenant creado exitosamente', 201);
  } catch (err) {
    console.error('Admin.createTenant error:', err);
    return error(res, err.message, err.status || 500);
  }
}

async function getTenant(req, res) {
  try {
    const data = await service.getTenant(req.params.id);
    return success(res, data);
  } catch (err) {
    console.error('Admin.getTenant error:', err);
    return error(res, err.message, err.status || 500);
  }
}

async function updateTenant(req, res) {
  try {
    const data = await service.updateTenant(req.params.id, req.body);
    return success(res, data, 'Tenant actualizado');
  } catch (err) {
    console.error('Admin.updateTenant error:', err);
    return error(res, err.message, err.status || 500);
  }
}

async function deleteTenant(req, res) {
  try {
    const data = await service.deleteTenant(req.params.id);
    return success(res, data, 'Tenant desactivado');
  } catch (err) {
    console.error('Admin.deleteTenant error:', err);
    return error(res, err.message, err.status || 500);
  }
}

async function getTenantStats(req, res) {
  try {
    const data = await service.getTenantStats(req.params.id);
    return success(res, data);
  } catch (err) {
    console.error('Admin.getTenantStats error:', err);
    return error(res, err.message, err.status || 500);
  }
}

async function getPlans(req, res) {
  try {
    const data = service.getPlans();
    return success(res, data);
  } catch (err) {
    console.error('Admin.getPlans error:', err);
    return error(res, err.message, err.status || 500);
  }
}

async function updatePlan(req, res) {
  try {
    const data = service.updatePlan(req.params.plan, req.body);
    return success(res, data, 'Plan actualizado');
  } catch (err) {
    console.error('Admin.updatePlan error:', err);
    return error(res, err.message, err.status || 500);
  }
}

module.exports = {
  getDashboard, listTenants, createTenant, getTenant, updateTenant,
  deleteTenant, getTenantStats, getPlans, updatePlan,
};
