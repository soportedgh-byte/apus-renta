const router = require('express').Router();
const controller = require('./pqrs.controller');
const { validate } = require('../../middleware/validate');
const validators = require('./pqrs.validators');
const { verifyToken, authorize, injectTenantId } = require('../../middleware/auth');
const { uploadMultiple } = require('../../middleware/upload');

router.get('/', verifyToken, injectTenantId, controller.list);
router.get('/:id', verifyToken, controller.getById);
router.post('/', verifyToken, authorize('ARRENDATARIO'), uploadMultiple('attachments', 5), validators.create, validate, controller.create);
router.patch('/:id', verifyToken, authorize('PROPIETARIO', 'ENCARGADO'), validators.update, validate, controller.update);
router.patch('/:id/assign', verifyToken, authorize('PROPIETARIO'), controller.assign);
router.delete('/:id', verifyToken, authorize('PROPIETARIO'), controller.remove);

module.exports = router;
