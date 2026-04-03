'use client';

import React, { useState, useEffect } from 'react';
import {
  Shield,
  Users,
  Settings,
  Plus,
  Search,
  Edit3,
  Trash2,
  ShieldAlert,
  Power,
  Database,
  Server,
  Key,
} from 'lucide-react';
import { Tarjeta } from '@/components/ui/card';
import { Insignia } from '@/components/ui/badge';
import { Boton } from '@/components/ui/button';
import { Pestanas, ListaPestanas, DisparadorPestana, ContenidoPestana } from '@/components/ui/tabs';
import { esAdmin } from '@/lib/auth';

/**
 * Panel de administracion del sistema
 * Gestion de usuarios, configuracion y monitoreo
 * Solo accesible para administradores
 */
export default function PaginaAdmin() {
  const [tieneAcceso, setTieneAcceso] = useState(true);

  useEffect(() => {
    setTieneAcceso(esAdmin());
  }, []);

  if (!tieneAcceso) {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <div className="text-center max-w-md">
          <ShieldAlert className="mx-auto h-16 w-16 text-[#2D3748] mb-4" />
          <h2 className="font-titulo text-xl font-semibold text-[#E8EAED] mb-2">
            Acceso restringido
          </h2>
          <p className="text-sm text-[#9AA0A6]">
            El panel de administracion esta disponible unicamente para administradores del sistema.
          </p>
        </div>
      </div>
    );
  }

  /** Usuarios de ejemplo */
  const usuarios = [
    { id: '1', nombre: 'Dr. Carlos Rodriguez', correo: 'c.rodriguez@contraloria.gov.co', rol: 'director_dvf', direccion: 'DVF', activo: true },
    { id: '2', nombre: 'Dra. Patricia Ruiz', correo: 'p.ruiz@contraloria.gov.co', rol: 'director_des', direccion: 'DES', activo: true },
    { id: '3', nombre: 'Ana Gomez', correo: 'a.gomez@contraloria.gov.co', rol: 'auditor', direccion: 'DVF', activo: true },
    { id: '4', nombre: 'Luis Martinez', correo: 'l.martinez@contraloria.gov.co', rol: 'auditor', direccion: 'DVF', activo: true },
    { id: '5', nombre: 'Carolina Vargas', correo: 'c.vargas@contraloria.gov.co', rol: 'auditor', direccion: 'DES', activo: false },
    { id: '6', nombre: 'Admin Sistema', correo: 'admin@contraloria.gov.co', rol: 'admin', direccion: null, activo: true },
  ];

  const nombreRol: Record<string, string> = {
    auditor: 'Auditor',
    director_des: 'Director DES',
    director_dvf: 'Director DVF',
    admin: 'Administrador',
    superadmin: 'Super Admin',
  };

  return (
    <div className="p-6">
      {/* Encabezado */}
      <div className="mb-6">
        <h1 className="font-titulo text-xl font-bold text-[#E8EAED] flex items-center gap-2">
          <Shield className="h-6 w-6 text-[#C9A84C]" />
          Administracion del Sistema
        </h1>
        <p className="mt-1 text-xs text-[#5F6368]">
          Gestion de usuarios, configuracion y monitoreo de CecilIA v2
        </p>
      </div>

      <Pestanas defaultValue="usuarios">
        <ListaPestanas className="w-auto mb-4">
          <DisparadorPestana value="usuarios" className="text-xs">
            <Users className="h-3.5 w-3.5 mr-1.5" />
            Usuarios
          </DisparadorPestana>
          <DisparadorPestana value="configuracion" className="text-xs">
            <Settings className="h-3.5 w-3.5 mr-1.5" />
            Configuracion
          </DisparadorPestana>
          <DisparadorPestana value="sistema" className="text-xs">
            <Server className="h-3.5 w-3.5 mr-1.5" />
            Sistema
          </DisparadorPestana>
        </ListaPestanas>

        {/* Pestana: Usuarios */}
        <ContenidoPestana value="usuarios">
          <div className="flex items-center justify-between mb-4">
            <div className="relative max-w-sm flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#5F6368]" />
              <input
                type="text"
                placeholder="Buscar usuarios..."
                className="w-full rounded-lg border border-[#2D3748] bg-[#1A2332] py-2.5 pl-10 pr-4 text-sm text-[#E8EAED] placeholder:text-[#5F6368] focus:border-[#C9A84C] focus:outline-none"
              />
            </div>
            <Boton variante="primario">
              <Plus className="h-4 w-4" />
              Nuevo usuario
            </Boton>
          </div>

          <Tarjeta>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-[#2D3748]">
                    <th className="p-3 text-left font-medium text-[#9AA0A6]">Nombre</th>
                    <th className="p-3 text-left font-medium text-[#9AA0A6]">Correo</th>
                    <th className="p-3 text-left font-medium text-[#9AA0A6]">Rol</th>
                    <th className="p-3 text-left font-medium text-[#9AA0A6]">Direccion</th>
                    <th className="p-3 text-center font-medium text-[#9AA0A6]">Estado</th>
                    <th className="p-3 text-right font-medium text-[#9AA0A6]">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {usuarios.map((u) => (
                    <tr key={u.id} className="border-b border-[#2D3748]/30 hover:bg-[#1A2332]/50">
                      <td className="p-3 font-medium text-[#E8EAED]">{u.nombre}</td>
                      <td className="p-3 font-codigo text-[#9AA0A6]">{u.correo}</td>
                      <td className="p-3">
                        <Insignia variante={u.rol.includes('admin') ? 'oro' : u.rol.includes('director') ? 'info' : 'gris'}>
                          {nombreRol[u.rol]}
                        </Insignia>
                      </td>
                      <td className="p-3">
                        {u.direccion ? (
                          <Insignia variante={u.direccion === 'DES' ? 'des' : 'dvf'}>
                            {u.direccion}
                          </Insignia>
                        ) : (
                          <span className="text-[#5F6368]">—</span>
                        )}
                      </td>
                      <td className="p-3 text-center">
                        <span className={`inline-flex h-2 w-2 rounded-full ${u.activo ? 'bg-green-400' : 'bg-red-400'}`} />
                      </td>
                      <td className="p-3 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <button className="rounded p-1.5 text-[#5F6368] hover:text-[#E8EAED] hover:bg-[#243044] transition-colors">
                            <Edit3 className="h-3.5 w-3.5" />
                          </button>
                          <button className="rounded p-1.5 text-[#5F6368] hover:text-red-400 hover:bg-red-500/10 transition-colors">
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Tarjeta>
        </ContenidoPestana>

        {/* Pestana: Configuracion */}
        <ContenidoPestana value="configuracion">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Tarjeta className="p-5">
              <h3 className="text-sm font-medium text-[#E8EAED] mb-4 flex items-center gap-2">
                <Key className="h-4 w-4 text-[#C9A84C]" />
                Configuracion de API Keys
              </h3>
              <div className="space-y-3">
                {[
                  { nombre: 'Anthropic API Key', estado: 'Configurada', activa: true },
                  { nombre: 'OpenAI API Key', estado: 'Configurada', activa: true },
                  { nombre: 'Azure OpenAI Endpoint', estado: 'No configurada', activa: false },
                ].map((apiKey) => (
                  <div key={apiKey.nombre} className="flex items-center justify-between rounded-lg bg-[#0A0F14]/60 p-3 border border-[#2D3748]/30">
                    <div>
                      <p className="text-xs font-medium text-[#E8EAED]">{apiKey.nombre}</p>
                      <p className="text-[10px] text-[#5F6368]">{apiKey.estado}</p>
                    </div>
                    <span className={`h-2 w-2 rounded-full ${apiKey.activa ? 'bg-green-400' : 'bg-[#5F6368]'}`} />
                  </div>
                ))}
              </div>
            </Tarjeta>

            <Tarjeta className="p-5">
              <h3 className="text-sm font-medium text-[#E8EAED] mb-4 flex items-center gap-2">
                <Database className="h-4 w-4 text-[#2471A3]" />
                Base de datos vectorial
              </h3>
              <div className="space-y-3">
                {[
                  { etiqueta: 'Colecciones', valor: '5' },
                  { etiqueta: 'Documentos totales', valor: '1,247' },
                  { etiqueta: 'Chunks indexados', valor: '45,892' },
                  { etiqueta: 'Tamano del indice', valor: '2.3 GB' },
                ].map((item) => (
                  <div key={item.etiqueta} className="flex items-center justify-between text-xs">
                    <span className="text-[#9AA0A6]">{item.etiqueta}</span>
                    <span className="font-medium text-[#E8EAED]">{item.valor}</span>
                  </div>
                ))}
              </div>
            </Tarjeta>

            <Tarjeta className="p-5">
              <h3 className="text-sm font-medium text-[#E8EAED] mb-4 flex items-center gap-2">
                <Settings className="h-4 w-4 text-[#9B59B6]" />
                Configuracion general
              </h3>
              <div className="space-y-3">
                {[
                  { etiqueta: 'Modelo por defecto', valor: 'claude-sonnet-4-20250514' },
                  { etiqueta: 'Max tokens respuesta', valor: '8,192' },
                  { etiqueta: 'Temperatura', valor: '0.3' },
                  { etiqueta: 'Top-K documentos RAG', valor: '10' },
                  { etiqueta: 'Umbral similitud', valor: '0.75' },
                ].map((item) => (
                  <div key={item.etiqueta} className="flex items-center justify-between text-xs">
                    <span className="text-[#9AA0A6]">{item.etiqueta}</span>
                    <span className="font-codigo text-[#E8EAED]">{item.valor}</span>
                  </div>
                ))}
              </div>
            </Tarjeta>

            <Tarjeta className="p-5">
              <h3 className="text-sm font-medium text-[#E8EAED] mb-4 flex items-center gap-2">
                <Power className="h-4 w-4 text-[#27AE60]" />
                Estado del sistema
              </h3>
              <div className="space-y-3">
                {[
                  { servicio: 'Backend API', estado: 'En linea', activo: true },
                  { servicio: 'PostgreSQL', estado: 'En linea', activo: true },
                  { servicio: 'Qdrant (vectores)', estado: 'En linea', activo: true },
                  { servicio: 'Redis (cache)', estado: 'En linea', activo: true },
                  { servicio: 'Desktop Agent WS', estado: 'Disponible', activo: true },
                ].map((item) => (
                  <div key={item.servicio} className="flex items-center justify-between text-xs">
                    <span className="text-[#9AA0A6]">{item.servicio}</span>
                    <div className="flex items-center gap-1.5">
                      <span className={`h-1.5 w-1.5 rounded-full ${item.activo ? 'bg-green-400' : 'bg-red-400'}`} />
                      <span className={item.activo ? 'text-green-400' : 'text-red-400'}>{item.estado}</span>
                    </div>
                  </div>
                ))}
              </div>
            </Tarjeta>
          </div>
        </ContenidoPestana>

        {/* Pestana: Sistema */}
        <ContenidoPestana value="sistema">
          <Tarjeta className="p-5">
            <h3 className="text-sm font-medium text-[#E8EAED] mb-4">
              Informacion del sistema
            </h3>
            <div className="grid grid-cols-2 gap-4 text-xs">
              {[
                { etiqueta: 'Version', valor: 'CecilIA v2.0.0' },
                { etiqueta: 'Entorno', valor: 'Produccion' },
                { etiqueta: 'Backend', valor: 'FastAPI 0.115+' },
                { etiqueta: 'Frontend', valor: 'Next.js 16 + React 19' },
                { etiqueta: 'Base de datos', valor: 'PostgreSQL 16' },
                { etiqueta: 'Vector store', valor: 'Qdrant' },
                { etiqueta: 'Cache', valor: 'Redis 7' },
                { etiqueta: 'Python', valor: '3.12+' },
              ].map((item) => (
                <div key={item.etiqueta} className="flex items-center justify-between rounded-lg bg-[#0A0F14]/60 p-3 border border-[#2D3748]/30">
                  <span className="text-[#5F6368]">{item.etiqueta}</span>
                  <span className="font-codigo text-[#E8EAED]">{item.valor}</span>
                </div>
              ))}
            </div>
          </Tarjeta>
        </ContenidoPestana>
      </Pestanas>
    </div>
  );
}
