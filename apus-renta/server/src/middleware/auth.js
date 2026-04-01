const jwt = require('jsonwebtoken');

/**
 * Verifica el token JWT del header Authorization.
 * Adjunta el usuario decodificado (id, tenantId, role) a req.user.
 */
const verifyToken = (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({
      success: false,
      message: 'Token de autenticacion no proporcionado',
    });
  }

  const token = authHeader.split(' ')[1];

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = {
      id: decoded.id,
      tenantId: decoded.tenantId,
      role: decoded.role,
    };
    next();
  } catch (error) {
    return res.status(401).json({
      success: false,
      message: 'Token invalido o expirado',
    });
  }
};

/**
 * Middleware factory que verifica si el rol del usuario esta en la lista permitida.
 * @param  {...string} roles - Roles permitidos (e.g., 'ADMIN', 'MANAGER')
 */
const authorize = (...roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'No autenticado',
      });
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        message: 'No tiene permisos para realizar esta accion',
      });
    }

    next();
  };
};

/**
 * Inyecta el tenantId del usuario autenticado en req.body y req.query
 * para filtrado automatico multi-tenant.
 */
const injectTenantId = (req, res, next) => {
  if (req.user && req.user.tenantId) {
    if (req.body) {
      req.body.tenantId = req.user.tenantId;
    }
    if (req.query) {
      req.query.tenantId = req.user.tenantId;
    }
  }
  next();
};

module.exports = {
  verifyToken,
  authorize,
  injectTenantId,
};
