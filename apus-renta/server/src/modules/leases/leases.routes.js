const router = require('express').Router();
const controller = require('./leases.controller');
const validators = require('./leases.validators');
const { validate } = require('../../middleware/validate');
const { verifyToken, authorize, injectTenantId } = require('../../middleware/auth');

router.get('/', verifyToken, injectTenantId, controller.list);
router.get('/:id', verifyToken, controller.getById);
router.post('/', verifyToken, authorize('PROPIETARIO'), validators.create, validate, controller.create);
router.put('/:id', verifyToken, authorize('PROPIETARIO'), validators.update, validate, controller.update);
router.patch('/:id/status', verifyToken, authorize('PROPIETARIO'), controller.updateStatus);
router.post('/:id/sign', verifyToken, authorize('PROPIETARIO'), controller.sendToSign);
router.delete('/:id', verifyToken, authorize('PROPIETARIO'), controller.remove);

module.exports = router;
