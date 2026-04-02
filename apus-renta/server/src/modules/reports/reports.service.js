const prisma = require('../../config/database');
const { formatCurrency, formatDate } = require('../../utils/helpers');
const { generatePDF } = require('../../utils/pdf');

/**
 * Dashboard KPIs y datos resumidos para el propietario/encargado.
 */
async function getArrendatarioDashboard(tenantId, userId) {
  // Find tenant person and active lease
  const user = await prisma.user.findUnique({
    where: { id: userId },
    include: {
      tenantPerson: {
        include: {
          leases: {
            where: { status: 'ACTIVO' },
            take: 1,
            orderBy: { startDate: 'desc' },
            include: { property: true },
          },
        },
      },
    },
  });

  const tenantPerson = user?.tenantPerson;
  const activeLease = tenantPerson?.leases?.[0] || null;
  const propertyId = activeLease?.propertyId;

  // Get recent payments
  const recentPayments = await prisma.payment.findMany({
    where: { userId },
    orderBy: { createdAt: 'desc' },
    take: 5,
    include: {
      lease: { include: { property: { select: { id: true, name: true } } } },
    },
  });

  // Get utility status for their property
  let utilities = [];
  if (propertyId) {
    const types = ['AGUA', 'LUZ', 'GAS'];
    for (const type of types) {
      const latest = await prisma.utilityBill.findFirst({
        where: { propertyId, type },
        orderBy: { createdAt: 'desc' },
      });
      utilities.push({
        type,
        status: latest?.status || null,
        amount: latest ? Number(latest.amount) : null,
        period: latest?.period || null,
        dueDate: latest?.dueDate || null,
      });
    }
  }

  // Get open PQRS
  const openPQRS = await prisma.pQRS.count({
    where: { userId, status: { in: ['RADICADA', 'EN_PROCESO'] } },
  });

  const pqrsList = await prisma.pQRS.findMany({
    where: { userId, status: { in: ['RADICADA', 'EN_PROCESO'] } },
    orderBy: { createdAt: 'desc' },
    take: 5,
    include: { property: { select: { id: true, name: true } } },
  });

  return {
    role: 'ARRENDATARIO',
    property: activeLease?.property || null,
    lease: activeLease ? {
      id: activeLease.id,
      monthlyRent: Number(activeLease.monthlyRent),
      startDate: activeLease.startDate,
      endDate: activeLease.endDate,
      status: activeLease.status,
    } : null,
    recentPayments,
    utilities,
    openPQRS,
    pqrsList,
  };
}

async function getDashboard(tenantId, userId, role) {
  tenantId = Number(tenantId);

  if (role === 'ARRENDATARIO') {
    return getArrendatarioDashboard(tenantId, Number(userId));
  }
  const now = new Date();
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
  const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59);
  const in30Days = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);

  // --- Parallel queries ---
  const [
    totalProperties,
    occupiedProperties,
    activeLeases,
    expiringLeases,
    expectedIncomeAgg,
    actualIncomeAgg,
    pendingPayments,
    activeAlerts,
    openPQRS,
    recentPayments,
  ] = await Promise.all([
    prisma.property.count({ where: { tenantId } }),
    prisma.property.count({ where: { tenantId, status: 'OCUPADO' } }),
    prisma.lease.count({ where: { tenantId, status: 'ACTIVO' } }),
    prisma.lease.count({
      where: {
        tenantId,
        status: 'ACTIVO',
        endDate: { gte: now, lte: in30Days },
      },
    }),
    prisma.lease.aggregate({
      _sum: { monthlyRent: true },
      where: { tenantId, status: 'ACTIVO' },
    }),
    prisma.payment.aggregate({
      _sum: { amount: true },
      where: {
        lease: { tenantId },
        status: 'APROBADO',
        paymentDate: { gte: startOfMonth, lte: endOfMonth },
      },
    }),
    prisma.payment.count({
      where: { lease: { tenantId }, status: 'PENDIENTE' },
    }),
    prisma.alert.count({
      where: { tenantId, status: 'PENDIENTE' },
    }),
    prisma.pQRS.count({
      where: { tenantId, status: { in: ['RADICADA', 'EN_PROCESO'] } },
    }),
    prisma.payment.findMany({
      where: { lease: { tenantId } },
      orderBy: { createdAt: 'desc' },
      take: 5,
      include: {
        lease: {
          include: {
            property: { select: { id: true, name: true, address: true } },
          },
        },
        user: { select: { id: true, firstName: true, lastName: true, email: true } },
      },
    }),
  ]);

  const expectedMonthlyIncome = Number(expectedIncomeAgg._sum.monthlyRent || 0);
  const actualMonthlyIncome = Number(actualIncomeAgg._sum.amount || 0);
  const occupancyRate = totalProperties > 0
    ? Math.round((occupiedProperties / totalProperties) * 10000) / 100
    : 0;
  const collectionRate = expectedMonthlyIncome > 0
    ? Math.round((actualMonthlyIncome / expectedMonthlyIncome) * 10000) / 100
    : 0;
  const overdueAmount = Math.max(expectedMonthlyIncome - actualMonthlyIncome, 0);

  // --- Monthly trend: last 6 months ---
  const monthlyTrend = [];
  for (let i = 5; i >= 0; i--) {
    const mStart = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const mEnd = new Date(now.getFullYear(), now.getMonth() - i + 1, 0, 23, 59, 59);
    const monthLabel = mStart.toLocaleDateString('es-CO', { year: 'numeric', month: 'short' });

    const [expectedAgg, actualAgg] = await Promise.all([
      prisma.lease.aggregate({
        _sum: { monthlyRent: true },
        where: {
          tenantId,
          status: { in: ['ACTIVO', 'VENCIDO', 'RENOVADO'] },
          startDate: { lte: mEnd },
          endDate: { gte: mStart },
        },
      }),
      prisma.payment.aggregate({
        _sum: { amount: true },
        where: {
          lease: { tenantId },
          status: 'APROBADO',
          paymentDate: { gte: mStart, lte: mEnd },
        },
      }),
    ]);

    monthlyTrend.push({
      month: monthLabel,
      expected: Number(expectedAgg._sum.monthlyRent || 0),
      actual: Number(actualAgg._sum.amount || 0),
    });
  }

  return {
    totalProperties,
    occupiedProperties,
    occupancyRate,
    expectedMonthlyIncome,
    actualMonthlyIncome,
    collectionRate,
    pendingPayments,
    overdueAmount,
    activeLeases,
    expiringLeases,
    activeAlerts,
    openPQRS,
    recentPayments,
    monthlyTrend,
  };
}

/**
 * Reporte de ingresos agrupado por mes y propiedad.
 */
async function getIncomeReport(tenantId, { startDate, endDate, propertyId } = {}) {
  tenantId = Number(tenantId);
  const where = { lease: { tenantId }, status: 'APROBADO' };

  if (startDate || endDate) {
    where.paymentDate = {};
    if (startDate) where.paymentDate.gte = new Date(startDate);
    if (endDate) where.paymentDate.lte = new Date(endDate);
  }

  if (propertyId) {
    where.lease = { tenantId, propertyId: Number(propertyId) };
  }

  const payments = await prisma.payment.findMany({
    where,
    include: {
      lease: {
        include: {
          property: { select: { id: true, name: true, address: true } },
        },
      },
    },
    orderBy: { paymentDate: 'asc' },
  });

  // Group by month
  const byMonth = {};
  // Group by property
  const byProperty = {};
  let grandTotal = 0;

  for (const p of payments) {
    const amount = Number(p.amount);
    grandTotal += amount;

    const monthKey = `${p.paymentDate.getFullYear()}-${String(p.paymentDate.getMonth() + 1).padStart(2, '0')}`;
    if (!byMonth[monthKey]) byMonth[monthKey] = { month: monthKey, total: 0, count: 0 };
    byMonth[monthKey].total += amount;
    byMonth[monthKey].count += 1;

    const propName = p.lease?.property?.name || 'Sin propiedad';
    const propId = p.lease?.property?.id;
    if (!byProperty[propId]) byProperty[propId] = { propertyId: propId, name: propName, total: 0, count: 0 };
    byProperty[propId].total += amount;
    byProperty[propId].count += 1;
  }

  return {
    grandTotal,
    totalPayments: payments.length,
    byMonth: Object.values(byMonth),
    byProperty: Object.values(byProperty),
    payments,
  };
}

/**
 * Reporte de ocupacion de propiedades.
 */
async function getOccupancyReport(tenantId) {
  tenantId = Number(tenantId);
  const properties = await prisma.property.findMany({
    where: { tenantId },
    include: {
      leases: {
        where: { status: 'ACTIVO' },
        take: 1,
        orderBy: { startDate: 'desc' },
        include: {
          tenantPerson: {
            include: {
              user: { select: { id: true, firstName: true, lastName: true, email: true, phone: true } },
            },
          },
        },
      },
    },
    orderBy: { name: 'asc' },
  });

  const total = properties.length;
  const occupied = properties.filter((p) => p.status === 'OCUPADO').length;
  const available = properties.filter((p) => p.status === 'DISPONIBLE').length;
  const maintenance = properties.filter((p) => p.status === 'MANTENIMIENTO').length;

  const details = properties.map((p) => {
    const activeLease = p.leases[0] || null;
    return {
      id: p.id,
      name: p.name,
      type: p.type,
      address: p.address,
      status: p.status,
      tenant: activeLease
        ? {
            name: `${activeLease.tenantPerson.user.firstName} ${activeLease.tenantPerson.user.lastName}`,
            email: activeLease.tenantPerson.user.email,
            phone: activeLease.tenantPerson.user.phone,
          }
        : null,
      leaseStart: activeLease?.startDate || null,
      leaseEnd: activeLease?.endDate || null,
      monthlyRent: activeLease ? Number(activeLease.monthlyRent) : null,
    };
  });

  return {
    summary: { total, occupied, available, maintenance },
    occupancyRate: total > 0 ? Math.round((occupied / total) * 10000) / 100 : 0,
    details,
  };
}

/**
 * Reporte detallado de pagos con filtros.
 */
async function getPaymentsReport(tenantId, { startDate, endDate, status, propertyId, page = 1, limit = 50 } = {}) {
  tenantId = Number(tenantId);
  const where = { lease: { tenantId } };

  if (startDate || endDate) {
    where.paymentDate = {};
    if (startDate) where.paymentDate.gte = new Date(startDate);
    if (endDate) where.paymentDate.lte = new Date(endDate);
  }
  if (status) where.status = status;
  if (propertyId) where.lease = { tenantId, propertyId: Number(propertyId) };

  const [payments, total] = await Promise.all([
    prisma.payment.findMany({
      where,
      include: {
        lease: {
          include: {
            property: { select: { id: true, name: true, address: true } },
          },
        },
        user: { select: { id: true, firstName: true, lastName: true, email: true } },
      },
      orderBy: { paymentDate: 'desc' },
      skip: (Number(page) - 1) * Number(limit),
      take: Number(limit),
    }),
    prisma.payment.count({ where }),
  ]);

  const totalAmountAgg = await prisma.payment.aggregate({
    _sum: { amount: true },
    where,
  });

  return {
    payments,
    total,
    page: Number(page),
    limit: Number(limit),
    totalAmount: Number(totalAmountAgg._sum.amount || 0),
  };
}

/**
 * Exportar reporte a PDF.
 */
async function exportReport(tenantId, type, filters = {}) {
  tenantId = Number(tenantId);
  let title = '';
  let bodyHtml = '';

  switch (type) {
    case 'income': {
      title = 'Reporte de Ingresos';
      const data = await getIncomeReport(tenantId, filters);
      bodyHtml = `
        <h2>Resumen</h2>
        <p><strong>Total recaudado:</strong> ${formatCurrency(data.grandTotal)}</p>
        <p><strong>Total pagos:</strong> ${data.totalPayments}</p>
        <h2>Por mes</h2>
        <table>
          <thead><tr><th>Mes</th><th>Total</th><th>Pagos</th></tr></thead>
          <tbody>
            ${data.byMonth.map((m) => `<tr><td>${m.month}</td><td>${formatCurrency(m.total)}</td><td>${m.count}</td></tr>`).join('')}
          </tbody>
        </table>
        <h2>Por propiedad</h2>
        <table>
          <thead><tr><th>Propiedad</th><th>Total</th><th>Pagos</th></tr></thead>
          <tbody>
            ${data.byProperty.map((p) => `<tr><td>${p.name}</td><td>${formatCurrency(p.total)}</td><td>${p.count}</td></tr>`).join('')}
          </tbody>
        </table>
      `;
      break;
    }
    case 'occupancy': {
      title = 'Reporte de Ocupacion';
      const data = await getOccupancyReport(tenantId);
      bodyHtml = `
        <h2>Resumen</h2>
        <p><strong>Total propiedades:</strong> ${data.summary.total}</p>
        <p><strong>Ocupadas:</strong> ${data.summary.occupied}</p>
        <p><strong>Disponibles:</strong> ${data.summary.available}</p>
        <p><strong>Mantenimiento:</strong> ${data.summary.maintenance}</p>
        <p><strong>Tasa de ocupacion:</strong> ${data.occupancyRate}%</p>
        <h2>Detalle</h2>
        <table>
          <thead><tr><th>Propiedad</th><th>Tipo</th><th>Estado</th><th>Inquilino</th><th>Renta</th></tr></thead>
          <tbody>
            ${data.details.map((d) => `<tr>
              <td>${d.name}</td>
              <td>${d.type}</td>
              <td>${d.status}</td>
              <td>${d.tenant ? d.tenant.name : '-'}</td>
              <td>${d.monthlyRent ? formatCurrency(d.monthlyRent) : '-'}</td>
            </tr>`).join('')}
          </tbody>
        </table>
      `;
      break;
    }
    case 'payments': {
      title = 'Reporte de Pagos';
      const data = await getPaymentsReport(tenantId, { ...filters, limit: 1000 });
      bodyHtml = `
        <h2>Resumen</h2>
        <p><strong>Total registros:</strong> ${data.total}</p>
        <p><strong>Monto total:</strong> ${formatCurrency(data.totalAmount)}</p>
        <h2>Detalle de pagos</h2>
        <table>
          <thead><tr><th>Fecha</th><th>Propiedad</th><th>Inquilino</th><th>Monto</th><th>Metodo</th><th>Estado</th></tr></thead>
          <tbody>
            ${data.payments.map((p) => `<tr>
              <td>${formatDate(p.paymentDate)}</td>
              <td>${p.lease?.property?.name || '-'}</td>
              <td>${p.user ? `${p.user.firstName} ${p.user.lastName}` : '-'}</td>
              <td>${formatCurrency(Number(p.amount))}</td>
              <td>${p.method}</td>
              <td>${p.status}</td>
            </tr>`).join('')}
          </tbody>
        </table>
      `;
      break;
    }
    default:
      throw { status: 400, message: `Tipo de reporte no soportado: ${type}` };
  }

  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <title>${title}</title>
      <style>
        body { font-family: Arial, sans-serif; padding: 20px; color: #333; }
        h1 { color: #1a237e; border-bottom: 2px solid #1a237e; padding-bottom: 8px; }
        h2 { color: #283593; margin-top: 24px; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 12px; }
        th { background-color: #1a237e; color: #fff; }
        tr:nth-child(even) { background-color: #f5f5f5; }
        .footer { margin-top: 40px; font-size: 10px; color: #888; text-align: center; }
      </style>
    </head>
    <body>
      <h1>${title}</h1>
      <p><em>Generado el ${formatDate(new Date())}</em></p>
      ${bodyHtml}
      <div class="footer">APUS Renta - Reporte generado automaticamente</div>
    </body>
    </html>
  `;

  const pdfBuffer = await generatePDF(html);
  return pdfBuffer;
}

module.exports = {
  getDashboard,
  getIncomeReport,
  getOccupancyReport,
  getPaymentsReport,
  exportReport,
};
