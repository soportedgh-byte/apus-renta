'use client';

import React from 'react';
import Image from 'next/image';
import {
  User,
  BookOpen,
  Copy,
  Check,
} from 'lucide-react';
import { Insignia } from '@/components/ui/badge';
import { BotonesFeedback } from './FeedbackButtons';
import { RespuestaStreaming } from './StreamingResponse';
import type { Mensaje, CitaFuente, Direccion } from '@/lib/types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface PropiedadesBurbuja {
  mensaje: Mensaje;
  direccion: Direccion;
  enStreaming?: boolean;
  alEnviarFeedback?: (mensajeId: string, tipo: 'positivo' | 'negativo', comentario?: string) => void;
}

/**
 * Burbuja de mensaje individual en el chat
 * Usuario a la derecha (color del rol), CecilIA a la izquierda (#1A2332)
 * Badge CECILIA · DES/DVF en cada respuesta
 */
export function BurbujaMensaje({ mensaje, direccion, enStreaming, alEnviarFeedback }: PropiedadesBurbuja) {
  const [copiado, setCopiado] = React.useState(false);
  const esUsuario = mensaje.rol === 'user';

  const colorUsuario = direccion === 'DES' ? '#1A5276' : '#1E8449';
  const colorUsuarioLight = direccion === 'DES' ? '#2471A3' : '#27AE60';

  const copiarContenido = () => {
    navigator.clipboard.writeText(mensaje.contenido);
    setCopiado(true);
    setTimeout(() => setCopiado(false), 2000);
  };

  return (
    <div className={`flex gap-3 px-4 py-4 ${esUsuario ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div className="flex-shrink-0">
        {esUsuario ? (
          <div
            className="flex h-8 w-8 items-center justify-center rounded-lg"
            style={{ backgroundColor: `${colorUsuario}30`, border: `1px solid ${colorUsuario}50` }}
          >
            <User className="h-4 w-4" style={{ color: colorUsuario }} />
          </div>
        ) : (
          <div className="relative h-8 w-8 rounded-lg overflow-hidden bg-[#C9A84C]/10 border border-[#C9A84C]/20 flex items-center justify-center">
            <Image
              src="/logo-cecilia.png"
              alt="CecilIA"
              width={20}
              height={20}
              className="object-contain"
            />
          </div>
        )}
      </div>

      {/* Contenido */}
      <div className={`flex-1 min-w-0 ${esUsuario ? 'text-right' : ''}`}>
        {/* Nombre, badge y hora */}
        <div className={`flex items-center gap-2 mb-1 ${esUsuario ? 'justify-end' : ''}`}>
          <span className="text-xs font-medium text-[#E8EAED]">
            {esUsuario ? 'Tu' : 'CecilIA'}
          </span>
          {!esUsuario && (
            <span
              className="inline-flex items-center rounded-full px-2 py-0.5 text-[9px] font-semibold"
              style={{
                backgroundColor: `${colorUsuario}15`,
                color: colorUsuarioLight,
                border: `1px solid ${colorUsuario}30`,
              }}
            >
              CECILIA · {direccion}
            </span>
          )}
          <span className="text-[10px] text-[#5F6368]">
            {new Date(mensaje.fecha_creacion).toLocaleTimeString('es-CO', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>

        {/* Cuerpo del mensaje */}
        <div
          className={`rounded-xl px-4 py-3 ${
            esUsuario
              ? 'ml-auto max-w-[85%] text-left'
              : 'bg-[#1A2332]/60 max-w-full'
          }`}
          style={esUsuario ? {
            backgroundColor: `${colorUsuario}20`,
            border: `1px solid ${colorUsuario}30`,
          } : undefined}
        >
          {enStreaming ? (
            <RespuestaStreaming texto={mensaje.contenido} enCurso={true} />
          ) : (
            <div className="prose prose-invert prose-sm max-w-none text-[#E8EAED] leading-relaxed
                            prose-headings:text-[#E8EAED] prose-headings:font-semibold prose-headings:mt-4 prose-headings:mb-2
                            prose-p:my-1.5 prose-li:my-0.5
                            prose-strong:text-[#C9A84C]
                            prose-code:text-[#7DCEA0] prose-code:bg-[#0A0F14] prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-xs
                            prose-pre:bg-[#0A0F14] prose-pre:border prose-pre:border-[#2D3748]/30 prose-pre:rounded-lg
                            prose-a:text-[#2471A3] prose-a:no-underline hover:prose-a:underline
                            prose-table:border-collapse prose-th:border prose-th:border-[#2D3748] prose-th:px-3 prose-th:py-1.5 prose-th:bg-[#0A0F14]
                            prose-td:border prose-td:border-[#2D3748] prose-td:px-3 prose-td:py-1.5
                            prose-blockquote:border-[#C9A84C]/30 prose-blockquote:text-[#9AA0A6]
                            prose-hr:border-[#2D3748]">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {mensaje.contenido}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Disclaimer Circular 023 */}
        {!esUsuario && !enStreaming && (
          <div className="mt-2 px-1">
            <p className="text-[10px] leading-relaxed text-[#5F6368]">
              Asistido por IA — Requiere validacion humana.
              <span className="text-[#5F6368]/60 ml-1">Circular 023 CGR</span>
            </p>
          </div>
        )}

        {/* Citas de fuentes */}
        {mensaje.citas && mensaje.citas.length > 0 && (
          <div className="mt-3 space-y-1.5">
            <p className="text-[10px] font-medium text-[#5F6368] uppercase tracking-wider">
              Fuentes consultadas
            </p>
            {mensaje.citas.map((cita, indice) => (
              <CitaFuenteComponent key={indice} cita={cita} indice={indice + 1} />
            ))}
          </div>
        )}

        {/* Acciones (solo IA) */}
        {!esUsuario && !enStreaming && (
          <div className="mt-2 flex items-center gap-2 px-1">
            <button
              onClick={copiarContenido}
              className="flex items-center gap-1 rounded-md px-2 py-1 text-[10px] text-[#5F6368] hover:text-[#9AA0A6] hover:bg-[#1A2332] transition-colors"
            >
              {copiado ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
              {copiado ? 'Copiado' : 'Copiar'}
            </button>
            <BotonesFeedback
              mensajeId={mensaje.id}
              feedbackActual={mensaje.feedback}
              alEnviarFeedback={alEnviarFeedback}
            />
          </div>
        )}
      </div>
    </div>
  );
}

/** Componente de cita de fuente */
function CitaFuenteComponent({ cita, indice }: { cita: CitaFuente; indice: number }) {
  return (
    <div className="flex items-start gap-2 rounded-lg bg-[#0A0F14]/60 px-3 py-2 border border-[#2D3748]/30">
      <span className="flex h-4 w-4 flex-shrink-0 items-center justify-center rounded bg-[#1A5276]/20 text-[9px] font-mono text-[#2471A3]">
        {indice}
      </span>
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <BookOpen className="h-3 w-3 flex-shrink-0 text-[#5F6368]" />
          <span className="text-[10px] font-medium text-[#9AA0A6] truncate">
            {cita.documento}
          </span>
          {cita.pagina && (
            <span className="text-[9px] text-[#5F6368]">p. {cita.pagina}</span>
          )}
          <Insignia variante="gris" className="text-[8px]">
            {cita.coleccion}
          </Insignia>
        </div>
        <p className="mt-0.5 text-[10px] text-[#5F6368] line-clamp-2 italic">
          &ldquo;{cita.fragmento}&rdquo;
        </p>
      </div>
    </div>
  );
}

export default BurbujaMensaje;
