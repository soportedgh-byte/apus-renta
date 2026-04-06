'use client';

import React, { useState, useRef, useEffect } from 'react';
import { ThumbsUp, ThumbsDown, Send, X } from 'lucide-react';

interface PropiedadesFeedback {
  mensajeId: string;
  feedbackActual?: 'positivo' | 'negativo' | null;
  alEnviarFeedback?: (mensajeId: string, tipo: 'positivo' | 'negativo', comentario?: string) => void;
}

/**
 * Botones de retroalimentacion (pulgar arriba/abajo) para respuestas de IA
 * Incluye textarea para comentario cuando el feedback es negativo
 * Sprint 10 — Dashboard ejecutivo y analitica
 */
export function BotonesFeedback({ mensajeId, feedbackActual, alEnviarFeedback }: PropiedadesFeedback) {
  const [feedback, setFeedback] = useState(feedbackActual);
  const [mostrarComentario, setMostrarComentario] = useState(false);
  const [comentario, setComentario] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (mostrarComentario && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [mostrarComentario]);

  const manejarPositivo = () => {
    setFeedback('positivo');
    setMostrarComentario(false);
    alEnviarFeedback?.(mensajeId, 'positivo');
  };

  const manejarNegativo = () => {
    setFeedback('negativo');
    setMostrarComentario(true);
  };

  const enviarComentarioNegativo = () => {
    alEnviarFeedback?.(mensajeId, 'negativo', comentario || undefined);
    setMostrarComentario(false);
  };

  const cancelarComentario = () => {
    // Enviar feedback negativo sin comentario
    alEnviarFeedback?.(mensajeId, 'negativo');
    setMostrarComentario(false);
    setComentario('');
  };

  return (
    <div className="inline-flex flex-col">
      <div className="flex items-center gap-1">
        <button
          onClick={manejarPositivo}
          className={`rounded-md p-1 transition-colors ${
            feedback === 'positivo'
              ? 'text-green-400 bg-green-400/10'
              : 'text-[#5F6368] hover:text-[#9AA0A6] hover:bg-[#1A2332]'
          }`}
          title="Respuesta util"
        >
          <ThumbsUp className="h-3.5 w-3.5" />
        </button>
        <button
          onClick={manejarNegativo}
          className={`rounded-md p-1 transition-colors ${
            feedback === 'negativo'
              ? 'text-red-400 bg-red-400/10'
              : 'text-[#5F6368] hover:text-[#9AA0A6] hover:bg-[#1A2332]'
          }`}
          title="Respuesta no util"
        >
          <ThumbsDown className="h-3.5 w-3.5" />
        </button>
        {feedback === 'positivo' && (
          <span className="text-[10px] text-green-400/70 ml-1">Gracias por tu feedback</span>
        )}
      </div>

      {/* Textarea para comentario negativo */}
      {mostrarComentario && (
        <div className="mt-2 rounded-lg border border-red-400/20 bg-[#0A0F14]/80 p-2 max-w-md">
          <p className="text-[10px] text-[#9AA0A6] mb-1.5">
            Ayudanos a mejorar. ¿Que estuvo mal en esta respuesta?
          </p>
          <textarea
            ref={textareaRef}
            value={comentario}
            onChange={(e) => setComentario(e.target.value)}
            placeholder="Ej: La informacion no es precisa, falta contexto normativo..."
            className="w-full rounded-md border border-[#2D3748] bg-[#1A2332] px-3 py-2 text-xs text-[#E8EAED] placeholder-[#5F6368] focus:border-red-400/40 focus:outline-none resize-none"
            rows={2}
            maxLength={500}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                enviarComentarioNegativo();
              }
            }}
          />
          <div className="flex items-center justify-between mt-1.5">
            <span className="text-[9px] text-[#5F6368]">{comentario.length}/500</span>
            <div className="flex items-center gap-1.5">
              <button
                onClick={cancelarComentario}
                className="flex items-center gap-1 rounded px-2 py-1 text-[10px] text-[#5F6368] hover:text-[#9AA0A6] hover:bg-[#1A2332] transition-colors"
              >
                <X className="h-3 w-3" />
                Omitir
              </button>
              <button
                onClick={enviarComentarioNegativo}
                className="flex items-center gap-1 rounded px-2 py-1 text-[10px] text-red-400 hover:bg-red-400/10 transition-colors"
              >
                <Send className="h-3 w-3" />
                Enviar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default BotonesFeedback;
