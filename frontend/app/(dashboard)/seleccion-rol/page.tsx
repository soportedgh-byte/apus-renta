'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowRight,
  BarChart3,
  Shield,
  FileSearch,
  AlertTriangle,
  TrendingUp,
  Eye,
  Building2,
  FileText,
  ClipboardList,
} from 'lucide-react';
import { obtenerUsuario, establecerDireccionActiva, puedeVerDireccion } from '@/lib/auth';
import type { Direccion } from '@/lib/types';

/**
 * Pagina de seleccion de direccion (DES / DVF)
 * Diseno institucional con tarjetas grandes y animaciones
 */
export default function PaginaSeleccionRol() {
  const router = useRouter();
  const [usuario, setUsuario] = useState<{ nombre_completo: string } | null>(null);
  const [seleccionando, setSeleccionando] = useState<Direccion | null>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const u = obtenerUsuario();
    if (u) {
      setUsuario({ nombre_completo: u.nombre_completo });

      // Si solo tiene acceso a una direccion, redirigir automaticamente
      const puedeVerDES = puedeVerDireccion('DES');
      const puedeVerDVF = puedeVerDireccion('DVF');
      if (puedeVerDES && !puedeVerDVF) {
        establecerDireccionActiva('DES');
        router.push('/chat');
        return;
      }
      if (puedeVerDVF && !puedeVerDES) {
        establecerDireccionActiva('DVF');
        router.push('/chat');
        return;
      }
    }
    setTimeout(() => setVisible(true), 50);
  }, [router]);

  const seleccionarDireccion = (direccion: Direccion) => {
    setSeleccionando(direccion);
    establecerDireccionActiva(direccion);
    setTimeout(() => {
      router.push('/chat');
    }, 400);
  };

  const fasesDVF = ['Pre-planeacion', 'Planeacion', 'Ejecucion', 'Informe', 'Seguimiento'];
  const fasesDES = ['Planeacion', 'Ejecucion', 'Informe', 'Seguimiento'];

  return (
    <div className="flex min-h-full items-center justify-center p-8">
      <div
        className={`w-full max-w-[740px] transition-all duration-700 ease-out ${
          visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'
        }`}
      >
        {/* Encabezado */}
        <div className="mb-10 text-center">
          <h1 className="font-titulo text-2xl font-bold text-[#E8EAED] mb-2">
            Selecciona tu direccion
          </h1>
          <p className="text-sm text-[#9AA0A6]">
            {usuario?.nombre_completo
              ? `Bienvenido, ${usuario.nombre_completo}`
              : 'Bienvenido, Auditor'}
          </p>
          <p className="text-xs text-[#5F6368] mt-1">
            CecilIA configurara agentes, documentacion y herramientas segun tu rol
          </p>
        </div>

        {/* Tarjetas de seleccion */}
        <div className="flex flex-col md:flex-row gap-5 justify-center">
          {/* Card DES */}
          {(!usuario || puedeVerDireccion('DES')) && (
            <button
              onClick={() => seleccionarDireccion('DES')}
              disabled={seleccionando !== null}
              className={`group relative overflow-hidden rounded-2xl text-left transition-all duration-500 w-full md:max-w-[340px] ${
                seleccionando === 'DES'
                  ? 'scale-[1.02] shadow-2xl shadow-[#1A5276]/40'
                  : seleccionando === 'DVF'
                    ? 'scale-95 opacity-40'
                    : 'hover:shadow-xl hover:shadow-[#1A5276]/20 hover:-translate-y-0.5'
              }`}
              style={{ border: '1px solid #1A5276' }}
            >
              {/* Fondo */}
              <div className="absolute inset-0 bg-gradient-to-br from-[#1A5276]/90 to-[#154360]/90" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
              <div className="absolute -right-10 -top-10 h-36 w-36 rounded-full bg-[#2471A3]/15 blur-2xl" />

              <div className="relative p-7">
                {/* Icono grande */}
                <div className="mb-5 text-5xl">
                  <span role="img" aria-label="Estadisticas">📊</span>
                </div>

                {/* Titulo */}
                <h2 className="font-titulo text-xl font-bold text-white mb-1">
                  DES
                </h2>
                <p className="text-[11px] font-semibold uppercase tracking-[0.15em] text-[#85C1E9] mb-3">
                  CONTROL FISCAL MACRO
                </p>

                {/* Descripcion */}
                <p className="text-sm text-white/70 leading-relaxed mb-5">
                  Direccion de Estudios Sectoriales y Macroeconomicos.
                  Analisis sectorial, evaluaciones de politica publica,
                  indicadores macroeconomicos y observatorio fiscal.
                </p>

                {/* Features */}
                <div className="space-y-2 mb-5">
                  <div className="flex items-center gap-2 text-xs text-white/60">
                    <BarChart3 className="h-3.5 w-3.5 flex-shrink-0" />
                    <span>Observatorio sectorial en tiempo real</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-white/60">
                    <TrendingUp className="h-3.5 w-3.5 flex-shrink-0" />
                    <span>Analisis de riesgos transversales</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-white/60">
                    <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0" />
                    <span>Alertas tempranas sectoriales</span>
                  </div>
                </div>

                {/* Chips de fases */}
                <div className="flex flex-wrap gap-1.5 mb-5">
                  {fasesDES.map((fase) => (
                    <span
                      key={fase}
                      className="rounded-full bg-white/10 px-2.5 py-1 text-[10px] text-white/70 border border-white/10"
                    >
                      {fase}
                    </span>
                  ))}
                </div>

                {/* CTA */}
                <div className="flex items-center gap-2 text-sm font-medium text-white group-hover:gap-3 transition-all">
                  Ingresar a DES
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </div>
              </div>
            </button>
          )}

          {/* Card DVF */}
          {(!usuario || puedeVerDireccion('DVF')) && (
            <button
              onClick={() => seleccionarDireccion('DVF')}
              disabled={seleccionando !== null}
              className={`group relative overflow-hidden rounded-2xl text-left transition-all duration-500 w-full md:max-w-[340px] ${
                seleccionando === 'DVF'
                  ? 'scale-[1.02] shadow-2xl shadow-[#1E8449]/40'
                  : seleccionando === 'DES'
                    ? 'scale-95 opacity-40'
                    : 'hover:shadow-xl hover:shadow-[#1E8449]/20 hover:-translate-y-0.5'
              }`}
              style={{ border: '1px solid #1E8449' }}
            >
              {/* Fondo */}
              <div className="absolute inset-0 bg-gradient-to-br from-[#1E8449]/90 to-[#196F3D]/90" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
              <div className="absolute -right-10 -top-10 h-36 w-36 rounded-full bg-[#27AE60]/15 blur-2xl" />

              <div className="relative p-7">
                {/* Icono grande */}
                <div className="mb-5 text-5xl">
                  <span role="img" aria-label="Lupa">🔍</span>
                </div>

                {/* Titulo */}
                <h2 className="font-titulo text-xl font-bold text-white mb-1">
                  DVF
                </h2>
                <p className="text-[11px] font-semibold uppercase tracking-[0.15em] text-[#82E0AA] mb-3">
                  CONTROL FISCAL MICRO
                </p>

                {/* Descripcion */}
                <p className="text-sm text-white/70 leading-relaxed mb-5">
                  Direccion de Vigilancia Fiscal.
                  Auditorias individuales, hallazgos fiscales,
                  generacion de 30 formatos CGR y seguimiento de planes de mejoramiento.
                </p>

                {/* Features */}
                <div className="space-y-2 mb-5">
                  <div className="flex items-center gap-2 text-xs text-white/60">
                    <Shield className="h-3.5 w-3.5 flex-shrink-0" />
                    <span>Hallazgos con 5 elementos estructurados</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-white/60">
                    <FileText className="h-3.5 w-3.5 flex-shrink-0" />
                    <span>Generacion de 30 formatos de auditoria</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-white/60">
                    <ClipboardList className="h-3.5 w-3.5 flex-shrink-0" />
                    <span>Flujo de trabajo de hallazgos</span>
                  </div>
                </div>

                {/* Chips de fases */}
                <div className="flex flex-wrap gap-1.5 mb-5">
                  {fasesDVF.map((fase) => (
                    <span
                      key={fase}
                      className="rounded-full bg-white/10 px-2.5 py-1 text-[10px] text-white/70 border border-white/10"
                    >
                      {fase}
                    </span>
                  ))}
                </div>

                {/* CTA */}
                <div className="flex items-center gap-2 text-sm font-medium text-white group-hover:gap-3 transition-all">
                  Ingresar a DVF
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </div>
              </div>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
