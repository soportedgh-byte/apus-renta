/**
 * CecilIA v2 — Sistema de IA para Control Fiscal
 * Contraloría General de la República de Colombia
 *
 * Archivo : main.js
 * Propósito: Proceso principal de Electron — WebSocket, acceso a archivos, vigilancia y bandeja del sistema
 * Sprint  : 0
 * Autor   : Equipo Técnico CecilIA — CD-TIC-CGR
 * Fecha   : Abril 2026
 */

const { app, BrowserWindow, Tray, Menu, ipcMain, dialog, nativeImage } = require('electron');
const path = require('path');
const fs = require('fs');
const WebSocket = require('ws');
const chokidar = require('chokidar');
const Store = require('electron-store');
const winston = require('winston');

// ---------------------------------------------------------------------------
// Configuración
// ---------------------------------------------------------------------------
const CONFIG = {
  BACKEND_WS_URL: process.env.CECILIA_WS_URL || 'wss://cecilia.contraloria.gov.co/api/ws/',
  BACKEND_API_URL: process.env.CECILIA_API_URL || 'https://cecilia.contraloria.gov.co/api/v1',
  RECONNECT_INTERVAL_MS: 5000,
  MAX_RECONNECT_ATTEMPTS: 20,
  HEARTBEAT_INTERVAL_MS: 30000,
  LOG_DIR: path.join(app.getPath('userData'), 'logs'),
};

// ---------------------------------------------------------------------------
// Almacenamiento persistente
// ---------------------------------------------------------------------------
const store = new Store({
  name: 'cecilia-agent-config',
  defaults: {
    token: null,
    watchedFolders: [],
    autoStart: true,
    minimizeToTray: true,
  },
});

// ---------------------------------------------------------------------------
// Logger
// ---------------------------------------------------------------------------
if (!fs.existsSync(CONFIG.LOG_DIR)) {
  fs.mkdirSync(CONFIG.LOG_DIR, { recursive: true });
}

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json(),
  ),
  transports: [
    new winston.transports.File({
      filename: path.join(CONFIG.LOG_DIR, 'error.log'),
      level: 'error',
      maxsize: 5242880, // 5 MB
      maxFiles: 3,
    }),
    new winston.transports.File({
      filename: path.join(CONFIG.LOG_DIR, 'agent.log'),
      maxsize: 10485760, // 10 MB
      maxFiles: 5,
    }),
  ],
});

if (process.env.NODE_ENV === 'development') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple(),
  }));
}

// ---------------------------------------------------------------------------
// Variables globales
// ---------------------------------------------------------------------------
let mainWindow = null;
let tray = null;
let ws = null;
let reconnectAttempts = 0;
let heartbeatInterval = null;
let fileWatcher = null;

// ---------------------------------------------------------------------------
// Prevenir múltiples instancias
// ---------------------------------------------------------------------------
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

// ---------------------------------------------------------------------------
// Ventana principal
// ---------------------------------------------------------------------------
function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 900,
    height: 650,
    minWidth: 600,
    minHeight: 400,
    title: 'CecilIA Agent — Contraloría General de la República',
    icon: getIconPath(),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
    show: false,
  });

  mainWindow.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    logger.info('Ventana principal creada');
  });

  mainWindow.on('close', (event) => {
    if (store.get('minimizeToTray')) {
      event.preventDefault();
      mainWindow.hide();
      logger.info('Ventana minimizada a la bandeja del sistema');
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// ---------------------------------------------------------------------------
// Bandeja del sistema (System Tray)
// ---------------------------------------------------------------------------
function createTray() {
  const iconPath = getIconPath();
  tray = new Tray(iconPath);

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Abrir CecilIA Agent',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        } else {
          createMainWindow();
        }
      },
    },
    { type: 'separator' },
    {
      label: 'Estado de Conexión',
      enabled: false,
      id: 'connection-status',
    },
    { type: 'separator' },
    {
      label: 'Carpetas Vigiladas',
      submenu: buildWatchedFoldersMenu(),
    },
    {
      label: 'Agregar Carpeta...',
      click: addWatchedFolder,
    },
    { type: 'separator' },
    {
      label: 'Salir',
      click: () => {
        store.set('minimizeToTray', false);
        app.quit();
      },
    },
  ]);

  tray.setToolTip('CecilIA Agent — Control Fiscal CGR');
  tray.setContextMenu(contextMenu);

  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });

  logger.info('Bandeja del sistema creada');
}

function getIconPath() {
  const iconName = process.platform === 'win32' ? 'icon.ico' : 'icon.png';
  const iconPath = path.join(__dirname, '..', 'assets', iconName);
  if (fs.existsSync(iconPath)) {
    return nativeImage.createFromPath(iconPath);
  }
  // Icono por defecto si no se encuentra el archivo
  return nativeImage.createEmpty();
}

function buildWatchedFoldersMenu() {
  const folders = store.get('watchedFolders') || [];
  if (folders.length === 0) {
    return [{ label: '(ninguna carpeta configurada)', enabled: false }];
  }
  return folders.map((folder) => ({
    label: folder,
    type: 'checkbox',
    checked: true,
    click: () => removeWatchedFolder(folder),
  }));
}

// ---------------------------------------------------------------------------
// Conexión WebSocket al backend
// ---------------------------------------------------------------------------
function connectWebSocket() {
  const token = store.get('token');

  if (!token) {
    logger.warn('No hay token de autenticación. Se omite la conexión WebSocket.');
    updateConnectionStatus('Sin autenticar');
    return;
  }

  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    logger.info('WebSocket ya está conectado o conectando.');
    return;
  }

  const wsUrl = `${CONFIG.BACKEND_WS_URL}?token=${encodeURIComponent(token)}`;

  logger.info('Conectando al backend vía WebSocket...');
  updateConnectionStatus('Conectando...');

  ws = new WebSocket(wsUrl, {
    headers: {
      'User-Agent': `CecilIA-Desktop-Agent/${app.getVersion()}`,
    },
  });

  ws.on('open', () => {
    logger.info('WebSocket conectado exitosamente');
    reconnectAttempts = 0;
    updateConnectionStatus('Conectado');
    startHeartbeat();
    notifyRenderer('ws:connected');
  });

  ws.on('message', (data) => {
    try {
      const mensaje = JSON.parse(data.toString());
      logger.info('Mensaje recibido del backend', { tipo: mensaje.tipo });
      handleBackendMessage(mensaje);
    } catch (error) {
      logger.error('Error al procesar mensaje WebSocket', { error: error.message });
    }
  });

  ws.on('close', (code, reason) => {
    logger.warn('WebSocket desconectado', { code, reason: reason.toString() });
    updateConnectionStatus('Desconectado');
    stopHeartbeat();
    scheduleReconnect();
  });

  ws.on('error', (error) => {
    logger.error('Error en WebSocket', { error: error.message });
    updateConnectionStatus('Error');
  });
}

function scheduleReconnect() {
  if (reconnectAttempts >= CONFIG.MAX_RECONNECT_ATTEMPTS) {
    logger.error('Se alcanzó el máximo de intentos de reconexión');
    updateConnectionStatus('Error de conexión');
    return;
  }

  reconnectAttempts++;
  const delay = CONFIG.RECONNECT_INTERVAL_MS * Math.min(reconnectAttempts, 6);
  logger.info(`Reintento de conexión ${reconnectAttempts}/${CONFIG.MAX_RECONNECT_ATTEMPTS} en ${delay}ms`);

  setTimeout(connectWebSocket, delay);
}

function startHeartbeat() {
  stopHeartbeat();
  heartbeatInterval = setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.ping();
    }
  }, CONFIG.HEARTBEAT_INTERVAL_MS);
}

function stopHeartbeat() {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval);
    heartbeatInterval = null;
  }
}

function sendToBackend(message) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(message));
    logger.info('Mensaje enviado al backend', { tipo: message.tipo });
  } else {
    logger.warn('No se puede enviar mensaje: WebSocket no conectado');
  }
}

function updateConnectionStatus(status) {
  if (tray) {
    tray.setToolTip(`CecilIA Agent — ${status}`);
  }
  notifyRenderer('ws:status', { status });
}

// ---------------------------------------------------------------------------
// Manejo de mensajes del backend
// ---------------------------------------------------------------------------
function handleBackendMessage(mensaje) {
  switch (mensaje.tipo) {
    case 'solicitar_archivo':
      handleFileRequest(mensaje);
      break;

    case 'solicitar_listado':
      handleListDirectoryRequest(mensaje);
      break;

    case 'notificacion':
      showNotification(mensaje.titulo || 'CecilIA', mensaje.contenido);
      break;

    default:
      // Reenviar al renderer para manejo en la interfaz
      notifyRenderer('backend:message', mensaje);
  }
}

// ---------------------------------------------------------------------------
// Acceso al sistema de archivos local
// ---------------------------------------------------------------------------
async function handleFileRequest(mensaje) {
  const { ruta, solicitud_id } = mensaje;

  // Verificar que la ruta está dentro de una carpeta vigilada
  const folders = store.get('watchedFolders') || [];
  const autorizado = folders.some((folder) => ruta.startsWith(folder));

  if (!autorizado) {
    logger.warn('Acceso denegado a archivo fuera de carpetas autorizadas', { ruta });
    sendToBackend({
      tipo: 'respuesta_archivo',
      solicitud_id,
      error: 'Acceso denegado: la ruta no está dentro de las carpetas autorizadas',
    });
    return;
  }

  try {
    const stats = fs.statSync(ruta);
    if (stats.size > 50 * 1024 * 1024) {
      // Límite de 50 MB
      sendToBackend({
        tipo: 'respuesta_archivo',
        solicitud_id,
        error: 'El archivo excede el tamaño máximo permitido (50 MB)',
      });
      return;
    }

    const contenido = fs.readFileSync(ruta);
    sendToBackend({
      tipo: 'respuesta_archivo',
      solicitud_id,
      nombre: path.basename(ruta),
      contenido: contenido.toString('base64'),
      tamano: stats.size,
      modificado: stats.mtime.toISOString(),
    });
    logger.info('Archivo enviado al backend', { ruta, tamano: stats.size });
  } catch (error) {
    logger.error('Error al leer archivo', { ruta, error: error.message });
    sendToBackend({
      tipo: 'respuesta_archivo',
      solicitud_id,
      error: `Error al leer el archivo: ${error.message}`,
    });
  }
}

async function handleListDirectoryRequest(mensaje) {
  const { ruta, solicitud_id } = mensaje;

  const folders = store.get('watchedFolders') || [];
  const autorizado = folders.some((folder) => ruta.startsWith(folder));

  if (!autorizado) {
    sendToBackend({
      tipo: 'respuesta_listado',
      solicitud_id,
      error: 'Acceso denegado',
    });
    return;
  }

  try {
    const items = fs.readdirSync(ruta, { withFileTypes: true });
    const listado = items.map((item) => ({
      nombre: item.name,
      es_directorio: item.isDirectory(),
      ruta: path.join(ruta, item.name),
    }));

    sendToBackend({
      tipo: 'respuesta_listado',
      solicitud_id,
      archivos: listado,
    });
  } catch (error) {
    logger.error('Error al listar directorio', { ruta, error: error.message });
    sendToBackend({
      tipo: 'respuesta_listado',
      solicitud_id,
      error: `Error al listar directorio: ${error.message}`,
    });
  }
}

// ---------------------------------------------------------------------------
// Vigilancia de archivos (File Watching)
// ---------------------------------------------------------------------------
function initFileWatcher() {
  const folders = store.get('watchedFolders') || [];

  if (folders.length === 0) {
    logger.info('No hay carpetas configuradas para vigilancia');
    return;
  }

  if (fileWatcher) {
    fileWatcher.close();
  }

  fileWatcher = chokidar.watch(folders, {
    persistent: true,
    ignoreInitial: true,
    depth: 3,
    awaitWriteFinish: {
      stabilityThreshold: 2000,
      pollInterval: 100,
    },
    ignored: [
      /(^|[/\\])\../,        // Archivos ocultos
      /node_modules/,
      /\.tmp$/,
      /~$/,
    ],
  });

  fileWatcher.on('add', (filePath) => {
    logger.info('Archivo creado', { ruta: filePath });
    sendToBackend({
      tipo: 'evento_archivo',
      accion: 'creado',
      ruta: filePath,
      nombre: path.basename(filePath),
    });
  });

  fileWatcher.on('change', (filePath) => {
    logger.info('Archivo modificado', { ruta: filePath });
    sendToBackend({
      tipo: 'evento_archivo',
      accion: 'modificado',
      ruta: filePath,
      nombre: path.basename(filePath),
    });
  });

  fileWatcher.on('unlink', (filePath) => {
    logger.info('Archivo eliminado', { ruta: filePath });
    sendToBackend({
      tipo: 'evento_archivo',
      accion: 'eliminado',
      ruta: filePath,
      nombre: path.basename(filePath),
    });
  });

  fileWatcher.on('error', (error) => {
    logger.error('Error en el vigilante de archivos', { error: error.message });
  });

  logger.info('Vigilancia de archivos iniciada', { carpetas: folders });
}

// ---------------------------------------------------------------------------
// Gestión de carpetas vigiladas
// ---------------------------------------------------------------------------
async function addWatchedFolder() {
  const result = await dialog.showOpenDialog({
    title: 'Seleccionar carpeta para vigilancia',
    properties: ['openDirectory'],
    buttonLabel: 'Seleccionar',
  });

  if (result.canceled || result.filePaths.length === 0) return;

  const folder = result.filePaths[0];
  const folders = store.get('watchedFolders') || [];

  if (folders.includes(folder)) {
    logger.info('La carpeta ya está en vigilancia', { carpeta: folder });
    return;
  }

  folders.push(folder);
  store.set('watchedFolders', folders);
  logger.info('Carpeta agregada a vigilancia', { carpeta: folder });

  // Reiniciar vigilante
  initFileWatcher();
  updateTrayMenu();
}

function removeWatchedFolder(folder) {
  const folders = store.get('watchedFolders') || [];
  const updated = folders.filter((f) => f !== folder);
  store.set('watchedFolders', updated);
  logger.info('Carpeta removida de vigilancia', { carpeta: folder });

  initFileWatcher();
  updateTrayMenu();
}

function updateTrayMenu() {
  if (tray) {
    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'Abrir CecilIA Agent',
        click: () => {
          if (mainWindow) {
            mainWindow.show();
            mainWindow.focus();
          }
        },
      },
      { type: 'separator' },
      {
        label: 'Carpetas Vigiladas',
        submenu: buildWatchedFoldersMenu(),
      },
      {
        label: 'Agregar Carpeta...',
        click: addWatchedFolder,
      },
      { type: 'separator' },
      {
        label: 'Salir',
        click: () => {
          store.set('minimizeToTray', false);
          app.quit();
        },
      },
    ]);
    tray.setContextMenu(contextMenu);
  }
}

// ---------------------------------------------------------------------------
// Notificaciones
// ---------------------------------------------------------------------------
function showNotification(title, body) {
  const { Notification } = require('electron');
  if (Notification.isSupported()) {
    new Notification({ title, body }).show();
  }
}

function notifyRenderer(channel, data = {}) {
  if (mainWindow && mainWindow.webContents) {
    mainWindow.webContents.send(channel, data);
  }
}

// ---------------------------------------------------------------------------
// IPC: comunicación con el proceso renderer
// ---------------------------------------------------------------------------
ipcMain.handle('auth:login', async (_event, { token }) => {
  store.set('token', token);
  connectWebSocket();
  return { ok: true };
});

ipcMain.handle('auth:logout', async () => {
  store.delete('token');
  if (ws) ws.close();
  return { ok: true };
});

ipcMain.handle('folders:list', async () => {
  return store.get('watchedFolders') || [];
});

ipcMain.handle('folders:add', async () => {
  await addWatchedFolder();
  return store.get('watchedFolders') || [];
});

ipcMain.handle('folders:remove', async (_event, folder) => {
  removeWatchedFolder(folder);
  return store.get('watchedFolders') || [];
});

ipcMain.handle('config:get', async (_event, key) => {
  return store.get(key);
});

ipcMain.handle('config:set', async (_event, key, value) => {
  store.set(key, value);
  return { ok: true };
});

// ---------------------------------------------------------------------------
// Ciclo de vida de la aplicación
// ---------------------------------------------------------------------------
app.whenReady().then(() => {
  logger.info('CecilIA Desktop Agent iniciado', { version: app.getVersion() });

  createMainWindow();
  createTray();
  initFileWatcher();
  connectWebSocket();
});

app.on('window-all-closed', () => {
  // En Windows y Linux, no cerrar la app al cerrar todas las ventanas
  // (la app vive en la bandeja del sistema)
  if (process.platform === 'darwin') {
    // En macOS tampoco cerramos, mantenemos en dock
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createMainWindow();
  }
});

app.on('before-quit', () => {
  logger.info('CecilIA Desktop Agent cerrándose');
  stopHeartbeat();
  if (ws) ws.close();
  if (fileWatcher) fileWatcher.close();
  store.set('minimizeToTray', true);
});
