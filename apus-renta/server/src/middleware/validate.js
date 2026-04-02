const { validationResult } = require('express-validator');

/**
 * Middleware que verifica los resultados de express-validator.
 * Retorna 400 con los errores formateados si la validacion falla.
 */
const validate = (req, res, next) => {
  const errors = validationResult(req);

  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      message: 'Errores de validacion',
      errors: errors.array().map((err) => ({
        field: err.path,
        message: err.msg,
      })),
    });
  }

  next();
};

module.exports = { validate };
