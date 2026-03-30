const { Server } = require('socket.io');
const logger = require('./logger');

let io;

/**
 * Initialize Socket.IO with the HTTP server
 * @param {import('http').Server} httpServer
 * @returns {import('socket.io').Server}
 */
const init = (httpServer) => {
  io = new Server(httpServer, {
    cors: {
      origin: process.env.APP_URL || 'http://localhost:3000',
      methods: ['GET', 'POST'],
      credentials: true,
    },
  });

  io.on('connection', (socket) => {
    logger.info(`Socket connected: ${socket.id}`);

    // Join the user to their tenant room
    socket.on('join:tenant', (tenantId) => {
      if (tenantId) {
        socket.join(`tenant:${tenantId}`);
        logger.debug(`Socket ${socket.id} joined tenant room: ${tenantId}`);
      }
    });

    socket.on('disconnect', (reason) => {
      logger.info(`Socket disconnected: ${socket.id} - ${reason}`);
    });
  });

  logger.info('Socket.IO initialized');
  return io;
};

/**
 * Get the Socket.IO instance
 * @returns {import('socket.io').Server}
 */
const getIO = () => {
  if (!io) {
    throw new Error('Socket.IO has not been initialized. Call init() first.');
  }
  return io;
};

module.exports = { init, getIO };
