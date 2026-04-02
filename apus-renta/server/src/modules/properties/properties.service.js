const prisma = require('../../config/database');

async function list(tenantId, { page = 1, limit = 10, status, type, search } = {}) {
  const skip = (Number(page) - 1) * Number(limit);
  const take = Number(limit);
  const where = { tenantId: Number(tenantId) };
  if (status) where.status = status;
  if (type) where.type = type;
  if (search) {
    where.OR = [
      { name: { contains: search } },
      { address: { contains: search } },
    ];
  }

  const [properties, total] = await Promise.all([
    prisma.property.findMany({
      where, skip, take,
      include: { _count: { select: { leases: true } } },
      orderBy: { createdAt: 'desc' },
    }),
    prisma.property.count({ where }),
  ]);
  return { properties, total, page: Number(page), limit: take };
}

async function getById(id, tenantId) {
  const property = await prisma.property.findFirst({
    where: { id: Number(id), tenantId: Number(tenantId) },
    include: {
      leases: {
        include: {
          tenantPerson: {
            include: { user: { select: { id: true, firstName: true, lastName: true, email: true } } },
          },
        },
      },
      utilityBills: { orderBy: { createdAt: 'desc' }, take: 10 },
    },
  });
  if (!property) throw { status: 404, message: 'Propiedad no encontrada' };
  return property;
}

async function create(data, tenantId, files = []) {
  const photos = files.map((f) => f.path.replace(/\\/g, '/'));
  return prisma.property.create({
    data: {
      tenantId: Number(tenantId),
      name: data.name,
      type: data.type,
      address: data.address,
      city: data.city,
      state: data.state || 'Cesar',
      country: data.country || 'Colombia',
      area: data.area ? parseFloat(data.area) : null,
      bedrooms: data.bedrooms ? parseInt(data.bedrooms) : null,
      bathrooms: data.bathrooms ? parseInt(data.bathrooms) : null,
      description: data.description || null,
      status: data.status || 'DISPONIBLE',
      photos: photos.length > 0 ? photos : [],
      monthlyRent: parseFloat(data.monthlyRent) || 0,
    },
  });
}

async function update(id, data, tenantId, files = []) {
  const existing = await prisma.property.findFirst({
    where: { id: Number(id), tenantId: Number(tenantId) },
  });
  if (!existing) throw { status: 404, message: 'Propiedad no encontrada' };

  const updateData = {};
  if (data.name !== undefined) updateData.name = data.name;
  if (data.type !== undefined) updateData.type = data.type;
  if (data.address !== undefined) updateData.address = data.address;
  if (data.city !== undefined) updateData.city = data.city;
  if (data.state !== undefined) updateData.state = data.state;
  if (data.area !== undefined) updateData.area = parseFloat(data.area);
  if (data.bedrooms !== undefined) updateData.bedrooms = parseInt(data.bedrooms);
  if (data.bathrooms !== undefined) updateData.bathrooms = parseInt(data.bathrooms);
  if (data.description !== undefined) updateData.description = data.description;
  if (data.status !== undefined) updateData.status = data.status;
  if (data.monthlyRent !== undefined) updateData.monthlyRent = parseFloat(data.monthlyRent);

  if (files && files.length > 0) {
    const newPhotos = files.map((f) => f.path.replace(/\\/g, '/'));
    const existingPhotos = Array.isArray(existing.photos) ? existing.photos : [];
    updateData.photos = [...existingPhotos, ...newPhotos];
  }

  return prisma.property.update({ where: { id: Number(id) }, data: updateData });
}

async function remove(id, tenantId) {
  const existing = await prisma.property.findFirst({
    where: { id: Number(id), tenantId: Number(tenantId) },
    include: { _count: { select: { leases: true } } },
  });
  if (!existing) throw { status: 404, message: 'Propiedad no encontrada' };
  if (existing._count.leases > 0) throw { status: 400, message: 'No se puede eliminar, tiene contratos asociados' };
  await prisma.property.delete({ where: { id: Number(id) } });
  return { message: 'Propiedad eliminada' };
}

async function updateStatus(id, status, tenantId) {
  const existing = await prisma.property.findFirst({
    where: { id: Number(id), tenantId: Number(tenantId) },
  });
  if (!existing) throw { status: 404, message: 'Propiedad no encontrada' };
  return prisma.property.update({ where: { id: Number(id) }, data: { status } });
}

module.exports = { list, getById, create, update, remove, updateStatus };
