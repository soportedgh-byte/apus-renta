'use client';

import React, { useState, useEffect } from 'react';
import { FolderOpen, File, ChevronRight, ChevronDown, Wifi, WifiOff, RefreshCw } from 'lucide-react';
import { Boton } from '@/components/ui/button';

interface NodoArchivo {
  nombre: string;
  ruta: string;
  tipo: 'archivo' | 'directorio';
  hijos?: NodoArchivo[];
  expandido?: boolean;
}

/**
 * Navegador de archivos locales para el Desktop Agent
 * Permite explorar el sistema de archivos del equipo del auditor
 */
export function NavegadorArchivosLocal() {
  const [conectado, setConectado] = useState(false);
  const [arbol, setArbol] = useState<NodoArchivo[]>([]);
  const [rutaActual, setRutaActual] = useState('');

  // Estado de ejemplo (en produccion se conectaria via WebSocket)
  const arbolEjemplo: NodoArchivo[] = [
    {
      nombre: 'Auditorias 2025',
      ruta: '/Documentos/Auditorias 2025',
      tipo: 'directorio',
      hijos: [
        { nombre: 'Informe_MinTIC.pdf', ruta: '/Documentos/Auditorias 2025/Informe_MinTIC.pdf', tipo: 'archivo' },
        { nombre: 'Hallazgos_DIAN.docx', ruta: '/Documentos/Auditorias 2025/Hallazgos_DIAN.docx', tipo: 'archivo' },
        { nombre: 'Ejecucion_Presupuestal.xlsx', ruta: '/Documentos/Auditorias 2025/Ejecucion_Presupuestal.xlsx', tipo: 'archivo' },
      ],
    },
    {
      nombre: 'Normativa',
      ruta: '/Documentos/Normativa',
      tipo: 'directorio',
      hijos: [
        { nombre: 'Ley_42_1993.pdf', ruta: '/Documentos/Normativa/Ley_42_1993.pdf', tipo: 'archivo' },
        { nombre: 'Resolucion_CGR_2024.pdf', ruta: '/Documentos/Normativa/Resolucion_CGR_2024.pdf', tipo: 'archivo' },
      ],
    },
  ];

  const [nodos, setNodos] = useState<NodoArchivo[]>(arbolEjemplo);

  const alternarNodo = (ruta: string) => {
    setNodos((prev) =>
      prev.map((nodo) =>
        nodo.ruta === ruta ? { ...nodo, expandido: !nodo.expandido } : nodo,
      ),
    );
  };

  const renderNodo = (nodo: NodoArchivo, nivel: number = 0) => (
    <div key={nodo.ruta}>
      <button
        onClick={() => nodo.tipo === 'directorio' ? alternarNodo(nodo.ruta) : setRutaActual(nodo.ruta)}
        className={`flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-xs transition-colors hover:bg-[#1A2332] ${
          rutaActual === nodo.ruta ? 'bg-[#1A2332] text-[#C9A84C]' : 'text-[#9AA0A6]'
        }`}
        style={{ paddingLeft: `${nivel * 16 + 8}px` }}
      >
        {nodo.tipo === 'directorio' ? (
          nodo.expandido ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />
        ) : (
          <span className="w-3" />
        )}
        {nodo.tipo === 'directorio' ? (
          <FolderOpen className="h-3.5 w-3.5 text-[#C9A84C]" />
        ) : (
          <File className="h-3.5 w-3.5 text-[#5F6368]" />
        )}
        <span className="truncate">{nodo.nombre}</span>
      </button>
      {nodo.tipo === 'directorio' && nodo.expandido && nodo.hijos?.map((hijo) => renderNodo(hijo, nivel + 1))}
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
          <span className="text-xs text-[#9AA0A6]">
            {conectado ? 'Desktop Agent conectado' : 'Desktop Agent desconectado'}
          </span>
        </div>
        <Boton variante="fantasma" tamano="sm" onClick={() => setConectado(!conectado)}>
          <RefreshCw className="h-3 w-3" />
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
        /* Arbol de archivos */
        <div className="rounded-lg border border-[#2D3748]/30 bg-[#0A0F14]/60 p-2">
          {nodos.map((nodo) => renderNodo(nodo))}
        </div>
      )}
    </div>
  );
}

export default NavegadorArchivosLocal;
