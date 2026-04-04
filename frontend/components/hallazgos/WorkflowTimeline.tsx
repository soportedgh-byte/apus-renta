'use client';

import React from 'react';
import {
  FileEdit,
  Search,
  CheckCircle,
  Send,
  MessageSquare,
  Reply,
  ClipboardCheck,
} from 'lucide-react';
import type { EventoWorkflow, EstadoHallazgo } from '@/lib/types';

interface PropiedadesTimeline {
  eventos: EventoWorkflow[];
  estadoActual: EstadoHallazgo;
}

/** Configuracion visual de cada estado del workflow CGR */
const configEstado: Record<
  EstadoHallazgo,
  { icono: React.ElementType; color: string; etiqueta: string }
> = {
  BORRADOR: { icono: FileEdit, color: '#5F6368', etiqueta: 'Borrador' },
  EN_REVISION: { icono: Search, color: '#C9A84C', etiqueta: 'En revision' },
  OBSERVACION_TRASLADADA: {
    icono: MessageSquare,
    color: '#F39C12',
    etiqueta: 'Observacion trasladada',
  },
  RESPUESTA_RECIBIDA: {
    icono: Reply,
    color: '#2471A3',
    etiqueta: 'Respuesta recibida',
  },
  HALLAZGO_CONFIGURADO: {
    icono: ClipboardCheck,
    color: '#8E44AD',
    etiqueta: 'Hallazgo configurado',
  },
  APROBADO: { icono: CheckCircle, color: '#27AE60', etiqueta: 'Aprobado' },
  TRASLADADO: { icono: Send, color: '#E74C3C', etiqueta: 'Trasladado' },
};

/** Orden de las fases del workflow para el stepper horizontal */
const FASES_WORKFLOW: EstadoHallazgo[] = [
  'BORRADOR',
  'EN_REVISION',
  'OBSERVACION_TRASLADADA',
  'RESPUESTA_RECIBIDA',
  'HALLAZGO_CONFIGURADO',
  'APROBADO',
  'TRASLADADO',
];

/**
 * Stepper horizontal del workflow de hallazgos CGR.
 * Muestra las 7 fases con indicador visual de progreso.
 */
export function StepperWorkflow({
  estadoActual,
}: {
  estadoActual: EstadoHallazgo;
}) {
  const indiceActual = FASES_WORKFLOW.indexOf(estadoActual);

  return (
    <div className="flex items-center gap-1 overflow-x-auto pb-2">
      {FASES_WORKFLOW.map((fase, idx) => {
        const config = configEstado[fase];
        const Icono = config.icono;
        const esActual = fase === estadoActual;
        const completado = idx < indiceActual;

        return (
          <React.Fragment key={fase}>
            <div className="flex flex-col items-center min-w-[80px]">
              <div
                className={`flex items-center justify-center h-8 w-8 rounded-full border-2 transition-all ${
                  esActual
                    ? 'scale-110 shadow-lg'
                    : completado
                      ? 'opacity-100'
                      : 'opacity-40'
                }`}
                style={{
                  borderColor: esActual
                    ? config.color
                    : completado
                      ? '#27AE60'
                      : '#2D3748',
                  backgroundColor: completado
                    ? '#27AE6020'
                    : esActual
                      ? `${config.color}20`
                      : 'transparent',
                }}
              >
                {completado ? (
                  <CheckCircle className="h-4 w-4 text-[#27AE60]" />
                ) : (
                  <Icono
                    className="h-4 w-4"
                    style={{ color: esActual ? config.color : '#5F6368' }}
                  />
                )}
              </div>
              <span
                className={`text-[9px] mt-1 text-center leading-tight ${
                  esActual ? 'font-semibold' : ''
                }`}
                style={{
                  color: esActual
                    ? config.color
                    : completado
                      ? '#27AE60'
                      : '#5F6368',
                }}
              >
                {config.etiqueta}
              </span>
            </div>
            {idx < FASES_WORKFLOW.length - 1 && (
              <div
                className="h-0.5 flex-1 min-w-[12px]"
                style={{
                  backgroundColor: idx < indiceActual ? '#27AE60' : '#2D3748',
                }}
              />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}

/**
 * Linea de tiempo vertical del workflow de un hallazgo.
 * Muestra los cambios de estado cronologicamente.
 */
export function LineaTiempoFlujo({
  eventos,
  estadoActual,
}: PropiedadesTimeline) {
  const configActual = configEstado[estadoActual];

  return (
    <div className="space-y-4">
      {/* Estado actual */}
      <div
        className="flex items-center gap-2 rounded-lg border p-3"
        style={{
          borderColor: `${configActual.color}40`,
          backgroundColor: `${configActual.color}10`,
        }}
      >
        <configActual.icono
          className="h-4 w-4"
          style={{ color: configActual.color }}
        />
        <span
          className="text-xs font-medium"
          style={{ color: configActual.color }}
        >
          Estado actual: {configActual.etiqueta}
        </span>
      </div>

      {/* Timeline de eventos */}
      <div className="relative ml-3 border-l border-[#2D3748]">
        {eventos.map((evento, indice) => {
          const configNuevo =
            configEstado[evento.estado_nuevo] || configEstado.BORRADOR;
          const Icono = configNuevo.icono;
          return (
            <div key={indice} className="relative pb-4 pl-6 last:pb-0">
              <div
                className="absolute -left-[5px] top-1 h-2.5 w-2.5 rounded-full border-2"
                style={{
                  backgroundColor: configNuevo.color,
                  borderColor: '#0F1419',
                }}
              />

              <div>
                <div className="flex items-center gap-2">
                  <Icono
                    className="h-3 w-3"
                    style={{ color: configNuevo.color }}
                  />
                  <span className="text-xs font-medium text-[#E8EAED]">
                    {configNuevo.etiqueta}
                  </span>
                  <span className="text-[10px] text-[#5F6368]">
                    {new Date(evento.fecha).toLocaleDateString('es-CO', {
                      day: '2-digit',
                      month: 'short',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </div>
                <p className="mt-0.5 text-[10px] text-[#9AA0A6]">
                  por {evento.usuario_nombre} &mdash;{' '}
                  <span className="capitalize">{evento.accion}</span>
                </p>
                {evento.comentarios && (
                  <p className="mt-1 text-[10px] text-[#5F6368] italic">
                    &ldquo;{evento.comentarios}&rdquo;
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default LineaTiempoFlujo;
