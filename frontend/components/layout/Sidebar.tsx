'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import {
  MessageSquare,
  FolderOpen,
  Plug,
  Search,
  FileText,
  AlertTriangle,
  BarChart3,
  Shield,
  ClipboardList,
  FileCheck,
  Eye,
  Plus,
  ChevronDown,
} from 'lucide-react';
import { Pestanas, ListaPestanas, DisparadorPestana, ContenidoPestana } from '@/components/ui/tabs';
import { Insignia } from '@/components/ui/badge';
import { obtenerUsuario, obtenerDireccionActiva, esAdmin, esDirector } from '@/lib/auth';
import type { Direccion, ResumenConversacion } from '@/lib/types';

/**
 * Barra lateral de navegacion principal
 * Fondo oscuro #0A0F14 con tres pestanas: Chats, Workspace, APIs
 */
export function BarraLateral() {
  const rutaActual = usePathname();
  const [direccionActiva, setDireccionActiva] = useState<Direccion | null>(null);
  const [conversaciones, setConversaciones] = useState<ResumenConversacion[]>([]);
  const usuario = obtenerUsuario();

  useEffect(() => {
    setDireccionActiva(obtenerDireccionActiva());
    // En produccion se cargarian las conversaciones del API
    setConversaciones([
      {
        id: '1',
        titulo: 'Analisis sectorial MinTIC 2025',
        direccion: 'DES',
        ultimo_mensaje: 'Los indicadores muestran...',
        fecha_actualizacion: new Date().toISOString(),
      },
      {
        id: '2',
        titulo: 'Hallazgo fiscal entidad XYZ',
        direccion: 'DVF',
        ultimo_mensaje: 'Se identifico una presunta...',
        fecha_actualizacion: new Date().toISOString(),
      },
    ]);
  }, []);

  const colorDireccion = direccionActiva === 'DES' ? '#1A5276' : '#1E8449';

  /** Enlaces de navegacion segun permisos */
  const enlacesNavegacion = [
    { href: '/chat', icono: MessageSquare, etiqueta: 'Chat IA', visible: true },
    { href: '/workspace', icono: FolderOpen, etiqueta: 'Workspace', visible: true },
    { href: '/auditorias', icono: ClipboardList, etiqueta: 'Auditorias', visible: true },
    { href: '/hallazgos', icono: AlertTriangle, etiqueta: 'Hallazgos', visible: true },
    { href: '/formatos', icono: FileCheck, etiqueta: 'Formatos', visible: true },
    { href: '/observatorio', icono: Eye, etiqueta: 'Observatorio', visible: direccionActiva === 'DES' },
    { href: '/analytics', icono: BarChart3, etiqueta: 'Analitica', visible: esDirector() || esAdmin() },
    { href: '/admin', icono: Shield, etiqueta: 'Administracion', visible: esAdmin() },
  ];

  return (
    <aside className="flex h-full w-64 flex-col bg-[#0A0F14] border-r border-[#2D3748]/30">
      {/* Logo de CecilIA */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-[#2D3748]/30">
        <div className="relative h-8 w-8 flex-shrink-0">
          <Image
            src="/logo-cecilia.png"
            alt="CecilIA"
            fill
            className="object-contain"
            sizes="32px"
          />
        </div>
        <div>
          <h1 className="font-titulo text-base font-bold text-[#C9A84C]">CecilIA v2</h1>
          <p className="text-[10px] text-[#5F6368]">Control Fiscal Inteligente</p>
        </div>
        {direccionActiva && (
          <Insignia variante={direccionActiva === 'DES' ? 'des' : 'dvf'} className="ml-auto text-[10px]">
            {direccionActiva}
          </Insignia>
        )}
      </div>

      {/* Pestanas: Chats | Workspace | APIs */}
      <Pestanas defaultValue="chats" className="flex flex-1 flex-col overflow-hidden">
        <ListaPestanas className="mx-2 mt-3 w-auto">
          <DisparadorPestana value="chats" className="flex-1 text-xs">
            Chats
          </DisparadorPestana>
          <DisparadorPestana value="workspace" className="flex-1 text-xs">
            Workspace
          </DisparadorPestana>
          <DisparadorPestana value="apis" className="flex-1 text-xs">
            APIs
          </DisparadorPestana>
        </ListaPestanas>

        {/* Contenido: Historial de chats */}
        <ContenidoPestana value="chats" className="flex-1 overflow-hidden">
          <div className="p-2">
            <button className="flex w-full items-center gap-2 rounded-lg border border-dashed border-[#2D3748] p-2.5 text-xs text-[#9AA0A6] hover:border-[#C9A84C]/50 hover:text-[#C9A84C] transition-colors">
              <Plus className="h-3.5 w-3.5" />
              Nueva conversacion
            </button>
          </div>
          <div className="flex-1 overflow-y-auto px-2">
            {conversaciones.map((conv) => (
              <Link
                key={conv.id}
                href={`/chat?id=${conv.id}`}
                className="group flex flex-col gap-1 rounded-lg px-3 py-2.5 text-xs hover:bg-[#1A2332]/60 transition-colors mb-0.5"
              >
                <div className="flex items-center gap-2">
                  <span
                    className="h-1.5 w-1.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: conv.direccion === 'DES' ? '#1A5276' : '#1E8449' }}
                  />
                  <span className="truncate text-[#E8EAED] group-hover:text-white font-medium">
                    {conv.titulo}
                  </span>
                </div>
                <p className="truncate text-[10px] text-[#5F6368] pl-3.5">
                  {conv.ultimo_mensaje}
                </p>
              </Link>
            ))}
          </div>
        </ContenidoPestana>

        {/* Contenido: Workspace */}
        <ContenidoPestana value="workspace" className="flex-1 overflow-y-auto p-2">
          <div className="space-y-2">
            <div className="rounded-lg bg-[#1A2332]/40 p-3 border border-[#2D3748]/30">
              <div className="flex items-center gap-2 text-xs text-[#9AA0A6] mb-2">
                <FolderOpen className="h-3.5 w-3.5" />
                Proyecto Activo
              </div>
              <p className="text-xs text-[#E8EAED]">Sin proyecto seleccionado</p>
            </div>
            <div className="rounded-lg bg-[#1A2332]/40 p-3 border border-[#2D3748]/30">
              <div className="flex items-center gap-2 text-xs text-[#9AA0A6] mb-2">
                <FileText className="h-3.5 w-3.5" />
                Documentos
              </div>
              <p className="text-xs text-[#5F6368]">0 documentos cargados</p>
            </div>
          </div>
        </ContenidoPestana>

        {/* Contenido: APIs */}
        <ContenidoPestana value="apis" className="flex-1 overflow-y-auto p-2">
          <div className="space-y-2">
            <div className="rounded-lg bg-[#1A2332]/40 p-3 border border-[#2D3748]/30">
              <div className="flex items-center gap-2 text-xs text-[#9AA0A6] mb-1">
                <Plug className="h-3.5 w-3.5" />
                Conectores
              </div>
              <div className="space-y-1.5 mt-2">
                <div className="flex items-center gap-2 text-[10px]">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
                  <span className="text-[#E8EAED]">CHIP - MHCP</span>
                </div>
                <div className="flex items-center gap-2 text-[10px]">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
                  <span className="text-[#E8EAED]">SIIF Nacion</span>
                </div>
                <div className="flex items-center gap-2 text-[10px]">
                  <span className="h-1.5 w-1.5 rounded-full bg-yellow-400" />
                  <span className="text-[#E8EAED]">SIA Observa</span>
                </div>
              </div>
            </div>
          </div>
        </ContenidoPestana>
      </Pestanas>

      {/* Navegacion principal */}
      <nav className="border-t border-[#2D3748]/30 p-2">
        <div className="space-y-0.5">
          {enlacesNavegacion
            .filter((e) => e.visible)
            .map((enlace) => {
              const activo = rutaActual?.startsWith(enlace.href);
              const Icono = enlace.icono;
              return (
                <Link
                  key={enlace.href}
                  href={enlace.href}
                  className={`flex items-center gap-2.5 rounded-lg px-3 py-2 text-xs transition-all ${
                    activo
                      ? 'bg-[#1A2332] text-[#E8EAED]'
                      : 'text-[#9AA0A6] hover:bg-[#1A2332]/50 hover:text-[#E8EAED]'
                  }`}
                  style={activo ? { borderLeft: `2px solid ${colorDireccion}` } : undefined}
                >
                  <Icono className="h-4 w-4 flex-shrink-0" />
                  {enlace.etiqueta}
                </Link>
              );
            })}
        </div>
      </nav>

      {/* Indicador de proyecto activo */}
      <div className="border-t border-[#2D3748]/30 px-3 py-3">
        <button className="flex w-full items-center gap-2 rounded-lg bg-[#1A2332]/40 px-3 py-2 text-xs text-[#9AA0A6] hover:bg-[#1A2332] transition-colors">
          <Search className="h-3.5 w-3.5" />
          <span className="flex-1 text-left truncate">Buscar...</span>
          <kbd className="rounded bg-[#0A0F14] px-1.5 py-0.5 text-[10px] text-[#5F6368]">
            Ctrl+K
          </kbd>
        </button>
      </div>
    </aside>
  );
}

export default BarraLateral;
