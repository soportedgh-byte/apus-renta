/**
 * Cliente API para CecilIA v2
 * Maneja autenticacion JWT y comunicacion con el backend
 */

// URL base del API - en desarrollo apunta al proxy de Next.js
const URL_BASE_API = process.env.NEXT_PUBLIC_API_URL || '/api';

/**
 * Obtiene el token JWT almacenado en localStorage
 */
function obtenerToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('cecilia_token');
}

/**
 * Construye los headers de la peticion incluyendo autorizacion
 */
function construirHeaders(headersExtra?: Record<string, string>): HeadersInit {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...headersExtra,
  };

  const token = obtenerToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
}

/**
 * Clase de error personalizada para respuestas del API
 */
export class ErrorAPI extends Error {
  constructor(
    public codigo: number,
    public detalle: string,
    message?: string,
  ) {
    super(message || `Error ${codigo}: ${detalle}`);
    this.name = 'ErrorAPI';
  }
}

/**
 * Realiza una peticion HTTP al backend
 */
async function peticion<T>(
  ruta: string,
  opciones: RequestInit = {},
): Promise<T> {
  const url = `${URL_BASE_API}${ruta}`;

  const respuesta = await fetch(url, {
    ...opciones,
    headers: construirHeaders(opciones.headers as Record<string, string>),
  });

  // Si la respuesta no es exitosa, lanzar error
  if (!respuesta.ok) {
    let detalle = 'Error desconocido';
    try {
      const cuerpoError = await respuesta.json();
      detalle = cuerpoError.detail || cuerpoError.message || detalle;
    } catch {
      detalle = respuesta.statusText;
    }

    // Si es 401, limpiar token y redirigir
    if (respuesta.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('cecilia_token');
        localStorage.removeItem('cecilia_usuario');
        window.location.href = '/login';
      }
    }

    throw new ErrorAPI(respuesta.status, detalle);
  }

  // Si no hay contenido, retornar vacio
  if (respuesta.status === 204) {
    return {} as T;
  }

  return respuesta.json();
}

/**
 * Cliente API con metodos HTTP
 */
export const apiCliente = {
  get: <T>(ruta: string) => peticion<T>(ruta, { method: 'GET' }),

  post: <T>(ruta: string, datos?: unknown) =>
    peticion<T>(ruta, {
      method: 'POST',
      body: datos ? JSON.stringify(datos) : undefined,
    }),

  put: <T>(ruta: string, datos?: unknown) =>
    peticion<T>(ruta, {
      method: 'PUT',
      body: datos ? JSON.stringify(datos) : undefined,
    }),

  patch: <T>(ruta: string, datos?: unknown) =>
    peticion<T>(ruta, {
      method: 'PATCH',
      body: datos ? JSON.stringify(datos) : undefined,
    }),

  delete: <T>(ruta: string) => peticion<T>(ruta, { method: 'DELETE' }),

  /**
   * Sube un archivo al backend
   */
  subirArchivo: async <T>(ruta: string, archivo: File, camposExtra?: Record<string, string>): Promise<T> => {
    const formData = new FormData();
    formData.append('archivo', archivo);

    if (camposExtra) {
      Object.entries(camposExtra).forEach(([clave, valor]) => {
        formData.append(clave, valor);
      });
    }

    const token = obtenerToken();
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    // No establecer Content-Type para FormData (el navegador lo pone automaticamente)

    const respuesta = await fetch(`${URL_BASE_API}${ruta}`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!respuesta.ok) {
      let detalle = 'Error al subir archivo';
      try {
        const cuerpoError = await respuesta.json();
        detalle = cuerpoError.detail || detalle;
      } catch {
        detalle = respuesta.statusText;
      }
      throw new ErrorAPI(respuesta.status, detalle);
    }

    return respuesta.json();
  },
};

export default apiCliente;
