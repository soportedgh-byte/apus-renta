'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Eye,
  AlertTriangle,
  TrendingUp,
  BarChart3,
  Activity,
  ShieldAlert,
  FileSearch,
  Newspaper,
  Gavel,
  Radio,
  RefreshCw,
  ExternalLink,
  MessageSquare,
  Filter,
  ChevronDown,
  ChevronUp,
  Clock,
  Building2,
  Zap,
  Archive,
  CheckCircle,
} from 'lucide-react';
import { Tarjeta } from '@/components/ui/card';
import { Boton } from '@/components/ui/button';
import { Insignia } from '@/components/ui/badge';
import { apiCliente } from '@/lib/api';
import { obtenerDireccionActiva, obtenerUsuario } from '@/lib/auth';
import type { AlertaObservatorio, ContadoresObservatorio } from '@/lib/types';

// ── Constantes de UI ────────────────────────────────────────────────────────

const ICONOS_TIPO: Record<string, React.ReactNode> = {
  REGULATORIA: <Gavel className="h-4 w-4" />,
  LEGISLATIVA: <FileSearch className="h-4 w-4" />,
  NOTICIA: <Newspaper className="h-4 w-4" />,
  INDICADOR: <Activity className="h-4 w-4" />,
};

const COLORES_RELEVANCIA = {
  ALTA: { bg: 'bg-red-500/10', texto: 'text-red-400', borde: 'border-red-500/30', variante: 'rojo' as const },
  MEDIA: { bg: 'bg-yellow-500/10', texto: 'text-yellow-400', borde: 'border-yellow-500/30', variante: 'amarillo' as const },
  BAJA: { bg: 'bg-green-500/10', texto: 'text-green-400', borde: 'border-green-500/30', variante: 'exito' as const },
};

const COLORES_ESTADO = {
  NUEVA: { bg: 'bg-blue-500/10', texto: 'text-blue-400', variante: 'info' as const },
  VISTA: { bg: 'bg-gray-500/10', texto: 'text-gray-400', variante: 'gris' as const },
  EN_ANALISIS: { bg: 'bg-yellow-500/10', texto: 'text-yellow-400', variante: 'amarillo' as const },
  ARCHIVADA: { bg: 'bg-gray-500/10', texto: 'text-gray-500', variante: 'gris' as const },
};

const NOMBRES_TIPO: Record<string, string> = {
  REGULATORIA: 'Regulatoria',
  LEGISLATIVA: 'Legislativa',
  NOTICIA: 'Noticia',
  INDICADOR: 'Indicador',
};

const NOMBRES_IMPACTO: Record<string, string> = {
  presupuestal: 'Presupuestal',
  regulatorio: 'Regulatorio',
  contractual: 'Contractual',
};

// ── Componente principal ────────────────────────────────────────────────────

export default function PaginaObservatorio() {
  const [direccion, setDireccion] = useState<string | null>(null);
  const [alertas, setAlertas] = useState<AlertaObservatorio[]>([]);
  const [contadores, setContadores] = useState<ContadoresObservatorio | null>(null);
  const [cargando, setCargando] = useState(true);
  const [ejecutandoCrawl, setEjecutandoCrawl] = useState(false);
  const [alertaExpandida, setAlertaExpandida] = useState<string | null>(null);

  // Filtros
  const [filtroTipo, setFiltroTipo] = useState<string>('');
  const [filtroRelevancia, setFiltroRelevancia] = useState<string>('');
  const [filtroEstado, setFiltroEstado] = useState<string>('');
  const [filtroFuente, setFiltroFuente] = useState<string>('');
  const [mostrarFiltros, setMostrarFiltros] = useState(false);

  // ── Carga de datos ──────────────────────────────────────────────────────

  const cargarDatos = useCallback(async () => {
    setCargando(true);
    try {
      const params = new URLSearchParams();
      if (filtroTipo) params.set('tipo', filtroTipo);
      if (filtroRelevancia) params.set('relevancia', filtroRelevancia);
      if (filtroEstado) params.set('estado', filtroEstado);
      if (filtroFuente) params.set('fuente', filtroFuente);
      params.set('limite', '50');

      const [alertasData, contadoresData] = await Promise.all([
        apiCliente.get<AlertaObservatorio[]>(`/observatorio/alertas?${params.toString()}`),
        apiCliente.get<ContadoresObservatorio>('/observatorio/alertas/contadores'),
      ]);
      setAlertas(alertasData);
      setContadores(contadoresData);
    } catch {
      // Si no hay datos, usar valores vacios
      setAlertas([]);
      setContadores({ total: 0, por_estado: {}, por_tipo: {}, por_relevancia: {}, por_fuente: {}, nuevas: 0, en_analisis: 0 });
    } finally {
      setCargando(false);
    }
  }, [filtroTipo, filtroRelevancia, filtroEstado, filtroFuente]);

  useEffect(() => {
    setDireccion(obtenerDireccionActiva());
    cargarDatos();
  }, [cargarDatos]);

  // ── Acciones ────────────────────────────────────────────────────────────

  const ejecutarCrawl = async () => {
    setEjecutandoCrawl(true);
    try {
      await apiCliente.post('/observatorio/crawl', {});
      await cargarDatos();
    } catch {
      // silenciar
    } finally {
      setEjecutandoCrawl(false);
    }
  };

  const cambiarEstado = async (alertaId: string, nuevoEstado: string) => {
    try {
      await apiCliente.put(`/observatorio/alertas/${alertaId}/estado`, { estado: nuevoEstado });
      await cargarDatos();
    } catch {
      // silenciar
    }
  };

  const iniciarAnalisis = (alerta: AlertaObservatorio) => {
    // Cambiar estado a EN_ANALISIS
    cambiarEstado(alerta.id, 'EN_ANALISIS');
    // Redirigir al chat con contexto de la alerta
    const contexto = encodeURIComponent(
      `Analiza esta alerta del Observatorio TIC:\n\nTitulo: ${alerta.titulo}\nTipo: ${alerta.tipo}\nRelevancia: ${alerta.relevancia}\nFuente: ${alerta.fuente_nombre}\nResumen: ${alerta.resumen}\nEntidades: ${(alerta.entidades_afectadas || []).join(', ')}\nURL: ${alerta.fuente_url}\n\nPor favor realiza un analisis detallado de esta alerta desde la perspectiva de control fiscal.`
    );
    window.location.href = `/chat?contexto=${contexto}`;
  };

  // ── Verificar acceso DES ────────────────────────────────────────────────

  if (direccion && direccion !== 'DES') {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <div className="text-center max-w-md">
          <ShieldAlert className="mx-auto h-16 w-16 text-[#2D3748] mb-4" />
          <h2 className="font-titulo text-xl font-semibold text-[#E8EAED] mb-2">
            Acceso restringido
          </h2>
          <p className="text-sm text-[#9AA0A6] mb-1">
            El Observatorio TIC esta disponible unicamente para la
            Direccion de Estudios Sectoriales (DES).
          </p>
          <p className="text-xs text-[#5F6368]">
            Si necesita acceso, contacte al administrador del sistema.
          </p>
        </div>
      </div>
    );
  }

  if (cargando) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#C9A84C] border-t-transparent" />
      </div>
    );
  }

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Encabezado */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="font-titulo text-xl font-bold text-[#E8EAED] flex items-center gap-2">
            <Eye className="h-6 w-6 text-[#1A5276]" />
            Observatorio TIC
          </h1>
          <p className="mt-1 text-xs text-[#5F6368]">
            Alertas inteligentes del sector TIC colombiano clasificadas por IA — DES
          </p>
        </div>
        <div className="flex gap-2">
          <Boton
            variante="secundario"
            tamano="sm"
            onClick={() => setMostrarFiltros(!mostrarFiltros)}
            className="text-[10px]"
          >
            <Filter className="h-3 w-3 mr-1" />
            Filtros
          </Boton>
          <Boton
            variante="primario"
            tamano="sm"
            onClick={ejecutarCrawl}
            disabled={ejecutandoCrawl}
            className="text-[10px]"
          >
            <RefreshCw className={`h-3 w-3 mr-1 ${ejecutandoCrawl ? 'animate-spin' : ''}`} />
            {ejecutandoCrawl ? 'Escaneando...' : 'Ejecutar crawl'}
          </Boton>
        </div>
      </div>

      {/* Contadores */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
        {[
          { titulo: 'Total alertas', valor: contadores?.total ?? 0, icono: Activity, color: '#C9A84C' },
          { titulo: 'Nuevas', valor: contadores?.nuevas ?? 0, icono: Zap, color: '#3B82F6' },
          { titulo: 'En analisis', valor: contadores?.en_analisis ?? 0, icono: FileSearch, color: '#F59E0B' },
          { titulo: 'Alta relevancia', valor: contadores?.por_relevancia?.ALTA ?? 0, icono: AlertTriangle, color: '#EF4444' },
          { titulo: 'Fuentes activas', valor: Object.keys(contadores?.por_fuente ?? {}).length, icono: Radio, color: '#10B981' },
        ].map((ind) => (
          <Tarjeta key={ind.titulo} className="p-3">
            <div className="flex items-center gap-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg"
                style={{ backgroundColor: `${ind.color}15` }}>
                <ind.icono className="h-4 w-4" style={{ color: ind.color }} />
              </div>
              <div>
                <p className="text-[9px] text-[#5F6368] uppercase tracking-wider">{ind.titulo}</p>
                <p className="text-lg font-bold text-[#E8EAED]">{ind.valor}</p>
              </div>
            </div>
          </Tarjeta>
        ))}
      </div>

      {/* Panel de filtros */}
      {mostrarFiltros && (
        <Tarjeta className="p-4 mb-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div>
              <label className="text-[10px] text-[#5F6368] uppercase tracking-wider mb-1 block">Tipo</label>
              <select
                value={filtroTipo}
                onChange={(e) => setFiltroTipo(e.target.value)}
                className="w-full rounded-md border border-[#2D3748] bg-[#0F1419] px-2 py-1.5 text-xs text-[#E8EAED] focus:border-[#C9A84C] focus:outline-none"
              >
                <option value="">Todos</option>
                <option value="REGULATORIA">Regulatoria</option>
                <option value="LEGISLATIVA">Legislativa</option>
                <option value="NOTICIA">Noticia</option>
                <option value="INDICADOR">Indicador</option>
              </select>
            </div>
            <div>
              <label className="text-[10px] text-[#5F6368] uppercase tracking-wider mb-1 block">Relevancia</label>
              <select
                value={filtroRelevancia}
                onChange={(e) => setFiltroRelevancia(e.target.value)}
                className="w-full rounded-md border border-[#2D3748] bg-[#0F1419] px-2 py-1.5 text-xs text-[#E8EAED] focus:border-[#C9A84C] focus:outline-none"
              >
                <option value="">Todas</option>
                <option value="ALTA">Alta</option>
                <option value="MEDIA">Media</option>
                <option value="BAJA">Baja</option>
              </select>
            </div>
            <div>
              <label className="text-[10px] text-[#5F6368] uppercase tracking-wider mb-1 block">Estado</label>
              <select
                value={filtroEstado}
                onChange={(e) => setFiltroEstado(e.target.value)}
                className="w-full rounded-md border border-[#2D3748] bg-[#0F1419] px-2 py-1.5 text-xs text-[#E8EAED] focus:border-[#C9A84C] focus:outline-none"
              >
                <option value="">Todos</option>
                <option value="NUEVA">Nueva</option>
                <option value="VISTA">Vista</option>
                <option value="EN_ANALISIS">En analisis</option>
                <option value="ARCHIVADA">Archivada</option>
              </select>
            </div>
            <div>
              <label className="text-[10px] text-[#5F6368] uppercase tracking-wider mb-1 block">Fuente</label>
              <select
                value={filtroFuente}
                onChange={(e) => setFiltroFuente(e.target.value)}
                className="w-full rounded-md border border-[#2D3748] bg-[#0F1419] px-2 py-1.5 text-xs text-[#E8EAED] focus:border-[#C9A84C] focus:outline-none"
              >
                <option value="">Todas</option>
                <option value="MinTIC">MinTIC</option>
                <option value="CRC">CRC</option>
                <option value="ANE">ANE</option>
                <option value="Congreso">Congreso</option>
                <option value="Noticias">Noticias TIC</option>
              </select>
            </div>
          </div>
        </Tarjeta>
      )}

      {/* Distribucion por tipo (mini graficos) */}
      {contadores && contadores.total > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          {Object.entries(contadores.por_tipo).map(([tipo, cantidad]) => {
            const porcentaje = contadores.total > 0 ? Math.round((cantidad / contadores.total) * 100) : 0;
            return (
              <Tarjeta key={tipo} className="p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-1.5">
                    {ICONOS_TIPO[tipo]}
                    <span className="text-[10px] font-medium text-[#9AA0A6]">{NOMBRES_TIPO[tipo] || tipo}</span>
                  </div>
                  <span className="text-xs font-bold text-[#E8EAED]">{cantidad}</span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-[#2D3748]/50">
                  <div
                    className="h-full rounded-full bg-[#C9A84C]"
                    style={{ width: `${porcentaje}%` }}
                  />
                </div>
              </Tarjeta>
            );
          })}
        </div>
      )}

      {/* Timeline de alertas */}
      <h2 className="font-titulo text-sm font-semibold text-[#E8EAED] mb-3 flex items-center gap-2">
        <Clock className="h-4 w-4 text-[#C9A84C]" />
        Alertas recientes ({alertas.length})
      </h2>

      {alertas.length === 0 ? (
        <Tarjeta className="p-8 text-center">
          <Eye className="mx-auto h-12 w-12 text-[#2D3748] mb-3" />
          <p className="text-sm text-[#9AA0A6] mb-1">No hay alertas{filtroTipo || filtroRelevancia || filtroEstado ? ' con los filtros seleccionados' : ' aun'}.</p>
          <p className="text-xs text-[#5F6368]">
            Ejecute un crawl para monitorear las fuentes TIC.
          </p>
        </Tarjeta>
      ) : (
        <div className="space-y-3">
          {alertas.map((alerta) => {
            const rel = COLORES_RELEVANCIA[alerta.relevancia] || COLORES_RELEVANCIA.BAJA;
            const est = COLORES_ESTADO[alerta.estado] || COLORES_ESTADO.NUEVA;
            const expandida = alertaExpandida === alerta.id;

            return (
              <Tarjeta
                key={alerta.id}
                className={`${rel.borde} border hover:border-opacity-60 transition-all cursor-pointer`}
                onClick={() => setAlertaExpandida(expandida ? null : alerta.id)}
              >
                <div className="p-4">
                  {/* Header de alerta */}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={rel.texto}>{ICONOS_TIPO[alerta.tipo]}</span>
                        <h3 className="text-sm font-medium text-[#E8EAED] truncate">
                          {alerta.titulo}
                        </h3>
                      </div>
                      <p className="text-xs text-[#9AA0A6] line-clamp-2 leading-relaxed">
                        {alerta.resumen}
                      </p>
                    </div>
                    <div className="flex flex-col items-end gap-1 flex-shrink-0">
                      <Insignia variante={rel.variante}>
                        {alerta.relevancia}
                      </Insignia>
                      <Insignia variante={est.variante}>
                        {alerta.estado.replace('_', ' ')}
                      </Insignia>
                      {expandida ? (
                        <ChevronUp className="h-3 w-3 text-[#5F6368]" />
                      ) : (
                        <ChevronDown className="h-3 w-3 text-[#5F6368]" />
                      )}
                    </div>
                  </div>

                  {/* Tags rapidos */}
                  <div className="flex items-center gap-2 mt-2 flex-wrap">
                    <span className="text-[9px] text-[#5F6368] flex items-center gap-1">
                      <Radio className="h-2.5 w-2.5" /> {alerta.fuente_nombre}
                    </span>
                    <span className="text-[9px] text-[#5F6368]">|</span>
                    <span className="text-[9px] text-[#5F6368]">
                      {NOMBRES_TIPO[alerta.tipo]} · {NOMBRES_IMPACTO[alerta.tipo_impacto] || alerta.tipo_impacto}
                    </span>
                    <span className="text-[9px] text-[#5F6368]">|</span>
                    <span className="text-[9px] text-[#5F6368] flex items-center gap-1">
                      <Clock className="h-2.5 w-2.5" />
                      {new Date(alerta.fecha_deteccion).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })}
                    </span>
                  </div>

                  {/* Detalle expandido */}
                  {expandida && (
                    <div className="mt-4 pt-3 border-t border-[#2D3748]/30 space-y-3" onClick={(e) => e.stopPropagation()}>
                      {/* Entidades afectadas */}
                      {alerta.entidades_afectadas && alerta.entidades_afectadas.length > 0 && (
                        <div>
                          <p className="text-[10px] text-[#5F6368] uppercase tracking-wider mb-1.5 flex items-center gap-1">
                            <Building2 className="h-3 w-3" /> Entidades afectadas
                          </p>
                          <div className="flex flex-wrap gap-1.5">
                            {alerta.entidades_afectadas.map((entidad, idx) => (
                              <span
                                key={idx}
                                className="rounded-full px-2 py-0.5 text-[10px] font-medium bg-[#1A5276]/20 text-[#5DADE2] border border-[#1A5276]/30"
                              >
                                {entidad}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Impacto */}
                      <div className="grid grid-cols-3 gap-2">
                        <div className="rounded-lg bg-[#0A0F14]/60 p-2.5">
                          <p className="text-[9px] text-[#5F6368] mb-0.5">Tipo impacto</p>
                          <p className="text-xs font-medium text-[#E8EAED]">
                            {NOMBRES_IMPACTO[alerta.tipo_impacto] || alerta.tipo_impacto}
                          </p>
                        </div>
                        <div className="rounded-lg bg-[#0A0F14]/60 p-2.5">
                          <p className="text-[9px] text-[#5F6368] mb-0.5">Relevancia</p>
                          <p className={`text-xs font-medium ${rel.texto}`}>{alerta.relevancia}</p>
                        </div>
                        <div className="rounded-lg bg-[#0A0F14]/60 p-2.5">
                          <p className="text-[9px] text-[#5F6368] mb-0.5">Fuente</p>
                          <p className="text-xs font-medium text-[#E8EAED]">{alerta.fuente_nombre}</p>
                        </div>
                      </div>

                      {/* Acciones */}
                      <div className="flex items-center gap-2 pt-1">
                        <Boton
                          variante="primario"
                          tamano="sm"
                          onClick={() => iniciarAnalisis(alerta)}
                          className="text-[10px]"
                        >
                          <MessageSquare className="h-3 w-3 mr-1" />
                          Iniciar analisis
                        </Boton>
                        {alerta.fuente_url && (
                          <Boton
                            variante="secundario"
                            tamano="sm"
                            onClick={() => window.open(alerta.fuente_url, '_blank')}
                            className="text-[10px]"
                          >
                            <ExternalLink className="h-3 w-3 mr-1" />
                            Ver fuente
                          </Boton>
                        )}
                        {alerta.estado === 'NUEVA' && (
                          <Boton
                            variante="fantasma"
                            tamano="sm"
                            onClick={() => cambiarEstado(alerta.id, 'VISTA')}
                            className="text-[10px]"
                          >
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Marcar vista
                          </Boton>
                        )}
                        {alerta.estado !== 'ARCHIVADA' && (
                          <Boton
                            variante="fantasma"
                            tamano="sm"
                            onClick={() => cambiarEstado(alerta.id, 'ARCHIVADA')}
                            className="text-[10px]"
                          >
                            <Archive className="h-3 w-3 mr-1" />
                            Archivar
                          </Boton>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </Tarjeta>
            );
          })}
        </div>
      )}
    </div>
  );
}
