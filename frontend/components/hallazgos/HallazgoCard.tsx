'use client';

import React, { useState } from 'react';
import {
  ChevronDown,
  ChevronUp,
  Bot,
  DollarSign,
  Users,
  FileText,
} from 'lucide-react';
import { Tarjeta } from '@/components/ui/card';
import { Insignia } from '@/components/ui/badge';
import { InsigniaConnotacion } from './ConnotacionBadge';
import type { Hallazgo, EstadoHallazgo } from '@/lib/types';

interface PropiedadesTarjetaHallazgo {
  hallazgo: Hallazgo;
  alClick?: (id: string) => void;
}

/** Etiquetas de estado */
const etiquetaEstado: Record<EstadoHallazgo, { texto: string; variante: 'oro' | 'exito' | 'rojo' | 'gris' | 'info' }> = {
  borrador: { texto: 'Borrador', variante: 'gris' },
  en_revision: { texto: 'En revision', variante: 'oro' },
  aprobado: { texto: 'Aprobado', variante: 'exito' },
  rechazado: { texto: 'Rechazado', variante: 'rojo' },
  trasladado: { texto: 'Trasladado', variante: 'info' },
  archivado: { texto: 'Archivado', variante: 'gris' },
};

/**
 * Tarjeta de hallazgo con los 5 elementos fiscales
 * Muestra connotacion, estado, cuantia y detalles expandibles
 */
export function TarjetaHallazgo({ hallazgo, alClick }: PropiedadesTarjetaHallazgo) {
  const [expandido, setExpandido] = useState(false);
  const estadoConfig = etiquetaEstado[hallazgo.estado];

  const formatearMoneda = (valor: number): string => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(valor);
  };

  return (
    <Tarjeta
      className="cursor-pointer hover:border-[#4A5568] transition-all"
      onClick={() => alClick?.(hallazgo.id)}
    >
      <div className="p-4">
        {/* Encabezado */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="min-w-0 flex-1">
            <h3 className="text-sm font-medium text-[#E8EAED] line-clamp-2">
              {hallazgo.titulo}
            </h3>
          </div>
          <div className="flex items-center gap-1.5 flex-shrink-0">
            <InsigniaConnotacion tipo={hallazgo.connotacion} />
            <Insignia variante={estadoConfig.variante}>{estadoConfig.texto}</Insignia>
          </div>
        </div>

        {/* Metadatos */}
        <div className="flex items-center gap-4 text-[10px] text-[#5F6368] mb-3">
          {hallazgo.cuantia && (
            <span className="flex items-center gap-1">
              <DollarSign className="h-3 w-3" />
              {formatearMoneda(hallazgo.cuantia)}
            </span>
          )}
          {hallazgo.responsables && hallazgo.responsables.length > 0 && (
            <span className="flex items-center gap-1">
              <Users className="h-3 w-3" />
              {hallazgo.responsables.length} responsable(s)
            </span>
          )}
          <span className="flex items-center gap-1">
            <FileText className="h-3 w-3" />
            {hallazgo.evidencias.length} evidencia(s)
          </span>
          {hallazgo.generado_por_ia && (
            <span className="flex items-center gap-1 text-[#C9A84C]">
              <Bot className="h-3 w-3" />
              Asistido por IA
            </span>
          )}
        </div>

        {/* Boton expandir */}
        <button
          onClick={(e) => { e.stopPropagation(); setExpandido(!expandido); }}
          className="flex items-center gap-1 text-[10px] text-[#9AA0A6] hover:text-[#E8EAED] transition-colors"
        >
          {expandido ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
          {expandido ? 'Ocultar elementos' : 'Ver 5 elementos'}
        </button>

        {/* Elementos expandidos */}
        {expandido && (
          <div className="mt-3 space-y-2.5 border-t border-[#2D3748]/30 pt-3">
            {[
              { etiqueta: 'Condicion', contenido: hallazgo.elementos.condicion, color: '#2471A3' },
              { etiqueta: 'Criterio', contenido: hallazgo.elementos.criterio, color: '#C9A84C' },
              { etiqueta: 'Causa', contenido: hallazgo.elementos.causa, color: '#E74C3C' },
              { etiqueta: 'Efecto', contenido: hallazgo.elementos.efecto, color: '#F39C12' },
              { etiqueta: 'Recomendacion', contenido: hallazgo.elementos.recomendacion, color: '#27AE60' },
            ].map((elem) => (
              <div key={elem.etiqueta}>
                <div className="flex items-center gap-1.5 mb-0.5">
                  <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: elem.color }} />
                  <span className="text-[10px] font-medium uppercase tracking-wider" style={{ color: elem.color }}>
                    {elem.etiqueta}
                  </span>
                </div>
                <p className="text-xs text-[#9AA0A6] pl-3 leading-relaxed">
                  {elem.contenido || 'Sin completar'}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </Tarjeta>
  );
}

export default TarjetaHallazgo;
