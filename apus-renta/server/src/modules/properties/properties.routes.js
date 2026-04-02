const router = require('express').Router();
const controller = require('./properties.controller');
const { validate } = require('../../middleware/validate');
const validators = require('./properties.validators');
const { verifyToken, authorize, injectTenantId } = require('../../middleware/auth');
const { uploadMultiple } = require('../../middleware/upload');

router.get('/', verifyToken, injectTenantId, controller.list);
router.get('/list', verifyToken, controller.listAll);
router.get('/:id', verifyToken, controller.getById);
router.post('/', verifyToken, authorize('PROPIETARIO', 'ENCARGADO'), uploadMultiple('photos', 10), validators.create, validate, controller.create);
router.put('/:id', verifyToken, authorize('PROPIETARIO', 'ENCARGADO'), uploadMultiple('photos', 10), validators.update, validate, controller.update);
router.delete('/:id', verifyToken, authorize('PROPIETARIO'), controller.remove);
router.patch('/:id/status', verifyToken, authorize('PROPIETARIO', 'ENCARGADO'), controller.updateStatus);

module.exports = router;
