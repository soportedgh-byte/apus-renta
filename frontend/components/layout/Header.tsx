'use client';

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import {
  Cpu,
  ChevronDown,
  LogOut,
  Settings,
  User,
  Wifi,
  HardDrive,
} from 'lucide-react';
import { Insignia } from '@/components/ui/badge';
import { obtenerUsuario, obtenerDireccionActiva, cerrarSesion } from '@/lib/auth';
import type { Direccion } from '@/lib/types';

/**
 * Encabezado superior del dashboard
 * Muestra estado de conexion, modelo activo, workspace y usuario
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
        setModeloActivo('claude-sonnet-4-20250514');
      }
    };
    cargarModelo();
  }, []);

  const nombreRol: Record<string, string> = {
    auditor: 'Auditor',
    director_des: 'Director DES',
    director_dvf: 'Director DVF',
    admin: 'Administrador',
    superadmin: 'Super Admin',
  };

  return (
    <header className="flex h-14 items-center justify-between border-b border-[#2D3748]/30 bg-[#0F1419] px-4">
      {/* Lado izquierdo: Estado de conexion */}
      <div className="flex items-center gap-4">
        {/* Indicador CecilIA conectada */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <div className="h-2 w-2 rounded-full bg-green-400 pulso-conexion" />
          </div>
          <span className="text-xs font-medium text-[#E8EAED]">CecilIA conectada</span>
        </div>

        {/* Separador */}
        <div className="h-4 w-px bg-[#2D3748]" />

        {/* Modelo activo */}
        <div className="flex items-center gap-1.5 text-xs text-[#9AA0A6]">
          <Cpu className="h-3.5 w-3.5" />
          <span>{modeloActivo || 'Conectando...'}</span>
        </div>

        {/* Separador */}
        <div className="h-4 w-px bg-[#2D3748]" />

        {/* Workspace activo */}
        <div className="flex items-center gap-1.5 text-xs text-[#9AA0A6]">
          <HardDrive className="h-3.5 w-3.5" />
          <span>Workspace activo</span>
        </div>
      </div>

      {/* Lado derecho: Usuario */}
      <div className="flex items-center gap-3">
        {/* Insignia de direccion */}
        {direccion && (
          <Insignia variante={direccion === 'DES' ? 'des' : 'dvf'}>
            {direccion === 'DES' ? 'Estudios Sectoriales' : 'Vigilancia Fiscal'}
          </Insignia>
        )}

        {/* Menu de usuario */}
        <div className="relative">
          <button
            onClick={() => setMenuAbierto(!menuAbierto)}
            className="flex items-center gap-2 rounded-lg px-2 py-1.5 hover:bg-[#1A2332] transition-colors"
          >
            {/* Avatar */}
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

          {/* Dropdown del usuario */}
          {menuAbierto && (
            <>
              <div className="fixed inset-0 z-40" onClick={() => setMenuAbierto(false)} />
              <div className="absolute right-0 top-full z-50 mt-1 w-48 rounded-lg border border-[#2D3748] bg-[#1A2332] shadow-xl">
                <div className="p-1">
                  <button className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-xs text-[#9AA0A6] hover:bg-[#243044] hover:text-[#E8EAED] transition-colors">
                    <User className="h-3.5 w-3.5" />
                    Mi perfil
                  </button>
                  <button className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-xs text-[#9AA0A6] hover:bg-[#243044] hover:text-[#E8EAED] transition-colors">
                    <Settings className="h-3.5 w-3.5" />
                    Configuracion
                  </button>
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
