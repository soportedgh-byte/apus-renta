const router = require('express').Router();
const controller = require('./payments.controller');
const validators = require('./payments.validators');
const { validate } = require('../../middleware/validate');
const { verifyToken, authorize, injectTenantId } = require('../../middleware/auth');
const { uploadSingle } = require('../../middleware/upload');

router.get('/', verifyToken, injectTenantId, controller.list);
router.get('/:id', verifyToken, controller.getById);
router.post('/', verifyToken, authorize('ARRENDATARIO'), uploadSingle('support'), validators.create, validate, controller.create);
router.patch('/:id/approve', verifyToken, authorize('PROPIETARIO'), controller.approve);
router.patch('/:id/reject', verifyToken, authorize('PROPIETARIO'), validators.reject, validate, controller.reject);
router.get('/:id/receipt', verifyToken, controller.getReceipt);
router.get('/:id/receipt/download', verifyToken, controller.downloadReceipt);

module.exports = router;
