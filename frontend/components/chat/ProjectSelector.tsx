'use client';

/**
 * CecilIA v2 — Selector de proyecto de auditoria
 * Sprint 11 — Permite seleccionar proyecto al entrar al chat
 * para cargar contexto de sesion anterior.
 * Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
 */

import React, { useState, useEffect } from 'react';
import {
  Briefcase,
  Clock,
  FileText,
  AlertTriangle,
  ChevronDown,
  X,
} from 'lucide-react';
import { obtenerUsuario } from '@/lib/auth';
import apiCliente from '@/lib/api';

interface ProyectoResumen {
  id: string;
  nombre_sesion: string;
  auditoria_id: string;
  sujeto_control: string | null;
  vigencia: string | null;
  fase: string;
  tiene_resumen: boolean;
  documentos: number;
  hallazgos: number;
  formatos: number;
  ultima_actividad: string | null;
}

interface PropiedadesSelector {
  alSeleccionar: (proyectoId: string | null) => void;
  proyectoActivo: string | null;
}

export function SelectorProyecto({ alSeleccionar, proyectoActivo }: PropiedadesSelector) {
  const [proyectos, setProyectos] = useState<ProyectoResumen[]>([]);
  const [abierto, setAbierto] = useState(false);
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    cargarProyectos();
  }, []);

  const cargarProyectos = async () => {
    setCargando(true);
    try {
      const usuario = obtenerUsuario();
      if (!usuario) return;
      const resp = await apiCliente.get(`/sesion/proyectos?usuario_id=${usuario.id || 0}`) as {
        proyectos: ProyectoResumen[];
      };
      setProyectos(resp.proyectos || []);
    } catch {
      // Silenciar — la tabla puede no existir aun
    } finally {
      setCargando(false);
    }
  };

  const proyectoSeleccionado = proyectos.find((p) => p.id === proyectoActivo);

  const formatearFecha = (iso: string | null) => {
    if (!iso) return 'Sin actividad';
    const fecha = new Date(iso);
    const ahora = new Date();
    const diffMs = ahora.getTime() - fecha.getTime();
    const diffHoras = Math.floor(diffMs / (1000 * 60 * 60));

    if (diffHoras < 1) return 'Hace menos de 1 hora';
    if (diffHoras < 24) return `Hace ${diffHoras}h`;
    const diffDias = Math.floor(diffHoras / 24);
    if (diffDias === 1) return 'Ayer';
    if (diffDias < 7) return `Hace ${diffDias} dias`;
    return fecha.toLocaleDateString('es-CO', { day: 'numeric', month: 'short' });
  };

  if (proyectos.length === 0 && !cargando) return null;

  return (
    <div className="relative">
      <button
        onClick={() => setAbierto(!abierto)}
        className="flex items-center gap-2 rounded-lg border border-[#2D3748] bg-[#1A2332] px-3 py-2 text-xs text-[#9AA0A6] hover:border-[#C9A84C]/30 hover:text-[#E8EAED] transition-colors"
      >
        <Briefcase className="h-3.5 w-3.5 text-[#C9A84C]" />
        {proyectoSeleccionado ? (
          <span className="max-w-[200px] truncate text-[#E8EAED]">
            {proyectoSeleccionado.nombre_sesion}
          </span>
        ) : (
          <span>Seleccionar proyecto...</span>
        )}
        <ChevronDown className="h-3 w-3" />
      </button>

      {abierto && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setAbierto(false)} />
          <div className="absolute left-0 top-full z-50 mt-1 w-80 rounded-lg border border-[#2D3748] bg-[#1A2332] shadow-xl">
            <div className="p-2 border-b border-[#2D3748]/50">
              <p className="text-[10px] text-[#5F6368] uppercase tracking-wider">Proyectos de auditoria</p>
            </div>

            {/* Opcion: sin proyecto */}
            <button
              onClick={() => { alSeleccionar(null); setAbierto(false); }}
              className={`flex w-full items-center gap-2 px-3 py-2.5 text-xs hover:bg-[#243044] transition-colors ${
                !proyectoActivo ? 'bg-[#243044] text-[#C9A84C]' : 'text-[#9AA0A6]'
              }`}
            >
              <X className="h-3.5 w-3.5" />
              Chat libre (sin proyecto)
            </button>

            <div className="max-h-60 overflow-y-auto">
              {proyectos.map((p) => (
                <button
                  key={p.id}
                  onClick={() => { alSeleccionar(p.id); setAbierto(false); }}
                  className={`flex w-full flex-col px-3 py-2.5 text-left hover:bg-[#243044] transition-colors border-t border-[#2D3748]/20 ${
                    proyectoActivo === p.id ? 'bg-[#243044]' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-[#E8EAED] truncate max-w-[60%]">
                      {p.nombre_sesion}
                    </span>
                    <span className="text-[9px] text-[#5F6368]">{p.fase}</span>
                  </div>
                  {p.sujeto_control && (
                    <span className="text-[10px] text-[#6B7B8D] truncate">{p.sujeto_control}</span>
                  )}
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-[9px] text-[#5F6368] flex items-center gap-1">
                      <Clock className="h-2.5 w-2.5" />
                      {formatearFecha(p.ultima_actividad)}
                    </span>
                    {p.tiene_resumen && (
                      <span className="text-[9px] text-[#C9A84C] flex items-center gap-1">
                        <FileText className="h-2.5 w-2.5" />
                        Memoria
                      </span>
                    )}
                    {p.documentos > 0 && (
                      <span className="text-[9px] text-[#5F6368]">{p.documentos} docs</span>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default SelectorProyecto;
