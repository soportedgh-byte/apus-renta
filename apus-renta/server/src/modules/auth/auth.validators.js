const { body } = require('express-validator');

const register = [
  body('email')
    .isEmail().withMessage('Debe ser un correo electrónico válido')
    .normalizeEmail(),
  body('password')
    .isLength({ min: 8 }).withMessage('La contraseña debe tener al menos 8 caracteres')
    .matches(/[A-Z]/).withMessage('La contraseña debe contener al menos una letra mayúscula')
    .matches(/[a-z]/).withMessage('La contraseña debe contener al menos una letra minúscula')
    .matches(/\d/).withMessage('La contraseña debe contener al menos un dígito'),
  body('firstName')
    .notEmpty().withMessage('El nombre es obligatorio')
    .trim(),
  body('lastName')
    .notEmpty().withMessage('El apellido es obligatorio')
    .trim(),
  body('role')
    .optional()
    .isIn(['ADMIN', 'MANAGER', 'ARRENDATARIO', 'VIEWER'])
    .withMessage('Rol no válido'),
];

const login = [
  body('email')
    .isEmail().withMessage('Debe ser un correo electrónico válido'),
  body('password')
    .notEmpty().withMessage('La contraseña es obligatoria'),
];

const forgotPassword = [
  body('email')
    .isEmail().withMessage('Debe ser un correo electrónico válido'),
];

const resetPassword = [
  body('token')
    .notEmpty().withMessage('El token es obligatorio'),
  body('password')
    .isLength({ min: 8 }).withMessage('La contraseña debe tener al menos 8 caracteres'),
];

const changePassword = [
  body('currentPassword')
    .notEmpty().withMessage('La contraseña actual es obligatoria'),
  body('newPassword')
    .isLength({ min: 8 }).withMessage('La nueva contraseña debe tener al menos 8 caracteres')
    .matches(/[A-Z]/).withMessage('La contraseña debe contener al menos una letra mayúscula')
    .matches(/[a-z]/).withMessage('La contraseña debe contener al menos una letra minúscula')
    .matches(/\d/).withMessage('La contraseña debe contener al menos un dígito'),
];

module.exports = {
  register,
  login,
  forgotPassword,
  resetPassword,
  changePassword,
};
