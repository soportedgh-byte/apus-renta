const router = require('express').Router();
const controller = require('./tenants.controller');
const { validate } = require('../../middleware/validate');
const validators = require('./tenants.validators');
const { verifyToken, authorize, injectTenantId } = require('../../middleware/auth');

router.get('/', verifyToken, authorize('PROPIETARIO', 'ENCARGADO'), injectTenantId, controller.list);
router.get('/list', verifyToken, authorize('PROPIETARIO', 'ENCARGADO'), controller.listAll);
router.get('/:id', verifyToken, authorize('PROPIETARIO', 'ENCARGADO'), controller.getById);
router.post('/', verifyToken, authorize('PROPIETARIO'), validators.create, validate, controller.create);
router.put('/:id', verifyToken, authorize('PROPIETARIO'), validators.update, validate, controller.update);
router.delete('/:id', verifyToken, authorize('PROPIETARIO'), controller.delete);

module.exports = router;
