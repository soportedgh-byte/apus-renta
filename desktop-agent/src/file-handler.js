/**
 * CecilIA v2 — Sistema de IA para Control Fiscal
 * Contraloria General de la Republica de Colombia
 *
 * Archivo : file-handler.js
 * Proposito: Operaciones de archivos con SANDBOX ESTRICTO —
 *            solo opera dentro de carpetas autorizadas por el usuario.
 *            Rechaza path traversal (../) y acceso fuera del sandbox.
 * Sprint  : 11
 * Autor   : Equipo Tecnico CecilIA — CD-TIC-CGR
 * Fecha   : Abril 2026
 */

const fs = require('fs');
const path = require('path');

// Tamano maximo de archivo: 50 MB
const MAX_FILE_SIZE = 50 * 1024 * 1024;

/**
 * Verifica que una ruta este dentro de alguna carpeta autorizada.
 * Rechaza path traversal y rutas absolutas fuera del sandbox.
 *
 * @param {string} rutaSolicitada - Ruta a verificar
 * @param {string[]} carpetasAutorizadas - Lista de carpetas del sandbox
 * @returns {{ valida: boolean, rutaResuelta: string, error?: string }}
 */
function verificarSandbox(rutaSolicitada, carpetasAutorizadas) {
  if (!rutaSolicitada || typeof rutaSolicitada !== 'string') {
    return { valida: false, rutaResuelta: '', error: 'Ruta vacia o invalida' };
  }

  // Rechazar path traversal explicito
  if (rutaSolicitada.includes('..')) {
    return { valida: false, rutaResuelta: '', error: 'Acceso denegado: path traversal detectado (..)' };
  }

  // Resolver ruta absoluta normalizada
  const rutaResuelta = path.resolve(rutaSolicitada);

  // Verificar que esta dentro de alguna carpeta autorizada
  const autorizada = carpetasAutorizadas.some((carpeta) => {
    const carpetaNormalizada = path.resolve(carpeta);
    return rutaResuelta.startsWith(carpetaNormalizada + path.sep) || rutaResuelta === carpetaNormalizada;
  });

  if (!autorizada) {
    return {
      valida: false,
      rutaResuelta,
      error: `Acceso denegado: la ruta '${rutaResuelta}' no esta dentro de las carpetas autorizadas`,
    };
  }

  return { valida: true, rutaResuelta };
}

/**
 * Lista el contenido de un directorio dentro del sandbox.
 *
 * @param {string} ruta - Directorio a listar
 * @param {string[]} carpetasAutorizadas
 * @returns {{ exito: boolean, archivos?: object[], error?: string }}
 */
function listarDirectorio(ruta, carpetasAutorizadas) {
  const check = verificarSandbox(ruta, carpetasAutorizadas);
  if (!check.valida) return { exito: false, error: check.error };

  try {
    const items = fs.readdirSync(check.rutaResuelta, { withFileTypes: true });
    const archivos = items
      .filter((item) => !item.name.startsWith('.'))
      .map((item) => {
        const rutaCompleta = path.join(check.rutaResuelta, item.name);
        const stats = fs.statSync(rutaCompleta);
        return {
          nombre: item.name,
          ruta: rutaCompleta,
          es_directorio: item.isDirectory(),
          tamano: item.isFile() ? stats.size : null,
          modificado: stats.mtime.toISOString(),
          extension: item.isFile() ? path.extname(item.name).toLowerCase() : null,
        };
      })
      .sort((a, b) => {
        // Directorios primero, luego por nombre
        if (a.es_directorio !== b.es_directorio) return a.es_directorio ? -1 : 1;
        return a.nombre.localeCompare(b.nombre);
      });

    return { exito: true, archivos, total: archivos.length };
  } catch (error) {
    return { exito: false, error: `Error al listar directorio: ${error.message}` };
  }
}

/**
 * Lee el contenido de un archivo dentro del sandbox.
 *
 * @param {string} ruta - Archivo a leer
 * @param {string[]} carpetasAutorizadas
 * @returns {{ exito: boolean, contenido?: string, tamano?: number, error?: string }}
 */
function leerArchivo(ruta, carpetasAutorizadas) {
  const check = verificarSandbox(ruta, carpetasAutorizadas);
  if (!check.valida) return { exito: false, error: check.error };

  try {
    const stats = fs.statSync(check.rutaResuelta);

    if (stats.isDirectory()) {
      return { exito: false, error: 'La ruta apunta a un directorio, no a un archivo' };
    }

    if (stats.size > MAX_FILE_SIZE) {
      return { exito: false, error: `El archivo excede el tamano maximo (${MAX_FILE_SIZE / 1024 / 1024} MB)` };
    }

    // Detectar si es binario o texto
    const extension = path.extname(check.rutaResuelta).toLowerCase();
    const extensionesBinarias = ['.pdf', '.docx', '.xlsx', '.pptx', '.zip', '.rar', '.exe', '.dll', '.png', '.jpg', '.gif'];

    if (extensionesBinarias.includes(extension)) {
      const contenido = fs.readFileSync(check.rutaResuelta);
      return {
        exito: true,
        contenido: contenido.toString('base64'),
        encoding: 'base64',
        tamano: stats.size,
        nombre: path.basename(check.rutaResuelta),
        modificado: stats.mtime.toISOString(),
      };
    }

    const contenido = fs.readFileSync(check.rutaResuelta, 'utf-8');
    return {
      exito: true,
      contenido,
      encoding: 'utf-8',
      tamano: stats.size,
      nombre: path.basename(check.rutaResuelta),
      modificado: stats.mtime.toISOString(),
    };
  } catch (error) {
    return { exito: false, error: `Error al leer archivo: ${error.message}` };
  }
}

/**
 * Escribe contenido en un archivo dentro del sandbox.
 *
 * @param {string} ruta - Archivo a escribir
 * @param {string} contenido - Contenido a escribir
 * @param {string[]} carpetasAutorizadas
 * @returns {{ exito: boolean, tamano?: number, error?: string }}
 */
function escribirArchivo(ruta, contenido, carpetasAutorizadas) {
  const check = verificarSandbox(ruta, carpetasAutorizadas);
  if (!check.valida) return { exito: false, error: check.error };

  try {
    // Crear directorio padre si no existe
    const directorioPadre = path.dirname(check.rutaResuelta);
    if (!fs.existsSync(directorioPadre)) {
      fs.mkdirSync(directorioPadre, { recursive: true });
    }

    fs.writeFileSync(check.rutaResuelta, contenido, 'utf-8');
    const stats = fs.statSync(check.rutaResuelta);

    return {
      exito: true,
      tamano: stats.size,
      ruta: check.rutaResuelta,
      modificado: stats.mtime.toISOString(),
    };
  } catch (error) {
    return { exito: false, error: `Error al escribir archivo: ${error.message}` };
  }
}

/**
 * Crea una carpeta dentro del sandbox.
 *
 * @param {string} ruta - Carpeta a crear
 * @param {string[]} carpetasAutorizadas
 * @returns {{ exito: boolean, error?: string }}
 */
function crearCarpeta(ruta, carpetasAutorizadas) {
  const check = verificarSandbox(ruta, carpetasAutorizadas);
  if (!check.valida) return { exito: false, error: check.error };

  try {
    fs.mkdirSync(check.rutaResuelta, { recursive: true });
    return { exito: true, ruta: check.rutaResuelta };
  } catch (error) {
    return { exito: false, error: `Error al crear carpeta: ${error.message}` };
  }
}

module.exports = {
  verificarSandbox,
  listarDirectorio,
  leerArchivo,
  escribirArchivo,
  crearCarpeta,
  MAX_FILE_SIZE,
};
