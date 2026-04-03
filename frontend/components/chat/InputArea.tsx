'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Mic, StopCircle } from 'lucide-react';
import type { Direccion } from '@/lib/types';

interface PropiedadesEntrada {
  alEnviar: (texto: string) => void;
  alAdjuntar?: () => void;
  direccion: Direccion;
  deshabilitado?: boolean;
  /** Si hay un streaming en curso */
  enStreaming?: boolean;
  alDetenerStreaming?: () => void;
}

/**
 * Area de entrada de mensajes del chat
 * Incluye campo de texto expandible, boton de enviar y adjuntar
 */
export function AreaEntrada({
  alEnviar,
  alAdjuntar,
  direccion,
  deshabilitado,
  enStreaming,
  alDetenerStreaming,
}: PropiedadesEntrada) {
  const [texto, setTexto] = useState('');
  const refTextarea = useRef<HTMLTextAreaElement>(null);

  // Ajustar altura automaticamente
  useEffect(() => {
    const textarea = refTextarea.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`;
    }
  }, [texto]);

  const manejarEnvio = () => {
    const textoLimpio = texto.trim();
    if (!textoLimpio || deshabilitado) return;
    alEnviar(textoLimpio);
    setTexto('');
    // Resetear altura
    if (refTextarea.current) {
      refTextarea.current.style.height = 'auto';
    }
  };

  const manejarTecla = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      manejarEnvio();
    }
  };

  const colorAccento = direccion === 'DES' ? '#1A5276' : '#1E8449';

  return (
    <div className="border-t border-[#2D3748]/30 bg-[#0F1419] p-4">
      <div className="mx-auto max-w-3xl">
        <div className="relative flex items-end gap-2 rounded-xl border border-[#2D3748] bg-[#1A2332] p-2 focus-within:border-[#4A5568] transition-colors">
          {/* Boton de adjuntar */}
          <button
            onClick={alAdjuntar}
            className="flex-shrink-0 rounded-lg p-2 text-[#5F6368] hover:text-[#9AA0A6] hover:bg-[#243044] transition-colors"
            title="Adjuntar archivo"
          >
            <Paperclip className="h-4 w-4" />
          </button>

          {/* Textarea */}
          <textarea
            ref={refTextarea}
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            onKeyDown={manejarTecla}
            placeholder={
              direccion === 'DES'
                ? 'Pregunta sobre analisis sectorial, indicadores, riesgos...'
                : 'Pregunta sobre auditorias, hallazgos, normativa, formatos...'
            }
            disabled={deshabilitado || enStreaming}
            rows={1}
            className="flex-1 resize-none bg-transparent py-2 text-sm text-[#E8EAED] placeholder:text-[#5F6368] focus:outline-none disabled:opacity-50"
          />

          {/* Boton de enviar o detener */}
          {enStreaming ? (
            <button
              onClick={alDetenerStreaming}
              className="flex-shrink-0 rounded-lg bg-red-500/20 p-2 text-red-400 hover:bg-red-500/30 transition-colors"
              title="Detener generacion"
            >
              <StopCircle className="h-4 w-4" />
            </button>
          ) : (
            <button
              onClick={manejarEnvio}
              disabled={!texto.trim() || deshabilitado}
              className="flex-shrink-0 rounded-lg p-2 transition-all disabled:opacity-30"
              style={{
                backgroundColor: texto.trim() ? `${colorAccento}` : 'transparent',
                color: texto.trim() ? 'white' : '#5F6368',
              }}
              title="Enviar mensaje (Enter)"
            >
              <Send className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Indicador */}
        <p className="mt-2 text-center text-[10px] text-[#5F6368]">
          CecilIA puede cometer errores. Verifique la informacion importante.
          <span className="mx-1">|</span>
          <kbd className="rounded bg-[#1A2332] px-1 py-0.5 text-[9px]">Shift+Enter</kbd> para nueva linea
        </p>
      </div>
    </div>
  );
}

export default AreaEntrada;
