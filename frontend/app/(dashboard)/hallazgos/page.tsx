'use client';

import React, { useState, useEffect } from 'react';
import { AlertTriangle, Plus, Search, Filter } from 'lucide-react';
import { Boton } from '@/components/ui/button';
import { TarjetaHallazgo } from '@/components/hallazgos/HallazgoCard';
import { LineaTiempoFlujo } from '@/components/hallazgos/WorkflowTimeline';
import type { Hallazgo, TipoConnotacion } from '@/lib/types';

/**
 * Pagina de hallazgos de auditoria
 * Lista de hallazgos con filtros, tarjetas expandibles y flujo de trabajo
 */
export default function PaginaHallazgos() {
  const [hallazgos, setHallazgos] = useState<Hallazgo[]>([]);
  const [busqueda, setBusqueda] = useState('');
  const [filtroConnotacion, setFiltroConnotacion] = useState<TipoConnotacion | 'todos'>('todos');
  const [hallazgoSeleccionado, setHallazgoSeleccionado] = useState<string | null>(null);

  useEffect(() => {
    // Datos de ejemplo
    setHallazgos([
      {
        id: '1',
        auditoria_id: '1',
        titulo: 'Sobrecostos en contratacion de servicios de conectividad',
        connotacion: 'fiscal',
        estado: 'en_revision',
        elementos: {
          condicion: 'Se identificaron contratos de conectividad con valores superiores al promedio del mercado en un 35%, correspondientes a 12 contratos suscritos durante la vigencia 2024.',
          criterio: 'Ley 80 de 1993, articulo 25, numeral 12. Decreto 1082 de 2015, articulo 2.2.1.1.2.1.1. Principio de economia y eficiencia del gasto publico.',
          causa: 'Deficiencia en los estudios de mercado y ausencia de analisis comparativo de precios al momento de estructurar los procesos de contratacion.',
          efecto: 'Presunto detrimento patrimonial por $2.345.678.900 correspondiente a la diferencia entre los valores contratados y los precios del mercado para servicios equivalentes.',
          recomendacion: 'Fortalecer los mecanismos de elaboracion de estudios de mercado, implementar bases de datos de precios de referencia y establecer controles de verificacion previos a la adjudicacion.',
        },
        cuantia: 2345678900,
        responsables: ['Director de Contratacion', 'Ordenador del Gasto'],
        evidencias: ['Contratos 001-012/2024', 'Estudios de mercado', 'Cotizaciones proveedores'],
        generado_por_ia: true,
        validado_por: undefined,
        fecha_creacion: '2025-08-15T10:00:00Z',
        fecha_actualizacion: '2025-09-01T14:30:00Z',
        historial_flujo: [
          {
            estado_anterior: 'borrador',
            estado_nuevo: 'borrador',
            usuario: 'CecilIA (IA)',
            comentario: 'Hallazgo generado automaticamente por CecilIA a partir del analisis documental.',
            fecha: '2025-08-15T10:00:00Z',
          },
          {
            estado_anterior: 'borrador',
            estado_nuevo: 'en_revision',
            usuario: 'Dr. Carlos Rodriguez',
            comentario: 'Enviado a revision por el equipo auditor.',
            fecha: '2025-09-01T14:30:00Z',
          },
        ],
      },
      {
        id: '2',
        auditoria_id: '1',
        titulo: 'Incumplimiento en la ejecucion del plan anual de adquisiciones',
        connotacion: 'administrativo',
        estado: 'aprobado',
        elementos: {
          condicion: 'El plan anual de adquisiciones presento una ejecucion del 62% al cierre de la vigencia, dejando sin ejecutar el 38% de los recursos programados.',
          criterio: 'Ley 1474 de 2011. Decreto 1082 de 2015. Plan Nacional de Desarrollo 2022-2026.',
          causa: 'Debilidades en la planeacion y programacion de la ejecucion contractual, asi como demoras en los procesos de seleccion.',
          efecto: 'Ineficiencia en el uso de los recursos publicos y afectacion en el cumplimiento de metas institucionales.',
          recomendacion: 'Implementar mecanismos de seguimiento periodico al plan de adquisiciones con alertas tempranas de incumplimiento.',
        },
        cuantia: undefined,
        responsables: ['Subdirector Administrativo'],
        evidencias: ['Plan de adquisiciones 2024', 'Informe de ejecucion'],
        generado_por_ia: false,
        validado_por: 'Dra. Patricia Ruiz',
        fecha_creacion: '2025-07-20T08:00:00Z',
        fecha_actualizacion: '2025-10-15T16:00:00Z',
        historial_flujo: [
          {
            estado_anterior: 'borrador',
            estado_nuevo: 'borrador',
            usuario: 'Ana Gomez',
            fecha: '2025-07-20T08:00:00Z',
          },
          {
            estado_anterior: 'borrador',
            estado_nuevo: 'en_revision',
            usuario: 'Ana Gomez',
            fecha: '2025-08-10T10:00:00Z',
          },
          {
            estado_anterior: 'en_revision',
            estado_nuevo: 'aprobado',
            usuario: 'Dra. Patricia Ruiz',
            comentario: 'Hallazgo aprobado. Cumple con los requisitos de estructura y evidencia.',
            fecha: '2025-10-15T16:00:00Z',
          },
        ],
      },
    ]);
  }, []);

  const hallazgosFiltrados = hallazgos.filter((h) => {
    const coincideBusqueda = h.titulo.toLowerCase().includes(busqueda.toLowerCase());
    const coincideConnotacion = filtroConnotacion === 'todos' || h.connotacion === filtroConnotacion;
    return coincideBusqueda && coincideConnotacion;
  });

  const hallazgoDetalle = hallazgos.find((h) => h.id === hallazgoSeleccionado);

  return (
    <div className="flex h-full">
      {/* Panel izquierdo: Lista de hallazgos */}
      <div className="flex w-1/2 flex-col border-r border-[#2D3748]/30 overflow-hidden">
        <div className="p-4 border-b border-[#2D3748]/30">
          <div className="flex items-center justify-between mb-4">
            <h1 className="font-titulo text-lg font-bold text-[#E8EAED] flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-[#C9A84C]" />
              Hallazgos
            </h1>
            <Boton variante="primario" tamano="sm">
              <Plus className="h-3.5 w-3.5" />
              Nuevo hallazgo
            </Boton>
          </div>

          {/* Busqueda */}
          <div className="relative mb-3">
            <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[#5F6368]" />
            <input
              type="text"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              placeholder="Buscar hallazgos..."
              className="w-full rounded-lg border border-[#2D3748] bg-[#0A0F14] py-2 pl-9 pr-4 text-xs text-[#E8EAED] placeholder:text-[#5F6368] focus:border-[#C9A84C] focus:outline-none"
            />
          </div>

          {/* Filtros de connotacion */}
          <div className="flex flex-wrap gap-1.5">
            {(['todos', 'fiscal', 'disciplinario', 'penal', 'administrativo'] as const).map((tipo) => (
              <button
                key={tipo}
                onClick={() => setFiltroConnotacion(tipo)}
                className={`rounded-full px-2.5 py-1 text-[10px] transition-colors ${
                  filtroConnotacion === tipo
                    ? 'bg-[#C9A84C]/20 text-[#C9A84C] border border-[#C9A84C]/40'
                    : 'bg-[#1A2332] text-[#9AA0A6] border border-[#2D3748] hover:border-[#4A5568]'
                }`}
              >
                {tipo === 'todos' ? 'Todos' : tipo.charAt(0).toUpperCase() + tipo.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Lista */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {hallazgosFiltrados.map((hallazgo) => (
            <TarjetaHallazgo
              key={hallazgo.id}
              hallazgo={hallazgo}
              alClick={setHallazgoSeleccionado}
            />
          ))}
        </div>
      </div>

      {/* Panel derecho: Detalle y timeline */}
      <div className="flex-1 overflow-y-auto p-6">
        {hallazgoDetalle ? (
          <div className="space-y-6">
            <h2 className="font-titulo text-lg font-semibold text-[#E8EAED]">
              Flujo de trabajo
            </h2>
            <LineaTiempoFlujo
              eventos={hallazgoDetalle.historial_flujo}
              estadoActual={hallazgoDetalle.estado}
            />
          </div>
        ) : (
          <div className="flex h-full items-center justify-center text-center">
            <div>
              <AlertTriangle className="mx-auto h-12 w-12 text-[#2D3748] mb-3" />
              <p className="text-sm text-[#5F6368]">
                Seleccione un hallazgo para ver su detalle y flujo de trabajo
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
