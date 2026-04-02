const bcrypt = require('bcryptjs');
const prisma = require('../../config/database');

const SALT_ROUNDS = 12;

/**
 * Listar arrendatarios con filtros y paginacion.
 */
async function list(tenantId, { page = 1, limit = 10, search } = {}) {
  const skip = (page - 1) * limit;

  const where = {
    role: 'ARRENDATARIO',
    tenantId: Number(tenantId),
  };

  if (search) {
    where.OR = [
      { firstName: { contains: search } },
      { lastName: { contains: search } },
      { email: { contains: search } },
    ];
  }

  const [users, total] = await Promise.all([
    prisma.user.findMany({
      where,
      skip,
      take: Number(limit),
      select: {
        id: true,
        email: true,
        firstName: true,
        lastName: true,
        phone: true,
        status: true,
        createdAt: true,
        tenantPerson: {
          include: {
            leases: {
              where: { status: 'ACTIVO' },
              take: 1,
              include: { property: { select: { id: true, name: true, address: true } } },
              orderBy: { startDate: 'desc' },
            },
          },
        },
      },
      orderBy: { createdAt: 'desc' },
    }),
    prisma.user.count({ where }),
  ]);

  return { tenants: users, total, page: Number(page), limit: Number(limit) };
}

/**
 * Obtener arrendatario por ID con relaciones.
 */
async function getById(id, tenantId) {
  const user = await prisma.user.findFirst({
    where: { id: Number(id), tenantId: Number(tenantId), role: 'ARRENDATARIO' },
    select: {
      id: true,
      email: true,
      firstName: true,
      lastName: true,
      phone: true,
      status: true,
      createdAt: true,
      updatedAt: true,
      tenantPerson: {
        include: {
          leases: {
            include: {
              property: { select: { id: true, name: true, address: true } },
              payments: { orderBy: { createdAt: 'desc' }, take: 10 },
            },
            orderBy: { startDate: 'desc' },
          },
        },
      },
    },
  });

  if (!user) {
    throw { status: 404, message: 'Arrendatario no encontrado' };
  }

  return user;
}

/**
 * Crear un nuevo arrendatario (User + TenantPerson) en transaccion.
 */
async function create(data, tenantId) {
  const { email, password, firstName, lastName, documentType, documentNumber, phone, emergencyContactName, emergencyContactPhone } = data;

  // Verificar si el email ya existe
  const existing = await prisma.user.findUnique({ where: { email } });
  if (existing) {
    throw { status: 409, message: 'El correo electronico ya esta registrado' };
  }

  const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);

  const result = await prisma.$transaction(async (tx) => {
    const user = await tx.user.create({
      data: {
        email,
        passwordHash: hashedPassword,
        firstName,
        lastName,
        phone,
        role: 'ARRENDATARIO',
        tenantId: Number(tenantId),
      },
    });

    const tenantPerson = await tx.tenantPerson.create({
      data: {
        userId: user.id,
        documentType,
        documentNumber,
        emergencyContactName,
        emergencyContactPhone,
      },
    });

    const { passwordHash: _, ...userWithoutPassword } = user;
    return { ...userWithoutPassword, tenantPerson };
  });

  return result;
}

/**
 * Actualizar arrendatario (User + TenantPerson) en transaccion.
 */
async function update(id, data, tenantId) {
  const existingUser = await prisma.user.findUnique({
    where: { id: Number(id) },
    include: { tenantPerson: true },
  });

  if (!existingUser) {
    throw { status: 404, message: 'Arrendatario no encontrado' };
  }

  const { email, password, firstName, lastName, phone, documentType, documentNumber, emergencyContactName, emergencyContactPhone, notes } = data;

  const result = await prisma.$transaction(async (tx) => {
    // Actualizar datos del usuario
    const userData = {};
    if (email !== undefined) userData.email = email;
    if (firstName !== undefined) userData.firstName = firstName;
    if (lastName !== undefined) userData.lastName = lastName;
    if (phone !== undefined) userData.phone = phone;
    if (password) {
      userData.passwordHash = await bcrypt.hash(password, SALT_ROUNDS);
    }

    const user = await tx.user.update({
      where: { id: Number(id) },
      data: userData,
    });

    // Actualizar datos de TenantPerson
    const tenantPersonData = {};
    if (documentType !== undefined) tenantPersonData.documentType = documentType;
    if (documentNumber !== undefined) tenantPersonData.documentNumber = documentNumber;
    if (emergencyContactName !== undefined) tenantPersonData.emergencyContactName = emergencyContactName;
    if (emergencyContactPhone !== undefined) tenantPersonData.emergencyContactPhone = emergencyContactPhone;
    if (notes !== undefined) tenantPersonData.notes = notes;

    let tenantPerson = existingUser.tenantPerson;
    if (Object.keys(tenantPersonData).length > 0 && tenantPerson) {
      tenantPerson = await tx.tenantPerson.update({
        where: { id: tenantPerson.id },
        data: tenantPersonData,
      });
    }

    const { passwordHash: _, ...userWithoutPassword } = user;
    return { ...userWithoutPassword, tenantPerson };
  });

  return result;
}

/**
 * Hard delete: eliminar arrendatario y sus relaciones.
 */
async function remove(id, tenantId) {
  const existing = await prisma.user.findFirst({
    where: { id: Number(id), tenantId: Number(tenantId), role: 'ARRENDATARIO' },
    include: { tenantPerson: true },
  });

  if (!existing) {
    throw { status: 404, message: 'Arrendatario no encontrado' };
  }

  // Delete TenantPerson first (if exists), then User
  await prisma.$transaction(async (tx) => {
    if (existing.tenantPerson) {
      // Delete leases associated with this tenant person first
      await tx.lease.deleteMany({ where: { tenantPersonId: existing.tenantPerson.id } });
      await tx.tenantPerson.delete({ where: { id: existing.tenantPerson.id } });
    }
    // Delete payments by this user
    await tx.payment.deleteMany({ where: { userId: Number(id) } });
    // Delete PQRS by this user
    await tx.pQRS.deleteMany({ where: { userId: Number(id) } });
    // Delete audit logs by this user
    await tx.auditLog.deleteMany({ where: { userId: Number(id) } });
    // Finally delete the user
    await tx.user.delete({ where: { id: Number(id) } });
  });

  return { message: 'Arrendatario eliminado correctamente' };
}

module.exports = {
  list,
  getById,
  create,
  update,
  remove,
};
