'use client';

import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';

interface PropiedadesFeedback {
  mensajeId: string;
  feedbackActual?: 'positivo' | 'negativo' | null;
  alEnviarFeedback?: (mensajeId: string, tipo: 'positivo' | 'negativo') => void;
}

/**
 * Botones de retroalimentacion (pulgar arriba/abajo) para respuestas de IA
 */
export function BotonesFeedback({ mensajeId, feedbackActual, alEnviarFeedback }: PropiedadesFeedback) {
  const [feedback, setFeedback] = useState(feedbackActual);

  const manejarClick = (tipo: 'positivo' | 'negativo') => {
    setFeedback(tipo);
    alEnviarFeedback?.(mensajeId, tipo);
  };

  return (
    <div className="flex items-center gap-1">
      <button
        onClick={() => manejarClick('positivo')}
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
        onClick={() => manejarClick('negativo')}
        className={`rounded-md p-1 transition-colors ${
          feedback === 'negativo'
            ? 'text-red-400 bg-red-400/10'
            : 'text-[#5F6368] hover:text-[#9AA0A6] hover:bg-[#1A2332]'
        }`}
        title="Respuesta no util"
      >
        <ThumbsDown className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}

export default BotonesFeedback;
