const router = require('express').Router();
const controller = require('./utilities.controller');
const { validate } = require('../../middleware/validate');
const validators = require('./utilities.validators');
const { verifyToken, authorize, injectTenantId } = require('../../middleware/auth');
const { uploadSingle } = require('../../middleware/upload');

router.get('/', verifyToken, injectTenantId, controller.list);
router.get('/summary', verifyToken, authorize('PROPIETARIO', 'ENCARGADO'), injectTenantId, controller.getSummary);
router.get('/:id', verifyToken, controller.getById);
router.post('/', verifyToken, uploadSingle('receipt'), validators.create, validate, controller.create);
router.put('/:id', verifyToken, validators.update, validate, controller.update);
router.patch('/:id/status', verifyToken, authorize('PROPIETARIO', 'ENCARGADO'), controller.updateStatus);

module.exports = router;
