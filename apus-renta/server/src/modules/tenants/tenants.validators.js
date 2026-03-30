const { body } = require('express-validator');

const create = [
  body('email')
    .isEmail().withMessage('Debe ser un correo electronico valido')
    .normalizeEmail(),
  body('firstName')
    .notEmpty().withMessage('El nombre es obligatorio')
    .trim(),
  body('lastName')
    .notEmpty().withMessage('El apellido es obligatorio')
    .trim(),
  body('password')
    .isLength({ min: 8 }).withMessage('La contrasena debe tener al menos 8 caracteres'),
  body('documentType')
    .isIn(['CC', 'CE', 'PASAPORTE', 'NIT'])
    .withMessage('Tipo de documento no valido'),
  body('documentNumber')
    .notEmpty().withMessage('El numero de documento es obligatorio')
    .trim(),
  body('phone')
    .optional()
    .trim(),
  body('emergencyContactName')
    .optional()
    .trim(),
  body('emergencyContactPhone')
    .optional()
    .trim(),
];

const update = [
  body('email')
    .optional()
    .isEmail().withMessage('Debe ser un correo electronico valido')
    .normalizeEmail(),
  body('firstName')
    .optional()
    .trim(),
  body('lastName')
    .optional()
    .trim(),
  body('password')
    .optional()
    .isLength({ min: 8 }).withMessage('La contrasena debe tener al menos 8 caracteres'),
  body('documentType')
    .optional()
    .isIn(['CC', 'CE', 'PASAPORTE', 'NIT'])
    .withMessage('Tipo de documento no valido'),
  body('documentNumber')
    .optional()
    .trim(),
  body('phone')
    .optional()
    .trim(),
  body('emergencyContactName')
    .optional()
    .trim(),
  body('emergencyContactPhone')
    .optional()
    .trim(),
];

module.exports = {
  create,
  update,
};
