const { body } = require('express-validator');

const create = [
  body('propertyId')
    .isInt({ min: 1 }).withMessage('El ID de la propiedad debe ser un entero valido'),
  body('tenantPersonId')
    .isInt({ min: 1 }).withMessage('El ID del arrendatario debe ser un entero valido'),
  body('startDate')
    .isISO8601().withMessage('La fecha de inicio debe ser una fecha valida (ISO 8601)'),
  body('endDate')
    .isISO8601().withMessage('La fecha de fin debe ser una fecha valida (ISO 8601)'),
  body('monthlyRent')
    .isDecimal().withMessage('El arriendo mensual debe ser un numero decimal'),
  body('deposit')
    .optional()
    .isDecimal().withMessage('El deposito debe ser un numero decimal'),
  body('terms')
    .optional()
    .trim(),
];

const update = [
  body('propertyId')
    .optional()
    .isInt({ min: 1 }).withMessage('El ID de la propiedad debe ser un entero valido'),
  body('tenantPersonId')
    .optional()
    .isInt({ min: 1 }).withMessage('El ID del arrendatario debe ser un entero valido'),
  body('startDate')
    .optional()
    .isISO8601().withMessage('La fecha de inicio debe ser una fecha valida (ISO 8601)'),
  body('endDate')
    .optional()
    .isISO8601().withMessage('La fecha de fin debe ser una fecha valida (ISO 8601)'),
  body('monthlyRent')
    .optional()
    .isDecimal().withMessage('El arriendo mensual debe ser un numero decimal'),
  body('deposit')
    .optional()
    .isDecimal().withMessage('El deposito debe ser un numero decimal'),
  body('terms')
    .optional()
    .trim(),
];

module.exports = {
  create,
  update,
};
