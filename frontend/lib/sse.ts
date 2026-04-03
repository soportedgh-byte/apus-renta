/**
 * Cliente SSE (Server-Sent Events) para streaming de respuestas de CecilIA
 * Maneja la recepcion en tiempo real de tokens desde el backend
 */

import type { CitaFuente, EventoSSE } from './types';

/** Callbacks para eventos de streaming */
export interface CallbacksStreaming {
  alRecibirToken: (token: string) => void;
  alRecibirCita: (cita: CitaFuente) => void;
  alCompletar: () => void;
  alError: (error: string) => void;
}

/**
 * Inicia una conexion SSE para streaming de respuesta del chat
 * Retorna una funcion para cancelar el streaming
 */
export function iniciarStreaming(
  conversacionId: string,
  mensaje: string,
  callbacks: CallbacksStreaming,
): () => void {
  const token = typeof window !== 'undefined'
    ? localStorage.getItem('cecilia_token')
    : null;

  const urlBase = process.env.NEXT_PUBLIC_API_URL || '/api';
  const url = `${urlBase}/chat/${conversacionId}/stream`;

  let controlador: AbortController | null = new AbortController();

  // Realizar la peticion POST con streaming
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ mensaje }),
    signal: controlador.signal,
  })
    .then(async (respuesta) => {
      if (!respuesta.ok) {
        throw new Error(`Error ${respuesta.status}: ${respuesta.statusText}`);
      }

      const lector = respuesta.body?.getReader();
      if (!lector) {
        throw new Error('No se pudo obtener el lector del stream');
      }

      const decodificador = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await lector.read();
        if (done) break;

        buffer += decodificador.decode(value, { stream: true });
        const lineas = buffer.split('\n');
        buffer = lineas.pop() || '';

        for (const linea of lineas) {
          if (linea.startsWith('data: ')) {
            const datosTexto = linea.slice(6).trim();
            if (datosTexto === '[DONE]') {
              callbacks.alCompletar();
              return;
            }

            try {
              const evento: EventoSSE = JSON.parse(datosTexto);

              switch (evento.tipo) {
                case 'token':
                  if (evento.contenido) {
                    callbacks.alRecibirToken(evento.contenido);
                  }
                  break;
                case 'cita':
                  if (evento.cita) {
                    callbacks.alRecibirCita(evento.cita);
                  }
                  break;
                case 'error':
                  callbacks.alError(evento.error || 'Error desconocido en el streaming');
                  break;
                case 'fin':
                  callbacks.alCompletar();
                  return;
              }
            } catch {
              // Si no es JSON valido, tratar como token de texto
              if (datosTexto) {
                callbacks.alRecibirToken(datosTexto);
              }
            }
          }
        }
      }

      callbacks.alCompletar();
    })
    .catch((error) => {
      if (error.name !== 'AbortError') {
        callbacks.alError(error.message || 'Error de conexion con el servidor');
      }
    });

  // Retornar funcion para cancelar
  return () => {
    if (controlador) {
      controlador.abort();
      controlador = null;
    }
  };
}
