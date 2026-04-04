'use client';

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { User, Lock, Eye, EyeOff, AlertCircle, ArrowRight } from 'lucide-react';
import { iniciarSesion } from '@/lib/auth';

/**
 * Pagina de inicio de sesion de CecilIA v2
 * Diseno institucional de alto nivel — CGR
 * Fondo degradado oscuro, logos centrados, efecto glass profesional
 */
export default function PaginaLogin() {
  const router = useRouter();
  const [usuario, setUsuario] = useState('');
  const [contrasena, setContrasena] = useState('');
  const [mostrarContrasena, setMostrarContrasena] = useState(false);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState('');
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Fade-in suave al cargar
    const t = setTimeout(() => setVisible(true), 50);
    return () => clearTimeout(t);
  }, []);

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
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden"
      style={{ background: 'linear-gradient(180deg, #0A0F1A 0%, #1A2332 50%, #0D1520 100%)' }}
    >
      {/* Particulas decorativas */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute -top-1/4 left-1/2 h-[700px] w-[900px] -translate-x-1/2 rounded-full bg-[#C9A84C]/[0.025] blur-[120px]" />
        <div className="absolute -bottom-1/3 -left-1/4 h-[500px] w-[500px] rounded-full bg-[#1A5276]/[0.04] blur-[100px]" />
        <div className="absolute -bottom-1/3 -right-1/4 h-[500px] w-[500px] rounded-full bg-[#1E8449]/[0.04] blur-[100px]" />
        {/* Grid sutil */}
        <div
          className="absolute inset-0 opacity-[0.012]"
          style={{
            backgroundImage: `linear-gradient(rgba(201,168,76,0.4) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(201,168,76,0.4) 1px, transparent 1px)`,
            backgroundSize: '60px 60px',
          }}
        />
      </div>

      {/* Contenedor con fade-in */}
      <div
        className={`relative z-10 w-full max-w-[440px] mx-4 transition-all duration-700 ease-out ${
          visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
        }`}
      >
        {/* Logo CGR centrado arriba */}
        <div className="flex justify-center mb-8">
          <div className="relative" style={{ width: 340, height: 91 }}>
            <Image
              src="/logo-cgr.png"
              alt="Contraloria General de la Republica de Colombia"
              fill
              className="object-contain"
              sizes="340px"
              priority
            />
          </div>
        </div>

        {/* Tarjeta de login glass */}
        <div className="rounded-2xl border border-white/[0.06] bg-[#1A2332]/60 shadow-2xl backdrop-blur-xl">
          {/* Linea dorada superior */}
          <div className="absolute -top-px left-12 right-12 h-px bg-gradient-to-r from-transparent via-[#C9A84C]/30 to-transparent" />

          <div className="p-8 pb-6">
            {/* Logo CecilIA centrado */}
            <div className="flex justify-center mb-5">
              <div className="relative h-[120px] w-[120px]">
                <Image
                  src="/logo-cecilia.png"
                  alt="CecilIA"
                  fill
                  className="object-contain"
                  sizes="120px"
                  priority
                />
              </div>
            </div>

            {/* Titulo */}
            <div className="text-center mb-7">
              <h1 className="font-titulo text-4xl font-bold text-[#C9A84C] mb-1.5" style={{ fontSize: '36px' }}>
                CecilIA v2
              </h1>
              <p className="text-[#2980B9] font-interfaz" style={{ fontSize: '16px' }}>
                Sistema de IA para Control Fiscal
              </p>
              <div className="mt-3 flex items-center justify-center">
                <div className="h-px w-10 bg-gradient-to-r from-transparent to-[#2D3748]" />
                <p className="mx-3 text-[10px] uppercase tracking-[0.2em] text-[#556677]">
                  Contraloria General de la Republica
                </p>
                <div className="h-px w-10 bg-gradient-to-l from-transparent to-[#2D3748]" />
              </div>
            </div>

            {/* Formulario */}
            <form onSubmit={manejarEnvio} className="space-y-5">
              {/* Campo de usuario */}
              <div>
                <label htmlFor="usuario" className="mb-1.5 block text-[#8899AA]" style={{ fontSize: '12px' }}>
                  Usuario institucional
                </label>
                <div className="relative">
                  <User className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[#556677]" />
                  <input
                    id="usuario"
                    type="text"
                    value={usuario}
                    onChange={(e) => setUsuario(e.target.value)}
                    placeholder="Ingrese su usuario"
                    required
                    autoComplete="username"
                    className="w-full py-3 pl-11 pr-4 text-sm text-[#E8EAED] placeholder:text-[#556677] transition-all duration-200 focus:outline-none focus:ring-1 focus:ring-[#C9A84C]/50 focus:border-[#C9A84C]/60"
                    style={{
                      background: 'rgba(255,255,255,0.05)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '10px',
                    }}
                  />
                </div>
              </div>

              {/* Campo de contrasena */}
              <div>
                <label htmlFor="contrasena" className="mb-1.5 block text-[#8899AA]" style={{ fontSize: '12px' }}>
                  Contrasena
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[#556677]" />
                  <input
                    id="contrasena"
                    type={mostrarContrasena ? 'text' : 'password'}
                    value={contrasena}
                    onChange={(e) => setContrasena(e.target.value)}
                    placeholder="Ingrese su contrasena"
                    required
                    autoComplete="current-password"
                    className="w-full py-3 pl-11 pr-12 text-sm text-[#E8EAED] placeholder:text-[#556677] transition-all duration-200 focus:outline-none focus:ring-1 focus:ring-[#C9A84C]/50 focus:border-[#C9A84C]/60"
                    style={{
                      background: 'rgba(255,255,255,0.05)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '10px',
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => setMostrarContrasena(!mostrarContrasena)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[#556677] hover:text-[#8899AA] transition-colors"
                    tabIndex={-1}
                  >
                    {mostrarContrasena ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              {/* Error */}
              {error && (
                <div className="flex items-start gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-3">
                  <AlertCircle className="h-4 w-4 flex-shrink-0 text-red-400 mt-0.5" />
                  <p className="text-xs text-red-300">{error}</p>
                </div>
              )}

              {/* Boton dorado */}
              <button
                type="submit"
                disabled={cargando || !usuario || !contrasena}
                className="group relative w-full overflow-hidden py-3 text-sm text-[#0F1419] shadow-lg shadow-[#C9A84C]/20 transition-all duration-300 hover:shadow-[#C9A84C]/30 disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  background: 'linear-gradient(135deg, #C9A84C 0%, #B8963F 100%)',
                  borderRadius: '10px',
                  fontWeight: 600,
                }}
              >
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

            {/* Nota AD */}
            <p className="mt-4 text-center text-[#556677]" style={{ fontSize: '11px' }}>
              Integracion con Active Directory CGR
            </p>
          </div>

          {/* Pie de la tarjeta */}
          <div className="border-t border-white/[0.06] px-8 py-4 space-y-1.5">
            <p className="text-center text-[10px] text-[#556677] leading-relaxed">
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

        {/* Version */}
        <p className="mt-6 text-center text-[10px] text-[#556677]/50">
          CecilIA v2.0 — Entorno seguro de la CGR — Todos los derechos reservados
        </p>
      </div>
    </div>
  );
}
