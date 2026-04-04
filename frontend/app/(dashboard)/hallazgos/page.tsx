'use client';

/**
 * CecilIA v2 — Sistema de IA para Control Fiscal
 * Contraloria General de la Republica de Colombia
 *
 * Pagina: Gestion de Hallazgos
 * Sprint: 5
 * Proposito: KPIs, tabla con filtros, detalle con 4 elementos expandibles,
 *            workflow stepper horizontal, botones por rol/estado,
 *            Circular 023 y generacion de oficios de traslado.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  AlertTriangle,
  Plus,
  Search,
  FileText,
  DollarSign,
  ClipboardCheck,
  Send,
  CheckCircle,
  Edit3,
  ChevronDown,
  ChevronUp,
  Download,
  Bot,
  ShieldAlert,
  Users,
  BarChart3,
  RefreshCcw,
  X,
  Info,
} from 'lucide-react';
import { Boton } from '@/components/ui/button';
import { Tarjeta } from '@/components/ui/card';
import { Insignia } from '@/components/ui/badge';
import { TarjetaHallazgo } from '@/components/hallazgos/HallazgoCard';
import {
  LineaTiempoFlujo,
  StepperWorkflow,
} from '@/components/hallazgos/WorkflowTimeline';
import { apiCliente } from '@/lib/api';
import { obtenerUsuario, esDirector } from '@/lib/auth';
import type {
  Hallazgo,
  EstadoHallazgo,
  TipoConnotacion,
  EstadisticasHallazgos,
} from '@/lib/types';

// ── Constantes ──────────────────────────────────────────────────────────────

const COLORES_CONNOTACION: Record<string, string> = {
  administrativo: '#3498DB',
  fiscal: '#E74C3C',
  disciplinario: '#F39C12',
  penal: '#8E44AD',
};

const ESTADOS_FILTRO: { valor: EstadoHallazgo | ''; etiqueta: string }[] = [
  { valor: '', etiqueta: 'Todos los estados' },
  { valor: 'BORRADOR', etiqueta: 'Borrador' },
  { valor: 'EN_REVISION', etiqueta: 'En revision' },
  { valor: 'OBSERVACION_TRASLADADA', etiqueta: 'Observacion trasladada' },
  { valor: 'RESPUESTA_RECIBIDA', etiqueta: 'Respuesta recibida' },
  { valor: 'HALLAZGO_CONFIGURADO', etiqueta: 'Hallazgo configurado' },
  { valor: 'APROBADO', etiqueta: 'Aprobado' },
  { valor: 'TRASLADADO', etiqueta: 'Trasladado' },
];

const CONNOTACIONES_FILTRO: TipoConnotacion[] = [
  'fiscal',
  'disciplinario',
  'penal',
  'administrativo',
];

// ── Helpers ─────────────────────────────────────────────────────────────────

function formatearMoneda(valor: number): string {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(valor);
}

function etiquetaEstado(estado: EstadoHallazgo): string {
  const mapa: Record<EstadoHallazgo, string> = {
    BORRADOR: 'Borrador',
    EN_REVISION: 'En revision',
    OBSERVACION_TRASLADADA: 'Obs. trasladada',
    RESPUESTA_RECIBIDA: 'Resp. recibida',
    HALLAZGO_CONFIGURADO: 'Configurado',
    APROBADO: 'Aprobado',
    TRASLADADO: 'Trasladado',
  };
  return mapa[estado] || estado;
}

// ── Datos de demo (fallback sin API) ────────────────────────────────────────

function hallazgosDemoFallback(): Hallazgo[] {
  return [
    {
      id: 'demo-001',
      auditoria_id: 'aud-001',
      numero_hallazgo: 1,
      titulo:
        'Sobrecostos en contratacion de servicios de conectividad MinTIC',
      condicion:
        'Se identificaron contratos de conectividad con valores superiores al promedio del mercado en un 35%, correspondientes a 12 contratos suscritos durante la vigencia 2025.',
      criterio:
        'Ley 80 de 1993, articulo 25, numeral 12. Decreto 1082 de 2015, articulo 2.2.1.1.2.1.1. Principio de economia y eficiencia del gasto publico.',
      causa:
        'Deficiencia en los estudios de mercado y ausencia de analisis comparativo de precios al momento de estructurar los procesos de contratacion.',
      efecto:
        'Presunto detrimento patrimonial por $2.345.678.900 correspondiente a la diferencia entre los valores contratados y los precios del mercado.',
      recomendacion:
        'Fortalecer los mecanismos de estudios de mercado e implementar bases de datos de precios de referencia.',
      connotaciones: [
        {
          tipo: 'fiscal',
          fundamentacion_legal: 'Ley 610 de 2000',
          descripcion: 'Presunto detrimento patrimonial al Estado',
        },
      ],
      cuantia_presunto_dano: 2345678900,
      presuntos_responsables: [
        {
          nombre: 'Director de Contratacion',
          cargo: 'Director',
          periodo: '2024-2025',
          fundamentacion: 'Ordenador del gasto',
        },
      ],
      evidencias: [
        {
          documento_id: 'doc-01',
          descripcion: 'Contratos 001-012/2025',
          folio: '1-120',
          tipo: 'documental',
        },
        {
          documento_id: 'doc-02',
          descripcion: 'Estudios de mercado',
          folio: '121-180',
          tipo: 'documental',
        },
      ],
      estado: 'EN_REVISION',
      fase_actual_workflow: 'supervisor',
      historial_workflow: [
        {
          usuario_id: 1,
          usuario_nombre: 'CecilIA (IA)',
          accion: 'crear',
          estado_anterior: 'BORRADOR',
          estado_nuevo: 'BORRADOR',
          fecha: '2026-03-15T10:00:00Z',
          comentarios: 'Hallazgo generado con asistencia de CecilIA.',
        },
        {
          usuario_id: 2,
          usuario_nombre: 'Dr. Carlos Rodriguez',
          accion: 'enviar_revision',
          estado_anterior: 'BORRADOR',
          estado_nuevo: 'EN_REVISION',
          fecha: '2026-03-20T14:30:00Z',
          comentarios: 'Enviado a revision por el equipo auditor.',
        },
      ],
      redaccion_validada_humano: true,
      generado_por_ia: true,
      validado_por: 2,
      fecha_validacion: '2026-03-18T09:00:00Z',
      created_by: 1,
      updated_by: 2,
      created_at: '2026-03-15T10:00:00Z',
      updated_at: '2026-03-20T14:30:00Z',
    },
    {
      id: 'demo-002',
      auditoria_id: 'aud-001',
      numero_hallazgo: 2,
      titulo:
        'Incumplimiento en la ejecucion del plan anual de adquisiciones',
      condicion:
        'El plan anual de adquisiciones presento una ejecucion del 62% al cierre de la vigencia, dejando sin ejecutar el 38% de los recursos.',
      criterio:
        'Ley 1474 de 2011. Decreto 1082 de 2015. Plan Nacional de Desarrollo 2022-2026.',
      causa:
        'Debilidades en la planeacion y programacion de la ejecucion contractual.',
      efecto:
        'Ineficiencia en el uso de los recursos publicos y afectacion en el cumplimiento de metas institucionales.',
      recomendacion:
        'Implementar mecanismos de seguimiento periodico al plan de adquisiciones con alertas tempranas.',
      connotaciones: [
        {
          tipo: 'administrativo',
          fundamentacion_legal: 'Ley 1474 de 2011',
          descripcion: 'Incumplimiento de plan de adquisiciones',
        },
      ],
      cuantia_presunto_dano: null,
      presuntos_responsables: [
        {
          nombre: 'Subdirector Administrativo',
          cargo: 'Subdirector',
          periodo: '2024-2025',
          fundamentacion: 'Responsable del PAA',
        },
      ],
      evidencias: [
        {
          documento_id: 'doc-03',
          descripcion: 'Plan de adquisiciones 2025',
          folio: '1-45',
          tipo: 'documental',
        },
      ],
      estado: 'APROBADO',
      fase_actual_workflow: 'director',
      historial_workflow: [
        {
          usuario_id: 3,
          usuario_nombre: 'Ana Gomez',
          accion: 'crear',
          estado_anterior: 'BORRADOR',
          estado_nuevo: 'BORRADOR',
          fecha: '2026-02-20T08:00:00Z',
          comentarios: '',
        },
        {
          usuario_id: 3,
          usuario_nombre: 'Ana Gomez',
          accion: 'enviar_revision',
          estado_anterior: 'BORRADOR',
          estado_nuevo: 'EN_REVISION',
          fecha: '2026-02-28T10:00:00Z',
          comentarios: '',
        },
        {
          usuario_id: 4,
          usuario_nombre: 'Dra. Patricia Ruiz',
          accion: 'configurar',
          estado_anterior: 'EN_REVISION',
          estado_nuevo: 'HALLAZGO_CONFIGURADO',
          fecha: '2026-03-10T11:00:00Z',
          comentarios: 'Hallazgo configurado tras revision.',
        },
        {
          usuario_id: 5,
          usuario_nombre: 'Director DVF',
          accion: 'aprobar',
          estado_anterior: 'HALLAZGO_CONFIGURADO',
          estado_nuevo: 'APROBADO',
          fecha: '2026-03-25T16:00:00Z',
          comentarios: 'Aprobado. Cumple requisitos de estructura y evidencia.',
        },
      ],
      redaccion_validada_humano: true,
      generado_por_ia: false,
      validado_por: 4,
      fecha_validacion: '2026-03-08T14:00:00Z',
      created_by: 3,
      updated_by: 5,
      created_at: '2026-02-20T08:00:00Z',
      updated_at: '2026-03-25T16:00:00Z',
    },
  ];
}

function estadisticasDemoFallback(): EstadisticasHallazgos {
  return {
    total_hallazgos: 2,
    por_estado: { BORRADOR: 0, EN_REVISION: 1, APROBADO: 1 },
    por_connotacion: { fiscal: 1, administrativo: 1 },
    cuantia_total_presunto_dano: 2345678900,
    borradores: 0,
    en_revision: 1,
    aprobados: 1,
    trasladados: 0,
  };
}

// ── Componente KPI Card ─────────────────────────────────────────────────────

function TarjetaKPI({
  titulo,
  valor,
  icono: Icono,
  color,
  subtitulo,
}: {
  titulo: string;
  valor: string | number;
  icono: React.ElementType;
  color: string;
  subtitulo?: string;
}) {
  return (
    <Tarjeta className="p-4 flex items-center gap-3">
      <div
        className="flex items-center justify-center h-10 w-10 rounded-lg"
        style={{ backgroundColor: `${color}20` }}
      >
        <Icono className="h-5 w-5" style={{ color }} />
      </div>
      <div>
        <p className="text-[10px] uppercase tracking-wider text-[#5F6368]">
          {titulo}
        </p>
        <p className="text-lg font-bold text-[#E8EAED]">{valor}</p>
        {subtitulo && (
          <p className="text-[10px] text-[#9AA0A6]">{subtitulo}</p>
        )}
      </div>
    </Tarjeta>
  );
}

// ── Componente de seccion expandible ────────────────────────────────────────

function SeccionExpandible({
  titulo,
  contenido,
  color,
  abierta,
  alToggle,
}: {
  titulo: string;
  contenido: string;
  color: string;
  abierta: boolean;
  alToggle: () => void;
}) {
  return (
    <div className="border border-[#2D3748]/50 rounded-lg overflow-hidden">
      <button
        onClick={alToggle}
        className="w-full flex items-center justify-between p-3 hover:bg-[#1A2332]/50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span
            className="h-2 w-2 rounded-full"
            style={{ backgroundColor: color }}
          />
          <span
            className="text-xs font-semibold uppercase tracking-wider"
            style={{ color }}
          >
            {titulo}
          </span>
        </div>
        {abierta ? (
          <ChevronUp className="h-3.5 w-3.5 text-[#5F6368]" />
        ) : (
          <ChevronDown className="h-3.5 w-3.5 text-[#5F6368]" />
        )}
      </button>
      {abierta && (
        <div className="px-4 pb-3 border-t border-[#2D3748]/30">
          <p className="text-xs text-[#9AA0A6] leading-relaxed mt-2 whitespace-pre-wrap">
            {contenido || 'Sin completar'}
          </p>
        </div>
      )}
    </div>
  );
}

// ── Pagina principal ────────────────────────────────────────────────────────

export default function PaginaHallazgos() {
  // Estado principal
  const [hallazgos, setHallazgos] = useState<Hallazgo[]>([]);
  const [estadisticas, setEstadisticas] = useState<EstadisticasHallazgos | null>(null);
  const [cargando, setCargando] = useState(true);

  // Filtros
  const [busqueda, setBusqueda] = useState('');
  const [filtroEstado, setFiltroEstado] = useState<EstadoHallazgo | ''>('');
  const [filtrosConnotacion, setFiltrosConnotacion] = useState<Set<TipoConnotacion>>(new Set());

  // Detalle
  const [hallazgoSeleccionadoId, setHallazgoSeleccionadoId] = useState<string | null>(null);
  const [seccionesAbiertas, setSeccionesAbiertas] = useState<Set<string>>(
    new Set(['condicion']),
  );

  // Acciones
  const [ejecutandoAccion, setEjecutandoAccion] = useState(false);

  // Usuario
  const usuario = obtenerUsuario();
  const usuarioEsDirector = esDirector();

  // ── Cargar datos ────────────────────────────────────────────────────────

  const cargarDatos = useCallback(async () => {
    setCargando(true);
    try {
      const [hallazgosResp, statsResp] = await Promise.all([
        apiCliente.get<Hallazgo[]>(
          `/hallazgos/?limite=200${filtroEstado ? `&estado=${filtroEstado}` : ''}`,
        ),
        apiCliente.get<EstadisticasHallazgos>('/hallazgos/estadisticas'),
      ]);
      setHallazgos(hallazgosResp);
      setEstadisticas(statsResp);
    } catch {
      // Fallback a datos demo si la API no esta disponible
      setHallazgos(hallazgosDemoFallback());
      setEstadisticas(estadisticasDemoFallback());
    } finally {
      setCargando(false);
    }
  }, [filtroEstado]);

  useEffect(() => {
    cargarDatos();
  }, [cargarDatos]);

  // ── Filtrado local ────────────────────────────────────────────────────────

  const hallazgosFiltrados = hallazgos.filter((h) => {
    const coincideBusqueda =
      busqueda === '' ||
      h.titulo.toLowerCase().includes(busqueda.toLowerCase()) ||
      h.condicion.toLowerCase().includes(busqueda.toLowerCase());

    const coincideConnotacion =
      filtrosConnotacion.size === 0 ||
      h.connotaciones?.some((c) =>
        filtrosConnotacion.has(c.tipo as TipoConnotacion),
      );

    return coincideBusqueda && coincideConnotacion;
  });

  const hallazgoDetalle = hallazgos.find(
    (h) => h.id === hallazgoSeleccionadoId,
  );

  // ── Acciones ────────────────────────────────────────────────────────────

  const toggleConnotacion = (tipo: TipoConnotacion) => {
    setFiltrosConnotacion((prev) => {
      const next = new Set(prev);
      if (next.has(tipo)) next.delete(tipo);
      else next.add(tipo);
      return next;
    });
  };

  const toggleSeccion = (seccion: string) => {
    setSeccionesAbiertas((prev) => {
      const next = new Set(prev);
      if (next.has(seccion)) next.delete(seccion);
      else next.add(seccion);
      return next;
    });
  };

  const ejecutarAccionWorkflow = async (
    hallazgoId: string,
    accion: string,
    datos?: Record<string, unknown>,
  ) => {
    setEjecutandoAccion(true);
    try {
      let endpoint = '';
      let body: Record<string, unknown> = {};

      switch (accion) {
        case 'enviar_revision':
          endpoint = `/hallazgos/${hallazgoId}/cambiar-estado`;
          body = { nuevo_estado: 'EN_REVISION', comentarios: '' };
          break;
        case 'validar_redaccion':
          endpoint = `/hallazgos/${hallazgoId}/validar-redaccion`;
          break;
        case 'aprobar':
          endpoint = `/hallazgos/${hallazgoId}/aprobar`;
          break;
        case 'configurar':
          endpoint = `/hallazgos/${hallazgoId}/cambiar-estado`;
          body = { nuevo_estado: 'HALLAZGO_CONFIGURADO', comentarios: '' };
          break;
        case 'trasladar_observacion':
          endpoint = `/hallazgos/${hallazgoId}/cambiar-estado`;
          body = { nuevo_estado: 'OBSERVACION_TRASLADADA', comentarios: '' };
          break;
        default:
          return;
      }

      await apiCliente.post(endpoint, Object.keys(body).length > 0 ? body : undefined);
      await cargarDatos();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error desconocido';
      alert(`Error: ${msg}`);
    } finally {
      setEjecutandoAccion(false);
    }
  };

  const descargarOficioTraslado = async (
    hallazgoId: string,
    destino: string,
  ) => {
    try {
      const token =
        typeof window !== 'undefined'
          ? localStorage.getItem('cecilia_token')
          : null;
      const urlBase = process.env.NEXT_PUBLIC_API_URL || '/api';
      const resp = await fetch(
        `${urlBase}/hallazgos/${hallazgoId}/oficio-traslado`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({ destino }),
        },
      );
      if (!resp.ok) throw new Error('Error generando oficio');
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Oficio_Traslado_${destino}_${hallazgoId.slice(0, 8)}.docx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert('Error al generar el oficio de traslado.');
    }
  };

  // ── KPIs ──────────────────────────────────────────────────────────────────

  const stats = estadisticas || estadisticasDemoFallback();

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header + KPIs */}
      <div className="border-b border-[#2D3748]/30 p-4 space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="font-titulo text-lg font-bold text-[#E8EAED] flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-[#C9A84C]" />
            Gestion de Hallazgos
          </h1>
          <div className="flex items-center gap-2">
            <Boton
              variante="fantasma"
              tamano="sm"
              onClick={() => cargarDatos()}
            >
              <RefreshCcw className="h-3.5 w-3.5" />
            </Boton>
            <Boton variante="primario" tamano="sm">
              <Plus className="h-3.5 w-3.5" />
              Nuevo hallazgo
            </Boton>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-5 gap-3">
          <TarjetaKPI
            titulo="Total"
            valor={stats.total_hallazgos}
            icono={BarChart3}
            color="#C9A84C"
          />
          <TarjetaKPI
            titulo="Borradores"
            valor={stats.borradores}
            icono={Edit3}
            color="#5F6368"
          />
          <TarjetaKPI
            titulo="En revision"
            valor={stats.en_revision}
            icono={Search}
            color="#F39C12"
          />
          <TarjetaKPI
            titulo="Aprobados"
            valor={stats.aprobados}
            icono={CheckCircle}
            color="#27AE60"
          />
          <TarjetaKPI
            titulo="Cuantia total"
            valor={formatearMoneda(stats.cuantia_total_presunto_dano)}
            icono={DollarSign}
            color="#E74C3C"
            subtitulo="Presunto dano patrimonial"
          />
        </div>
      </div>

      {/* Contenido principal */}
      <div className="flex flex-1 overflow-hidden">
        {/* Panel izquierdo: Lista */}
        <div className="flex w-2/5 flex-col border-r border-[#2D3748]/30 overflow-hidden">
          {/* Filtros */}
          <div className="p-3 border-b border-[#2D3748]/30 space-y-2">
            {/* Busqueda */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[#5F6368]" />
              <input
                type="text"
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                placeholder="Buscar en hallazgos..."
                className="w-full rounded-lg border border-[#2D3748] bg-[#0A0F14] py-2 pl-9 pr-4 text-xs text-[#E8EAED] placeholder:text-[#5F6368] focus:border-[#C9A84C] focus:outline-none"
              />
            </div>

            {/* Filtro estado */}
            <select
              value={filtroEstado}
              onChange={(e) =>
                setFiltroEstado(e.target.value as EstadoHallazgo | '')
              }
              className="w-full rounded-lg border border-[#2D3748] bg-[#0A0F14] py-1.5 px-3 text-xs text-[#E8EAED] focus:border-[#C9A84C] focus:outline-none"
            >
              {ESTADOS_FILTRO.map((e) => (
                <option key={e.valor} value={e.valor}>
                  {e.etiqueta}
                </option>
              ))}
            </select>

            {/* Checkboxes connotacion */}
            <div className="flex flex-wrap gap-1.5">
              {CONNOTACIONES_FILTRO.map((tipo) => (
                <button
                  key={tipo}
                  onClick={() => toggleConnotacion(tipo)}
                  className={`rounded-full px-2.5 py-1 text-[10px] transition-colors border ${
                    filtrosConnotacion.has(tipo)
                      ? 'border-current'
                      : 'border-[#2D3748] hover:border-[#4A5568]'
                  }`}
                  style={{
                    color: filtrosConnotacion.has(tipo)
                      ? COLORES_CONNOTACION[tipo]
                      : '#9AA0A6',
                    backgroundColor: filtrosConnotacion.has(tipo)
                      ? `${COLORES_CONNOTACION[tipo]}15`
                      : '#1A2332',
                  }}
                >
                  {tipo.charAt(0).toUpperCase() + tipo.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Lista de hallazgos */}
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {cargando ? (
              <div className="flex items-center justify-center h-32">
                <RefreshCcw className="h-5 w-5 text-[#5F6368] animate-spin" />
              </div>
            ) : hallazgosFiltrados.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-32 text-center">
                <AlertTriangle className="h-8 w-8 text-[#2D3748] mb-2" />
                <p className="text-xs text-[#5F6368]">
                  No se encontraron hallazgos
                </p>
              </div>
            ) : (
              hallazgosFiltrados.map((h) => (
                <TarjetaHallazgo
                  key={h.id}
                  hallazgo={h}
                  alClick={setHallazgoSeleccionadoId}
                />
              ))
            )}
          </div>
        </div>

        {/* Panel derecho: Detalle */}
        <div className="flex-1 overflow-y-auto">
          {hallazgoDetalle ? (
            <div className="p-5 space-y-5">
              {/* Encabezado del hallazgo */}
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono text-[#C9A84C]">
                      H-
                      {String(hallazgoDetalle.numero_hallazgo).padStart(
                        3,
                        '0',
                      )}
                    </span>
                    {hallazgoDetalle.generado_por_ia && (
                      <Insignia variante="oro">
                        <Bot className="h-3 w-3 mr-1" />
                        Asistido por IA
                      </Insignia>
                    )}
                    {hallazgoDetalle.redaccion_validada_humano && (
                      <Insignia variante="exito">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Validado
                      </Insignia>
                    )}
                  </div>
                  <h2 className="font-titulo text-base font-semibold text-[#E8EAED]">
                    {hallazgoDetalle.titulo}
                  </h2>
                </div>
                <button
                  onClick={() => setHallazgoSeleccionadoId(null)}
                  className="text-[#5F6368] hover:text-[#E8EAED]"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Workflow Stepper horizontal */}
              <Tarjeta className="p-4">
                <h3 className="text-xs font-semibold text-[#9AA0A6] uppercase tracking-wider mb-3">
                  Workflow de aprobacion
                </h3>
                <StepperWorkflow estadoActual={hallazgoDetalle.estado} />
              </Tarjeta>

              {/* Panel lateral: Connotaciones + Cuantia + Responsables */}
              <div className="grid grid-cols-3 gap-3">
                {/* Connotaciones */}
                <Tarjeta className="p-3">
                  <h4 className="text-[10px] uppercase tracking-wider text-[#5F6368] mb-2">
                    Connotaciones
                  </h4>
                  <div className="space-y-1.5">
                    {hallazgoDetalle.connotaciones?.length > 0 ? (
                      hallazgoDetalle.connotaciones.map((c, i) => (
                        <div key={i} className="flex items-center gap-2">
                          <span
                            className="h-2 w-2 rounded-full"
                            style={{
                              backgroundColor:
                                COLORES_CONNOTACION[c.tipo] || '#5F6368',
                            }}
                          />
                          <span className="text-xs text-[#E8EAED] capitalize">
                            {c.tipo}
                          </span>
                        </div>
                      ))
                    ) : (
                      <p className="text-[10px] text-[#5F6368]">
                        Sin connotaciones
                      </p>
                    )}
                  </div>
                </Tarjeta>

                {/* Cuantia */}
                <Tarjeta className="p-3">
                  <h4 className="text-[10px] uppercase tracking-wider text-[#5F6368] mb-2">
                    Cuantia presunto dano
                  </h4>
                  {hallazgoDetalle.cuantia_presunto_dano != null &&
                  hallazgoDetalle.cuantia_presunto_dano > 0 ? (
                    <p className="text-sm font-bold text-[#E74C3C]">
                      {formatearMoneda(hallazgoDetalle.cuantia_presunto_dano)}
                    </p>
                  ) : (
                    <p className="text-xs text-[#5F6368]">No cuantificado</p>
                  )}
                </Tarjeta>

                {/* Responsables */}
                <Tarjeta className="p-3">
                  <h4 className="text-[10px] uppercase tracking-wider text-[#5F6368] mb-2">
                    Presuntos responsables
                  </h4>
                  <div className="space-y-1">
                    {hallazgoDetalle.presuntos_responsables?.length > 0 ? (
                      hallazgoDetalle.presuntos_responsables.map((r, i) => (
                        <div key={i}>
                          <p className="text-xs text-[#E8EAED]">{r.nombre}</p>
                          <p className="text-[10px] text-[#5F6368]">
                            {r.cargo} ({r.periodo})
                          </p>
                        </div>
                      ))
                    ) : (
                      <p className="text-[10px] text-[#5F6368]">
                        Sin responsables
                      </p>
                    )}
                  </div>
                </Tarjeta>
              </div>

              {/* 4 Secciones expandibles */}
              <div className="space-y-2">
                <h3 className="text-xs font-semibold text-[#9AA0A6] uppercase tracking-wider">
                  Elementos del hallazgo
                </h3>
                <SeccionExpandible
                  titulo="Condicion"
                  contenido={hallazgoDetalle.condicion}
                  color="#2471A3"
                  abierta={seccionesAbiertas.has('condicion')}
                  alToggle={() => toggleSeccion('condicion')}
                />
                <SeccionExpandible
                  titulo="Criterio"
                  contenido={hallazgoDetalle.criterio}
                  color="#C9A84C"
                  abierta={seccionesAbiertas.has('criterio')}
                  alToggle={() => toggleSeccion('criterio')}
                />
                <SeccionExpandible
                  titulo="Causa"
                  contenido={hallazgoDetalle.causa}
                  color="#E74C3C"
                  abierta={seccionesAbiertas.has('causa')}
                  alToggle={() => toggleSeccion('causa')}
                />
                <SeccionExpandible
                  titulo="Efecto"
                  contenido={hallazgoDetalle.efecto}
                  color="#F39C12"
                  abierta={seccionesAbiertas.has('efecto')}
                  alToggle={() => toggleSeccion('efecto')}
                />
                {hallazgoDetalle.recomendacion && (
                  <SeccionExpandible
                    titulo="Recomendacion"
                    contenido={hallazgoDetalle.recomendacion}
                    color="#27AE60"
                    abierta={seccionesAbiertas.has('recomendacion')}
                    alToggle={() => toggleSeccion('recomendacion')}
                  />
                )}
              </div>

              {/* Evidencias */}
              {hallazgoDetalle.evidencias?.length > 0 && (
                <Tarjeta className="p-4">
                  <h3 className="text-xs font-semibold text-[#9AA0A6] uppercase tracking-wider mb-2">
                    Evidencias ({hallazgoDetalle.evidencias.length})
                  </h3>
                  <div className="space-y-1.5">
                    {hallazgoDetalle.evidencias.map((e, i) => (
                      <div
                        key={i}
                        className="flex items-center gap-2 text-xs text-[#9AA0A6]"
                      >
                        <FileText className="h-3 w-3 text-[#5F6368]" />
                        <span>{e.descripcion}</span>
                        {e.folio && (
                          <span className="text-[10px] text-[#5F6368]">
                            (Folios: {e.folio})
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </Tarjeta>
              )}

              {/* Circular 023 — Aviso */}
              {hallazgoDetalle.generado_por_ia &&
                !hallazgoDetalle.redaccion_validada_humano && (
                  <div className="flex items-start gap-3 rounded-lg border border-[#F39C12]/30 bg-[#F39C12]/5 p-3">
                    <ShieldAlert className="h-5 w-5 text-[#F39C12] flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-xs font-semibold text-[#F39C12]">
                        Circular 023 — Validacion requerida
                      </p>
                      <p className="text-[10px] text-[#9AA0A6] mt-0.5">
                        Este hallazgo fue generado con asistencia de IA. Segun
                        la Circular 023, requiere validacion humana antes de
                        poder ser aprobado. Un auditor debe revisar y validar
                        la redaccion.
                      </p>
                    </div>
                  </div>
                )}

              {/* Botones de accion segun estado y rol */}
              <Tarjeta className="p-4">
                <h3 className="text-xs font-semibold text-[#9AA0A6] uppercase tracking-wider mb-3">
                  Acciones
                </h3>
                <div className="flex flex-wrap gap-2">
                  {/* Validar redaccion — visible para hallazgos IA sin validar */}
                  {hallazgoDetalle.generado_por_ia &&
                    !hallazgoDetalle.redaccion_validada_humano &&
                    hallazgoDetalle.estado !== 'APROBADO' &&
                    hallazgoDetalle.estado !== 'TRASLADADO' && (
                      <Boton
                        variante="contorno"
                        tamano="sm"
                        cargando={ejecutandoAccion}
                        onClick={() =>
                          ejecutarAccionWorkflow(
                            hallazgoDetalle.id,
                            'validar_redaccion',
                          )
                        }
                      >
                        <Edit3 className="h-3.5 w-3.5" />
                        Validar redaccion
                      </Boton>
                    )}

                  {/* Enviar a revision — solo BORRADOR */}
                  {hallazgoDetalle.estado === 'BORRADOR' && (
                    <Boton
                      variante="dvf"
                      tamano="sm"
                      cargando={ejecutandoAccion}
                      onClick={() =>
                        ejecutarAccionWorkflow(
                          hallazgoDetalle.id,
                          'enviar_revision',
                        )
                      }
                    >
                      <Send className="h-3.5 w-3.5" />
                      Enviar a revision
                    </Boton>
                  )}

                  {/* Trasladar observacion — EN_REVISION */}
                  {hallazgoDetalle.estado === 'EN_REVISION' && (
                    <Boton
                      variante="secundario"
                      tamano="sm"
                      cargando={ejecutandoAccion}
                      onClick={() =>
                        ejecutarAccionWorkflow(
                          hallazgoDetalle.id,
                          'trasladar_observacion',
                        )
                      }
                    >
                      Trasladar observacion
                    </Boton>
                  )}

                  {/* Configurar hallazgo — EN_REVISION o RESPUESTA_RECIBIDA */}
                  {(hallazgoDetalle.estado === 'EN_REVISION' ||
                    hallazgoDetalle.estado === 'RESPUESTA_RECIBIDA') && (
                    <Boton
                      variante="des"
                      tamano="sm"
                      cargando={ejecutandoAccion}
                      onClick={() =>
                        ejecutarAccionWorkflow(
                          hallazgoDetalle.id,
                          'configurar',
                        )
                      }
                    >
                      <ClipboardCheck className="h-3.5 w-3.5" />
                      Configurar hallazgo
                    </Boton>
                  )}

                  {/* Aprobar — SOLO director, SOLO si validado, SOLO en HALLAZGO_CONFIGURADO */}
                  {hallazgoDetalle.estado === 'HALLAZGO_CONFIGURADO' && (
                    <Boton
                      variante="primario"
                      tamano="sm"
                      cargando={ejecutandoAccion}
                      disabled={
                        !usuarioEsDirector ||
                        (hallazgoDetalle.generado_por_ia &&
                          !hallazgoDetalle.redaccion_validada_humano)
                      }
                      onClick={() =>
                        ejecutarAccionWorkflow(hallazgoDetalle.id, 'aprobar')
                      }
                      title={
                        !usuarioEsDirector
                          ? 'Solo el Director DVF puede aprobar'
                          : hallazgoDetalle.generado_por_ia &&
                              !hallazgoDetalle.redaccion_validada_humano
                            ? 'Requiere validacion humana (Circular 023)'
                            : 'Aprobar hallazgo'
                      }
                    >
                      <CheckCircle className="h-3.5 w-3.5" />
                      Aprobar
                    </Boton>
                  )}

                  {/* Generar oficio de traslado — APROBADO con connotaciones */}
                  {hallazgoDetalle.estado === 'APROBADO' &&
                    hallazgoDetalle.connotaciones?.length > 0 && (
                      <>
                        {hallazgoDetalle.connotaciones
                          .filter((c) =>
                            ['fiscal', 'disciplinario', 'penal'].includes(
                              c.tipo,
                            ),
                          )
                          .map((c) => (
                            <Boton
                              key={c.tipo}
                              variante="contorno"
                              tamano="sm"
                              onClick={() =>
                                descargarOficioTraslado(
                                  hallazgoDetalle.id,
                                  c.tipo,
                                )
                              }
                            >
                              <Download className="h-3.5 w-3.5" />
                              Oficio traslado {c.tipo}
                            </Boton>
                          ))}
                      </>
                    )}
                </div>

                {/* Info para no-directores */}
                {hallazgoDetalle.estado === 'HALLAZGO_CONFIGURADO' &&
                  !usuarioEsDirector && (
                    <div className="flex items-center gap-2 mt-3 text-[10px] text-[#5F6368]">
                      <Info className="h-3 w-3" />
                      Solo el Director DVF puede aprobar hallazgos.
                    </div>
                  )}
              </Tarjeta>

              {/* Historial de workflow */}
              <div>
                <h3 className="text-xs font-semibold text-[#9AA0A6] uppercase tracking-wider mb-3">
                  Historial de workflow
                </h3>
                <LineaTiempoFlujo
                  eventos={hallazgoDetalle.historial_workflow || []}
                  estadoActual={hallazgoDetalle.estado}
                />
              </div>
            </div>
          ) : (
            <div className="flex h-full items-center justify-center text-center p-8">
              <div>
                <AlertTriangle className="mx-auto h-12 w-12 text-[#2D3748] mb-3" />
                <p className="text-sm text-[#5F6368]">
                  Seleccione un hallazgo para ver su detalle y flujo de trabajo
                </p>
                <p className="text-[10px] text-[#2D3748] mt-1">
                  Workflow: Borrador &rarr; En revision &rarr; Observacion &rarr;
                  Respuesta &rarr; Configurado &rarr; Aprobado &rarr; Trasladado
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
