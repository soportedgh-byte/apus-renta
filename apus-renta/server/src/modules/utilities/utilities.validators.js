const { body } = require('express-validator');

const create = [
  body('propertyId')
    .isInt().withMessage('El ID de la propiedad debe ser un entero'),
  body('type')
    .isIn(['AGUA', 'LUZ', 'GAS'])
    .withMessage('Tipo de servicio no valido. Debe ser AGUA, LUZ o GAS'),
  body('amount')
    .isDecimal().withMessage('El monto debe ser un numero decimal'),
  body('period')
    .matches(/^\d{4}-(0[1-9]|1[0-2])$/)
    .withMessage('El periodo debe tener formato YYYY-MM'),
  body('dueDate')
    .isISO8601().withMessage('La fecha de vencimiento debe ser una fecha valida ISO8601'),
];

const update = [
  body('amount')
    .optional()
    .isDecimal().withMessage('El monto debe ser un numero decimal'),
  body('status')
    .optional()
    .isIn(['PENDIENTE', 'PAGADO', 'VENCIDO'])
    .withMessage('Estado no valido'),
];

module.exports = {
  create,
  update,
};
