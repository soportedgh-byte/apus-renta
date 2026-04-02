const path = require('path');
const paymentsService = require('./payments.service');
const { success, error, paginated } = require('../../utils/response');

async function list(req, res) {
  try {
    const { page, limit, status, leaseId, startDate, endDate } = req.query;
    const result = await paymentsService.list(
      req.user.tenantId,
      req.user.id,
      req.user.role,
      { page, limit, status, leaseId, startDate, endDate }
    );
    return paginated(res, result.data, result.page, result.limit, result.total);
  } catch (err) {
    console.error('Payments.list error:', err);
    return error(res, err.message || 'Error al listar pagos', err.status || 500);
  }
}

async function getById(req, res) {
  try {
    const payment = await paymentsService.getById(req.params.id, req.user.tenantId);
    return success(res, payment, 'Pago obtenido exitosamente');
  } catch (err) {
    console.error('Payments.getById error:', err);
    return error(res, err.message || 'Error al obtener pago', err.status || 500);
  }
}

async function create(req, res) {
  try {
    const payment = await paymentsService.create(
      req.body,
      req.user.id,
      req.user.tenantId,
      req.file || null
    );
    return success(res, payment, 'Pago registrado exitosamente', 201);
  } catch (err) {
    console.error('Payments.create error:', err);
    return error(res, err.message || 'Error al registrar pago', err.status || 500);
  }
}

async function approve(req, res) {
  try {
    const payment = await paymentsService.approve(req.params.id, req.user.id, req.user.tenantId);
    return success(res, payment, 'Pago aprobado exitosamente');
  } catch (err) {
    console.error('Payments.approve error:', err);
    return error(res, err.message || 'Error al aprobar pago', err.status || 500);
  }
}

async function reject(req, res) {
  try {
    const { rejectionReason } = req.body;
    const payment = await paymentsService.reject(req.params.id, req.user.id, req.user.tenantId, rejectionReason);
    return success(res, payment, 'Pago rechazado');
  } catch (err) {
    console.error('Payments.reject error:', err);
    return error(res, err.message || 'Error al rechazar pago', err.status || 500);
  }
}

async function getReceipt(req, res) {
  try {
    const receipt = await paymentsService.getReceipt(req.params.id);
    return success(res, receipt, 'Recibo obtenido exitosamente');
  } catch (err) {
    console.error('Payments.getReceipt error:', err);
    return error(res, err.message || 'Error al obtener recibo', err.status || 500);
  }
}

async function downloadReceipt(req, res) {
  try {
    const receipt = await paymentsService.getReceipt(req.params.id);
    const filePath = path.join(__dirname, '../../../', receipt.pdfUrl);
    return res.download(filePath, `recibo-pago-${req.params.id}.pdf`);
  } catch (err) {
    console.error('Payments.downloadReceipt error:', err);
    return error(res, err.message || 'Error al descargar recibo', err.status || 500);
  }
}

module.exports = {
  list,
  getById,
  create,
  approve,
  reject,
  getReceipt,
  downloadReceipt,
};
