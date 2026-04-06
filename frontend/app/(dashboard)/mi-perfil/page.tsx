'use client';

import React, { useState, useEffect } from 'react';
import {
  User,
  Mail,
  Shield,
  Building2,
  Calendar,
  Clock,
  Save,
  CheckCircle,
  AlertTriangle,
  KeyRound,
  Briefcase,
} from 'lucide-react';
import { Tarjeta } from '@/components/ui/card';
import { Boton } from '@/components/ui/button';
import { Insignia } from '@/components/ui/badge';
import { apiCliente } from '@/lib/api';
import { obtenerUsuario, obtenerDireccionActiva } from '@/lib/auth';
import type { Direccion } from '@/lib/types';

interface PerfilUsuario {
  id: number;
  usuario: string;
  nombre_completo: string;
  email: string;
  rol: string;
  direccion: string | null;
  activo: boolean;
  modulos: string[];
  permisos: string[];
  acciones_rapidas: string[];
}

const NOMBRES_ROL: Record<string, string> = {
  auditor: 'Auditor',
  auditor_des: 'Auditor DES',
  auditor_dvf: 'Auditor DVF',
  profesional_des: 'Profesional DES',
  profesional_dvf: 'Profesional DVF',
  director_des: 'Director DES',
  director_dvf: 'Director DVF',
  admin_tic: 'Administrador TIC',
  observatorio: 'Observatorio',
  aprendiz: 'Aprendiz',
};

const NOMBRES_MODULO: Record<string, string> = {
  chat: 'Chat IA',
  formatos: 'Formatos',
  auditorias: 'Auditorias',
  hallazgos: 'Hallazgos',
  analytics: 'Analitica',
  observatorio: 'Observatorio',
  capacitacion: 'Capacitacion',
  admin: 'Administracion',
  workspace: 'Workspace',
};

export default function PaginaMiPerfil() {
  const [perfil, setPerfil] = useState<PerfilUsuario | null>(null);
  const [cargando, setCargando] = useState(true);
  const [direccionActiva, setDireccionActiva] = useState<Direccion>('DES');

  // Cambio de contrasena
  const [mostrarCambioPass, setMostrarCambioPass] = useState(false);
  const [passActual, setPassActual] = useState('');
  const [passNueva, setPassNueva] = useState('');
  const [passConfirmar, setPassConfirmar] = useState('');
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState<{ tipo: 'exito' | 'error'; texto: string } | null>(null);

  useEffect(() => {
    const dir = obtenerDireccionActiva();
    if (dir) setDireccionActiva(dir);
    cargarPerfil();
  }, []);

  const cargarPerfil = async () => {
    setCargando(true);
    try {
      const data = await apiCliente.get<PerfilUsuario>('/auth/me');
      setPerfil(data);
    } catch {
      // Fallback: usar datos locales
      const u = obtenerUsuario();
      if (u) {
        setPerfil({
          id: u.id,
          usuario: u.usuario,
          nombre_completo: u.nombre_completo,
          email: u.email,
          rol: u.rol,
          direccion: u.direccion,
          activo: true,
          modulos: u.modulos || [],
          permisos: u.permisos || [],
          acciones_rapidas: u.acciones_rapidas || [],
        });
      }
    } finally {
      setCargando(false);
    }
  };

  const cambiarContrasena = async () => {
    if (passNueva !== passConfirmar) {
      setMensaje({ tipo: 'error', texto: 'Las contrasenas no coinciden.' });
      return;
    }
    if (passNueva.length < 8) {
      setMensaje({ tipo: 'error', texto: 'La contrasena debe tener al menos 8 caracteres.' });
      return;
    }

    setGuardando(true);
    try {
      await apiCliente.post('/auth/cambiar-contrasena', {
        contrasena_actual: passActual,
        contrasena_nueva: passNueva,
      });
      setMensaje({ tipo: 'exito', texto: 'Contrasena actualizada exitosamente.' });
      setPassActual('');
      setPassNueva('');
      setPassConfirmar('');
      setMostrarCambioPass(false);
    } catch {
      setMensaje({ tipo: 'error', texto: 'No se pudo cambiar la contrasena. Verifique la contrasena actual.' });
    } finally {
      setGuardando(false);
    }
  };

  const colorDir = direccionActiva === 'DES' ? '#1A5276' : '#1E8449';

  if (cargando) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#C9A84C] border-t-transparent" />
      </div>
    );
  }

  if (!perfil) {
    return (
      <div className="flex h-full items-center justify-center text-[#5F6368] text-sm">
        No se pudo cargar el perfil.
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Encabezado */}
      <div className="mb-6">
        <h1 className="font-titulo text-xl font-bold text-[#E8EAED] flex items-center gap-2">
          <User className="h-6 w-6 text-[#C9A84C]" />
          Mi Perfil
        </h1>
        <p className="mt-1 text-xs text-[#5F6368]">
          Informacion de su cuenta en CecilIA — Contraloria General de la Republica
        </p>
      </div>

      {/* Mensaje de estado */}
      {mensaje && (
        <div
          className={`mb-4 flex items-center gap-2 rounded-lg border px-4 py-3 text-xs ${
            mensaje.tipo === 'exito'
              ? 'border-green-500/30 bg-green-500/10 text-green-400'
              : 'border-red-500/30 bg-red-500/10 text-red-400'
          }`}
        >
          {mensaje.tipo === 'exito' ? (
            <CheckCircle className="h-4 w-4" />
          ) : (
            <AlertTriangle className="h-4 w-4" />
          )}
          {mensaje.texto}
          <button onClick={() => setMensaje(null)} className="ml-auto text-[#5F6368] hover:text-[#9AA0A6]">
            &times;
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Tarjeta principal del perfil */}
        <div className="md:col-span-2">
          <Tarjeta className="p-6">
            <div className="flex items-start gap-4">
              {/* Avatar */}
              <div
                className="flex h-16 w-16 items-center justify-center rounded-full"
                style={{ background: `linear-gradient(135deg, #C9A84C, ${colorDir})` }}
              >
                <User className="h-8 w-8 text-[#0F1419]" />
              </div>

              <div className="flex-1">
                <h2 className="text-lg font-bold text-[#E8EAED]">{perfil.nombre_completo}</h2>
                <p className="text-xs text-[#9AA0A6]">@{perfil.usuario}</p>

                <div className="mt-3 flex flex-wrap gap-2">
                  <Insignia variante="oro">
                    <Shield className="h-3 w-3 mr-1" />
                    {NOMBRES_ROL[perfil.rol] || perfil.rol}
                  </Insignia>
                  {perfil.direccion && (
                    <Insignia variante={perfil.direccion === 'DES' ? 'info' : 'exito'}>
                      <Building2 className="h-3 w-3 mr-1" />
                      {perfil.direccion === 'DES' ? 'Estudios Sectoriales' : 'Vigilancia Fiscal'}
                    </Insignia>
                  )}
                  <Insignia variante={perfil.activo ? 'exito' : 'rojo'}>
                    {perfil.activo ? 'Activo' : 'Inactivo'}
                  </Insignia>
                </div>
              </div>
            </div>

            {/* Detalles */}
            <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex items-center gap-3 rounded-lg border border-[#2D3748]/30 bg-[#0F1419]/50 px-4 py-3">
                <Mail className="h-4 w-4 text-[#5F6368]" />
                <div>
                  <p className="text-[10px] text-[#5F6368] uppercase tracking-wider">Correo</p>
                  <p className="text-xs text-[#E8EAED]">{perfil.email}</p>
                </div>
              </div>

              <div className="flex items-center gap-3 rounded-lg border border-[#2D3748]/30 bg-[#0F1419]/50 px-4 py-3">
                <Briefcase className="h-4 w-4 text-[#5F6368]" />
                <div>
                  <p className="text-[10px] text-[#5F6368] uppercase tracking-wider">Rol</p>
                  <p className="text-xs text-[#E8EAED]">{NOMBRES_ROL[perfil.rol] || perfil.rol}</p>
                </div>
              </div>

              <div className="flex items-center gap-3 rounded-lg border border-[#2D3748]/30 bg-[#0F1419]/50 px-4 py-3">
                <Building2 className="h-4 w-4 text-[#5F6368]" />
                <div>
                  <p className="text-[10px] text-[#5F6368] uppercase tracking-wider">Direccion</p>
                  <p className="text-xs text-[#E8EAED]">
                    {perfil.direccion === 'DES'
                      ? 'Direccion de Estudios Sectoriales'
                      : perfil.direccion === 'DVF'
                      ? 'Direccion de Vigilancia Fiscal'
                      : 'Sin asignar'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 rounded-lg border border-[#2D3748]/30 bg-[#0F1419]/50 px-4 py-3">
                <Shield className="h-4 w-4 text-[#5F6368]" />
                <div>
                  <p className="text-[10px] text-[#5F6368] uppercase tracking-wider">Estado</p>
                  <p className="text-xs text-[#E8EAED]">{perfil.activo ? 'Cuenta activa' : 'Cuenta inactiva'}</p>
                </div>
              </div>
            </div>
          </Tarjeta>
        </div>

        {/* Panel lateral */}
        <div className="space-y-4">
          {/* Modulos habilitados */}
          <Tarjeta className="p-4">
            <h3 className="text-xs font-semibold text-[#E8EAED] mb-3 flex items-center gap-2">
              <KeyRound className="h-3.5 w-3.5 text-[#C9A84C]" />
              Modulos habilitados
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {perfil.modulos.length > 0 ? (
                perfil.modulos.map((mod) => (
                  <span
                    key={mod}
                    className="rounded-full px-2 py-0.5 text-[10px] font-medium bg-[#C9A84C]/10 text-[#D4B96A] border border-[#C9A84C]/20"
                  >
                    {NOMBRES_MODULO[mod] || mod}
                  </span>
                ))
              ) : (
                <span className="text-[10px] text-[#5F6368]">Todos los modulos</span>
              )}
            </div>
          </Tarjeta>

          {/* Cambiar contrasena */}
          <Tarjeta className="p-4">
            <h3 className="text-xs font-semibold text-[#E8EAED] mb-3 flex items-center gap-2">
              <KeyRound className="h-3.5 w-3.5 text-[#C9A84C]" />
              Seguridad
            </h3>
            {!mostrarCambioPass ? (
              <Boton
                variante="secundario"
                tamano="sm"
                onClick={() => setMostrarCambioPass(true)}
                className="w-full text-[10px]"
              >
                Cambiar contrasena
              </Boton>
            ) : (
              <div className="space-y-2">
                <input
                  type="password"
                  placeholder="Contrasena actual"
                  value={passActual}
                  onChange={(e) => setPassActual(e.target.value)}
                  className="w-full rounded-md border border-[#2D3748] bg-[#0F1419] px-3 py-2 text-xs text-[#E8EAED] placeholder-[#5F6368] focus:border-[#C9A84C] focus:outline-none"
                />
                <input
                  type="password"
                  placeholder="Nueva contrasena"
                  value={passNueva}
                  onChange={(e) => setPassNueva(e.target.value)}
                  className="w-full rounded-md border border-[#2D3748] bg-[#0F1419] px-3 py-2 text-xs text-[#E8EAED] placeholder-[#5F6368] focus:border-[#C9A84C] focus:outline-none"
                />
                <input
                  type="password"
                  placeholder="Confirmar contrasena"
                  value={passConfirmar}
                  onChange={(e) => setPassConfirmar(e.target.value)}
                  className="w-full rounded-md border border-[#2D3748] bg-[#0F1419] px-3 py-2 text-xs text-[#E8EAED] placeholder-[#5F6368] focus:border-[#C9A84C] focus:outline-none"
                />
                <div className="flex gap-2">
                  <Boton
                    variante="primario"
                    tamano="sm"
                    onClick={cambiarContrasena}
                    disabled={guardando}
                    className="flex-1 text-[10px]"
                  >
                    {guardando ? 'Guardando...' : 'Guardar'}
                  </Boton>
                  <Boton
                    variante="fantasma"
                    tamano="sm"
                    onClick={() => {
                      setMostrarCambioPass(false);
                      setPassActual('');
                      setPassNueva('');
                      setPassConfirmar('');
                    }}
                    className="text-[10px]"
                  >
                    Cancelar
                  </Boton>
                </div>
              </div>
            )}
          </Tarjeta>
        </div>
      </div>
    </div>
  );
}
