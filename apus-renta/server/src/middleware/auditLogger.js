const auditService = require('../modules/audit/audit.service');

/**
 * Helper para crear un log de auditoria desde cualquier punto de la app.
 * Extrae automaticamente tenantId, userId, IP y User-Agent del request.
 *
 * @param {object} req - Express request (debe tener req.user poblado)
 * @param {string} action - Accion realizada (CREATE, UPDATE, DELETE, APPROVE, REJECT, LOGIN, etc.)
 * @param {string} entity - Entidad afectada (Payment, Property, Lease, User, etc.)
 * @param {number|null} entityId - ID de la entidad afectada
 * @param {object|null} details - Detalles adicionales en formato JSON
 * @returns {Promise<object>} El registro de auditoria creado
 */
async function createAuditLog(req, action, entity, entityId = null, details = null) {
  const tenantId = req.user?.tenantId;
  const userId = req.user?.id;

  if (!tenantId || !userId) {
    console.warn('auditLogger: No se pudo crear log - usuario no autenticado');
    return null;
  }

  const ipAddress =
    req.headers['x-forwarded-for']?.split(',')[0]?.trim() ||
    req.connection?.remoteAddress ||
    req.ip ||
    null;

  const userAgent = req.headers['user-agent'] || null;

  try {
    return await auditService.log({
      tenantId,
      userId,
      action,
      entity,
      entityId,
      details,
      ipAddress,
      userAgent,
    });
  } catch (err) {
    console.error('auditLogger: Error al crear log de auditoria:', err.message);
    return null;
  }
}

module.exports = { createAuditLog };
