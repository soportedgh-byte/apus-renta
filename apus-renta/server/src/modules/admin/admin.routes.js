const router = require('express').Router();
const controller = require('./admin.controller');
const { verifyToken, authorize } = require('../../middleware/auth');

const superOnly = [verifyToken, authorize('SUPER_ADMIN')];

router.get('/dashboard', ...superOnly, controller.getDashboard);
router.get('/tenants', ...superOnly, controller.listTenants);
router.post('/tenants', ...superOnly, controller.createTenant);
router.get('/tenants/:id', ...superOnly, controller.getTenant);
router.put('/tenants/:id', ...superOnly, controller.updateTenant);
router.delete('/tenants/:id', ...superOnly, controller.deleteTenant);
router.get('/tenants/:id/stats', ...superOnly, controller.getTenantStats);
router.get('/plans', ...superOnly, controller.getPlans);
router.put('/plans/:plan', ...superOnly, controller.updatePlan);

module.exports = router;
