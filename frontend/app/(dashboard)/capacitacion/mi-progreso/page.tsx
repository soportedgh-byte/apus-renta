'use client';

/**
 * CecilIA v2 — Dashboard del Aprendiz
 * XP, nivel, racha, insignias, repasos pendientes y progreso por ruta
 * Sprint: Capacitacion 2.0
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft, Trophy, Flame, Star, Target, BookOpen,
  Clock, Award, Zap, TrendingUp, Calendar, ChevronRight,
  Loader2, RefreshCw,
} from 'lucide-react';
import { obtenerUsuario } from '@/lib/auth';
import { apiCliente } from '@/lib/api';
import type { PerfilGamificacion, RepasoPendiente, Insignia } from '@/lib/types';

const NIVELES_COLORES: Record<string, string> = {
  'Practicante': '#6B7B8D',
  'Auxiliar': '#2471A3',
  'Auditor Junior': '#27AE60',
  'Auditor Senior': '#C9A84C',
  'Experto': '#E74C3C',
};

export default function PaginaMiProgreso() {
  const router = useRouter();
  const usuario = obtenerUsuario();
  const [gamificacion, setGamificacion] = useState<PerfilGamificacion | null>(null);
  const [repasos, setRepasos] = useState<RepasoPendiente[]>([]);
  const [progreso, setProgreso] = useState<any>(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => { cargarDatos(); }, []);

  const cargarDatos = async () => {
    if (!usuario?.id) return;
    setCargando(true);
    try {
      const resp = await apiCliente.get<any>(`/capacitacion/mi-progreso/${usuario.id}`);
      setGamificacion(resp.gamificacion);
      setRepasos(resp.repasos_pendientes || []);
      setProgreso(resp.progreso);
    } catch {
      // Datos de fallback
      setGamificacion({
        xp_total: 0, nivel: 'Practicante', racha_dias: 0, mejor_racha: 0,
        insignias: [], ultima_actividad: null, xp_siguiente_nivel: 500, progreso_nivel: 0,
      });
    } finally {
      setCargando(false);
    }
  };

  if (cargando) {
    return (
      <div className="flex items-center justify-center h-full bg-[#0F1419]">
        <Loader2 className="h-8 w-8 text-[#C9A84C] animate-spin" />
      </div>
    );
  }

  const g = gamificacion!;
  const colorNivel = NIVELES_COLORES[g.nivel] || '#C9A84C';

  return (
    <div className="flex flex-col h-full bg-[#0F1419] text-[#E8EAED] overflow-y-auto">
      {/* Header */}
      <div className="border-b border-[#2D3748]/30 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button onClick={() => router.push('/capacitacion')} className="flex items-center gap-1 text-[10px] text-[#5F6368] hover:text-[#9AA0A6]">
              <ArrowLeft className="h-3 w-3" />
            </button>
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#C9A84C]/10 border border-[#C9A84C]/20">
              <Trophy className="h-5 w-5 text-[#C9A84C]" />
            </div>
            <div>
              <h1 className="text-base font-bold text-[#C9A84C]">Mi Progreso</h1>
              <p className="text-[10px] text-[#5F6368]">{usuario?.nombre_completo || 'Aprendiz'}</p>
            </div>
          </div>
          <button onClick={cargarDatos} className="flex items-center gap-1 text-[10px] text-[#5F6368] hover:text-[#C9A84C]">
            <RefreshCw className="h-3 w-3" /> Actualizar
          </button>
        </div>
      </div>

      <div className="flex-1 p-6 space-y-5">
        {/* Tarjeta de nivel y XP */}
        <div className="rounded-xl border p-5" style={{ borderColor: `${colorNivel}30`, backgroundColor: `${colorNivel}08` }}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-[10px] text-[#5F6368] uppercase tracking-wider">Nivel actual</p>
              <h2 className="text-xl font-bold" style={{ color: colorNivel }}>{g.nivel}</h2>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-[#E8EAED]">{g.xp_total}</p>
              <p className="text-[10px] text-[#5F6368]">XP totales</p>
            </div>
          </div>
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[10px]">
              <span className="text-[#9AA0A6]">Progreso al siguiente nivel</span>
              <span className="font-semibold" style={{ color: colorNivel }}>{g.progreso_nivel}%</span>
            </div>
            <div className="h-2.5 rounded-full bg-[#2D3748]/50 overflow-hidden">
              <div className="h-full rounded-full transition-all duration-1000" style={{ width: `${g.progreso_nivel}%`, backgroundColor: colorNivel }} />
            </div>
            <p className="text-[10px] text-[#5F6368]">Siguiente nivel en {g.xp_siguiente_nivel} XP</p>
          </div>
        </div>

        {/* KPIs: racha, mejor racha, insignias */}
        <div className="grid grid-cols-3 gap-3">
          <div className="rounded-lg border border-[#E74C3C]/20 bg-[#E74C3C]/5 p-3 text-center">
            <Flame className="h-5 w-5 text-[#E74C3C] mx-auto mb-1" />
            <p className="text-lg font-bold text-[#E8EAED]">{g.racha_dias}</p>
            <p className="text-[9px] text-[#5F6368]">Dias de racha</p>
          </div>
          <div className="rounded-lg border border-[#C9A84C]/20 bg-[#C9A84C]/5 p-3 text-center">
            <Star className="h-5 w-5 text-[#C9A84C] mx-auto mb-1" />
            <p className="text-lg font-bold text-[#E8EAED]">{g.mejor_racha}</p>
            <p className="text-[9px] text-[#5F6368]">Mejor racha</p>
          </div>
          <div className="rounded-lg border border-[#2471A3]/20 bg-[#2471A3]/5 p-3 text-center">
            <Award className="h-5 w-5 text-[#2471A3] mx-auto mb-1" />
            <p className="text-lg font-bold text-[#E8EAED]">{g.insignias.length}</p>
            <p className="text-[9px] text-[#5F6368]">Insignias</p>
          </div>
        </div>

        {/* Insignias */}
        {g.insignias.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-[#E8EAED] mb-3 flex items-center gap-2">
              <Award className="h-4 w-4 text-[#C9A84C]" /> Insignias obtenidas
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {g.insignias.map((ins: Insignia) => (
                <div key={ins.id} className="rounded-lg border border-[#2D3748]/50 bg-[#1A2332]/40 p-3 text-center">
                  <span className="text-2xl">{ins.icono}</span>
                  <p className="text-[10px] font-semibold text-[#E8EAED] mt-1">{ins.nombre}</p>
                  <p className="text-[9px] text-[#5F6368]">{ins.descripcion}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Repasos pendientes */}
        <div>
          <h3 className="text-sm font-semibold text-[#E8EAED] mb-3 flex items-center gap-2">
            <Calendar className="h-4 w-4 text-[#27AE60]" /> Repasos pendientes ({repasos.length})
          </h3>
          {repasos.length === 0 ? (
            <div className="rounded-lg border border-[#2D3748]/50 bg-[#1A2332]/40 p-4 text-center">
              <p className="text-xs text-[#5F6368]">No tienes repasos pendientes. Completa lecciones para activar el repaso espaciado.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {repasos.map((r) => (
                <div key={r.repaso_id} className="flex items-center justify-between rounded-lg border border-[#27AE60]/20 bg-[#27AE60]/5 p-3">
                  <div>
                    <p className="text-xs font-medium text-[#E8EAED]">{r.leccion_titulo}</p>
                    <p className="text-[10px] text-[#5F6368]">Intervalo: {r.intervalo_dias} dias | Intentos: {r.intentos}</p>
                  </div>
                  <ChevronRight className="h-4 w-4 text-[#27AE60]" />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Progreso por ruta */}
        {progreso?.por_ruta && (
          <div>
            <h3 className="text-sm font-semibold text-[#E8EAED] mb-3 flex items-center gap-2">
              <BookOpen className="h-4 w-4 text-[#C9A84C]" /> Avance por ruta
            </h3>
            <div className="space-y-2">
              {progreso.por_ruta.map((r: any) => (
                <div key={r.ruta_id} className="rounded-lg border border-[#2D3748]/50 bg-[#1A2332]/40 p-3">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-medium text-[#E8EAED]">{r.ruta_nombre}</span>
                    <span className="text-xs font-semibold text-[#C9A84C]">{r.porcentaje}%</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-[#2D3748]/50 overflow-hidden">
                    <div className="h-full rounded-full bg-[#C9A84C] transition-all" style={{ width: `${r.porcentaje}%` }} />
                  </div>
                  <p className="text-[10px] text-[#5F6368] mt-1">{r.completadas}/{r.total_lecciones} lecciones</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Disclaimer */}
        <div className="rounded-lg border border-[#C9A84C]/20 bg-[#C9A84C]/5 p-3 text-center">
          <p className="text-[10px] text-[#C9A84C]/80">
            Sistema de gamificacion educativa — CecilIA Modo Tutor — Circular 023 CGR
          </p>
        </div>
      </div>
    </div>
  );
}
