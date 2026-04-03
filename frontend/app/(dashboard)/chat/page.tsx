'use client';

import React, { Suspense, useCallback } from 'react';
import { useSearchParams } from 'next/navigation';
import { VentanaChat } from '@/components/chat/ChatWindow';
import { SpinnerCarga } from '@/components/shared/LoadingSpinner';

/**
 * Componente interno que lee los parametros de busqueda
 */
function ContenidoChat() {
  const params = useSearchParams();
  const idConversacion = params.get('id') || undefined;

  const alCambiarConversacion = useCallback((id: string, titulo: string) => {
    // Notificar al sidebar para que recargue la lista
    if (typeof window !== 'undefined' && (window as any).__cecilia_recargar_conversaciones) {
      (window as any).__cecilia_recargar_conversaciones();
    }
  }, []);

  return (
    <VentanaChat
      conversacionId={idConversacion}
      alCambiarConversacion={alCambiarConversacion}
    />
  );
}

/**
 * Pagina principal de chat con CecilIA
 * Recibe opcionalmente un ID de conversacion existente via query string
 */
export default function PaginaChat() {
  return (
    <div className="h-full">
      <Suspense
        fallback={
          <div className="flex h-full items-center justify-center">
            <SpinnerCarga texto="Preparando chat..." />
          </div>
        }
      >
        <ContenidoChat />
      </Suspense>
    </div>
  );
}
