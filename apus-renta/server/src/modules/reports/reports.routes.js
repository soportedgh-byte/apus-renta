const router = require('express').Router();
const controller = require('./reports.controller');
const { verifyToken, authorize, injectTenantId } = require('../../middleware/auth');

router.get(
  '/dashboard',
  verifyToken,
  authorize('PROPIETARIO', 'ENCARGADO'),
  injectTenantId,
  controller.getDashboard
);

router.get(
  '/income',
  verifyToken,
  authorize('PROPIETARIO'),
  injectTenantId,
  controller.getIncomeReport
);

router.get(
  '/occupancy',
  verifyToken,
  authorize('PROPIETARIO'),
  injectTenantId,
  controller.getOccupancyReport
);

router.get(
  '/payments',
  verifyToken,
  authorize('PROPIETARIO'),
  injectTenantId,
  controller.getPaymentsReport
);

router.get(
  '/export/:type',
  verifyToken,
  authorize('PROPIETARIO'),
  injectTenantId,
  controller.exportReport
);

module.exports = router;
