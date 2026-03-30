const reportsService = require('./reports.service');
const { success, error, paginated } = require('../../utils/response');

async function getDashboard(req, res) {
  try {
    const data = await reportsService.getDashboard(req.user.tenantId);
    return success(res, data, 'Dashboard obtenido exitosamente');
  } catch (err) {
    return error(res, err.message || 'Error al obtener dashboard', err.status || 500);
  }
}

async function getIncomeReport(req, res) {
  try {
    const { startDate, endDate, propertyId } = req.query;
    const data = await reportsService.getIncomeReport(req.user.tenantId, { startDate, endDate, propertyId });
    return success(res, data, 'Reporte de ingresos obtenido exitosamente');
  } catch (err) {
    return error(res, err.message || 'Error al obtener reporte de ingresos', err.status || 500);
  }
}

async function getOccupancyReport(req, res) {
  try {
    const data = await reportsService.getOccupancyReport(req.user.tenantId);
    return success(res, data, 'Reporte de ocupacion obtenido exitosamente');
  } catch (err) {
    return error(res, err.message || 'Error al obtener reporte de ocupacion', err.status || 500);
  }
}

async function getPaymentsReport(req, res) {
  try {
    const { startDate, endDate, status, propertyId, page, limit } = req.query;
    const data = await reportsService.getPaymentsReport(req.user.tenantId, {
      startDate,
      endDate,
      status,
      propertyId,
      page: page || 1,
      limit: limit || 50,
    });
    return paginated(res, data.payments, data.page, data.limit, data.total);
  } catch (err) {
    return error(res, err.message || 'Error al obtener reporte de pagos', err.status || 500);
  }
}

async function exportReport(req, res) {
  try {
    const { type } = req.params;
    const filters = req.query;
    const pdfBuffer = await reportsService.exportReport(req.user.tenantId, type, filters);

    res.set({
      'Content-Type': 'application/pdf',
      'Content-Disposition': `attachment; filename=reporte-${type}-${Date.now()}.pdf`,
      'Content-Length': pdfBuffer.length,
    });

    return res.end(pdfBuffer);
  } catch (err) {
    return error(res, err.message || 'Error al exportar reporte', err.status || 500);
  }
}

module.exports = {
  getDashboard,
  getIncomeReport,
  getOccupancyReport,
  getPaymentsReport,
  exportReport,
};
