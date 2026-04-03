'use client';

import React, { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { VentanaChat } from '@/components/chat/ChatWindow';
import { SpinnerCarga } from '@/components/shared/LoadingSpinner';

/**
 * Componente interno que lee los parametros de busqueda
 */
function ContenidoChat() {
  const params = useSearchParams();
  const idConversacion = params.get('id') || undefined;

  return <VentanaChat conversacionId={idConversacion} />;
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
