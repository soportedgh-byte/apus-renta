'use client';

import React from 'react';
import {
  FileEdit,
  Search,
  CheckCircle,
  XCircle,
  Send,
  Archive,
} from 'lucide-react';
import type { EventoFlujo, EstadoHallazgo } from '@/lib/types';

interface PropiedadesTimeline {
  eventos: EventoFlujo[];
  estadoActual: EstadoHallazgo;
}

/** Configuracion visual de cada estado */
const configEstado: Record<EstadoHallazgo, { icono: React.ElementType; color: string; etiqueta: string }> = {
  borrador: { icono: FileEdit, color: '#5F6368', etiqueta: 'Borrador' },
  en_revision: { icono: Search, color: '#C9A84C', etiqueta: 'En revision' },
  aprobado: { icono: CheckCircle, color: '#27AE60', etiqueta: 'Aprobado' },
  rechazado: { icono: XCircle, color: '#E74C3C', etiqueta: 'Rechazado' },
  trasladado: { icono: Send, color: '#2471A3', etiqueta: 'Trasladado' },
  archivado: { icono: Archive, color: '#5F6368', etiqueta: 'Archivado' },
};

/**
 * Linea de tiempo del flujo de trabajo de un hallazgo
 * Muestra los cambios de estado cronologicamente
 */
export function LineaTiempoFlujo({ eventos, estadoActual }: PropiedadesTimeline) {
  const configActual = configEstado[estadoActual];

  return (
    <div className="space-y-4">
      {/* Estado actual */}
      <div className="flex items-center gap-2 rounded-lg border p-3"
        style={{ borderColor: `${configActual.color}40`, backgroundColor: `${configActual.color}10` }}>
        <configActual.icono className="h-4 w-4" style={{ color: configActual.color }} />
        <span className="text-xs font-medium" style={{ color: configActual.color }}>
          Estado actual: {configActual.etiqueta}
        </span>
      </div>

      {/* Timeline de eventos */}
      <div className="relative ml-3 border-l border-[#2D3748]">
        {eventos.map((evento, indice) => {
          const configNuevo = configEstado[evento.estado_nuevo];
          const Icono = configNuevo.icono;
          return (
            <div key={indice} className="relative pb-4 pl-6 last:pb-0">
              {/* Punto en la linea */}
              <div
                className="absolute -left-[5px] top-1 h-2.5 w-2.5 rounded-full border-2"
                style={{ backgroundColor: configNuevo.color, borderColor: '#0F1419' }}
              />

              <div>
                <div className="flex items-center gap-2">
                  <Icono className="h-3 w-3" style={{ color: configNuevo.color }} />
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
                  por {evento.usuario}
                </p>
                {evento.comentario && (
                  <p className="mt-1 text-[10px] text-[#5F6368] italic">
                    &ldquo;{evento.comentario}&rdquo;
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
