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
import type { Hallazgo, EstadoHallazgo, TipoConnotacion } from '@/lib/types';

interface PropiedadesTarjetaHallazgo {
  hallazgo: Hallazgo;
  alClick?: (id: string) => void;
}

/** Etiquetas de estado para el workflow CGR */
const etiquetaEstado: Record<
  EstadoHallazgo,
  { texto: string; variante: 'oro' | 'exito' | 'rojo' | 'gris' | 'info' | 'amarillo' }
> = {
  BORRADOR: { texto: 'Borrador', variante: 'gris' },
  EN_REVISION: { texto: 'En revision', variante: 'oro' },
  OBSERVACION_TRASLADADA: { texto: 'Obs. trasladada', variante: 'amarillo' },
  RESPUESTA_RECIBIDA: { texto: 'Respuesta recibida', variante: 'info' },
  HALLAZGO_CONFIGURADO: { texto: 'Configurado', variante: 'oro' },
  APROBADO: { texto: 'Aprobado', variante: 'exito' },
  TRASLADADO: { texto: 'Trasladado', variante: 'rojo' },
};

/**
 * Tarjeta de hallazgo con los 4 elementos obligatorios + recomendacion.
 * Muestra connotaciones multiples, estado del workflow, cuantia y detalles expandibles.
 */
export function TarjetaHallazgo({ hallazgo, alClick }: PropiedadesTarjetaHallazgo) {
  const [expandido, setExpandido] = useState(false);
  const estadoConfig = etiquetaEstado[hallazgo.estado] || etiquetaEstado.BORRADOR;

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
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono text-[#C9A84C]">
                H-{String(hallazgo.numero_hallazgo).padStart(3, '0')}
              </span>
              {hallazgo.generado_por_ia && (
                <span className="flex items-center gap-0.5 text-[10px] text-[#C9A84C]">
                  <Bot className="h-3 w-3" />
                  IA
                </span>
              )}
            </div>
            <h3 className="text-sm font-medium text-[#E8EAED] line-clamp-2">
              {hallazgo.titulo}
            </h3>
          </div>
          <div className="flex items-center gap-1.5 flex-shrink-0 flex-wrap justify-end">
            {hallazgo.connotaciones?.map((c, i) => (
              <Insignia
                key={i}
                variante={(c.tipo as TipoConnotacion) === 'fiscal' ? 'fiscal'
                  : c.tipo === 'disciplinario' ? 'disciplinario'
                  : c.tipo === 'penal' ? 'penal'
                  : c.tipo === 'administrativo' ? 'administrativo'
                  : 'gris'}
              >
                {c.tipo.charAt(0).toUpperCase() + c.tipo.slice(1)}
              </Insignia>
            ))}
            <Insignia variante={estadoConfig.variante}>{estadoConfig.texto}</Insignia>
          </div>
        </div>

        {/* Metadatos */}
        <div className="flex items-center gap-4 text-[10px] text-[#5F6368] mb-3">
          {hallazgo.cuantia_presunto_dano != null && hallazgo.cuantia_presunto_dano > 0 && (
            <span className="flex items-center gap-1 text-[#E74C3C]">
              <DollarSign className="h-3 w-3" />
              {formatearMoneda(hallazgo.cuantia_presunto_dano)}
            </span>
          )}
          {hallazgo.presuntos_responsables && hallazgo.presuntos_responsables.length > 0 && (
            <span className="flex items-center gap-1">
              <Users className="h-3 w-3" />
              {hallazgo.presuntos_responsables.length} responsable(s)
            </span>
          )}
          {hallazgo.evidencias && (
            <span className="flex items-center gap-1">
              <FileText className="h-3 w-3" />
              {hallazgo.evidencias.length} evidencia(s)
            </span>
          )}
          {hallazgo.redaccion_validada_humano && (
            <span className="text-[#27AE60]">Validado</span>
          )}
        </div>

        {/* Condicion resumida */}
        <p className="text-xs text-[#9AA0A6] line-clamp-2 mb-2">
          {hallazgo.condicion?.substring(0, 120)}
          {(hallazgo.condicion?.length || 0) > 120 ? '...' : ''}
        </p>

        {/* Boton expandir */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            setExpandido(!expandido);
          }}
          className="flex items-center gap-1 text-[10px] text-[#9AA0A6] hover:text-[#E8EAED] transition-colors"
        >
          {expandido ? (
            <ChevronUp className="h-3 w-3" />
          ) : (
            <ChevronDown className="h-3 w-3" />
          )}
          {expandido ? 'Ocultar elementos' : 'Ver 4 elementos'}
        </button>

        {/* Elementos expandidos */}
        {expandido && (
          <div className="mt-3 space-y-2.5 border-t border-[#2D3748]/30 pt-3">
            {[
              { etiqueta: 'Condicion', contenido: hallazgo.condicion, color: '#2471A3' },
              { etiqueta: 'Criterio', contenido: hallazgo.criterio, color: '#C9A84C' },
              { etiqueta: 'Causa', contenido: hallazgo.causa, color: '#E74C3C' },
              { etiqueta: 'Efecto', contenido: hallazgo.efecto, color: '#F39C12' },
              { etiqueta: 'Recomendacion', contenido: hallazgo.recomendacion, color: '#27AE60' },
            ].map((elem) => (
              <div key={elem.etiqueta}>
                <div className="flex items-center gap-1.5 mb-0.5">
                  <span
                    className="h-1.5 w-1.5 rounded-full"
                    style={{ backgroundColor: elem.color }}
                  />
                  <span
                    className="text-[10px] font-medium uppercase tracking-wider"
                    style={{ color: elem.color }}
                  >
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
