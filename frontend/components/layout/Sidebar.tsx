'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname, useRouter } from 'next/navigation';
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
  MoreHorizontal,
  Pencil,
  Trash2,
  X,
  Check,
} from 'lucide-react';
import { Pestanas, ListaPestanas, DisparadorPestana, ContenidoPestana } from '@/components/ui/tabs';
import { Insignia } from '@/components/ui/badge';
import { obtenerUsuario, obtenerDireccionActiva, esAdmin, esDirector } from '@/lib/auth';
import { apiCliente } from '@/lib/api';
import type { Direccion, ResumenConversacion } from '@/lib/types';

/** Agrupacion temporal de conversaciones */
interface GrupoConversaciones {
  etiqueta: string;
  items: ResumenConversacion[];
}

function agruparPorFecha(conversaciones: ResumenConversacion[]): GrupoConversaciones[] {
  const ahora = new Date();
  const hoy = new Date(ahora.getFullYear(), ahora.getMonth(), ahora.getDate());
  const ayer = new Date(hoy.getTime() - 86400000);
  const inicioSemana = new Date(hoy.getTime() - hoy.getDay() * 86400000);

  const grupos: GrupoConversaciones[] = [
    { etiqueta: 'Hoy', items: [] },
    { etiqueta: 'Ayer', items: [] },
    { etiqueta: 'Esta semana', items: [] },
    { etiqueta: 'Anteriores', items: [] },
  ];

  for (const conv of conversaciones) {
    const fecha = new Date(conv.fecha_actualizacion);
    if (fecha >= hoy) {
      grupos[0].items.push(conv);
    } else if (fecha >= ayer) {
      grupos[1].items.push(conv);
    } else if (fecha >= inicioSemana) {
      grupos[2].items.push(conv);
    } else {
      grupos[3].items.push(conv);
    }
  }

  return grupos.filter((g) => g.items.length > 0);
}

function fechaRelativa(iso: string): string {
  const fecha = new Date(iso);
  const ahora = new Date();
  const diff = ahora.getTime() - fecha.getTime();
  const mins = Math.floor(diff / 60000);
  const horas = Math.floor(diff / 3600000);
  const dias = Math.floor(diff / 86400000);

  if (mins < 1) return 'ahora';
  if (mins < 60) return `hace ${mins}m`;
  if (horas < 24) return `hace ${horas}h`;
  if (dias < 7) return `hace ${dias}d`;
  return fecha.toLocaleDateString('es-CO', { day: 'numeric', month: 'short' });
}

/**
 * Barra lateral de navegacion principal
 */
export function BarraLateral() {
  const rutaActual = usePathname();
  const router = useRouter();
  const [direccionActiva, setDireccionActiva] = useState<Direccion | null>(null);
  const [conversaciones, setConversaciones] = useState<ResumenConversacion[]>([]);
  const [conversacionActiva, setConversacionActiva] = useState<string | null>(null);
  const [menuAbiertoId, setMenuAbiertoId] = useState<string | null>(null);
  const [editandoId, setEditandoId] = useState<string | null>(null);
  const [tituloEdicion, setTituloEdicion] = useState('');
  const [eliminandoId, setEliminandoId] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);
  const refInputEdicion = useRef<HTMLInputElement>(null);
  const usuario = obtenerUsuario();

  useEffect(() => {
    setDireccionActiva(obtenerDireccionActiva());
    cargarConversaciones();
  }, []);

  // Detectar conversacion activa de la URL
  useEffect(() => {
    if (rutaActual?.startsWith('/chat')) {
      const params = new URLSearchParams(window.location.search);
      const id = params.get('id');
      setConversacionActiva(id);
    }
  }, [rutaActual]);

  // Focus en input de edicion
  useEffect(() => {
    if (editandoId && refInputEdicion.current) {
      refInputEdicion.current.focus();
      refInputEdicion.current.select();
    }
  }, [editandoId]);

  const cargarConversaciones = useCallback(async () => {
    setCargando(true);
    try {
      const datos = await apiCliente.get<ResumenConversacion[]>('/chat/conversaciones');
      // Mapear campos del backend
      const mapped = (datos || []).map((c: any) => ({
        id: c.id,
        titulo: c.titulo,
        direccion: c.direccion || 'DES',
        ultimo_mensaje: c.ultimo_mensaje,
        fecha_actualizacion: c.updated_at || c.fecha_actualizacion || new Date().toISOString(),
      }));
      setConversaciones(mapped);
    } catch (error) {
      console.error('[CecilIA] Error al cargar conversaciones:', error);
    } finally {
      setCargando(false);
    }
  }, []);

  const nuevaConversacion = () => {
    setConversacionActiva(null);
    router.push('/chat');
    // Refrescar la lista despues de que se cree
    setTimeout(() => cargarConversaciones(), 500);
  };

  const seleccionarConversacion = (id: string) => {
    setConversacionActiva(id);
    setMenuAbiertoId(null);
    router.push(`/chat?id=${id}`);
  };

  const iniciarEdicion = (conv: ResumenConversacion) => {
    setEditandoId(conv.id);
    setTituloEdicion(conv.titulo);
    setMenuAbiertoId(null);
  };

  const guardarEdicion = async () => {
    if (!editandoId || !tituloEdicion.trim()) return;
    try {
      await apiCliente.patch(`/chat/conversaciones/${editandoId}`, { titulo: tituloEdicion.trim() });
      setConversaciones((prev) =>
        prev.map((c) => (c.id === editandoId ? { ...c, titulo: tituloEdicion.trim() } : c))
      );
    } catch (error) {
      console.error('[CecilIA] Error al renombrar:', error);
    }
    setEditandoId(null);
  };

  const cancelarEdicion = () => {
    setEditandoId(null);
    setTituloEdicion('');
  };

  const confirmarEliminar = (id: string) => {
    setEliminandoId(id);
    setMenuAbiertoId(null);
  };

  const ejecutarEliminar = async () => {
    if (!eliminandoId) return;
    try {
      await apiCliente.delete(`/chat/conversaciones/${eliminandoId}`);
      setConversaciones((prev) => prev.filter((c) => c.id !== eliminandoId));
      if (conversacionActiva === eliminandoId) {
        setConversacionActiva(null);
        router.push('/chat');
      }
    } catch (error) {
      console.error('[CecilIA] Error al eliminar:', error);
    }
    setEliminandoId(null);
  };

  // Exponer recarga para que ChatWindow la use
  useEffect(() => {
    (window as any).__cecilia_recargar_conversaciones = cargarConversaciones;
    return () => {
      delete (window as any).__cecilia_recargar_conversaciones;
    };
  }, [cargarConversaciones]);

  const colorDireccion = direccionActiva === 'DES' ? '#1A5276' : '#1E8449';
  const grupos = agruparPorFecha(conversaciones);

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
        <ContenidoPestana value="chats" className="flex-1 overflow-hidden flex flex-col">
          <div className="p-2">
            <button
              onClick={nuevaConversacion}
              className="flex w-full items-center gap-2 rounded-lg border border-dashed border-[#2D3748] p-2.5 text-xs text-[#9AA0A6] hover:border-[#C9A84C]/50 hover:text-[#C9A84C] transition-colors"
            >
              <Plus className="h-3.5 w-3.5" />
              Nueva conversacion
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-2">
            {cargando && conversaciones.length === 0 ? (
              <p className="text-center text-[10px] text-[#5F6368] py-4">Cargando...</p>
            ) : conversaciones.length === 0 ? (
              <p className="text-center text-[10px] text-[#5F6368] py-4">Sin conversaciones aun</p>
            ) : (
              grupos.map((grupo) => (
                <div key={grupo.etiqueta} className="mb-2">
                  <p className="px-3 py-1 text-[10px] font-medium text-[#5F6368] uppercase tracking-wider">
                    {grupo.etiqueta}
                  </p>
                  {grupo.items.map((conv) => (
                    <div key={conv.id} className="relative group">
                      {/* Modal de confirmacion de eliminacion */}
                      {eliminandoId === conv.id && (
                        <div className="absolute inset-0 z-20 flex items-center justify-center rounded-lg bg-[#0A0F14]/95 border border-red-500/30">
                          <div className="text-center px-2">
                            <p className="text-[10px] text-[#E8EAED] mb-2">Eliminar conversacion?</p>
                            <div className="flex gap-1.5 justify-center">
                              <button
                                onClick={ejecutarEliminar}
                                className="rounded px-2 py-1 text-[10px] bg-red-600/80 text-white hover:bg-red-600"
                              >
                                Eliminar
                              </button>
                              <button
                                onClick={() => setEliminandoId(null)}
                                className="rounded px-2 py-1 text-[10px] bg-[#2D3748] text-[#9AA0A6] hover:text-white"
                              >
                                Cancelar
                              </button>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Edicion inline */}
                      {editandoId === conv.id ? (
                        <div className="flex items-center gap-1 px-3 py-2">
                          <input
                            ref={refInputEdicion}
                            value={tituloEdicion}
                            onChange={(e) => setTituloEdicion(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') guardarEdicion();
                              if (e.key === 'Escape') cancelarEdicion();
                            }}
                            className="flex-1 rounded bg-[#1A2332] border border-[#C9A84C]/30 px-2 py-1 text-xs text-[#E8EAED] outline-none focus:border-[#C9A84C]"
                          />
                          <button onClick={guardarEdicion} className="p-0.5 text-green-400 hover:text-green-300">
                            <Check className="h-3.5 w-3.5" />
                          </button>
                          <button onClick={cancelarEdicion} className="p-0.5 text-[#5F6368] hover:text-[#9AA0A6]">
                            <X className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => seleccionarConversacion(conv.id)}
                          className={`flex w-full flex-col gap-1 rounded-lg px-3 py-2.5 text-xs transition-colors mb-0.5 text-left ${
                            conversacionActiva === conv.id
                              ? 'bg-[#1A2332] border-l-2'
                              : 'hover:bg-[#1A2332]/60'
                          }`}
                          style={conversacionActiva === conv.id ? { borderLeftColor: conv.direccion === 'DES' ? '#1A5276' : '#1E8449' } : undefined}
                        >
                          <div className="flex items-center gap-2 w-full">
                            <span
                              className="h-1.5 w-1.5 rounded-full flex-shrink-0"
                              style={{ backgroundColor: conv.direccion === 'DES' ? '#1A5276' : '#1E8449' }}
                            />
                            <span className="truncate text-[#E8EAED] font-medium flex-1">
                              {conv.titulo}
                            </span>
                            <span className="text-[9px] text-[#5F6368] flex-shrink-0">
                              {fechaRelativa(conv.fecha_actualizacion)}
                            </span>

                            {/* Boton menu contextual */}
                            <div
                              className="opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                              onClick={(e) => {
                                e.stopPropagation();
                                setMenuAbiertoId(menuAbiertoId === conv.id ? null : conv.id);
                              }}
                            >
                              <MoreHorizontal className="h-3.5 w-3.5 text-[#5F6368] hover:text-[#9AA0A6]" />
                            </div>
                          </div>
                          {conv.ultimo_mensaje && (
                            <p className="truncate text-[10px] text-[#5F6368] pl-3.5">
                              {conv.ultimo_mensaje}
                            </p>
                          )}
                        </button>
                      )}

                      {/* Menu contextual */}
                      {menuAbiertoId === conv.id && (
                        <div className="absolute right-2 top-8 z-30 rounded-lg bg-[#1A2332] border border-[#2D3748] shadow-xl py-1 min-w-[140px]">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              iniciarEdicion(conv);
                            }}
                            className="flex items-center gap-2 w-full px-3 py-1.5 text-xs text-[#9AA0A6] hover:bg-[#2D3748] hover:text-[#E8EAED]"
                          >
                            <Pencil className="h-3 w-3" />
                            Renombrar
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              confirmarEliminar(conv.id);
                            }}
                            className="flex items-center gap-2 w-full px-3 py-1.5 text-xs text-red-400 hover:bg-red-500/10 hover:text-red-300"
                          >
                            <Trash2 className="h-3 w-3" />
                            Eliminar
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ))
            )}
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

      {/* Barra de busqueda */}
      <div className="border-t border-[#2D3748]/30 px-3 py-3">
        <button className="flex w-full items-center gap-2 rounded-lg bg-[#1A2332]/40 px-3 py-2 text-xs text-[#9AA0A6] hover:bg-[#1A2332] transition-colors">
          <Search className="h-3.5 w-3.5" />
          <span className="flex-1 text-left truncate">Buscar...</span>
          <kbd className="rounded bg-[#0A0F14] px-1.5 py-0.5 text-[10px] text-[#5F6368]">
            Ctrl+K
          </kbd>
        </button>
      </div>

      {/* Click fuera cierra menus */}
      {(menuAbiertoId || eliminandoId) && (
        <div
          className="fixed inset-0 z-10"
          onClick={() => {
            setMenuAbiertoId(null);
            if (!eliminandoId) setEliminandoId(null);
          }}
        />
      )}
    </aside>
  );
}

export default BarraLateral;
