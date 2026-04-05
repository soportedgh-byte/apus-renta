'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Cpu,
  ChevronDown,
  LogOut,
  Settings,
  User,
  HardDrive,
  Info,
  RefreshCw,
} from 'lucide-react';
import { obtenerUsuario, obtenerDireccionActiva, cerrarSesion } from '@/lib/auth';
import type { Direccion } from '@/lib/types';

/**
 * Encabezado superior del dashboard
 * Indicador de conexion, modelo activo, workspace y perfil de usuario
 */
export function Encabezado() {
  const [usuario, setUsuario] = useState<{ nombre_completo: string; rol: string } | null>(null);
  const [direccion, setDireccion] = useState<Direccion | null>(null);
  const [menuAbierto, setMenuAbierto] = useState(false);
  const [modeloActivo, setModeloActivo] = useState<string | null>(null);

  useEffect(() => {
    const u = obtenerUsuario();
    if (u) {
      setUsuario({ nombre_completo: u.nombre_completo, rol: u.rol });
    }
    setDireccion(obtenerDireccionActiva());
  }, []);

  useEffect(() => {
    const cargarModelo = async () => {
      try {
        const urlBase = process.env.NEXT_PUBLIC_API_URL || '/api';
        const resp = await fetch(`${urlBase}/config/modelo-activo`);
        if (resp.ok) {
          const data = await resp.json();
          setModeloActivo(data.nombre_display || data.modelo);
        }
      } catch {
        setModeloActivo(null);
      }
    };
    cargarModelo();
  }, []);

  const nombreRol: Record<string, string> = {
    auditor: 'Auditor',
    auditor_des: 'Auditor DES',
    auditor_dvf: 'Auditor DVF',
    profesional_des: 'Profesional DES',
    profesional_dvf: 'Profesional DVF',
    director_des: 'Director DES',
    director_dvf: 'Director DVF',
    admin_tic: 'Administrador',
    observatorio: 'Observatorio',
  };

  const colorDireccion = direccion === 'DES' ? '#1A5276' : '#1E8449';
  const colorDireccionLight = direccion === 'DES' ? '#2471A3' : '#27AE60';

  return (
    <header className="flex h-12 items-center justify-between border-b border-[#2D3748]/30 bg-[#0F1419] px-4">
      {/* Lado izquierdo: Status */}
      <div className="flex items-center gap-3">
        {/* Indicador CecilIA conectada */}
        <div className="flex items-center gap-1.5">
          <div className="relative">
            <div className="h-2 w-2 rounded-full bg-green-400 pulso-conexion" />
          </div>
          <span className="text-[11px] font-medium text-[#E8EAED]">CecilIA conectada</span>
        </div>

        <div className="h-3.5 w-px bg-[#2D3748]" />

        {/* Modelo activo */}
        <div className="flex items-center gap-1.5">
          <Cpu className="h-3 w-3 text-[#5F6368]" />
          <span
            className="rounded-full px-2 py-0.5 text-[10px] font-medium"
            style={{
              backgroundColor: '#C9A84C15',
              color: '#D4B96A',
              border: '1px solid #C9A84C30',
            }}
          >
            {modeloActivo || 'Conectando...'}
          </span>
        </div>

        <div className="h-3.5 w-px bg-[#2D3748] hidden md:block" />

        {/* Workspace */}
        <div className="items-center gap-1.5 text-[11px] text-[#9AA0A6] hidden md:flex">
          <HardDrive className="h-3 w-3" />
          <span>Workspace: Conectado</span>
        </div>

        <div className="h-3.5 w-px bg-[#2D3748] hidden md:block" />

        {/* Info tooltip Circular 023 */}
        <div className="relative group hidden md:block">
          <div className="flex items-center gap-1 text-[#5F6368] cursor-help">
            <Info className="h-3.5 w-3.5" />
          </div>
          <div className="absolute left-0 top-full z-50 mt-2 w-72 rounded-lg border border-[#2D3748] bg-[#1A2332] p-3 shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
            <p className="text-[11px] text-[#9AA0A6] leading-relaxed">
              CecilIA utiliza inteligencia artificial para asistir en el control fiscal.
              Todos los resultados requieren validacion humana conforme a la Circular 023 de la CGR.
            </p>
          </div>
        </div>
      </div>

      {/* Lado derecho: Direccion + Usuario */}
      <div className="flex items-center gap-3">
        {/* Badge direccion */}
        {direccion && (
          <span
            className="rounded-full px-2.5 py-0.5 text-[10px] font-semibold hidden sm:inline-flex"
            style={{
              backgroundColor: `${colorDireccion}20`,
              color: colorDireccionLight,
              border: `1px solid ${colorDireccion}40`,
            }}
          >
            {direccion === 'DES' ? 'Estudios Sectoriales' : 'Vigilancia Fiscal'}
          </span>
        )}

        {/* Menu de usuario */}
        <div className="relative">
          <button
            onClick={() => setMenuAbierto(!menuAbierto)}
            className="flex items-center gap-2 rounded-lg px-2 py-1.5 hover:bg-[#1A2332] transition-colors"
          >
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-[#C9A84C] to-[#A88B3D]">
              <User className="h-3.5 w-3.5 text-[#0F1419]" />
            </div>
            <div className="hidden md:block text-left">
              <p className="text-xs font-medium text-[#E8EAED]">
                {usuario?.nombre_completo || 'Usuario'}
              </p>
              <p className="text-[10px] text-[#5F6368]">
                {usuario?.rol ? nombreRol[usuario.rol] || usuario.rol : ''}
              </p>
            </div>
            <ChevronDown className="h-3 w-3 text-[#5F6368]" />
          </button>

          {menuAbierto && (
            <>
              <div className="fixed inset-0 z-40" onClick={() => setMenuAbierto(false)} />
              <div className="absolute right-0 top-full z-50 mt-1 w-48 rounded-lg border border-[#2D3748] bg-[#1A2332] shadow-xl">
                <div className="p-1">
                  <Link href="/mi-perfil" onClick={() => setMenuAbierto(false)} className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-xs text-[#9AA0A6] hover:bg-[#243044] hover:text-[#E8EAED] transition-colors">
                    <User className="h-3.5 w-3.5" />
                    Mi perfil
                  </Link>
                  <Link href="/configuracion" onClick={() => setMenuAbierto(false)} className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-xs text-[#9AA0A6] hover:bg-[#243044] hover:text-[#E8EAED] transition-colors">
                    <Settings className="h-3.5 w-3.5" />
                    Configuracion
                  </Link>
                  <Link href="/seleccion-rol" className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-xs text-[#9AA0A6] hover:bg-[#243044] hover:text-[#E8EAED] transition-colors">
                    <RefreshCw className="h-3.5 w-3.5" />
                    Cambiar direccion
                  </Link>
                  <div className="my-1 border-t border-[#2D3748]" />
                  <button
                    onClick={cerrarSesion}
                    className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-xs text-red-400 hover:bg-red-500/10 transition-colors"
                  >
                    <LogOut className="h-3.5 w-3.5" />
                    Cerrar sesion
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

export default Encabezado;
