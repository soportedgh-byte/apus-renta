/**
 * CecilIA v2 — Sistema de IA para Control Fiscal
 * Contraloria General de la Republica de Colombia
 *
 * Archivo : preload.js
 * Proposito: Puente seguro entre proceso principal y renderer (contextIsolation)
 * Sprint  : 11
 * Autor   : Equipo Tecnico CecilIA — CD-TIC-CGR
 * Fecha   : Abril 2026
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('ceciliaAgent', {
  // ── Autenticacion ─────────────────────────────────────────────────────────
  login: (token) => ipcRenderer.invoke('auth:login', { token }),
  logout: () => ipcRenderer.invoke('auth:logout'),

  // ── Carpetas vigiladas ────────────────────────────────────────────────────
  listarCarpetas: () => ipcRenderer.invoke('folders:list'),
  agregarCarpeta: () => ipcRenderer.invoke('folders:add'),
  removerCarpeta: (ruta) => ipcRenderer.invoke('folders:remove', ruta),

  // ── Operaciones de archivos (sandbox) ─────────────────────────────────────
  listarDirectorio: (ruta) => ipcRenderer.invoke('files:list', ruta),
  leerArchivo: (ruta) => ipcRenderer.invoke('files:read', ruta),
  escribirArchivo: (ruta, contenido) => ipcRenderer.invoke('files:write', ruta, contenido),
  crearCarpeta: (ruta) => ipcRenderer.invoke('files:mkdir', ruta),

  // ── Configuracion ─────────────────────────────────────────────────────────
  obtenerConfig: (clave) => ipcRenderer.invoke('config:get', clave),
  guardarConfig: (clave, valor) => ipcRenderer.invoke('config:set', clave, valor),

  // ── Estado de conexion ────────────────────────────────────────────────────
  obtenerEstadoConexion: () => ipcRenderer.invoke('connection:status'),

  // ── Eventos del proceso principal ─────────────────────────────────────────
  onEstadoConexion: (callback) => {
    const handler = (_event, data) => callback(data);
    ipcRenderer.on('ws:status', handler);
    return () => ipcRenderer.removeListener('ws:status', handler);
  },
  onConectado: (callback) => {
    const handler = () => callback();
    ipcRenderer.on('ws:connected', handler);
    return () => ipcRenderer.removeListener('ws:connected', handler);
  },
  onMensajeBackend: (callback) => {
    const handler = (_event, data) => callback(data);
    ipcRenderer.on('backend:message', handler);
    return () => ipcRenderer.removeListener('backend:message', handler);
  },
  onEventoArchivo: (callback) => {
    const handler = (_event, data) => callback(data);
    ipcRenderer.on('file:event', handler);
    return () => ipcRenderer.removeListener('file:event', handler);
  },
});
