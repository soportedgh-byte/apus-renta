'use client';

/**
 * CecilIA v2 — Dashboard Ejecutivo de Analitica
 * Contraloria General de la Republica de Colombia
 *
 * Archivo: app/(dashboard)/analytics/page.tsx
 * Proposito: Graficas Recharts, KPIs, comparativo DES vs DVF,
 *            exportacion Excel/DOCX/CSV, reporte Circular 023.
 * Sprint: 10
 * Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
 * Fecha: Abril 2026
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  BarChart3,
  MessageSquare,
  Users,
  FileCheck,
  GraduationCap,
  TrendingUp,
  Clock,
  FileSpreadsheet,
  FileText,
  Shield,
  Download,
  RefreshCw,
  ThumbsUp,
  ThumbsDown,
  AlertTriangle,
  ShieldAlert,
  ChevronDown,
  Loader2,
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Tarjeta } from '@/components/ui/card';
import { esDirector, esAdmin, esCoordinador, esLiderTecnico } from '@/lib/auth';
import apiCliente from '@/lib/api';

/* ============================================================
   TIPOS
   ============================================================ */

interface MetricasUso {
  total_consultas: number;
  usuarios_activos: number;
  consultas_hoy: number;
  consultas_semana: number;
  consultas_mes: number;
  por_direccion: Record<string, number>;
  por_fase: Record<string, number>;
  periodo_inicio: string;
  periodo_fin: string;
}

interface ConsultaPorDia {
  fecha: string;
  total: number;
}

interface MetricasAuditoria {
  total_auditorias: number;
  auditorias_por_fase: Record<string, number>;
  auditorias_por_tipo: Record<string, number>;
  total_hallazgos: number;
  hallazgos_por_estado: Record<string, number>;
  hallazgos_por_connotacion: Record<string, number>;
  hallazgos_generados_ia: number;
  hallazgos_validados_humano: number;
  tasa_hallazgos_aprobados: number;
  cuantia_total_presunto_dano: number;
  total_formatos: number;
  formatos_generados_ia: number;
}

interface MetricasCalidad {
  feedback_positivo: number;
  feedback_negativo: number;
  feedback_neutral: number;
  total_con_feedback: number;
  tasa_satisfaccion: number;
  total_respuestas: number;
  respuestas_con_fuentes: number;
  cobertura_fuentes: number;
  total_hallazgos: number;
  hallazgos_aprobados: number;
  tasa_hallazgos_aprobados: number;
}

interface MetricasCapacitacion {
  total_funcionarios_capacitados: number;
  lecciones_completadas: number;
  total_quizzes: number;
  quizzes_aprobados: number;
  tasa_aprobacion_quizzes: number;
  promedio_puntaje: number;
  rutas_activas: number;
  por_ruta: Array<{
    ruta_id: string;
    ruta_nombre: string;
    aprendices: number;
    promedio_avance: number;
    promedio_quiz: number;
  }>;
}

interface ComparativoDESvsDVF {
  des: Record<string, number>;
  dvf: Record<string, number>;
}

/* ============================================================
   COLORES INSTITUCIONALES
   ============================================================ */

const COLORES = {
  des: '#1A5276',
  desLight: '#2471A3',
  dvf: '#1E8449',
  dvfLight: '#27AE60',
  oro: '#C9A84C',
  fondo: '#0F1419',
  card: '#1A2332',
  muted: '#6B7B8D',
  texto: '#E8E8E8',
};

const COLORES_CONNOTACION: Record<string, string> = {
  administrativo: '#3498DB',
  fiscal: '#E74C3C',
  disciplinario: '#F39C12',
  penal: '#8E44AD',
};

const COLORES_FASE: string[] = [
  '#2471A3', '#27AE60', '#C9A84C', '#E74C3C', '#8E44AD', '#F39C12',
];

/* ============================================================
   COMPONENTE PRINCIPAL
   ============================================================ */

export default function PaginaAnalytics() {
  const [tieneAcceso, setTieneAcceso] = useState(true);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Datos
  const [uso, setUso] = useState<MetricasUso | null>(null);
  const [consultasDia, setConsultasDia] = useState<ConsultaPorDia[]>([]);
  const [auditoria, setAuditoria] = useState<MetricasAuditoria | null>(null);
  const [calidad, setCalidad] = useState<MetricasCalidad | null>(null);
  const [capacitacion, setCapacitacion] = useState<MetricasCapacitacion | null>(null);
  const [comparativo, setComparativo] = useState<ComparativoDESvsDVF | null>(null);

  // Estado de exportacion
  const [exportando, setExportando] = useState<string | null>(null);

  // Periodo
  const [periodo, setPeriodo] = useState<'30' | '90' | '365'>('30');

  useEffect(() => {
    setTieneAcceso(esDirector() || esAdmin() || esCoordinador() || esLiderTecnico());
  }, []);

  const cargarDatos = useCallback(async () => {
    setCargando(true);
    setError(null);
    try {
      const params = `?dias=${periodo}`;
      const [rUso, rDia, rAud, rCal, rCap, rComp] = await Promise.allSettled([
        apiCliente.get(`/analytics/uso${params}`),
        apiCliente.get(`/analytics/uso/consultas-por-dia${params}`),
        apiCliente.get(`/analytics/auditorias${params}`),
        apiCliente.get(`/analytics/calidad${params}`),
        apiCliente.get(`/analytics/capacitacion${params}`),
        apiCliente.get(`/analytics/uso/comparativo-des-dvf${params}`),
      ]);

      if (rUso.status === 'fulfilled') setUso(rUso.value as MetricasUso);
      if (rDia.status === 'fulfilled') {
        const d = rDia.value as { serie?: ConsultaPorDia[] };
        setConsultasDia(d?.serie || []);
      }
      if (rAud.status === 'fulfilled') setAuditoria(rAud.value as MetricasAuditoria);
      if (rCal.status === 'fulfilled') setCalidad(rCal.value as MetricasCalidad);
      if (rCap.status === 'fulfilled') setCapacitacion(rCap.value as MetricasCapacitacion);
      if (rComp.status === 'fulfilled') setComparativo(rComp.value as ComparativoDESvsDVF);
    } catch (err) {
      setError('Error al cargar metricas. Intente de nuevo.');
      console.error('[CecilIA] Error cargando analytics:', err);
    } finally {
      setCargando(false);
    }
  }, [periodo]);

  useEffect(() => {
    if (tieneAcceso) cargarDatos();
  }, [tieneAcceso, cargarDatos]);

  /* ------- Exportar archivos ------- */

  const descargarArchivo = async (url: string, nombreArchivo: string, tipo: string) => {
    setExportando(tipo);
    try {
      const response = await fetch(`/api${url}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('cecilia_token')}`,
        },
      });
      if (!response.ok) throw new Error('Error al descargar');
      const blob = await response.blob();
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = nombreArchivo;
      link.click();
      URL.revokeObjectURL(link.href);
    } catch (err) {
      console.error('[CecilIA] Error exportando:', err);
    } finally {
      setExportando(null);
    }
  };

  /* ------- Acceso restringido ------- */

  if (!tieneAcceso) {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <div className="text-center max-w-md">
          <ShieldAlert className="mx-auto h-16 w-16 text-[#2D3748] mb-4" />
          <h2 className="font-titulo text-xl font-semibold text-[#E8EAED] mb-2">
            Acceso restringido
          </h2>
          <p className="text-sm text-[#9AA0A6]">
            Las metricas y analitica estan disponibles unicamente para directores, coordinadores y administradores.
          </p>
        </div>
      </div>
    );
  }

  /* ------- Datos para graficas ------- */

  const datosConnotacion = auditoria
    ? Object.entries(auditoria.hallazgos_por_connotacion).map(([k, v]) => ({
        nombre: k.charAt(0).toUpperCase() + k.slice(1),
        valor: v,
      }))
    : [];

  const datosFaseAuditoria = auditoria
    ? Object.entries(auditoria.auditorias_por_fase).map(([k, v]) => ({
        nombre: k || 'Sin fase',
        valor: v,
      }))
    : [];

  // Backend retorna {"DES": {...}, "DVF": {...}} con claves conversaciones, usuarios_activos, mensajes
  const compDES = (comparativo as Record<string, Record<string, number>> | null)?.['DES'];
  const compDVF = (comparativo as Record<string, Record<string, number>> | null)?.['DVF'];
  const datosComparativo = comparativo
    ? [
        {
          metrica: 'Conversaciones',
          DES: compDES?.conversaciones || 0,
          DVF: compDVF?.conversaciones || 0,
        },
        {
          metrica: 'Mensajes',
          DES: compDES?.mensajes || 0,
          DVF: compDVF?.mensajes || 0,
        },
        {
          metrica: 'Usuarios',
          DES: compDES?.usuarios_activos || 0,
          DVF: compDVF?.usuarios_activos || 0,
        },
      ]
    : [];

  /* ------- Formateo ------- */
  const fmt = (n: number) => n?.toLocaleString('es-CO') ?? '0';
  const fmtPesos = (n: number) =>
    new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n || 0);

  return (
    <div className="p-4 md:p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* ============ ENCABEZADO ============ */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="font-titulo text-xl font-bold text-[#E8EAED] flex items-center gap-2">
            <BarChart3 className="h-6 w-6 text-[#C9A84C]" />
            Dashboard Ejecutivo
          </h1>
          <p className="mt-1 text-xs text-[#5F6368]">
            Metricas de uso, auditoria, calidad y capacitacion — Contraloria General de la Republica
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {/* Selector de periodo */}
          <div className="relative">
            <select
              value={periodo}
              onChange={(e) => setPeriodo(e.target.value as '30' | '90' | '365')}
              className="appearance-none rounded-lg border border-[#2D3748] bg-[#1A2332] px-3 py-2 pr-8 text-xs text-[#E8EAED] focus:border-[#C9A84C]/50 focus:outline-none"
            >
              <option value="30">Ultimos 30 dias</option>
              <option value="90">Ultimos 90 dias</option>
              <option value="365">Ultimo ano</option>
            </select>
            <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[#5F6368] pointer-events-none" />
          </div>

          {/* Boton refrescar */}
          <button
            onClick={cargarDatos}
            disabled={cargando}
            className="rounded-lg border border-[#2D3748] bg-[#1A2332] p-2 text-[#9AA0A6] hover:text-[#E8EAED] hover:border-[#C9A84C]/30 transition-colors disabled:opacity-50"
            title="Actualizar datos"
          >
            <RefreshCw className={`h-4 w-4 ${cargando ? 'animate-spin' : ''}`} />
          </button>

          {/* Botones de exportacion */}
          <button
            onClick={() => descargarArchivo('/analytics/exportar', 'cecilia_analytics.xlsx', 'excel')}
            disabled={!!exportando}
            className="flex items-center gap-1.5 rounded-lg border border-[#2D3748] bg-[#1A2332] px-3 py-2 text-xs text-[#9AA0A6] hover:text-[#27AE60] hover:border-[#27AE60]/30 transition-colors disabled:opacity-50"
          >
            {exportando === 'excel' ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <FileSpreadsheet className="h-3.5 w-3.5" />}
            Excel
          </button>

          <button
            onClick={() => descargarArchivo('/analytics/informe-ejecutivo', 'informe_ejecutivo.docx', 'docx')}
            disabled={!!exportando}
            className="flex items-center gap-1.5 rounded-lg border border-[#2D3748] bg-[#1A2332] px-3 py-2 text-xs text-[#9AA0A6] hover:text-[#2471A3] hover:border-[#2471A3]/30 transition-colors disabled:opacity-50"
          >
            {exportando === 'docx' ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <FileText className="h-3.5 w-3.5" />}
            Informe DOCX
          </button>

          <button
            onClick={() => descargarArchivo('/analytics/reporte-circular-023?formato=docx', 'reporte_circular_023.docx', 'c023')}
            disabled={!!exportando}
            className="flex items-center gap-1.5 rounded-lg border border-[#C9A84C]/30 bg-[#C9A84C]/10 px-3 py-2 text-xs text-[#C9A84C] hover:bg-[#C9A84C]/20 transition-colors disabled:opacity-50"
          >
            {exportando === 'c023' ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Shield className="h-3.5 w-3.5" />}
            Circular 023
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-red-400/20 bg-red-400/5 px-4 py-3 flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-red-400" />
          <span className="text-xs text-red-400">{error}</span>
        </div>
      )}

      {/* ============ KPIs PRINCIPALES ============ */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <KPICard
          titulo="Total Consultas"
          valor={fmt(uso?.total_consultas || 0)}
          subtitulo={`${fmt(uso?.consultas_hoy || 0)} hoy`}
          icono={MessageSquare}
          color="#C9A84C"
          cargando={cargando}
        />
        <KPICard
          titulo="Usuarios Activos"
          valor={fmt(uso?.usuarios_activos || 0)}
          subtitulo={`${periodo} dias`}
          icono={Users}
          color="#2471A3"
          cargando={cargando}
        />
        <KPICard
          titulo="Hallazgos Generados"
          valor={fmt(auditoria?.total_hallazgos || 0)}
          subtitulo={`${auditoria?.tasa_hallazgos_aprobados || 0}% aprobados`}
          icono={FileCheck}
          color="#27AE60"
          cargando={cargando}
        />
        <KPICard
          titulo="Formatos Producidos"
          valor={fmt(auditoria?.total_formatos || 0)}
          subtitulo={`${fmt(auditoria?.formatos_generados_ia || 0)} con IA`}
          icono={FileText}
          color="#E74C3C"
          cargando={cargando}
        />
        <KPICard
          titulo="Funcionarios Capacitados"
          valor={fmt(capacitacion?.total_funcionarios_capacitados || 0)}
          subtitulo={`${capacitacion?.rutas_activas || 0} rutas activas`}
          icono={GraduationCap}
          color="#8E44AD"
          cargando={cargando}
        />
      </div>

      {/* ============ GRAFICAS FILA 1: Tendencia + Connotaciones ============ */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Consultas por dia */}
        <Tarjeta className="p-5">
          <h3 className="text-sm font-medium text-[#E8EAED] mb-4 flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-[#27AE60]" />
            Consultas por dia
          </h3>
          {cargando ? (
            <PlaceholderGrafica />
          ) : consultasDia.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={consultasDia}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2D3748" />
                <XAxis
                  dataKey="fecha"
                  tick={{ fill: '#5F6368', fontSize: 10 }}
                  tickFormatter={(v: string) => v.slice(5)}
                />
                <YAxis tick={{ fill: '#5F6368', fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1A2332', border: '1px solid #2D3748', borderRadius: 8, fontSize: 11 }}
                  labelStyle={{ color: '#E8EAED' }}
                  itemStyle={{ color: '#C9A84C' }}
                />
                <Line
                  type="monotone"
                  dataKey="total"
                  stroke="#C9A84C"
                  strokeWidth={2}
                  dot={{ fill: '#C9A84C', r: 3 }}
                  activeDot={{ r: 5, fill: '#C9A84C' }}
                  name="Consultas"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <PlaceholderSinDatos />
          )}
        </Tarjeta>

        {/* Hallazgos por connotacion */}
        <Tarjeta className="p-5">
          <h3 className="text-sm font-medium text-[#E8EAED] mb-4 flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-[#E74C3C]" />
            Hallazgos por connotacion
          </h3>
          {cargando ? (
            <PlaceholderGrafica />
          ) : datosConnotacion.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={datosConnotacion} barSize={40}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2D3748" />
                <XAxis dataKey="nombre" tick={{ fill: '#5F6368', fontSize: 10 }} />
                <YAxis tick={{ fill: '#5F6368', fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1A2332', border: '1px solid #2D3748', borderRadius: 8, fontSize: 11 }}
                  labelStyle={{ color: '#E8EAED' }}
                />
                <Bar dataKey="valor" name="Hallazgos" radius={[4, 4, 0, 0]}>
                  {datosConnotacion.map((entry, i) => (
                    <Cell key={i} fill={COLORES_CONNOTACION[entry.nombre.toLowerCase()] || '#6B7B8D'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <PlaceholderSinDatos />
          )}
        </Tarjeta>
      </div>

      {/* ============ GRAFICAS FILA 2: Fases auditoria (pie) + Comparativo DES vs DVF ============ */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Fases auditoria - pie chart */}
        <Tarjeta className="p-5">
          <h3 className="text-sm font-medium text-[#E8EAED] mb-4 flex items-center gap-2">
            <Clock className="h-4 w-4 text-[#F39C12]" />
            Auditorias por fase
          </h3>
          {cargando ? (
            <PlaceholderGrafica />
          ) : datosFaseAuditoria.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={datosFaseAuditoria}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="valor"
                  nameKey="nombre"
                  label={({ nombre, valor }: { nombre: string; valor: number }) => `${nombre}: ${valor}`}
                  labelLine={{ stroke: '#5F6368' }}
                >
                  {datosFaseAuditoria.map((_, i) => (
                    <Cell key={i} fill={COLORES_FASE[i % COLORES_FASE.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1A2332', border: '1px solid #2D3748', borderRadius: 8, fontSize: 11 }}
                />
                <Legend
                  wrapperStyle={{ fontSize: 10, color: '#9AA0A6' }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <PlaceholderSinDatos />
          )}
        </Tarjeta>

        {/* Comparativo DES vs DVF */}
        <Tarjeta className="p-5">
          <h3 className="text-sm font-medium text-[#E8EAED] mb-4 flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-[#2471A3]" />
            Comparativo DES vs DVF
          </h3>
          {cargando ? (
            <PlaceholderGrafica />
          ) : datosComparativo.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={datosComparativo} barGap={4}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2D3748" />
                <XAxis dataKey="metrica" tick={{ fill: '#5F6368', fontSize: 10 }} />
                <YAxis tick={{ fill: '#5F6368', fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1A2332', border: '1px solid #2D3748', borderRadius: 8, fontSize: 11 }}
                  labelStyle={{ color: '#E8EAED' }}
                />
                <Legend wrapperStyle={{ fontSize: 10 }} />
                <Bar dataKey="DES" fill={COLORES.des} radius={[4, 4, 0, 0]} name="DES" />
                <Bar dataKey="DVF" fill={COLORES.dvf} radius={[4, 4, 0, 0]} name="DVF" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <PlaceholderSinDatos />
          )}
        </Tarjeta>
      </div>

      {/* ============ FILA 3: Calidad + Capacitacion ============ */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Calidad de respuestas */}
        <Tarjeta className="p-5">
          <h3 className="text-sm font-medium text-[#E8EAED] mb-4 flex items-center gap-2">
            <ThumbsUp className="h-4 w-4 text-[#27AE60]" />
            Calidad de Respuestas
          </h3>
          {cargando ? (
            <PlaceholderGrafica />
          ) : calidad ? (
            <div className="space-y-4">
              {/* Barra de satisfaccion */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-[#9AA0A6]">Tasa de satisfaccion</span>
                  <span className="text-sm font-bold text-[#E8EAED]">{calidad.tasa_satisfaccion}%</span>
                </div>
                <div className="h-3 rounded-full bg-[#0A0F14] overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${calidad.tasa_satisfaccion}%`,
                      backgroundColor: calidad.tasa_satisfaccion >= 80 ? '#27AE60' : calidad.tasa_satisfaccion >= 60 ? '#F39C12' : '#E74C3C',
                    }}
                  />
                </div>
              </div>

              {/* Feedback breakdown */}
              <div className="grid grid-cols-3 gap-3">
                <div className="rounded-lg bg-green-400/5 border border-green-400/10 p-3 text-center">
                  <ThumbsUp className="h-4 w-4 text-green-400 mx-auto mb-1" />
                  <p className="text-lg font-bold text-green-400">{fmt(calidad.feedback_positivo)}</p>
                  <p className="text-[9px] text-[#5F6368]">Positivos</p>
                </div>
                <div className="rounded-lg bg-red-400/5 border border-red-400/10 p-3 text-center">
                  <ThumbsDown className="h-4 w-4 text-red-400 mx-auto mb-1" />
                  <p className="text-lg font-bold text-red-400">{fmt(calidad.feedback_negativo)}</p>
                  <p className="text-[9px] text-[#5F6368]">Negativos</p>
                </div>
                <div className="rounded-lg bg-[#C9A84C]/5 border border-[#C9A84C]/10 p-3 text-center">
                  <FileCheck className="h-4 w-4 text-[#C9A84C] mx-auto mb-1" />
                  <p className="text-lg font-bold text-[#C9A84C]">{calidad.cobertura_fuentes}%</p>
                  <p className="text-[9px] text-[#5F6368]">Con fuentes</p>
                </div>
              </div>

              {/* Hallazgos aprobados */}
              <div className="flex items-center justify-between pt-2 border-t border-[#2D3748]/30">
                <span className="text-xs text-[#9AA0A6]">Hallazgos aprobados</span>
                <span className="text-xs font-medium text-[#E8EAED]">
                  {fmt(calidad.hallazgos_aprobados)}/{fmt(calidad.total_hallazgos)} ({calidad.tasa_hallazgos_aprobados}%)
                </span>
              </div>
            </div>
          ) : (
            <PlaceholderSinDatos />
          )}
        </Tarjeta>

        {/* Capacitacion */}
        <Tarjeta className="p-5">
          <h3 className="text-sm font-medium text-[#E8EAED] mb-4 flex items-center gap-2">
            <GraduationCap className="h-4 w-4 text-[#8E44AD]" />
            Modulo de Capacitacion
          </h3>
          {cargando ? (
            <PlaceholderGrafica />
          ) : capacitacion ? (
            <div className="space-y-4">
              {/* Stats principales */}
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg bg-[#8E44AD]/5 border border-[#8E44AD]/10 p-3">
                  <p className="text-lg font-bold text-[#8E44AD]">{fmt(capacitacion.lecciones_completadas)}</p>
                  <p className="text-[9px] text-[#5F6368]">Lecciones completadas</p>
                </div>
                <div className="rounded-lg bg-[#2471A3]/5 border border-[#2471A3]/10 p-3">
                  <p className="text-lg font-bold text-[#2471A3]">{capacitacion.tasa_aprobacion_quizzes}%</p>
                  <p className="text-[9px] text-[#5F6368]">Tasa aprobacion quizzes</p>
                </div>
              </div>

              {/* Detalle por ruta */}
              {capacitacion.por_ruta.length > 0 && (
                <div>
                  <p className="text-[10px] font-medium text-[#5F6368] uppercase tracking-wider mb-2">Rutas de aprendizaje</p>
                  <div className="space-y-2">
                    {capacitacion.por_ruta.map((ruta) => (
                      <div key={ruta.ruta_id} className="rounded-lg bg-[#0A0F14]/60 border border-[#2D3748]/30 px-3 py-2">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs text-[#E8EAED] truncate max-w-[60%]">{ruta.ruta_nombre}</span>
                          <span className="text-[10px] text-[#9AA0A6]">{ruta.aprendices} aprendices</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="flex-1 h-1.5 rounded-full bg-[#2D3748] overflow-hidden">
                            <div
                              className="h-full rounded-full bg-[#8E44AD] transition-all"
                              style={{ width: `${ruta.promedio_avance}%` }}
                            />
                          </div>
                          <span className="text-[10px] text-[#9AA0A6] w-10 text-right">{ruta.promedio_avance}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <PlaceholderSinDatos />
          )}
        </Tarjeta>
      </div>

      {/* ============ FILA 4: Cuantia + Resumen auditoria ============ */}
      {auditoria && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Tarjeta className="p-5">
            <p className="text-[10px] text-[#5F6368] uppercase tracking-wider mb-1">Cuantia Total Presunto Dano</p>
            <p className="text-xl font-bold text-[#E74C3C]">{fmtPesos(auditoria.cuantia_total_presunto_dano)}</p>
            <p className="text-[10px] text-[#5F6368] mt-1">Acumulado en el periodo</p>
          </Tarjeta>
          <Tarjeta className="p-5">
            <p className="text-[10px] text-[#5F6368] uppercase tracking-wider mb-1">Hallazgos IA</p>
            <p className="text-xl font-bold text-[#C9A84C]">{fmt(auditoria.hallazgos_generados_ia)}</p>
            <p className="text-[10px] text-[#5F6368] mt-1">
              {fmt(auditoria.hallazgos_validados_humano)} validados por humano
            </p>
          </Tarjeta>
          <Tarjeta className="p-5">
            <p className="text-[10px] text-[#5F6368] uppercase tracking-wider mb-1">Total Auditorias</p>
            <p className="text-xl font-bold text-[#2471A3]">{fmt(auditoria.total_auditorias)}</p>
            <p className="text-[10px] text-[#5F6368] mt-1">
              {Object.keys(auditoria.auditorias_por_tipo || {}).length} tipos diferentes
            </p>
          </Tarjeta>
        </div>
      )}

      {/* Disclaimer */}
      <p className="text-[9px] text-[#5F6368] text-center">
        Asistido por IA — Requiere validacion humana. Circular 023 CGR.
        Los datos reflejan el uso real del sistema CecilIA v2.
      </p>
    </div>
  );
}

/* ============================================================
   COMPONENTES AUXILIARES
   ============================================================ */

function KPICard({
  titulo,
  valor,
  subtitulo,
  icono: Icono,
  color,
  cargando,
}: {
  titulo: string;
  valor: string;
  subtitulo: string;
  icono: React.ElementType;
  color: string;
  cargando: boolean;
}) {
  return (
    <Tarjeta className="p-4">
      <div className="flex items-center justify-between mb-3">
        <div
          className="flex h-9 w-9 items-center justify-center rounded-lg"
          style={{ backgroundColor: `${color}15` }}
        >
          <Icono className="h-4.5 w-4.5" style={{ color }} />
        </div>
      </div>
      {cargando ? (
        <div className="h-8 w-20 rounded bg-[#2D3748] animate-pulse" />
      ) : (
        <p className="text-2xl font-bold text-[#E8EAED]">{valor}</p>
      )}
      <p className="text-[10px] text-[#5F6368] mt-1">{titulo}</p>
      <p className="text-[9px] text-[#5F6368]/60">{subtitulo}</p>
    </Tarjeta>
  );
}

function PlaceholderGrafica() {
  return (
    <div className="flex h-[220px] items-center justify-center rounded-lg bg-[#0A0F14]/60 border border-[#2D3748]/30">
      <Loader2 className="h-6 w-6 text-[#5F6368] animate-spin" />
    </div>
  );
}

function PlaceholderSinDatos() {
  return (
    <div className="flex h-[220px] items-center justify-center rounded-lg bg-[#0A0F14]/60 border border-[#2D3748]/30">
      <p className="text-xs text-[#5F6368]">Sin datos disponibles para el periodo seleccionado</p>
    </div>
  );
}
