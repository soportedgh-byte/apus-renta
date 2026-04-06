'use client';

/**
 * CecilIA v2 — Centro de Capacitacion
 * Pagina principal redise\u00f1ada: rutas, herramientas adaptativas, progreso real
 * Sprint: Capacitacion 2.0
 */

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  BookOpen, Clock, CheckCircle, Trophy, ChevronRight,
  BookMarked, Sparkles, Target, Brain, Zap, Headphones,
  Layers, GraduationCap, Loader2, ArrowRight,
} from 'lucide-react';
import { obtenerUsuario } from '@/lib/auth';
import { apiCliente } from '@/lib/api';
import type { RutaAprendizaje, PerfilGamificacion } from '@/lib/types';

// ── Tarjeta de Ruta con dise\u00f1o premium ──────────────────────────────────────
function TarjetaRuta({
  ruta,
  progreso,
  lecciones,
}: {
  ruta: RutaAprendizaje;
  progreso: { completadas: number; porcentaje: number };
  lecciones: any[];
}) {
  const estaCompleta = progreso.porcentaje === 100;
  const enProgreso = progreso.porcentaje > 0 && progreso.porcentaje < 100;

  // Encontrar la primera leccion no completada para navegar
  const primeraLeccion = lecciones.length > 0 ? lecciones[0] : null;
  const href = primeraLeccion
    ? `/capacitacion/${ruta.id}/${primeraLeccion.id}`
    : `/capacitacion/${ruta.id}`;

  return (
    <Link
      href={href}
      className="group relative flex flex-col rounded-2xl border bg-gradient-to-b from-[#1A2332]/80 to-[#0F1419]/80 p-6 transition-all duration-300 hover:shadow-xl hover:-translate-y-1"
      style={{ borderColor: `${ruta.color}25` }}
    >
      {/* Glow effect on hover */}
      <div
        className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{ boxShadow: `inset 0 1px 0 0 ${ruta.color}20, 0 0 30px -10px ${ruta.color}15` }}
      />

      {/* Badge completada */}
      {estaCompleta && (
        <div className="absolute -top-2.5 -right-2.5 flex h-8 w-8 items-center justify-center rounded-full bg-[#27AE60] shadow-lg shadow-[#27AE60]/30">
          <Trophy className="h-4 w-4 text-white" />
        </div>
      )}

      <div className="relative">
        {/* Icono + Direccion */}
        <div className="flex items-center justify-between mb-4">
          <div
            className="flex h-14 w-14 items-center justify-center rounded-2xl text-2xl shadow-lg"
            style={{ backgroundColor: `${ruta.color}12`, border: `1px solid ${ruta.color}20` }}
          >
            {ruta.icono}
          </div>
          <span
            className="rounded-full px-2.5 py-1 text-[9px] font-bold uppercase tracking-wider"
            style={{ backgroundColor: `${ruta.color}12`, color: ruta.color }}
          >
            {ruta.direccion}
          </span>
        </div>

        {/* Titulo */}
        <h3 className="text-base font-bold text-[#E8EAED] mb-2 group-hover:text-white transition-colors leading-tight">
          {ruta.nombre}
        </h3>
        <p className="text-xs text-[#6B7B8D] mb-5 line-clamp-2 leading-relaxed">{ruta.descripcion}</p>

        {/* Meta */}
        <div className="flex items-center gap-4 text-[10px] text-[#4A5568] mb-4">
          <span className="flex items-center gap-1.5">
            <BookOpen className="h-3 w-3" />
            {ruta.total_lecciones} lecciones
          </span>
          <span className="flex items-center gap-1.5">
            <Clock className="h-3 w-3" />
            ~{ruta.total_lecciones * 15} min
          </span>
        </div>

        {/* Barra de progreso */}
        <div>
          <div className="h-2 rounded-full bg-[#1A2332] overflow-hidden border border-[#2D3748]/30">
            <div
              className="h-full rounded-full transition-all duration-1000 ease-out"
              style={{
                width: `${progreso.porcentaje}%`,
                background: `linear-gradient(90deg, ${ruta.color}, ${ruta.color}CC)`,
              }}
            />
          </div>
          <div className="flex items-center justify-between mt-2">
            <span className="text-[10px] text-[#6B7B8D]">
              {progreso.completadas}/{ruta.total_lecciones}
            </span>
            <span
              className="flex items-center gap-1 text-[10px] font-semibold opacity-0 group-hover:opacity-100 transition-all"
              style={{ color: ruta.color }}
            >
              {estaCompleta ? 'Repasar' : enProgreso ? 'Continuar' : 'Comenzar'}
              <ArrowRight className="h-3 w-3" />
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
}

// ── Pagina Principal ────────────────────────────────────────────────────────
export default function PaginaCapacitacion() {
  const [rutas, setRutas] = useState<RutaAprendizaje[]>([]);
  const [progreso, setProgreso] = useState<Record<string, { completadas: number; porcentaje: number }>>({});
  const [leccionesPorRuta, setLeccionesPorRuta] = useState<Record<string, any[]>>({});
  const [gamificacion, setGamificacion] = useState<PerfilGamificacion | null>(null);
  const [cargando, setCargando] = useState(true);
  const [perfilEstilo, setPerfilEstilo] = useState<any>(null);
  const usuario = obtenerUsuario();

  useEffect(() => { cargarDatos(); }, []);

  const cargarDatos = async () => {
    setCargando(true);
    try {
      // Cargar rutas
      const rutasApi = await apiCliente.get<RutaAprendizaje[]>('/capacitacion/rutas');
      if (rutasApi && rutasApi.length > 0) {
        setRutas(rutasApi);
        // Cargar lecciones de cada ruta
        const leccionesMap: Record<string, any[]> = {};
        for (const ruta of rutasApi) {
          try {
            const lecs = await apiCliente.get<any[]>(`/capacitacion/rutas/${ruta.id}/lecciones`);
            leccionesMap[ruta.id] = lecs || [];
          } catch { leccionesMap[ruta.id] = []; }
        }
        setLeccionesPorRuta(leccionesMap);
      }
    } catch { /* sin rutas */ }

    if (usuario?.id) {
      try {
        const progresoApi = await apiCliente.get<any>(`/capacitacion/progreso?usuario_id=${usuario.id}`);
        if (progresoApi?.por_ruta) {
          const p: Record<string, { completadas: number; porcentaje: number }> = {};
          for (const r of progresoApi.por_ruta) {
            p[r.ruta_id] = { completadas: r.completadas, porcentaje: r.porcentaje };
          }
          setProgreso(p);
        }
      } catch { /* sin progreso */ }

      try {
        const gam = await apiCliente.get<PerfilGamificacion>(`/capacitacion/gamificacion/${usuario.id}`);
        setGamificacion(gam);
      } catch { /* sin gamificacion */ }

      try {
        const perfil = await apiCliente.get<any>(`/capacitacion/perfil-aprendizaje/${usuario.id}`);
        if (perfil?.tiene_perfil) setPerfilEstilo(perfil);
      } catch { /* sin perfil */ }
    }
    setCargando(false);
  };

  // Stats
  const totalLecciones = rutas.reduce((sum, r) => sum + r.total_lecciones, 0);
  const totalCompletadas = Object.values(progreso).reduce((sum, p) => sum + p.completadas, 0);
  const porcentajeGeneral = totalLecciones > 0 ? Math.round((totalCompletadas / totalLecciones) * 100) : 0;

  const herramientas = [
    { href: '/capacitacion/cuestionario', icono: Brain, nombre: 'Estilo de aprendizaje', desc: 'Descubre tu perfil VARK', color: '#E74C3C', badge: perfilEstilo ? perfilEstilo.estilo_predominante : null },
    { href: '/capacitacion/mi-progreso', icono: Trophy, nombre: 'Mi progreso', desc: 'XP, nivel e insignias', color: '#C9A84C', badge: gamificacion ? `${gamificacion.xp_total} XP` : null },
    { href: '/capacitacion/simulador', icono: Target, nombre: 'Simulador', desc: '3 escenarios guiados', color: '#1A5276' },
    { href: '/capacitacion/biblioteca', icono: Sparkles, nombre: 'Crear contenido', desc: 'Podcasts, flashcards, diagramas', color: '#8E44AD' },
    { href: '/capacitacion/glosario', icono: BookMarked, nombre: 'Glosario fiscal', desc: 'Terminos y definiciones', color: '#27AE60' },
  ];

  if (cargando) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-[#0F1419] gap-3">
        <Loader2 className="h-8 w-8 text-[#C9A84C] animate-spin" />
        <p className="text-xs text-[#5F6368]">Cargando centro de capacitacion...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-[#0F1419] text-[#E8EAED] overflow-y-auto">
      {/* Header con gradiente */}
      <div className="relative overflow-hidden border-b border-[#2D3748]/30">
        <div className="absolute inset-0 bg-gradient-to-r from-[#C9A84C]/5 via-transparent to-[#1A5276]/5" />
        <div className="relative px-8 py-7">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-[#C9A84C]/20 to-[#C9A84C]/5 border border-[#C9A84C]/20 shadow-lg shadow-[#C9A84C]/5">
                <GraduationCap className="h-6 w-6 text-[#C9A84C]" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-[#E8EAED]">
                  Centro de Capacitacion
                </h1>
                <p className="text-xs text-[#6B7B8D] mt-0.5">
                  {usuario?.nombre_completo
                    ? `Bienvenido, ${usuario.nombre_completo.split(' ')[0]}`
                    : 'Aprende sobre control fiscal con CecilIA'}
                </p>
              </div>
            </div>

            {/* Nivel badge */}
            {gamificacion && (
              <div className="hidden sm:flex items-center gap-3 rounded-xl bg-[#1A2332]/80 border border-[#C9A84C]/15 px-4 py-2.5">
                <div className="text-center">
                  <p className="text-[9px] text-[#6B7B8D] uppercase tracking-wider">Nivel</p>
                  <p className="text-sm font-bold text-[#C9A84C]">{gamificacion.nivel}</p>
                </div>
                <div className="w-px h-8 bg-[#2D3748]/50" />
                <div className="text-center">
                  <p className="text-[9px] text-[#6B7B8D] uppercase tracking-wider">XP</p>
                  <p className="text-sm font-bold text-[#E8EAED]">{gamificacion.xp_total}</p>
                </div>
                {gamificacion.racha_dias > 0 && (
                  <>
                    <div className="w-px h-8 bg-[#2D3748]/50" />
                    <div className="text-center">
                      <p className="text-[9px] text-[#6B7B8D] uppercase tracking-wider">Racha</p>
                      <p className="text-sm font-bold text-[#E74C3C]">{gamificacion.racha_dias}d</p>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>

          {/* Barra de progreso general */}
          {totalLecciones > 0 && (
            <div className="mt-5 max-w-2xl">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[10px] text-[#6B7B8D]">
                  Progreso general: {totalCompletadas} de {totalLecciones} lecciones
                </span>
                <span className="text-[10px] font-bold text-[#C9A84C]">{porcentajeGeneral}%</span>
              </div>
              <div className="h-2 rounded-full bg-[#1A2332] overflow-hidden border border-[#2D3748]/30">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-[#C9A84C] to-[#E8D48B] transition-all duration-1000"
                  style={{ width: `${porcentajeGeneral}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 px-8 py-6 space-y-8">
        {/* Herramientas de aprendizaje */}
        <div>
          <h2 className="text-sm font-bold text-[#E8EAED] mb-4 flex items-center gap-2">
            <Zap className="h-4 w-4 text-[#C9A84C]" />
            Herramientas de aprendizaje
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {herramientas.map((h) => {
              const Icono = h.icono;
              return (
                <Link
                  key={h.href}
                  href={h.href}
                  className="group flex flex-col rounded-xl border bg-[#1A2332]/40 p-4 transition-all duration-300 hover:bg-[#1A2332]/80 hover:-translate-y-0.5"
                  style={{ borderColor: `${h.color}15` }}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <div
                      className="flex h-9 w-9 items-center justify-center rounded-xl transition-transform group-hover:scale-110"
                      style={{ backgroundColor: `${h.color}10`, border: `1px solid ${h.color}20` }}
                    >
                      <Icono className="h-4.5 w-4.5" style={{ color: h.color }} />
                    </div>
                    {h.badge && (
                      <span className="rounded-full px-2 py-0.5 text-[8px] font-bold uppercase" style={{ backgroundColor: `${h.color}15`, color: h.color }}>
                        {h.badge}
                      </span>
                    )}
                  </div>
                  <span className="text-[11px] font-semibold text-[#E8EAED]">{h.nombre}</span>
                  <span className="text-[9px] text-[#4A5568] mt-0.5">{h.desc}</span>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Rutas de aprendizaje */}
        <div>
          <h2 className="text-sm font-bold text-[#E8EAED] mb-4 flex items-center gap-2">
            <BookOpen className="h-4 w-4 text-[#C9A84C]" />
            Rutas de aprendizaje
            {rutas.length > 0 && (
              <span className="text-[10px] font-normal text-[#4A5568]">({rutas.length} disponibles)</span>
            )}
          </h2>

          {rutas.length === 0 ? (
            <div className="rounded-2xl border border-[#2D3748]/30 bg-[#1A2332]/30 p-12 text-center">
              <GraduationCap className="h-12 w-12 text-[#2D3748] mx-auto mb-4" />
              <p className="text-sm text-[#6B7B8D] mb-1">No hay rutas de aprendizaje disponibles</p>
              <p className="text-[10px] text-[#4A5568]">Ejecute el seed de capacitacion para cargar las rutas iniciales</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
              {rutas.map((ruta) => (
                <TarjetaRuta
                  key={ruta.id}
                  ruta={ruta}
                  progreso={progreso[ruta.id] || { completadas: 0, porcentaje: 0 }}
                  lecciones={leccionesPorRuta[ruta.id] || []}
                />
              ))}
            </div>
          )}
        </div>

        {/* Disclaimer */}
        <div className="rounded-xl border border-[#C9A84C]/10 bg-[#C9A84C]/3 px-4 py-2.5 text-center">
          <p className="text-[9px] text-[#6B7B8D]">
            Contenido con fines educativos — Asistido por IA — Requiere validacion humana — Circular 023 CGR
          </p>
        </div>
      </div>
    </div>
  );
}
