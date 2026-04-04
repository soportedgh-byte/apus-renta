'use client';

/**
 * CecilIA v2 — Modulo de Capacitacion
 * Pagina principal: rutas de aprendizaje, progreso y acceso a lecciones
 * Sprint 6
 */

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  BookOpen, Clock, CheckCircle, Award, Trophy,
  ChevronRight, Download, FileText, Headphones,
  BookMarked, BarChart3, Sparkles,
} from 'lucide-react';
import { obtenerUsuario } from '@/lib/auth';
import { apiCliente } from '@/lib/api';
import type { RutaAprendizaje } from '@/lib/types';

// ── Datos demo (fallback si API no responde) ────────────────────────────────
const RUTAS_DEMO: RutaAprendizaje[] = [
  {
    id: 'ruta-001', nombre: 'Conoce la CGR', descripcion: 'Estructura, mision y funcionamiento de la Contraloria General',
    icono: '🏛️', color: '#1A5276', direccion: 'TODOS', orden: 1, activa: true, total_lecciones: 6, created_at: '',
  },
  {
    id: 'ruta-002', nombre: 'Auditoria DVF - Paso a paso', descripcion: 'Las 5 fases del proceso auditor y los 30 formatos de la GAF',
    icono: '🔍', color: '#C9A84C', direccion: 'DVF', orden: 2, activa: true, total_lecciones: 10, created_at: '',
  },
  {
    id: 'ruta-003', nombre: 'Estudios Sectoriales DES', descripcion: 'Control fiscal macro, estudios sectoriales y alertas tempranas',
    icono: '📊', color: '#27AE60', direccion: 'DES', orden: 3, activa: true, total_lecciones: 7, created_at: '',
  },
  {
    id: 'ruta-004', nombre: 'Normativa Esencial', descripcion: 'Leyes, decretos y ISSAI fundamentales para el control fiscal',
    icono: '⚖️', color: '#8E44AD', direccion: 'TODOS', orden: 4, activa: true, total_lecciones: 8, created_at: '',
  },
];

const PROGRESO_DEMO: Record<string, { completadas: number; porcentaje: number }> = {
  'ruta-001': { completadas: 3, porcentaje: 50 },
  'ruta-002': { completadas: 1, porcentaje: 10 },
  'ruta-003': { completadas: 0, porcentaje: 0 },
  'ruta-004': { completadas: 0, porcentaje: 0 },
};

// ── Componente: Tarjeta de Ruta ─────────────────────────────────────────────
function TarjetaRuta({
  ruta,
  progreso,
}: {
  ruta: RutaAprendizaje;
  progreso: { completadas: number; porcentaje: number };
}) {
  const estaCompleta = progreso.porcentaje === 100;
  const enProgreso = progreso.porcentaje > 0 && progreso.porcentaje < 100;

  return (
    <Link
      href={`/capacitacion/${ruta.id}/${ruta.id}-1`}
      className="group relative flex flex-col rounded-xl border border-[#2D3748]/50 bg-[#1A2332]/60 p-5 transition-all hover:border-opacity-80 hover:bg-[#1A2332]/80 hover:shadow-lg"
      style={{ borderColor: `${ruta.color}30` }}
    >
      {/* Badge estado */}
      {estaCompleta && (
        <div className="absolute -top-2 -right-2 flex h-7 w-7 items-center justify-center rounded-full bg-green-500/20 border border-green-500/40">
          <Trophy className="h-3.5 w-3.5 text-green-400" />
        </div>
      )}

      {/* Icono + Nombre */}
      <div className="flex items-start gap-3 mb-3">
        <div
          className="flex h-12 w-12 items-center justify-center rounded-xl text-2xl"
          style={{ backgroundColor: `${ruta.color}15`, border: `1px solid ${ruta.color}30` }}
        >
          {ruta.icono}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-[#E8EAED] group-hover:text-white transition-colors">
            {ruta.nombre}
          </h3>
          <span
            className="inline-block mt-1 rounded-full px-2 py-0.5 text-[9px] font-semibold"
            style={{ backgroundColor: `${ruta.color}20`, color: ruta.color }}
          >
            {ruta.direccion}
          </span>
        </div>
      </div>

      {/* Descripcion */}
      <p className="text-xs text-[#9AA0A6] mb-4 line-clamp-2">{ruta.descripcion}</p>

      {/* Info lecciones */}
      <div className="flex items-center gap-3 text-[10px] text-[#5F6368] mb-3">
        <span className="flex items-center gap-1">
          <BookOpen className="h-3 w-3" />
          {ruta.total_lecciones} lecciones
        </span>
        <span className="flex items-center gap-1">
          <Clock className="h-3 w-3" />
          ~{ruta.total_lecciones * 15} min
        </span>
      </div>

      {/* Barra de progreso */}
      <div className="mt-auto">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[10px] text-[#9AA0A6]">
            {progreso.completadas}/{ruta.total_lecciones} completadas
          </span>
          <span className="text-[10px] font-semibold" style={{ color: ruta.color }}>
            {progreso.porcentaje}%
          </span>
        </div>
        <div className="h-1.5 rounded-full bg-[#2D3748]/50 overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700 ease-out"
            style={{ width: `${progreso.porcentaje}%`, backgroundColor: ruta.color }}
          />
        </div>
      </div>

      {/* CTA */}
      <div className="mt-3 flex items-center justify-end">
        <span
          className="flex items-center gap-1 text-[10px] font-medium opacity-0 group-hover:opacity-100 transition-opacity"
          style={{ color: ruta.color }}
        >
          {enProgreso ? 'Continuar' : estaCompleta ? 'Repasar' : 'Comenzar'}
          <ChevronRight className="h-3 w-3" />
        </span>
      </div>
    </Link>
  );
}

// ── Componente: Acciones rapidas ────────────────────────────────────────────
function AccionesRapidas() {
  const acciones = [
    { icono: FileText, etiqueta: 'Generar manual', color: '#C9A84C', endpoint: 'generar-manual' },
    { icono: Headphones, etiqueta: 'Script podcast', color: '#2471A3', endpoint: 'generar-podcast-script' },
    { icono: BookMarked, etiqueta: 'Glosario fiscal', color: '#27AE60', endpoint: 'generar-glosario' },
    { icono: Sparkles, etiqueta: 'Guia formato', color: '#8E44AD', endpoint: 'generar-guia-formato' },
  ];

  const descargar = async (endpoint: string, nombre: string) => {
    try {
      let body: any = {};
      if (endpoint === 'generar-manual') body = { tema: 'auditoria', nivel: 'basico' };
      else if (endpoint === 'generar-podcast-script') body = { tema: 'control_fiscal' };
      else if (endpoint === 'generar-guia-formato') body = { numero_formato: 1 };

      const resp = await apiCliente.post<any>(`/capacitacion/${endpoint}`, body);

      if (resp.contenido_base64) {
        const byteChars = atob(resp.contenido_base64);
        const byteNumbers = new Array(byteChars.length);
        for (let i = 0; i < byteChars.length; i++) byteNumbers[i] = byteChars.charCodeAt(i);
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = resp.nombre_archivo || `${nombre}.docx`;
        a.click();
        URL.revokeObjectURL(url);
      } else if (resp.script) {
        const blob = new Blob([resp.script], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Script_Podcast_${resp.tema}.txt`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('[CecilIA] Error generando contenido:', error);
    }
  };

  return (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
      {acciones.map((a) => (
        <button
          key={a.endpoint}
          onClick={() => descargar(a.endpoint, a.etiqueta)}
          className="flex flex-col items-center gap-2 rounded-lg border border-[#2D3748]/50 bg-[#1A2332]/40 p-3 text-[10px] text-[#9AA0A6] transition-all hover:border-opacity-80 hover:bg-[#1A2332]/70 hover:text-[#E8EAED]"
          style={{ borderColor: `${a.color}20` }}
        >
          <a.icono className="h-5 w-5" style={{ color: a.color }} />
          <span>{a.etiqueta}</span>
          <Download className="h-3 w-3 opacity-50" />
        </button>
      ))}
    </div>
  );
}

// ── Pagina Principal ────────────────────────────────────────────────────────
export default function PaginaCapacitacion() {
  const [rutas, setRutas] = useState<RutaAprendizaje[]>(RUTAS_DEMO);
  const [progreso, setProgreso] = useState<Record<string, { completadas: number; porcentaje: number }>>(PROGRESO_DEMO);
  const usuario = obtenerUsuario();

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      const rutasApi = await apiCliente.get<RutaAprendizaje[]>('/capacitacion/rutas');
      if (rutasApi && rutasApi.length > 0) setRutas(rutasApi);
    } catch {
      // Usar datos demo
    }

    if (usuario?.id) {
      try {
        const progresoApi = await apiCliente.get<any>(`/capacitacion/progreso?usuario_id=${usuario.id}`);
        if (progresoApi && progresoApi.por_ruta) {
          const p: Record<string, { completadas: number; porcentaje: number }> = {};
          for (const r of progresoApi.por_ruta) {
            p[r.ruta_id] = { completadas: r.completadas, porcentaje: r.porcentaje };
          }
          setProgreso(p);
        }
      } catch {
        // Usar demo
      }
    }
  };

  // Calcular estadisticas generales
  const totalLecciones = rutas.reduce((sum, r) => sum + r.total_lecciones, 0);
  const totalCompletadas = Object.values(progreso).reduce((sum, p) => sum + p.completadas, 0);
  const porcentajeGeneral = totalLecciones > 0 ? Math.round((totalCompletadas / totalLecciones) * 100) : 0;

  return (
    <div className="flex flex-col h-full bg-[#0F1419] text-[#E8EAED] overflow-y-auto">
      {/* Header */}
      <div className="border-b border-[#2D3748]/30 px-6 py-5">
        <div className="flex items-center gap-3 mb-1">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#C9A84C]/10 border border-[#C9A84C]/20">
            <BookOpen className="h-5 w-5 text-[#C9A84C]" />
          </div>
          <div>
            <h1 className="text-lg font-titulo font-bold text-[#C9A84C]">
              Centro de Capacitacion
            </h1>
            <p className="text-xs text-[#5F6368]">
              Bienvenido{usuario?.nombre_completo ? `, ${usuario.nombre_completo.split(' ')[0]}` : ''}. Aprende sobre control fiscal con CecilIA.
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 p-6 space-y-6">
        {/* KPIs resumen */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="rounded-lg border border-[#2D3748]/50 bg-[#1A2332]/40 p-3">
            <div className="flex items-center gap-2 mb-1">
              <BookOpen className="h-4 w-4 text-[#C9A84C]" />
              <span className="text-[10px] text-[#5F6368]">Rutas disponibles</span>
            </div>
            <p className="text-xl font-bold text-[#E8EAED]">{rutas.length}</p>
          </div>
          <div className="rounded-lg border border-[#2D3748]/50 bg-[#1A2332]/40 p-3">
            <div className="flex items-center gap-2 mb-1">
              <CheckCircle className="h-4 w-4 text-[#27AE60]" />
              <span className="text-[10px] text-[#5F6368]">Lecciones completadas</span>
            </div>
            <p className="text-xl font-bold text-[#E8EAED]">{totalCompletadas}/{totalLecciones}</p>
          </div>
          <div className="rounded-lg border border-[#2D3748]/50 bg-[#1A2332]/40 p-3">
            <div className="flex items-center gap-2 mb-1">
              <BarChart3 className="h-4 w-4 text-[#2471A3]" />
              <span className="text-[10px] text-[#5F6368]">Avance general</span>
            </div>
            <p className="text-xl font-bold text-[#E8EAED]">{porcentajeGeneral}%</p>
          </div>
          <div className="rounded-lg border border-[#2D3748]/50 bg-[#1A2332]/40 p-3">
            <div className="flex items-center gap-2 mb-1">
              <Award className="h-4 w-4 text-[#8E44AD]" />
              <span className="text-[10px] text-[#5F6368]">Quizzes aprobados</span>
            </div>
            <p className="text-xl font-bold text-[#E8EAED]">0</p>
          </div>
        </div>

        {/* Barra de progreso general */}
        <div className="rounded-lg border border-[#C9A84C]/20 bg-[#C9A84C]/5 p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-[#C9A84C]">Tu progreso general</span>
            <span className="text-xs font-bold text-[#C9A84C]">{porcentajeGeneral}%</span>
          </div>
          <div className="h-2 rounded-full bg-[#2D3748]/50 overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-[#C9A84C] to-[#E8D48B] transition-all duration-1000"
              style={{ width: `${porcentajeGeneral}%` }}
            />
          </div>
        </div>

        {/* Grid de rutas */}
        <div>
          <h2 className="text-sm font-semibold text-[#E8EAED] mb-3 flex items-center gap-2">
            <BookOpen className="h-4 w-4 text-[#C9A84C]" />
            Rutas de Aprendizaje
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-4 gap-4">
            {rutas.map((ruta) => (
              <TarjetaRuta
                key={ruta.id}
                ruta={ruta}
                progreso={progreso[ruta.id] || { completadas: 0, porcentaje: 0 }}
              />
            ))}
          </div>
        </div>

        {/* Generadores de contenido */}
        <div>
          <h2 className="text-sm font-semibold text-[#E8EAED] mb-3 flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-[#C9A84C]" />
            Generadores de Contenido Didactico
          </h2>
          <AccionesRapidas />
        </div>

        {/* Disclaimer */}
        <div className="rounded-lg border border-[#C9A84C]/20 bg-[#C9A84C]/5 p-3 text-center">
          <p className="text-[10px] text-[#C9A84C]/80">
            📚 Contenido con fines educativos — Datos ficticios de ejemplo — CecilIA Modo Tutor — Circular 023 CGR
          </p>
        </div>
      </div>
    </div>
  );
}
