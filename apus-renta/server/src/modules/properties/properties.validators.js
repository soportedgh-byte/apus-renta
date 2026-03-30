const { body } = require('express-validator');

const create = [
  body('name')
    .notEmpty().withMessage('El nombre es obligatorio')
    .isLength({ max: 200 }).withMessage('El nombre no puede exceder 200 caracteres')
    .trim(),
  body('type')
    .isIn(['CASA', 'APARTAMENTO', 'LOCAL', 'OFICINA', 'BODEGA'])
    .withMessage('Tipo de propiedad no valido'),
  body('address')
    .notEmpty().withMessage('La direccion es obligatoria')
    .trim(),
  body('city')
    .notEmpty().withMessage('La ciudad es obligatoria')
    .trim(),
  body('area')
    .optional()
    .isDecimal().withMessage('El area debe ser un numero decimal'),
  body('bedrooms')
    .optional()
    .isInt({ min: 0 }).withMessage('Las habitaciones deben ser un entero mayor o igual a 0'),
  body('bathrooms')
    .optional()
    .isInt({ min: 0 }).withMessage('Los banos deben ser un entero mayor o igual a 0'),
  body('monthlyRent')
    .optional()
    .isDecimal().withMessage('El arriendo mensual debe ser un numero decimal'),
  body('status')
    .optional()
    .isIn(['DISPONIBLE', 'OCUPADO', 'MANTENIMIENTO'])
    .withMessage('Estado no valido'),
];

const update = [
  body('name')
    .optional()
    .isLength({ max: 200 }).withMessage('El nombre no puede exceder 200 caracteres')
    .trim(),
  body('type')
    .optional()
    .isIn(['CASA', 'APARTAMENTO', 'LOCAL', 'OFICINA', 'BODEGA'])
    .withMessage('Tipo de propiedad no valido'),
  body('address')
    .optional()
    .trim(),
  body('city')
    .optional()
    .trim(),
  body('area')
    .optional()
    .isDecimal().withMessage('El area debe ser un numero decimal'),
  body('bedrooms')
    .optional()
    .isInt({ min: 0 }).withMessage('Las habitaciones deben ser un entero mayor o igual a 0'),
  body('bathrooms')
    .optional()
    .isInt({ min: 0 }).withMessage('Los banos deben ser un entero mayor o igual a 0'),
  body('monthlyRent')
    .optional()
    .isDecimal().withMessage('El arriendo mensual debe ser un numero decimal'),
  body('status')
    .optional()
    .isIn(['DISPONIBLE', 'OCUPADO', 'MANTENIMIENTO'])
    .withMessage('Estado no valido'),
];

module.exports = {
  create,
  update,
};
