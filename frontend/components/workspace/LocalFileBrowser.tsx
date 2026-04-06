'use client';

/**
 * CecilIA v2 — Navegador de archivos locales (Desktop Agent)
 * Sprint 11 — Conecta via API al agente de escritorio
 * Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  FolderOpen,
  File,
  ChevronRight,
  ChevronDown,
  Wifi,
  WifiOff,
  RefreshCw,
  Shield,
} from 'lucide-react';
import { Boton } from '@/components/ui/button';
import { obtenerUsuario } from '@/lib/auth';
import apiCliente from '@/lib/api';

interface ArchivoRemoto {
  nombre: string;
  ruta: string;
  es_directorio: boolean;
  tamano: number | null;
  modificado: string;
  extension: string | null;
}

interface NodoArchivo {
  nombre: string;
  ruta: string;
  es_directorio: boolean;
  tamano: number | null;
  hijos?: NodoArchivo[];
  expandido?: boolean;
  cargado?: boolean;
}

export function NavegadorArchivosLocal() {
  const [conectado, setConectado] = useState(false);
  const [cargando, setCargando] = useState(false);
  const [carpetasRaiz, setCarpetasRaiz] = useState<NodoArchivo[]>([]);
  const [error, setError] = useState<string | null>(null);

  const verificarConexion = useCallback(async () => {
    try {
      const usuario = obtenerUsuario();
      if (!usuario) return;
      const resp = await apiCliente.get(`/ws/agente/estado?usuario_id=${usuario.id || 0}`) as { conectado: boolean };
      setConectado(resp.conectado === true);
    } catch {
      setConectado(false);
    }
  }, []);

  useEffect(() => {
    verificarConexion();
    const intervalo = setInterval(verificarConexion, 15000);
    return () => clearInterval(intervalo);
  }, [verificarConexion]);

  const cargarCarpetaRaiz = useCallback(async () => {
    setCargando(true);
    setError(null);
    try {
      // El agente envia sus carpetas vigiladas como raiz
      const resp = await apiCliente.get('/ws/agente/conectados') as { agentes: Array<{ carpetas_vigiladas?: string[] }> };
      // Por ahora mostramos un nodo raiz generico
      setCarpetasRaiz([
        {
          nombre: 'Workspace Local',
          ruta: '.',
          es_directorio: true,
          tamano: null,
          expandido: false,
          cargado: false,
        },
      ]);
    } catch (err) {
      setError('No se pudo conectar con el agente');
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    if (conectado) cargarCarpetaRaiz();
  }, [conectado, cargarCarpetaRaiz]);

  const alternarNodo = async (nodo: NodoArchivo) => {
    if (!nodo.es_directorio) return;

    if (nodo.expandido) {
      // Colapsar
      actualizarNodo(nodo.ruta, { expandido: false });
      return;
    }

    // Expandir: si no tiene hijos cargados, cargar del agente
    if (!nodo.cargado) {
      actualizarNodo(nodo.ruta, { expandido: true });
      // En produccion: llamar al endpoint que solicita al agente listar
      // Por ahora dejamos como placeholder
    } else {
      actualizarNodo(nodo.ruta, { expandido: true });
    }
  };

  const actualizarNodo = (ruta: string, cambios: Partial<NodoArchivo>) => {
    setCarpetasRaiz((prev) =>
      prev.map((n) =>
        n.ruta === ruta ? { ...n, ...cambios } : n
      )
    );
  };

  const formatearTamano = (bytes: number | null) => {
    if (!bytes) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const renderNodo = (nodo: NodoArchivo, nivel: number = 0) => (
    <div key={nodo.ruta}>
      <button
        onClick={() => alternarNodo(nodo)}
        className={`flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-xs transition-colors hover:bg-[#1A2332] text-[#9AA0A6]`}
        style={{ paddingLeft: `${nivel * 16 + 8}px` }}
      >
        {nodo.es_directorio ? (
          nodo.expandido ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />
        ) : (
          <span className="w-3" />
        )}
        {nodo.es_directorio ? (
          <FolderOpen className="h-3.5 w-3.5 text-[#C9A84C]" />
        ) : (
          <File className="h-3.5 w-3.5 text-[#5F6368]" />
        )}
        <span className="truncate flex-1 text-left">{nodo.nombre}</span>
        {nodo.tamano && (
          <span className="text-[10px] text-[#5F6368]">{formatearTamano(nodo.tamano)}</span>
        )}
      </button>
      {nodo.es_directorio && nodo.expandido && nodo.hijos?.map((hijo) => renderNodo(hijo, nivel + 1))}
    </div>
  );

  return (
    <div className="space-y-3">
      {/* Estado de conexion */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {conectado ? (
            <Wifi className="h-3.5 w-3.5 text-green-400" />
          ) : (
            <WifiOff className="h-3.5 w-3.5 text-[#5F6368]" />
          )}
          <span className={`text-xs ${conectado ? 'text-green-400' : 'text-[#9AA0A6]'}`}>
            {conectado ? 'Desktop Agent conectado' : 'Desktop Agent desconectado'}
          </span>
        </div>
        <Boton variante="fantasma" tamano="sm" onClick={verificarConexion}>
          <RefreshCw className={`h-3 w-3 ${cargando ? 'animate-spin' : ''}`} />
        </Boton>
      </div>

      {/* Aviso si no esta conectado */}
      {!conectado ? (
        <div className="rounded-lg border border-[#2D3748]/50 bg-[#1A2332]/40 p-4 text-center">
          <WifiOff className="mx-auto h-8 w-8 text-[#2D3748] mb-2" />
          <p className="text-xs text-[#9AA0A6] mb-1">Desktop Agent no disponible</p>
          <p className="text-[10px] text-[#5F6368]">
            Instale e inicie el Desktop Agent para acceder a archivos locales.
            Los archivos se procesan en streaming sin copiarse al servidor.
          </p>
        </div>
      ) : (
        <>
          {/* Arbol de archivos */}
          <div className="rounded-lg border border-[#2D3748]/30 bg-[#0A0F14]/60 p-2">
            {carpetasRaiz.length > 0 ? (
              carpetasRaiz.map((nodo) => renderNodo(nodo))
            ) : (
              <p className="text-xs text-[#5F6368] text-center py-4">
                Sin carpetas configuradas en el agente
              </p>
            )}
          </div>

          {/* Banner de privacidad */}
          <div className="flex items-start gap-2 rounded-lg border border-[#C9A84C]/20 bg-[#C9A84C]/5 px-3 py-2">
            <Shield className="h-3.5 w-3.5 text-[#C9A84C] mt-0.5 flex-shrink-0" />
            <p className="text-[9px] text-[#6B7B8D] leading-relaxed">
              Los datos de su auditoria se almacenan como contexto de sesion en servidores de la CGR.
              No se utilizan para entrenar modelos de IA.
              Los archivos locales se procesan en streaming sin copiarse permanentemente al servidor.
            </p>
          </div>
        </>
      )}

      {error && (
        <p className="text-[10px] text-red-400">{error}</p>
      )}
    </div>
  );
}

export default NavegadorArchivosLocal;
