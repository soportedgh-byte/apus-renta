const path = require('path');
const fs = require('fs');
const prisma = require('../../config/database');
const { generatePDF } = require('../../utils/pdf');
const { formatCurrency, formatDate, generateReference } = require('../../utils/helpers');

/**
 * Lista pagos con filtros y paginacion.
 */
async function list(tenantId, userId, role, { page = 1, limit = 10, status, leaseId, startDate, endDate }) {
  const skip = (page - 1) * limit;

  const where = {};

  // Filtrar por contratos del tenant
  where.lease = { tenantId: Number(tenantId) };

  // Si es ARRENDATARIO, solo ve sus propios pagos
  if (role === 'ARRENDATARIO') {
    where.userId = Number(userId);
  }

  if (status) {
    where.status = status;
  }

  if (leaseId) {
    where.leaseId = Number(leaseId);
  }

  if (startDate || endDate) {
    where.paymentDate = {};
    if (startDate) where.paymentDate.gte = new Date(startDate);
    if (endDate) where.paymentDate.lte = new Date(endDate);
  }

  const [data, total] = await Promise.all([
    prisma.payment.findMany({
      where,
      skip,
      take: Number(limit),
      orderBy: { createdAt: 'desc' },
      include: {
        lease: {
          include: { property: true },
        },
        user: { select: { id: true, firstName: true, lastName: true, email: true } },
      },
    }),
    prisma.payment.count({ where }),
  ]);

  return { data, total, page: Number(page), limit: Number(limit) };
}

/**
 * Obtiene un pago por ID con relaciones completas.
 */
async function getById(id, tenantId) {
  const payment = await prisma.payment.findFirst({
    where: {
      id: Number(id),
      lease: { tenantId: Number(tenantId) },
    },
    include: {
      lease: {
        include: { property: true },
      },
      user: { select: { id: true, firstName: true, lastName: true, email: true, phone: true } },
      paymentReceipt: true,
    },
  });

  if (!payment) {
    throw { status: 404, message: 'Pago no encontrado' };
  }

  return payment;
}

/**
 * Crea un nuevo pago en estado PENDIENTE.
 */
async function create(data, userId, tenantId, file) {
  const { leaseId, amount, paymentDate, method, reference, notes } = data;

  // Verificar que el contrato pertenece al tenant
  const lease = await prisma.lease.findFirst({
    where: { id: Number(leaseId), tenantId: Number(tenantId) },
  });
  if (!lease) {
    throw { status: 404, message: 'Contrato no encontrado o no pertenece a su organizacion' };
  }

  const paymentData = {
    leaseId: Number(leaseId),
    userId: Number(userId),
    tenantId: Number(tenantId),
    amount: parseFloat(amount),
    paymentDate: new Date(paymentDate),
    method,
    reference: reference || generateReference(),
    notes: notes || null,
    status: 'PENDIENTE',
  };

  if (file) {
    paymentData.supportUrl = `/uploads/payments/${file.filename}`;
  }

  const payment = await prisma.payment.create({
    data: paymentData,
    include: {
      lease: { include: { property: true } },
      user: { select: { id: true, firstName: true, lastName: true, email: true } },
    },
  });

  return payment;
}

/**
 * Aprueba un pago, genera recibo PDF y crea registro PaymentReceipt.
 */
async function approve(id, userId, tenantId) {
  const payment = await prisma.payment.findFirst({
    where: {
      id: Number(id),
      lease: { tenantId: Number(tenantId) },
    },
    include: {
      lease: { include: { property: true } },
      user: { select: { id: true, firstName: true, lastName: true, email: true } },
    },
  });

  if (!payment) {
    throw { status: 404, message: 'Pago no encontrado' };
  }

  if (payment.status !== 'PENDIENTE') {
    throw { status: 400, message: 'Solo se pueden aprobar pagos en estado PENDIENTE' };
  }

  // Obtener datos del aprobador
  const approver = await prisma.user.findUnique({
    where: { id: Number(userId) },
    select: { id: true, firstName: true, lastName: true, email: true },
  });

  const now = new Date();

  const updated = await prisma.payment.update({
    where: { id: Number(id) },
    data: {
      status: 'APROBADO',
      approvedBy: Number(userId),
      approvedAt: now,
    },
    include: {
      lease: { include: { property: true } },
      user: { select: { id: true, firstName: true, lastName: true, email: true } },
    },
  });

  // Generar recibo PDF
  const pdfUrl = await generateReceipt({ ...updated, approver, approvedAt: now });

  // Crear registro de recibo
  await prisma.paymentReceipt.create({
    data: {
      paymentId: updated.id,
      pdfUrl,
      generatedAt: now,
    },
  });

  return updated;
}

/**
 * Rechaza un pago con una razon.
 */
async function reject(id, userId, tenantId, reason) {
  const payment = await prisma.payment.findFirst({
    where: {
      id: Number(id),
      lease: { tenantId: Number(tenantId) },
    },
  });

  if (!payment) {
    throw { status: 404, message: 'Pago no encontrado' };
  }

  if (payment.status !== 'PENDIENTE') {
    throw { status: 400, message: 'Solo se pueden rechazar pagos en estado PENDIENTE' };
  }

  const updated = await prisma.payment.update({
    where: { id: Number(id) },
    data: {
      status: 'RECHAZADO',
      rejectionReason: reason,
    },
    include: {
      lease: { include: { property: true } },
      user: { select: { id: true, firstName: true, lastName: true, email: true } },
    },
  });

  return updated;
}

/**
 * Genera un recibo PDF profesional para un pago aprobado.
 */
async function generateReceipt(payment) {
  const property = payment.lease.property;
  const payer = payment.user;
  const approver = payment.approver;

  const html = `
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Segoe UI', Arial, sans-serif; color: #333; font-size: 14px; }
    .container { max-width: 700px; margin: 0 auto; padding: 30px; }
    .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #1B4F72; padding-bottom: 20px; margin-bottom: 25px; }
    .header-left { display: flex; align-items: center; gap: 15px; }
    .logo-placeholder { width: 60px; height: 60px; background: #1B4F72; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: bold; font-size: 12px; text-align: center; }
    .brand-name { font-size: 22px; font-weight: bold; color: #1B4F72; }
    .brand-subtitle { font-size: 11px; color: #666; }
    .receipt-title { text-align: right; }
    .receipt-title h1 { font-size: 20px; color: #1B4F72; margin-bottom: 5px; }
    .receipt-number { font-size: 12px; color: #666; }
    .section { margin-bottom: 20px; }
    .section-title { font-size: 14px; font-weight: bold; color: #1B4F72; margin-bottom: 10px; padding-bottom: 5px; border-bottom: 1px solid #e0e0e0; }
    .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
    .info-item label { font-size: 11px; color: #888; display: block; }
    .info-item span { font-size: 13px; font-weight: 500; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th { background: #1B4F72; color: #fff; padding: 10px 12px; text-align: left; font-size: 12px; text-transform: uppercase; }
    td { padding: 10px 12px; border-bottom: 1px solid #e8e8e8; font-size: 13px; }
    tr:nth-child(even) { background: #f9fafb; }
    .amount-row td { font-weight: bold; font-size: 15px; color: #1B4F72; }
    .status-badge { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .status-aprobado { background: #d4edda; color: #155724; }
    .approval-section { background: #f0f7ff; border: 1px solid #2E86C1; border-radius: 8px; padding: 15px; margin-top: 20px; }
    .approval-section h3 { color: #1B4F72; font-size: 13px; margin-bottom: 8px; }
    .footer { margin-top: 30px; padding-top: 15px; border-top: 2px solid #1B4F72; text-align: center; font-size: 11px; color: #888; }
    .footer strong { color: #1B4F72; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="header-left">
        <div class="logo-placeholder">APUS<br>Renta</div>
        <div>
          <div class="brand-name">APUS Renta</div>
          <div class="brand-subtitle">Gestion de Arrendamientos</div>
        </div>
      </div>
      <div class="receipt-title">
        <h1>Comprobante de Pago</h1>
        <div class="receipt-number">Ref: ${payment.reference || 'N/A'}</div>
        <div class="receipt-number">Fecha: ${formatDate(new Date())}</div>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Informacion del Inmueble</div>
      <div class="info-grid">
        <div class="info-item">
          <label>Propiedad</label>
          <span>${property.name}</span>
        </div>
        <div class="info-item">
          <label>Direccion</label>
          <span>${property.address}${property.city ? ', ' + property.city : ''}</span>
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Detalle del Pago</div>
      <table>
        <thead>
          <tr>
            <th>Concepto</th>
            <th>Detalle</th>
          </tr>
        </thead>
        <tbody>
          <tr class="amount-row">
            <td>Monto</td>
            <td>${formatCurrency(payment.amount)}</td>
          </tr>
          <tr>
            <td>Metodo de Pago</td>
            <td>${payment.method}</td>
          </tr>
          <tr>
            <td>Fecha de Pago</td>
            <td>${formatDate(payment.paymentDate)}</td>
          </tr>
          <tr>
            <td>Referencia</td>
            <td>${payment.reference || 'N/A'}</td>
          </tr>
          <tr>
            <td>Estado</td>
            <td><span class="status-badge status-aprobado">Aprobado</span></td>
          </tr>
          ${payment.notes ? `<tr><td>Notas</td><td>${payment.notes}</td></tr>` : ''}
        </tbody>
      </table>
    </div>

    <div class="approval-section">
      <h3>Informacion de Aprobacion</h3>
      <div class="info-grid">
        <div class="info-item">
          <label>Aprobado por</label>
          <span>${approver ? approver.firstName + ' ' + approver.lastName : 'N/A'}</span>
        </div>
        <div class="info-item">
          <label>Fecha de Aprobacion</label>
          <span>${formatDate(payment.approvedAt || new Date())}</span>
        </div>
      </div>
    </div>

    <div class="footer">
      <p><strong>APUS Renta</strong> - Comprobante generado automaticamente</p>
      <p>Pagado por: ${payer ? payer.firstName + ' ' + payer.lastName : 'N/A'} (${payer ? payer.email : 'N/A'})</p>
      <p>Este documento es un comprobante valido de pago.</p>
    </div>
  </div>
</body>
</html>`;

  const pdfBuffer = await generatePDF(html);

  // Guardar el PDF en disco
  const receiptsDir = path.join(__dirname, '../../../uploads/receipts');
  if (!fs.existsSync(receiptsDir)) {
    fs.mkdirSync(receiptsDir, { recursive: true });
  }

  const filename = `recibo-${payment.id}-${Date.now()}.pdf`;
  const filePath = path.join(receiptsDir, filename);
  fs.writeFileSync(filePath, pdfBuffer);

  return `/uploads/receipts/${filename}`;
}

/**
 * Obtiene la URL del recibo PDF de un pago.
 */
async function getReceipt(paymentId) {
  const receipt = await prisma.paymentReceipt.findFirst({
    where: { paymentId: Number(paymentId) },
  });

  if (!receipt) {
    throw { status: 404, message: 'Recibo no encontrado. El pago debe estar aprobado para generar recibo.' };
  }

  return receipt;
}

module.exports = {
  list,
  getById,
  create,
  approve,
  reject,
  generateReceipt,
  getReceipt,
};
