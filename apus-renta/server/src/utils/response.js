/**
 * Respuesta exitosa estandar.
 * @param {object} res - Express response
 * @param {*} data - Datos a retornar
 * @param {string} message - Mensaje descriptivo
 * @param {number} statusCode - Codigo HTTP (default: 200)
 */
const success = (res, data, message = 'Operacion exitosa', statusCode = 200) => {
  return res.status(statusCode).json({
    success: true,
    message,
    data,
  });
};

/**
 * Respuesta de error estandar.
 * @param {object} res - Express response
 * @param {string} message - Mensaje de error
 * @param {number} statusCode - Codigo HTTP (default: 500)
 * @param {*} errors - Detalles adicionales de errores
 */
const error = (res, message = 'Error interno del servidor', statusCode = 500, errors = null) => {
  return res.status(statusCode).json({
    success: false,
    message,
    errors,
  });
};

/**
 * Respuesta paginada estandar.
 * @param {object} res - Express response
 * @param {*} data - Datos de la pagina actual
 * @param {number} page - Numero de pagina actual
 * @param {number} limit - Elementos por pagina
 * @param {number} total - Total de elementos
 */
const paginated = (res, data, page, limit, total) => {
  return res.status(200).json({
    success: true,
    data,
    pagination: {
      page,
      limit,
      total,
      pages: Math.ceil(total / limit),
    },
  });
};

module.exports = {
  success,
  error,
  paginated,
};
