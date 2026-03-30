const router = require('express').Router();
const controller = require('./audit.controller');
const { verifyToken, authorize, injectTenantId } = require('../../middleware/auth');

router.get(
  '/',
  verifyToken,
  authorize('PROPIETARIO'),
  injectTenantId,
  controller.list
);

router.get(
  '/stats',
  verifyToken,
  authorize('PROPIETARIO'),
  injectTenantId,
  controller.getStats
);

module.exports = router;
