const cron = require('node-cron');
const prisma = require('../config/database');

/**
 * Cron job de alertas automaticas.
 * Se ejecuta diariamente a las 8:00 AM.
 *
 * Verifica:
 * 1. Contratos por vencer en 30, 60, 90 dias
 * 2. Pagos vencidos (arriendo del mes actual no pagado)
 * 3. Servicios publicos con fecha de vencimiento pasada
 * 4. PQRS en estado RADICADA por mas de 3 dias sin respuesta
 */

async function checkLeaseExpiry() {
  const now = new Date();
  const thresholds = [30, 60, 90];

  for (const days of thresholds) {
    const targetDate = new Date(now);
    targetDate.setDate(targetDate.getDate() + days);

    // Buscar contratos que vencen exactamente en N dias (rango de 1 dia)
    const startOfDay = new Date(targetDate);
    startOfDay.setHours(0, 0, 0, 0);
    const endOfDay = new Date(targetDate);
    endOfDay.setHours(23, 59, 59, 999);

    const leases = await prisma.lease.findMany({
      where: {
        endDate: {
          gte: startOfDay,
          lte: endOfDay,
        },
        status: 'ACTIVO',
      },
      include: {
        property: { select: { name: true } },
        tenantPerson: {
          include: {
            user: { select: { firstName: true, lastName: true, email: true } },
          },
        },
      },
    });

    for (const lease of leases) {
      const tenantName = lease.tenantPerson?.user
        ? `${lease.tenantPerson.user.firstName} ${lease.tenantPerson.user.lastName}`
        : 'Arrendatario';

      await prisma.alert.create({
        data: {
          tenantId: lease.tenantId,
          type: 'VENCIMIENTO_CONTRATO',
          message: `El contrato de ${tenantName} para la propiedad "${lease.property?.name || lease.propertyId}" vence en ${days} dias (${lease.endDate.toISOString().split('T')[0]}).`,
          channel: 'ALL',
          status: 'PENDIENTE',
          referenceId: lease.id,
          referenceType: 'LEASE',
        },
      });

      console.log(`[ALERT CRON] Alerta VENCIMIENTO_CONTRATO creada - Lease ${lease.id} vence en ${days} dias`);
    }
  }
}

async function checkOverduePayments() {
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth() + 1;
  const currentPeriod = `${currentYear}-${String(currentMonth).padStart(2, '0')}`;

  // Buscar contratos activos
  const activeLeases = await prisma.lease.findMany({
    where: { status: 'ACTIVO' },
    include: {
      property: { select: { name: true } },
    },
  });

  for (const lease of activeLeases) {
    // Verificar si existe un pago para el periodo actual
    const payment = await prisma.payment.findFirst({
      where: {
        leaseId: lease.id,
        period: currentPeriod,
        status: { in: ['PAGADO', 'VERIFICADO'] },
      },
    });

    if (!payment) {
      // Verificar que no exista ya una alerta para este periodo
      const existingAlert = await prisma.alert.findFirst({
        where: {
          tenantId: lease.tenantId,
          type: 'VENCIMIENTO_PAGO',
          referenceId: lease.id,
          referenceType: 'LEASE',
          message: { contains: currentPeriod },
          createdAt: {
            gte: new Date(currentYear, currentMonth - 1, 1),
          },
        },
      });

      if (!existingAlert) {
        await prisma.alert.create({
          data: {
            tenantId: lease.tenantId,
            type: 'VENCIMIENTO_PAGO',
            message: `No se ha registrado pago del arriendo para el periodo ${currentPeriod} de la propiedad "${lease.property?.name || lease.propertyId}". Monto esperado: $${lease.monthlyRent}.`,
            channel: 'ALL',
            status: 'PENDIENTE',
            referenceId: lease.id,
            referenceType: 'LEASE',
          },
        });

        console.log(`[ALERT CRON] Alerta VENCIMIENTO_PAGO creada - Lease ${lease.id}, periodo ${currentPeriod}`);
      }
    }
  }
}

async function checkOverdueUtilities() {
  const now = new Date();

  const overdueUtilities = await prisma.utilityBill.findMany({
    where: {
      status: 'PENDIENTE',
      dueDate: { lt: now },
    },
    include: {
      property: { select: { name: true } },
    },
  });

  for (const utility of overdueUtilities) {
    // Verificar que no exista alerta reciente para este servicio
    const existingAlert = await prisma.alert.findFirst({
      where: {
        tenantId: utility.tenantId,
        type: 'VENCIMIENTO_SERVICIO',
        referenceId: utility.id,
        referenceType: 'UTILITY',
      },
    });

    if (!existingAlert) {
      await prisma.alert.create({
        data: {
          tenantId: utility.tenantId,
          type: 'VENCIMIENTO_SERVICIO',
          message: `El pago de ${utility.type} para la propiedad "${utility.property?.name || utility.propertyId}" periodo ${utility.period} esta vencido desde ${utility.dueDate.toISOString().split('T')[0]}. Monto: $${utility.amount}.`,
          channel: 'ALL',
          status: 'PENDIENTE',
          referenceId: utility.id,
          referenceType: 'UTILITY',
        },
      });

      // Actualizar estado del servicio a VENCIDO
      await prisma.utilityBill.update({
        where: { id: utility.id },
        data: { status: 'VENCIDO' },
      });

      console.log(`[ALERT CRON] Alerta VENCIMIENTO_SERVICIO creada - Utility ${utility.id} (${utility.type})`);
    }
  }
}

async function checkUnansweredPqrs() {
  const threeDaysAgo = new Date();
  threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);

  const unansweredPqrs = await prisma.pQRS.findMany({
    where: {
      status: 'RADICADA',
      createdAt: { lt: threeDaysAgo },
    },
    include: {
      property: { select: { name: true } },
      user: { select: { firstName: true, lastName: true } },
    },
  });

  for (const pqrs of unansweredPqrs) {
    // Verificar que no exista alerta reciente para esta PQRS
    const existingAlert = await prisma.alert.findFirst({
      where: {
        tenantId: pqrs.tenantId,
        type: 'PQRS_SIN_RESPUESTA',
        referenceId: pqrs.id,
        referenceType: 'PQRS',
      },
    });

    if (!existingAlert) {
      const userName = pqrs.user
        ? `${pqrs.user.firstName} ${pqrs.user.lastName}`
        : 'Usuario';

      await prisma.alert.create({
        data: {
          tenantId: pqrs.tenantId,
          type: 'PQRS_SIN_RESPUESTA',
          message: `La ${pqrs.type} "${pqrs.subject}" de ${userName} para la propiedad "${pqrs.property?.name || pqrs.propertyId}" lleva mas de 3 dias sin respuesta.`,
          channel: 'ALL',
          status: 'PENDIENTE',
          referenceId: pqrs.id,
          referenceType: 'PQRS',
        },
      });

      console.log(`[ALERT CRON] Alerta PQRS_SIN_RESPUESTA creada - PQRS ${pqrs.id}`);
    }
  }
}

async function runAlertChecks() {
  console.log(`[ALERT CRON] Iniciando verificacion de alertas - ${new Date().toISOString()}`);

  try {
    await checkLeaseExpiry();
    await checkOverduePayments();
    await checkOverdueUtilities();
    await checkUnansweredPqrs();
    console.log(`[ALERT CRON] Verificacion completada - ${new Date().toISOString()}`);
  } catch (err) {
    console.error(`[ALERT CRON] Error durante verificacion de alertas:`, err);
  }

  // TODO: Implementar envio real de notificaciones por email/whatsapp
  // para las alertas creadas con status PENDIENTE
}

/**
 * Inicia el cron job de alertas. Se ejecuta diariamente a las 8:00 AM.
 */
function start() {
  cron.schedule('0 8 * * *', () => {
    runAlertChecks();
  });

  console.log('[ALERT CRON] Cron job de alertas programado - Ejecucion diaria a las 8:00 AM');
}

module.exports = {
  start,
  runAlertChecks,
};
