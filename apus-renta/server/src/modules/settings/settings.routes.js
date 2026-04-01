const router = require('express').Router();
const controller = require('./settings.controller');
const { verifyToken, authorize } = require('../../middleware/auth');

router.get('/alerts', verifyToken, authorize('PROPIETARIO'), controller.getAlertConfig);
router.put('/alerts', verifyToken, authorize('PROPIETARIO'), controller.updateAlertConfig);
router.get('/tenant', verifyToken, authorize('PROPIETARIO'), controller.getTenantInfo);
router.put('/tenant', verifyToken, authorize('PROPIETARIO'), controller.updateTenantInfo);

module.exports = router;
