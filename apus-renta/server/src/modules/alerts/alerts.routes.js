const router = require('express').Router();
const controller = require('./alerts.controller');
const { verifyToken, authorize, injectTenantId } = require('../../middleware/auth');

router.get('/', verifyToken, authorize('PROPIETARIO', 'ENCARGADO'), injectTenantId, controller.list);
router.get('/config', verifyToken, authorize('PROPIETARIO'), controller.getConfig);
router.put('/config', verifyToken, authorize('PROPIETARIO'), controller.updateConfig);
router.post('/test', verifyToken, authorize('PROPIETARIO'), controller.sendTest);

module.exports = router;
