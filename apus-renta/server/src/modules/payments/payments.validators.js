const { body } = require('express-validator');

const create = [
  body('leaseId')
    .isInt({ min: 1 }).withMessage('El ID del contrato debe ser un entero valido'),
  body('amount')
    .isDecimal().withMessage('El monto debe ser un numero decimal'),
  body('paymentDate')
    .isISO8601().withMessage('La fecha de pago debe ser una fecha valida (ISO 8601)'),
  body('method')
    .isIn(['NEQUI', 'BANCOLOMBIA', 'DAVIVIENDA', 'EFECTIVO', 'TRANSFERENCIA', 'OTRO'])
    .withMessage('Metodo de pago no valido'),
  body('reference')
    .optional()
    .trim(),
  body('notes')
    .optional()
    .trim(),
];

const reject = [
  body('rejectionReason')
    .notEmpty().withMessage('La razon de rechazo es obligatoria')
    .trim(),
];

module.exports = {
  create,
  reject,
};
