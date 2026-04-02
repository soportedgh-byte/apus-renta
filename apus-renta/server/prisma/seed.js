const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcryptjs');
const prisma = new PrismaClient();

async function main() {
  console.log('Seeding database...');

  // 1. Create default tenant
  const tenant = await prisma.tenant.upsert({
    where: { slug: 'apus-renta-valledupar' },
    update: {},
    create: {
      name: 'APUS Renta - Valledupar',
      slug: 'apus-renta-valledupar',
      plan: 'PRO',
      status: 'ACTIVE',
      maxProperties: 10,
      configJson: {
        alerts: {
          paymentReminder: { enabled: true, daysBefore: [5, 3, 1], channels: ['EMAIL', 'PUSH'] },
          contractExpiry: { enabled: true, daysBefore: [90, 60, 30], channels: ['EMAIL', 'WHATSAPP'] },
          utilityDue: { enabled: true, daysBefore: [5, 3, 1], channels: ['EMAIL', 'PUSH'] },
          pqrsNoResponse: { enabled: true, daysAfter: 3, channels: ['PUSH'] }
        },
        branding: { primaryColor: '#1B4F72', accentColor: '#2E86C1' }
      }
    }
  });

  // 2. Create admin user (propietario)
  const passwordHash = await bcrypt.hash('Admin123!', 12);
  const admin = await prisma.user.upsert({
    where: { email: 'admin@apusrenta.com' },
    update: {},
    create: {
      tenantId: tenant.id,
      email: 'admin@apusrenta.com',
      passwordHash,
      firstName: 'Gustavo',
      lastName: 'Castillo',
      role: 'PROPIETARIO',
      status: 'ACTIVE',
      phone: '+573001234567'
    }
  });

  // 3. Create encargado user
  const encargadoHash = await bcrypt.hash('Encargado123!', 12);
  const encargado = await prisma.user.upsert({
    where: { email: 'encargado@apusrenta.com' },
    update: {},
    create: {
      tenantId: tenant.id,
      email: 'encargado@apusrenta.com',
      passwordHash: encargadoHash,
      firstName: 'Carlos',
      lastName: 'Perez',
      role: 'ENCARGADO',
      status: 'ACTIVE',
      phone: '+573009876543'
    }
  });

  // 4. Create 5 properties (use create in loop - IDs are auto-increment)
  const propertiesData = [
    {
      name: 'Casa Principal',
      type: 'CASA',
      address: 'Diagonal 18D 21 33',
      city: 'Valledupar',
      state: 'Cesar',
      area: 180.00,
      bedrooms: 4,
      bathrooms: 3,
      description: 'Casa principal de la propiedad en Barrio Los Caciques',
      status: 'OCUPADO',
      monthlyRent: 1500000.00,
      photos: []
    },
    {
      name: 'Apartamento 101',
      type: 'APARTAMENTO',
      address: 'Diagonal 18D 21 33 - Apto 101',
      city: 'Valledupar',
      state: 'Cesar',
      area: 55.00,
      bedrooms: 2,
      bathrooms: 1,
      description: 'Apartamento primer piso, patio trasero',
      status: 'OCUPADO',
      monthlyRent: 800000.00,
      photos: []
    },
    {
      name: 'Apartamento 102',
      type: 'APARTAMENTO',
      address: 'Diagonal 18D 21 33 - Apto 102',
      city: 'Valledupar',
      state: 'Cesar',
      area: 55.00,
      bedrooms: 2,
      bathrooms: 1,
      description: 'Apartamento primer piso',
      status: 'DISPONIBLE',
      monthlyRent: 800000.00,
      photos: []
    },
    {
      name: 'Apartamento 201',
      type: 'APARTAMENTO',
      address: 'Diagonal 18D 21 33 - Apto 201',
      city: 'Valledupar',
      state: 'Cesar',
      area: 50.00,
      bedrooms: 1,
      bathrooms: 1,
      description: 'Apartamento segundo piso',
      status: 'OCUPADO',
      monthlyRent: 700000.00,
      photos: []
    },
    {
      name: 'Apartamento 202',
      type: 'APARTAMENTO',
      address: 'Diagonal 18D 21 33 - Apto 202',
      city: 'Valledupar',
      state: 'Cesar',
      area: 50.00,
      bedrooms: 1,
      bathrooms: 1,
      description: 'Apartamento segundo piso',
      status: 'MANTENIMIENTO',
      monthlyRent: 700000.00,
      photos: []
    }
  ];

  const properties = [];
  for (const prop of propertiesData) {
    const created = await prisma.property.create({
      data: { tenantId: tenant.id, ...prop }
    });
    properties.push(created);
  }

  // 5. Create sample tenants (arrendatarios)
  const tenantUsersData = [
    { email: 'maria.garcia@email.com', firstName: 'Maria', lastName: 'Garcia', phone: '+573001111111', doc: { type: 'CC', number: '1065111222' } },
    { email: 'pedro.martinez@email.com', firstName: 'Pedro', lastName: 'Martinez', phone: '+573002222222', doc: { type: 'CC', number: '1065333444' } },
    { email: 'ana.lopez@email.com', firstName: 'Ana', lastName: 'Lopez', phone: '+573003333333', doc: { type: 'CC', number: '1065555666' } }
  ];

  const arrendatarioHash = await bcrypt.hash('Tenant123!', 12);

  for (const t of tenantUsersData) {
    const user = await prisma.user.upsert({
      where: { email: t.email },
      update: {},
      create: {
        tenantId: tenant.id,
        email: t.email,
        passwordHash: arrendatarioHash,
        firstName: t.firstName,
        lastName: t.lastName,
        role: 'ARRENDATARIO',
        status: 'ACTIVE',
        phone: t.phone
      }
    });

    await prisma.tenantPerson.upsert({
      where: { userId: user.id },
      update: {},
      create: {
        userId: user.id,
        documentType: t.doc.type,
        documentNumber: t.doc.number,
        phone: t.phone,
        emergencyContactName: 'Contacto de Emergencia',
        emergencyContactPhone: '+573009999999'
      }
    });
  }

  // 6. Create SUPER_ADMIN user
  const superAdminHash = await bcrypt.hash('SuperAdmin123!', 12);
  await prisma.user.upsert({
    where: { email: 'superadmin@apusrenta.com' },
    update: {},
    create: {
      tenantId: tenant.id,
      email: 'superadmin@apusrenta.com',
      passwordHash: superAdminHash,
      firstName: 'APUS',
      lastName: 'Admin',
      role: 'SUPER_ADMIN',
      status: 'ACTIVE',
      phone: '+573000000000',
    },
  });

  console.log('Seed completed!');
  console.log('');
  console.log('Credenciales de acceso:');
  console.log('   Super Admin: superadmin@apusrenta.com / SuperAdmin123!');
  console.log('   Propietario: admin@apusrenta.com / Admin123!');
  console.log('   Encargado:   encargado@apusrenta.com / Encargado123!');
  console.log('   Inquilinos:  maria.garcia@email.com / Tenant123!');
  console.log('                pedro.martinez@email.com / Tenant123!');
  console.log('                ana.lopez@email.com / Tenant123!');
}

main()
  .catch(e => { console.error(e); process.exit(1); })
  .finally(() => prisma.$disconnect());
