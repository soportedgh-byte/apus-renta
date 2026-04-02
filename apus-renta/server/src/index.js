require('dotenv').config();

const express = require('express');
const path = require('path');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');

const logger = require('./config/logger');
const prisma = require('./config/database');

// Import module routes
const authRoutes = require('./modules/auth/auth.routes');
const tenantsRoutes = require('./modules/tenants/tenants.routes');
const propertiesRoutes = require('./modules/properties/properties.routes');
const leasesRoutes = require('./modules/leases/leases.routes');
const paymentsRoutes = require('./modules/payments/payments.routes');
const utilitiesRoutes = require('./modules/utilities/utilities.routes');
const pqrsRoutes = require('./modules/pqrs/pqrs.routes');
const reportsRoutes = require('./modules/reports/reports.routes');
const alertsRoutes = require('./modules/alerts/alerts.routes');
const auditRoutes = require('./modules/audit/audit.routes');
const settingsRoutes = require('./modules/settings/settings.routes');
const adminRoutes = require('./modules/admin/admin.routes');

const app = express();

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.APP_URL,
  credentials: true,
}));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));
app.use(morgan('combined', {
  stream: { write: (message) => logger.info(message.trim()) },
}));

// Static files
app.use('/uploads', express.static(path.join(__dirname, '../uploads')));

// API routes
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/tenants', tenantsRoutes);
app.use('/api/v1/properties', propertiesRoutes);
app.use('/api/v1/leases', leasesRoutes);
app.use('/api/v1/payments', paymentsRoutes);
app.use('/api/v1/utilities', utilitiesRoutes);
app.use('/api/v1/pqrs', pqrsRoutes);
app.use('/api/v1/reports', reportsRoutes);
app.use('/api/v1/alerts', alertsRoutes);
app.use('/api/v1/audit', auditRoutes);
app.use('/api/v1/settings', settingsRoutes);
app.use('/api/v1/sa', adminRoutes);

// Note: React SPA fallback is handled by web.config (IIS rewrite rules)

// Global error handler
app.use((err, req, res, _next) => {
  logger.error(`${err.status || 500} - ${err.message} - ${req.originalUrl} - ${req.method} - ${req.ip}`);

  res.status(err.status || 500).json({
    success: false,
    message: err.message || 'Error interno del servidor',
    errors: process.env.NODE_ENV === 'development' ? err.stack : null,
  });
});

// Start server — iisnode sets process.env.PORT via named pipe
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  logger.info(`Servidor APUS Renta ejecutandose en puerto ${PORT}`);
  logger.info(`Entorno: ${process.env.NODE_ENV || 'development'}`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM recibido. Cerrando servidor...');
  await prisma.$disconnect();
  process.exit(0);
});

module.exports = app;
