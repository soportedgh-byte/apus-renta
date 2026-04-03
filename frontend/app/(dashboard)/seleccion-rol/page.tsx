'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Eye, Building2, ArrowRight, BarChart3, Shield, FileSearch, AlertTriangle } from 'lucide-react';
import { obtenerUsuario, establecerDireccionActiva, puedeVerDireccion } from '@/lib/auth';
import type { Direccion } from '@/lib/types';

/**
 * Pagina de seleccion de rol/direccion
 * Muestra tarjetas grandes para DES y DVF segun los permisos del usuario
 */
export default function PaginaSeleccionRol() {
  const router = useRouter();
  const [usuario, setUsuario] = useState<{ nombre_completo: string; puede_ver: Direccion[] } | null>(null);
  const [seleccionando, setSeleccionando] = useState<Direccion | null>(null);

  useEffect(() => {
    const u = obtenerUsuario();
    if (u) {
      setUsuario({ nombre_completo: u.nombre_completo, puede_ver: u.puede_ver });
    }
  }, []);

  const seleccionarDireccion = (direccion: Direccion) => {
    setSeleccionando(direccion);
    establecerDireccionActiva(direccion);
    // Pequena pausa para la animacion visual
    setTimeout(() => {
      router.push('/chat');
    }, 400);
  };

  return (
    <div className="flex min-h-full items-center justify-center p-8">
      <div className="w-full max-w-4xl">
        {/* Encabezado */}
        <div className="mb-10 text-center">
          <h1 className="font-titulo text-2xl font-bold text-[#E8EAED] mb-2">
            Bienvenido, {usuario?.nombre_completo || 'Auditor'}
          </h1>
          <p className="text-sm text-[#9AA0A6]">
            Seleccione la direccion con la que desea trabajar en esta sesion
          </p>
        </div>

        {/* Tarjetas de seleccion */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Tarjeta DES */}
          {(!usuario || puedeVerDireccion('DES')) && (
            <button
              onClick={() => seleccionarDireccion('DES')}
              disabled={seleccionando !== null}
              className={`group relative overflow-hidden rounded-2xl border text-left transition-all duration-500 ${
                seleccionando === 'DES'
                  ? 'scale-[1.02] border-[#2471A3] shadow-2xl shadow-[#1A5276]/40'
                  : seleccionando === 'DVF'
                    ? 'scale-95 opacity-40'
                    : 'border-[#2D3748]/50 hover:border-[#1A5276]/60 hover:shadow-xl hover:shadow-[#1A5276]/20 hover:scale-[1.01]'
              }`}
            >
              {/* Fondo con gradiente */}
              <div className="absolute inset-0 bg-gradient-to-br from-[#1A5276] to-[#154360] opacity-90" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />

              {/* Patron decorativo */}
              <div className="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-[#2471A3]/20 blur-2xl" />
              <div className="absolute -left-4 bottom-0 h-24 w-24 rounded-full bg-[#1A5276]/30 blur-xl" />

              <div className="relative p-8">
                {/* Icono */}
                <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-xl bg-white/10 backdrop-blur-sm border border-white/10">
                  <Eye className="h-7 w-7 text-white" />
                </div>

                {/* Titulo */}
                <h2 className="font-titulo text-xl font-bold text-white mb-2">
                  Direccion de Estudios Sectoriales
                </h2>
                <p className="text-xs font-medium uppercase tracking-wider text-[#85C1E9] mb-4">
                  DES — Control Macro
                </p>

                {/* Descripcion */}
                <p className="text-sm text-white/70 leading-relaxed mb-6">
                  Analisis sectorial, observatorio fiscal, estudios transversales,
                  indicadores macroeconomicos y vigilancia sectorial preventiva.
                </p>

                {/* Caracteristicas */}
                <div className="space-y-2 mb-6">
                  <div className="flex items-center gap-2 text-xs text-white/60">
                    <BarChart3 className="h-3.5 w-3.5" />
                    <span>Observatorio sectorial en tiempo real</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-white/60">
                    <FileSearch className="h-3.5 w-3.5" />
                    <span>Analisis de riesgos transversales</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-white/60">
                    <AlertTriangle className="h-3.5 w-3.5" />
                    <span>Alertas tempranas sectoriales</span>
                  </div>
                </div>

                {/* Boton */}
                <div className="flex items-center gap-2 text-sm font-medium text-white group-hover:gap-3 transition-all">
                  Ingresar a DES
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </div>
              </div>
            </button>
          )}

          {/* Tarjeta DVF */}
          {(!usuario || puedeVerDireccion('DVF')) && (
            <button
              onClick={() => seleccionarDireccion('DVF')}
              disabled={seleccionando !== null}
              className={`group relative overflow-hidden rounded-2xl border text-left transition-all duration-500 ${
                seleccionando === 'DVF'
                  ? 'scale-[1.02] border-[#27AE60] shadow-2xl shadow-[#1E8449]/40'
                  : seleccionando === 'DES'
                    ? 'scale-95 opacity-40'
                    : 'border-[#2D3748]/50 hover:border-[#1E8449]/60 hover:shadow-xl hover:shadow-[#1E8449]/20 hover:scale-[1.01]'
              }`}
            >
              {/* Fondo con gradiente */}
              <div className="absolute inset-0 bg-gradient-to-br from-[#1E8449] to-[#196F3D] opacity-90" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />

              {/* Patron decorativo */}
              <div className="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-[#27AE60]/20 blur-2xl" />
              <div className="absolute -left-4 bottom-0 h-24 w-24 rounded-full bg-[#1E8449]/30 blur-xl" />

              <div className="relative p-8">
                {/* Icono */}
                <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-xl bg-white/10 backdrop-blur-sm border border-white/10">
                  <Building2 className="h-7 w-7 text-white" />
                </div>

                {/* Titulo */}
                <h2 className="font-titulo text-xl font-bold text-white mb-2">
                  Direccion de Vigilancia Fiscal
                </h2>
                <p className="text-xs font-medium uppercase tracking-wider text-[#82E0AA] mb-4">
                  DVF — Control Micro
                </p>

                {/* Descripcion */}
                <p className="text-sm text-white/70 leading-relaxed mb-6">
                  Auditorias individuales, hallazgos fiscales, generacion de formatos,
                  vigilancia fiscal puntual y seguimiento de planes de mejoramiento.
                </p>

                {/* Caracteristicas */}
                <div className="space-y-2 mb-6">
                  <div className="flex items-center gap-2 text-xs text-white/60">
                    <Shield className="h-3.5 w-3.5" />
                    <span>Hallazgos con 5 elementos estructurados</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-white/60">
                    <FileSearch className="h-3.5 w-3.5" />
                    <span>Generacion de 30 formatos de auditoria</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-white/60">
                    <AlertTriangle className="h-3.5 w-3.5" />
                    <span>Flujo de trabajo de hallazgos</span>
                  </div>
                </div>

                {/* Boton */}
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
