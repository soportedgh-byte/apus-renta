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
  Info,
  BookOpen,
  Upload,
  RefreshCw,
  Menu,
  ChevronLeft,
  Brain,
} from 'lucide-react';
import { Pestanas, ListaPestanas, DisparadorPestana, ContenidoPestana } from '@/components/ui/tabs';
import { Insignia } from '@/components/ui/badge';
import { obtenerUsuario, obtenerDireccionActiva, establecerDireccionActiva, esAdmin, esDirector, esAprendiz } from '@/lib/auth';
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

const iconosTipoArchivo: Record<string, string> = {
  pdf: '📕',
  xlsx: '📗',
  xls: '📗',
  docx: '📘',
  doc: '📘',
  csv: '📗',
  txt: '📄',
};

interface EstadoAPI {
  nombre: string;
  estado: 'disponible' | 'degradado' | 'no_disponible' | 'pendiente' | 'circuito_abierto' | 'cargando';
  latencia_ms?: number | null;
  mensaje?: string;
}

const apisIntegracionDefault: EstadoAPI[] = [
  { nombre: 'SECOP II', estado: 'cargando' },
  { nombre: 'DANE', estado: 'cargando' },
  { nombre: 'Congreso', estado: 'cargando' },
  { nombre: 'SIRECI', estado: 'pendiente', mensaje: 'Requiere VPN CGR' },
  { nombre: 'SIGECI', estado: 'pendiente', mensaje: 'Requiere VPN CGR' },
  { nombre: 'APA', estado: 'pendiente', mensaje: 'Requiere VPN CGR' },
  { nombre: 'DIARI', estado: 'pendiente', mensaje: 'Requiere VPN CGR' },
];

const colorEstadoAPI = (estado: string): string => {
  switch (estado) {
    case 'disponible': return '#27AE60';
    case 'degradado': return '#F1C40F';
    case 'no_disponible': return '#E74C3C';
    case 'circuito_abierto': return '#E74C3C';
    case 'pendiente': return '#F1C40F';
    case 'cargando': return '#5F6368';
    default: return '#5F6368';
  }
};

const textoEstadoAPI = (estado: string): string => {
  switch (estado) {
    case 'disponible': return 'Activo';
    case 'degradado': return 'Degradado';
    case 'no_disponible': return 'No disponible';
    case 'circuito_abierto': return 'Bloqueado';
    case 'pendiente': return 'Pendiente';
    case 'cargando': return 'Verificando...';
    default: return estado;
  }
};

const colorClaseEstadoAPI = (estado: string): string => {
  switch (estado) {
    case 'disponible': return 'text-green-400';
    case 'degradado': return 'text-yellow-400';
    case 'no_disponible': return 'text-red-400';
    case 'circuito_abierto': return 'text-red-400';
    case 'pendiente': return 'text-yellow-400';
    case 'cargando': return 'text-[#5F6368]';
    default: return 'text-[#5F6368]';
  }
};

/**
 * Barra lateral de navegacion principal — 280px
 * Con tabs Chats | Workspace | APIs, navegacion contextual y perfil de usuario
 */
export function BarraLateral() {
  const rutaActual = usePathname();
  const router = useRouter();
  const [direccionActiva, setDireccionActivaState] = useState<Direccion | null>(null);
  const [conversaciones, setConversaciones] = useState<ResumenConversacion[]>([]);
  const [conversacionActiva, setConversacionActiva] = useState<string | null>(null);
  const [menuAbiertoId, setMenuAbiertoId] = useState<string | null>(null);
  const [editandoId, setEditandoId] = useState<string | null>(null);
  const [tituloEdicion, setTituloEdicion] = useState('');
  const [eliminandoId, setEliminandoId] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);
  const [colapsado, setColapsado] = useState(false);
  const [estadoAPIs, setEstadoAPIs] = useState<EstadoAPI[]>(apisIntegracionDefault);
  const [cargandoAPIs, setCargandoAPIs] = useState(false);
  const refInputEdicion = useRef<HTMLInputElement>(null);
  const usuario = obtenerUsuario();

  const cargarEstadoAPIs = useCallback(async () => {
    setCargandoAPIs(true);
    try {
      const datos = await apiCliente.get<any[]>('/integraciones/estado');
      if (datos && Array.isArray(datos)) {
        const mapped: EstadoAPI[] = datos.map((s: any) => ({
          nombre: s.servicio,
          estado: s.estado as EstadoAPI['estado'],
          latencia_ms: s.latencia_ms,
          mensaje: s.mensaje,
        }));
        setEstadoAPIs(mapped);
      }
    } catch (error) {
      console.error('[CecilIA] Error al cargar estado APIs:', error);
    } finally {
      setCargandoAPIs(false);
    }
  }, []);

  useEffect(() => {
    setDireccionActivaState(obtenerDireccionActiva());
    cargarConversaciones();
    cargarEstadoAPIs();
  }, []);

  useEffect(() => {
    if (rutaActual?.startsWith('/chat')) {
      const params = new URLSearchParams(window.location.search);
      const id = params.get('id');
      setConversacionActiva(id);
    }
  }, [rutaActual]);

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

  const cambiarRol = () => {
    router.push('/seleccion-rol');
  };

  useEffect(() => {
    (window as any).__cecilia_recargar_conversaciones = cargarConversaciones;
    return () => {
      delete (window as any).__cecilia_recargar_conversaciones;
    };
  }, [cargarConversaciones]);

  const colorDireccion = direccionActiva === 'DES' ? '#1A5276' : '#1E8449';
  const colorDireccionLight = direccionActiva === 'DES' ? '#2471A3' : '#27AE60';
  const grupos = agruparPorFecha(conversaciones);

  const esAdministrador = esAdmin();

  const enlacesNavegacion = [
    { href: '/chat', icono: MessageSquare, etiqueta: 'Chat IA', visible: esAdministrador || !esAprendiz() },
    { href: '/capacitacion', icono: BookOpen, etiqueta: 'Capacitacion', visible: true },
    { href: '/workspace', icono: FolderOpen, etiqueta: 'Workspace', visible: esAdministrador || !esAprendiz() },
    { href: '/auditorias', icono: ClipboardList, etiqueta: 'Auditorias', visible: esAdministrador || !esAprendiz() },
    { href: '/hallazgos', icono: AlertTriangle, etiqueta: 'Hallazgos', visible: esAdministrador || !esAprendiz() },
    { href: '/formatos', icono: FileCheck, etiqueta: 'Formatos', visible: esAdministrador || !esAprendiz() },
    { href: '/observatorio', icono: Eye, etiqueta: 'Observatorio', visible: esAdministrador || (direccionActiva === 'DES' && !esAprendiz()) },
    { href: '/analytics', icono: BarChart3, etiqueta: 'Analitica', visible: esAdministrador || esDirector() },
    { href: '/admin', icono: Shield, etiqueta: 'Administracion', visible: esAdministrador },
    { href: '/admin/modelos', icono: Brain, etiqueta: 'Modelos IA', visible: esAdministrador },
    { href: '/guia-uso', icono: FileText, etiqueta: 'Guia de uso', visible: true },
    { href: '/acerca', icono: Info, etiqueta: 'Acerca de CecilIA', visible: true },
  ];

  // Sidebar colapsado para mobile/tablet
  if (colapsado) {
    return (
      <button
        onClick={() => setColapsado(false)}
        className="fixed top-4 left-4 z-50 flex h-10 w-10 items-center justify-center rounded-lg bg-[#1A2332] border border-[#2D3748]/50 text-[#9AA0A6] hover:text-white lg:hidden"
      >
        <Menu className="h-5 w-5" />
      </button>
    );
  }

  return (
    <>
      {/* Overlay mobile */}
      <div
        className="fixed inset-0 z-40 bg-black/50 lg:hidden"
        onClick={() => setColapsado(true)}
        style={{ display: colapsado ? 'none' : undefined }}
      />

      <aside className="fixed lg:relative z-50 flex h-full w-[280px] flex-col bg-[#0A0F14] border-r border-[#2D3748]/30">
        {/* Header: Logo + CecilIA v2 + Badge rol */}
        <div className="flex items-center gap-3 px-4 py-4 border-b border-[#2D3748]/30">
          <div className="relative h-8 w-8 flex-shrink-0">
            <Image
              src="/logo-cecilia.png"
              alt="CecilIA"
              fill
              className="object-contain"
              sizes="32px"
            />
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="font-titulo text-base font-bold text-[#C9A84C]">CecilIA v2</h1>
            <p className="text-[10px] text-[#5F6368]">Control Fiscal Inteligente</p>
          </div>
          {direccionActiva && (
            <span
              className="rounded-full px-2 py-0.5 text-[10px] font-semibold"
              style={{
                backgroundColor: `${colorDireccion}25`,
                color: colorDireccionLight,
                border: `1px solid ${colorDireccion}50`,
              }}
            >
              {direccionActiva}
            </span>
          )}
          {/* Boton colapsar mobile */}
          <button
            onClick={() => setColapsado(true)}
            className="lg:hidden p-1 text-[#5F6368] hover:text-white"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
        </div>

        {/* Tabs: Chats | Workspace | APIs */}
        <Pestanas defaultValue="chats" className="flex flex-1 flex-col overflow-hidden">
          <ListaPestanas className="mx-2 mt-3 w-auto">
            <DisparadorPestana value="chats" className="flex-1 text-xs gap-1">
              <MessageSquare className="h-3 w-3" />
              Chats
            </DisparadorPestana>
            <DisparadorPestana value="workspace" className="flex-1 text-xs gap-1">
              <FolderOpen className="h-3 w-3" />
              Workspace
            </DisparadorPestana>
            <DisparadorPestana value="apis" className="flex-1 text-xs gap-1">
              <Plug className="h-3 w-3" />
              APIs
            </DisparadorPestana>
          </ListaPestanas>

          {/* Tab: Chats */}
          <ContenidoPestana value="chats" className="flex-1 overflow-hidden flex flex-col">
            <div className="p-2">
              <button
                onClick={nuevaConversacion}
                className="flex w-full items-center gap-2 rounded-lg p-2.5 text-xs transition-colors"
                style={{
                  border: `1px dashed ${colorDireccion}60`,
                  color: colorDireccionLight,
                  background: `${colorDireccion}08`,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = `${colorDireccion}15`;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = `${colorDireccion}08`;
                }}
              >
                <Plus className="h-3.5 w-3.5" />
                Nueva conversacion
              </button>
            </div>

            <div className="flex-1 overflow-y-auto px-2">
              {cargando && conversaciones.length === 0 ? (
                <p className="text-center text-[10px] text-[#5F6368] py-4">Cargando...</p>
              ) : conversaciones.length === 0 ? (
                <div className="text-center py-8">
                  <MessageSquare className="h-8 w-8 text-[#2D3748] mx-auto mb-2" />
                  <p className="text-[11px] text-[#5F6368]">Sin conversaciones aun</p>
                  <p className="text-[10px] text-[#3D4750] mt-1">Inicia una nueva consulta</p>
                </div>
              ) : (
                grupos.map((grupo) => (
                  <div key={grupo.etiqueta} className="mb-2">
                    <p className="px-3 py-1 text-[10px] font-medium text-[#5F6368] uppercase tracking-wider">
                      {grupo.etiqueta}
                    </p>
                    {grupo.items.map((conv) => (
                      <div key={conv.id} className="relative group">
                        {/* Confirmacion eliminar */}
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
                              onClick={(e) => { e.stopPropagation(); iniciarEdicion(conv); }}
                              className="flex items-center gap-2 w-full px-3 py-1.5 text-xs text-[#9AA0A6] hover:bg-[#2D3748] hover:text-[#E8EAED]"
                            >
                              <Pencil className="h-3 w-3" />
                              Renombrar
                            </button>
                            <button
                              onClick={(e) => { e.stopPropagation(); confirmarEliminar(conv.id); }}
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

          {/* Tab: Workspace */}
          <ContenidoPestana value="workspace" className="flex-1 overflow-y-auto p-2">
            <div className="space-y-3">
              {/* Boton cargar documentos */}
              <button className="flex w-full items-center gap-2 rounded-lg border border-dashed border-[#2D3748] p-3 text-xs text-[#9AA0A6] hover:border-[#C9A84C]/40 hover:text-[#C9A84C] transition-colors">
                <Upload className="h-4 w-4" />
                <span>Cargar documentos</span>
              </button>

              {/* Archivos workspace */}
              <div className="rounded-lg bg-[#1A2332]/40 p-3 border border-[#2D3748]/30">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] font-medium text-[#9AA0A6]">Documentos cargados</span>
                  <button className="text-[#5F6368] hover:text-[#9AA0A6]">
                    <RefreshCw className="h-3 w-3" />
                  </button>
                </div>
                <div className="space-y-1.5 text-[10px]">
                  <div className="flex items-center gap-2 text-[#E8EAED]">
                    <span>📕</span> <span className="truncate">Decreto_403_2020.pdf</span>
                  </div>
                  <div className="flex items-center gap-2 text-[#E8EAED]">
                    <span>📗</span> <span className="truncate">Ejecucion_MinTIC_2025.xlsx</span>
                  </div>
                  <div className="flex items-center gap-2 text-[#E8EAED]">
                    <span>📘</span> <span className="truncate">Informe_Auditoria.docx</span>
                  </div>
                </div>
              </div>

              {/* Workspace local */}
              <div className="rounded-lg bg-[#1A2332]/40 p-3 border border-[#2D3748]/30">
                <div className="flex items-center gap-2 text-[11px] text-[#9AA0A6]">
                  <div className="h-1.5 w-1.5 rounded-full bg-green-400" />
                  Workspace Local: Conectado
                </div>
              </div>
            </div>
          </ContenidoPestana>

          {/* Tab: APIs */}
          <ContenidoPestana value="apis" className="flex-1 overflow-y-auto p-2">
            <div className="rounded-lg bg-[#1A2332]/40 p-3 border border-[#2D3748]/30">
              <div className="flex items-center justify-between mb-3">
                <p className="text-[11px] font-medium text-[#9AA0A6]">Conectores externos</p>
                <button
                  onClick={cargarEstadoAPIs}
                  className="text-[#5F6368] hover:text-[#9AA0A6]"
                  title="Verificar estado"
                >
                  <RefreshCw className={`h-3 w-3 ${cargandoAPIs ? 'animate-spin' : ''}`} />
                </button>
              </div>
              <div className="space-y-2">
                {estadoAPIs.map((api) => (
                  <div key={api.nombre} className="flex items-center gap-2 text-[10px]">
                    <span
                      className="h-1.5 w-1.5 rounded-full flex-shrink-0"
                      style={{ backgroundColor: colorEstadoAPI(api.estado) }}
                    />
                    <span className="text-[#E8EAED] flex-1">{api.nombre}</span>
                    {api.latencia_ms != null && api.latencia_ms > 0 && (
                      <span className="text-[8px] text-[#5F6368]">{api.latencia_ms.toFixed(0)}ms</span>
                    )}
                    <span className={`text-[9px] ${colorClaseEstadoAPI(api.estado)}`}>
                      {textoEstadoAPI(api.estado)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
            {esAdministrador && (
              <Link
                href="/admin/integraciones"
                className="flex items-center gap-2 mt-2 rounded-lg border border-dashed border-[#2D3748] p-2 text-[10px] text-[#9AA0A6] hover:border-[#C9A84C]/40 hover:text-[#C9A84C] transition-colors"
              >
                <Shield className="h-3 w-3" />
                Configurar integraciones
              </Link>
            )}
          </ContenidoPestana>
        </Pestanas>

        {/* Navegacion principal */}
        <nav className="border-t border-[#2D3748]/30 p-2 max-h-[220px] overflow-y-auto">
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

        {/* Footer: Perfil usuario */}
        <div className="border-t border-[#2D3748]/30 p-3">
          <div className="flex items-center gap-2.5">
            {/* Avatar con iniciales */}
            <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[#C9A84C] to-[#A88B3D]">
              <span className="text-xs font-bold text-[#0F1419]">
                {usuario?.nombre_completo
                  ? usuario.nombre_completo.split(' ').map((n) => n[0]).slice(0, 2).join('')
                  : 'U'}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-[#E8EAED] truncate">
                {usuario?.nombre_completo || 'Usuario'}
              </p>
              <p className="text-[10px] text-[#5F6368] truncate">
                {usuario?.rol || 'Auditor'} · {direccionActiva || 'Sin direccion'}
              </p>
            </div>
            <button
              onClick={cambiarRol}
              className="flex-shrink-0 rounded-md p-1.5 text-[#5F6368] hover:text-[#C9A84C] hover:bg-[#1A2332] transition-colors"
              title="Cambiar direccion"
            >
              <RefreshCw className="h-3.5 w-3.5" />
            </button>
          </div>
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
    </>
  );
}

export default BarraLateral;
