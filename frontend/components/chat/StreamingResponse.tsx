'use client';

import React from 'react';

interface PropiedadesStreaming {
  /** Texto acumulado hasta el momento */
  texto: string;
  /** Si la respuesta aun esta en curso */
  enCurso: boolean;
}

/**
 * Componente de visualizacion de respuesta en streaming
 * Muestra el texto con animacion de cursor parpadeante
 */
export function RespuestaStreaming({ texto, enCurso }: PropiedadesStreaming) {
  return (
    <div className="prose prose-invert prose-sm max-w-none">
      <div className="whitespace-pre-wrap text-sm text-[#E8EAED] leading-relaxed">
        {texto}
        {enCurso && (
          <span className="inline-block w-2 h-4 ml-0.5 bg-[#C9A84C] animate-pulse rounded-sm align-text-bottom" />
        )}
      </div>
      {enCurso && (
        <div className="mt-2 flex items-center gap-1.5">
          <div className="flex gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-[#C9A84C] animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="h-1.5 w-1.5 rounded-full bg-[#C9A84C] animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="h-1.5 w-1.5 rounded-full bg-[#C9A84C] animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <span className="text-[10px] text-[#5F6368]">CecilIA esta analizando...</span>
        </div>
      )}
    </div>
  );
}

export default RespuestaStreaming;
