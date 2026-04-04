'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { User, Lock, Eye, EyeOff, AlertCircle, ArrowRight } from 'lucide-react';
import { iniciarSesion } from '@/lib/auth';

/**
 * Pagina de inicio de sesion de CecilIA v2
 * Diseno oscuro profesional con acentos dorados y efecto glass
 */
export default function PaginaLogin() {
  const router = useRouter();
  const [usuario, setUsuario] = useState('');
  const [contrasena, setContrasena] = useState('');
  const [mostrarContrasena, setMostrarContrasena] = useState(false);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState('');

  const manejarEnvio = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setCargando(true);

    try {
      await iniciarSesion({ usuario, contrasena });
      router.push('/seleccion-rol');
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Error al iniciar sesion. Verifique sus credenciales.',
      );
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#0F1419]">
      {/* Fondo con gradiente sutil y particulas decorativas */}
      <div className="absolute inset-0">
        {/* Gradiente radial superior */}
        <div className="absolute -top-1/4 left-1/2 h-[600px] w-[800px] -translate-x-1/2 rounded-full bg-[#C9A84C]/[0.03] blur-[100px]" />
        {/* Gradiente radial inferior izquierdo */}
        <div className="absolute -bottom-1/4 -left-1/4 h-[500px] w-[500px] rounded-full bg-[#1A5276]/[0.05] blur-[80px]" />
        {/* Gradiente radial inferior derecho */}
        <div className="absolute -bottom-1/4 -right-1/4 h-[500px] w-[500px] rounded-full bg-[#1E8449]/[0.05] blur-[80px]" />
        {/* Patron de lineas sutiles */}
        <div
          className="absolute inset-0 opacity-[0.015]"
          style={{
            backgroundImage: `linear-gradient(rgba(201,168,76,0.3) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(201,168,76,0.3) 1px, transparent 1px)`,
            backgroundSize: '60px 60px',
          }}
        />
      </div>

      {/* Tarjeta de login con efecto glass */}
      <div className="relative z-10 w-full max-w-md mx-4">
        <div className="rounded-2xl border border-[#2D3748]/40 bg-[#1A2332]/70 shadow-2xl backdrop-blur-xl">
          {/* Borde dorado superior sutil */}
          <div className="absolute -top-px left-8 right-8 h-px bg-gradient-to-r from-transparent via-[#C9A84C]/40 to-transparent" />

          <div className="p-8">
            {/* Logos institucionales */}
            <div className="flex items-center justify-between mb-8">
              <div className="relative h-14 w-14">
                <Image
                  src="/logo-cgr.png"
                  alt="Contraloria General de la Republica"
                  fill
                  className="object-contain"
                  sizes="56px"
                  priority
                />
              </div>
              <div className="relative h-14 w-14">
                <Image
                  src="/logo-cecilia.png"
                  alt="CecilIA"
                  fill
                  className="object-contain"
                  sizes="56px"
                  priority
                />
              </div>
            </div>

            {/* Titulo principal */}
            <div className="text-center mb-8">
              <h1 className="font-titulo text-3xl font-bold text-[#C9A84C] mb-2">
                CecilIA v2
              </h1>
              <p className="text-sm text-[#9AA0A6] leading-relaxed">
                Sistema de Inteligencia Artificial
                <br />
                para Control Fiscal
              </p>
              <div className="mt-3 flex items-center justify-center">
                <div className="h-px w-8 bg-gradient-to-r from-transparent to-[#2D3748]" />
                <p className="mx-3 text-[10px] uppercase tracking-[0.2em] text-[#5F6368]">
                  Contraloria General de la Republica de Colombia
                </p>
                <div className="h-px w-8 bg-gradient-to-l from-transparent to-[#2D3748]" />
              </div>
            </div>

            {/* Formulario de login */}
            <form onSubmit={manejarEnvio} className="space-y-5">
              {/* Campo de usuario */}
              <div>
                <label htmlFor="usuario" className="mb-1.5 block text-xs font-medium text-[#9AA0A6]">
                  Usuario institucional
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#5F6368]" />
                  <input
                    id="usuario"
                    type="text"
                    value={usuario}
                    onChange={(e) => setUsuario(e.target.value)}
                    placeholder="Ingrese su usuario"
                    required
                    autoComplete="username"
                    className="w-full rounded-lg border border-[#2D3748] bg-[#0A0F14]/80 py-3 pl-10 pr-4 text-sm text-[#E8EAED] placeholder:text-[#5F6368] transition-all duration-200 focus:border-[#C9A84C] focus:outline-none focus:ring-1 focus:ring-[#C9A84C]/50"
                  />
                </div>
              </div>

              {/* Campo de contrasena */}
              <div>
                <label htmlFor="contrasena" className="mb-1.5 block text-xs font-medium text-[#9AA0A6]">
                  Contrasena
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#5F6368]" />
                  <input
                    id="contrasena"
                    type={mostrarContrasena ? 'text' : 'password'}
                    value={contrasena}
                    onChange={(e) => setContrasena(e.target.value)}
                    placeholder="Ingrese su contrasena"
                    required
                    autoComplete="current-password"
                    className="w-full rounded-lg border border-[#2D3748] bg-[#0A0F14]/80 py-3 pl-10 pr-12 text-sm text-[#E8EAED] placeholder:text-[#5F6368] transition-all duration-200 focus:border-[#C9A84C] focus:outline-none focus:ring-1 focus:ring-[#C9A84C]/50"
                  />
                  <button
                    type="button"
                    onClick={() => setMostrarContrasena(!mostrarContrasena)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-[#5F6368] hover:text-[#9AA0A6] transition-colors"
                    tabIndex={-1}
                  >
                    {mostrarContrasena ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Mensaje de error */}
              {error && (
                <div className="flex items-start gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-3">
                  <AlertCircle className="h-4 w-4 flex-shrink-0 text-red-400 mt-0.5" />
                  <p className="text-xs text-red-300">{error}</p>
                </div>
              )}

              {/* Boton de inicio de sesion */}
              <button
                type="submit"
                disabled={cargando || !usuario || !contrasena}
                className="group relative w-full overflow-hidden rounded-lg bg-gradient-to-r from-[#C9A84C] to-[#D4B96A] py-3 text-sm font-semibold text-[#0F1419] shadow-lg shadow-[#C9A84C]/20 transition-all duration-300 hover:from-[#D4B96A] hover:to-[#C9A84C] hover:shadow-[#C9A84C]/30 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {/* Efecto de brillo al hover */}
                <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent transition-transform duration-700 group-hover:translate-x-full" />
                <span className="relative flex items-center justify-center gap-2">
                  {cargando ? (
                    <>
                      <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      Verificando credenciales...
                    </>
                  ) : (
                    <>
                      Iniciar Sesion
                      <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                    </>
                  )}
                </span>
              </button>
            </form>
          </div>

          {/* Pie de la tarjeta — Creditos institucionales */}
          <div className="border-t border-[#2D3748]/30 px-8 py-4 space-y-1.5">
            <p className="text-center text-[10px] text-[#5F6368] leading-relaxed">
              Contraloria Delegada para el Sector TIC — CD-TIC-CGR
            </p>
            <p className="text-center text-[10px] italic text-[#8899AA] leading-relaxed">
              Proyecto concebido e impulsado bajo la direccion del
              <br />
              Dr. Omar Javier Contreras Socarras
              <br />
              Contralor Delegado para el Sector TIC
            </p>
          </div>
        </div>

        {/* Texto de version debajo de la tarjeta */}
        <p className="mt-6 text-center text-[10px] text-[#5F6368]/60">
          CecilIA v2.0 — Entorno seguro de la CGR — Todos los derechos reservados
        </p>
      </div>
    </div>
  );
}
