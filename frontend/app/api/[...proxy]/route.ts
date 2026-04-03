import { NextRequest, NextResponse } from 'next/server';

/**
 * Proxy API: reenvía todas las peticiones /api/* al backend FastAPI
 * Esto actúa como fallback en caso de que las rewrites de next.config.ts
 * no cubran algún caso particular.
 */

async function proxyPeticion(request: NextRequest): Promise<NextResponse> {
  // Leer BACKEND_URL en cada petición para garantizar que se use el valor de runtime
  const urlBackend = process.env.BACKEND_URL || 'http://localhost:8000';
  const url = new URL(request.url);
  const rutaAPI = url.pathname; // Ya incluye /api/...
  const queryString = url.search;
  const urlDestino = `${urlBackend}${rutaAPI}${queryString}`;

  try {
    // Construir headers, propagando autorizacion
    const headers: Record<string, string> = {
      'Content-Type': request.headers.get('content-type') || 'application/json',
    };

    const authHeader = request.headers.get('authorization');
    if (authHeader) {
      headers['Authorization'] = authHeader;
    }

    // Preparar cuerpo de la peticion
    let body: BodyInit | undefined;
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      body = await request.text();
    }

    // Realizar peticion al backend
    const respuesta = await fetch(urlDestino, {
      method: request.method,
      headers,
      body,
    });

    // Verificar si es una respuesta de streaming (SSE)
    const contentType = respuesta.headers.get('content-type');
    if (contentType?.includes('text/event-stream')) {
      // Retornar streaming directamente
      return new NextResponse(respuesta.body, {
        status: respuesta.status,
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
      });
    }

    // Respuesta normal JSON
    const datos = await respuesta.text();

    return new NextResponse(datos, {
      status: respuesta.status,
      headers: {
        'Content-Type': contentType || 'application/json',
      },
    });
  } catch (error) {
    console.error('[CecilIA Proxy] Error al conectar con el backend:', error);
    return NextResponse.json(
      {
        detail: 'Error de conexion con el servidor backend. Verifique que el servicio este activo.',
      },
      { status: 502 },
    );
  }
}

export async function GET(request: NextRequest) {
  return proxyPeticion(request);
}

export async function POST(request: NextRequest) {
  return proxyPeticion(request);
}

export async function PUT(request: NextRequest) {
  return proxyPeticion(request);
}

export async function PATCH(request: NextRequest) {
  return proxyPeticion(request);
}

export async function DELETE(request: NextRequest) {
  return proxyPeticion(request);
}
