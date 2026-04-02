const router = require('express').Router();
const controller = require('./settings.controller');
const { verifyToken, authorize } = require('../../middleware/auth');
const { uploadSingle } = require('../../middleware/upload');

router.get('/alerts', verifyToken, authorize('PROPIETARIO'), controller.getAlertConfig);
router.put('/alerts', verifyToken, authorize('PROPIETARIO'), controller.updateAlertConfig);
router.get('/tenant', verifyToken, authorize('PROPIETARIO'), controller.getTenantInfo);
router.put('/tenant', verifyToken, authorize('PROPIETARIO'), uploadSingle('logo'), controller.updateTenantInfo);

module.exports = router;
