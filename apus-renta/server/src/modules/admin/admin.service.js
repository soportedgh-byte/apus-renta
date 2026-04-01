const bcrypt = require('bcryptjs');
const prisma = require('../../config/database');
const { slugify } = require('../../utils/helpers');

const SALT_ROUNDS = 12;

const PLAN_CONFIG = {
  FREE: { price: 0, maxProperties: 2, features: ['Gestion basica', 'Email'] },
  BASIC: { price: 49900, maxProperties: 5, features: ['Gestion basica', 'Email', 'Firma electronica basica'] },
  PRO: { price: 99900, maxProperties: 20, features: ['Todo BASIC', 'WhatsApp', 'Reportes avanzados', 'Firma electronica'] },
  ENTERPRISE: { price: 199900, maxProperties: 999, features: ['Todo PRO', 'Soporte prioritario', 'Propiedades ilimitadas', 'API personalizada'] },
};

async function getDashboard() {
  const [totalTenants, activeTenants, suspendedTenants] = await Promise.all([
    prisma.tenant.count(),
    prisma.tenant.count({ where: { status: 'ACTIVE' } }),
    prisma.tenant.count({ where: { status: 'SUSPENDED' } }),
  ]);

  const byPlan = await prisma.tenant.groupBy({
    by: ['plan'],
    _count: { id: true },
  });

  const planDistribution = byPlan.map(p => ({
    plan: p.plan,
    count: p._count.id,
    estimatedRevenue: p._count.id * (PLAN_CONFIG[p.plan]?.price || 0),
  }));

  const totalEstimatedRevenue = planDistribution.reduce((sum, p) => sum + p.estimatedRevenue, 0);

  const recentTenants = await prisma.tenant.findMany({
    orderBy: { createdAt: 'desc' },
    take: 10,
    include: {
      users: {
        where: { role: 'PROPIETARIO' },
        take: 1,
        select: { id: true, firstName: true, lastName: true, email: true },
      },
      _count: { select: { properties: true, users: true } },
    },
  });

  return {
    totalTenants,
    activeTenants,
    suspendedTenants,
    cancelledTenants: totalTenants - activeTenants - suspendedTenants,
    planDistribution,
    totalEstimatedRevenue,
    recentTenants,
  };
}

async function listTenants({ page = 1, limit = 10, plan, status, search } = {}) {
  const skip = (Number(page) - 1) * Number(limit);
  const take = Number(limit);
  const where = {};
  if (plan) where.plan = plan;
  if (status) where.status = status;
  if (search) {
    where.OR = [
      { name: { contains: search } },
      { slug: { contains: search } },
    ];
  }

  const [tenants, total] = await Promise.all([
    prisma.tenant.findMany({
      where, skip, take,
      include: {
        users: {
          where: { role: 'PROPIETARIO' },
          take: 1,
          select: { id: true, firstName: true, lastName: true, email: true },
        },
        _count: { select: { properties: true, users: true } },
      },
      orderBy: { createdAt: 'desc' },
    }),
    prisma.tenant.count({ where }),
  ]);

  return { tenants, total, page: Number(page), limit: take };
}

async function createTenant({ name, email, password, firstName, lastName, plan, maxProperties }) {
  const slug = slugify(name) + '-' + Date.now().toString(36);

  const existingEmail = await prisma.user.findUnique({ where: { email } });
  if (existingEmail) throw { status: 409, message: 'El email ya esta registrado' };

  const existingSlug = await prisma.tenant.findUnique({ where: { slug } });
  if (existingSlug) throw { status: 409, message: 'El nombre de organizacion ya existe' };

  const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);
  const planConfig = PLAN_CONFIG[plan || 'FREE'];

  const result = await prisma.$transaction(async (tx) => {
    const tenant = await tx.tenant.create({
      data: {
        name,
        slug,
        plan: plan || 'FREE',
        status: 'ACTIVE',
        maxProperties: maxProperties || planConfig.maxProperties,
        configJson: {
          branding: { primaryColor: '#1B4F72', accentColor: '#2E86C1' },
          alerts: {
            paymentReminder: { enabled: true, daysBefore: [5, 3, 1], channels: ['EMAIL', 'PUSH'] },
            contractExpiry: { enabled: true, daysBefore: [90, 60, 30], channels: ['EMAIL'] },
          },
        },
      },
    });

    const owner = await tx.user.create({
      data: {
        tenantId: tenant.id,
        email,
        passwordHash: hashedPassword,
        firstName: firstName || 'Propietario',
        lastName: lastName || name,
        role: 'PROPIETARIO',
        status: 'ACTIVE',
      },
    });

    const { passwordHash: _, ...ownerData } = owner;
    return { tenant, owner: ownerData };
  });

  return result;
}

async function getTenant(id) {
  const tenant = await prisma.tenant.findUnique({
    where: { id: Number(id) },
    include: {
      users: {
        where: { role: 'PROPIETARIO' },
        take: 1,
        select: { id: true, firstName: true, lastName: true, email: true, phone: true },
      },
      _count: { select: { properties: true, users: true, leases: true } },
    },
  });
  if (!tenant) throw { status: 404, message: 'Tenant no encontrado' };
  return tenant;
}

async function updateTenant(id, data) {
  const existing = await prisma.tenant.findUnique({ where: { id: Number(id) } });
  if (!existing) throw { status: 404, message: 'Tenant no encontrado' };

  const updateData = {};
  if (data.name !== undefined) updateData.name = data.name;
  if (data.plan !== undefined) updateData.plan = data.plan;
  if (data.status !== undefined) updateData.status = data.status;
  if (data.maxProperties !== undefined) updateData.maxProperties = Number(data.maxProperties);
  if (data.logo !== undefined) updateData.logo = data.logo;

  return prisma.tenant.update({ where: { id: Number(id) }, data: updateData });
}

async function deleteTenant(id) {
  const existing = await prisma.tenant.findUnique({ where: { id: Number(id) } });
  if (!existing) throw { status: 404, message: 'Tenant no encontrado' };

  return prisma.tenant.update({
    where: { id: Number(id) },
    data: { status: 'CANCELLED' },
  });
}

async function getTenantStats(id) {
  const tenant = await prisma.tenant.findUnique({ where: { id: Number(id) } });
  if (!tenant) throw { status: 404, message: 'Tenant no encontrado' };

  const tid = Number(id);
  const now = new Date();
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);

  const [properties, users, activeLeases, paymentsThisMonth] = await Promise.all([
    prisma.property.count({ where: { tenantId: tid } }),
    prisma.user.count({ where: { tenantId: tid, role: 'ARRENDATARIO' } }),
    prisma.lease.count({ where: { tenantId: tid, status: 'ACTIVO' } }),
    prisma.payment.count({
      where: { tenantId: tid, status: 'APROBADO', paymentDate: { gte: startOfMonth } },
    }),
  ]);

  return { tenantId: tid, tenantName: tenant.name, properties, tenants: users, activeLeases, paymentsThisMonth };
}

function getPlans() {
  return Object.entries(PLAN_CONFIG).map(([key, val]) => ({
    id: key,
    name: key,
    ...val,
  }));
}

function updatePlan(planId, data) {
  if (!PLAN_CONFIG[planId]) throw { status: 404, message: 'Plan no encontrado' };
  // In production this would update a DB table. For now, return the config.
  return { id: planId, ...PLAN_CONFIG[planId], ...data };
}

module.exports = {
  getDashboard, listTenants, createTenant, getTenant, updateTenant,
  deleteTenant, getTenantStats, getPlans, updatePlan,
};
