'use client';

import React, { useState, useEffect } from 'react';
import { FolderOpen, ChevronDown, Plus } from 'lucide-react';
import type { Auditoria } from '@/lib/types';

interface PropiedadesSelectorProyecto {
  alSeleccionar?: (auditoria: Auditoria) => void;
}

/**
 * Selector de proyecto/auditoria activa
 * Permite cambiar el contexto de trabajo actual
 */
export function SelectorProyecto({ alSeleccionar }: PropiedadesSelectorProyecto) {
  const [abierto, setAbierto] = useState(false);
  const [proyectoActivo, setProyectoActivo] = useState<string | null>(null);

  // Proyectos de ejemplo (en produccion se cargarian del API)
  const proyectos = [
    { id: '1', nombre: 'Auditoria MinTIC 2025', entidad: 'MinTIC' },
    { id: '2', nombre: 'Auditoria DIAN 2025', entidad: 'DIAN' },
    { id: '3', nombre: 'Control Fiscal ANI', entidad: 'ANI' },
  ];

  return (
    <div className="relative">
      <button
        onClick={() => setAbierto(!abierto)}
        className="flex items-center gap-2 rounded-lg border border-[#2D3748] bg-[#1A2332] px-3 py-2 text-xs hover:border-[#4A5568] transition-colors"
      >
        <FolderOpen className="h-3.5 w-3.5 text-[#C9A84C]" />
        <span className="text-[#E8EAED] max-w-[160px] truncate">
          {proyectoActivo
            ? proyectos.find((p) => p.id === proyectoActivo)?.nombre
            : 'Seleccionar proyecto'}
        </span>
        <ChevronDown className="h-3 w-3 text-[#5F6368]" />
      </button>

      {abierto && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setAbierto(false)} />
          <div className="absolute left-0 top-full z-50 mt-1 w-64 rounded-lg border border-[#2D3748] bg-[#1A2332] shadow-xl">
            <div className="p-1">
              {proyectos.map((proyecto) => (
                <button
                  key={proyecto.id}
                  onClick={() => {
                    setProyectoActivo(proyecto.id);
                    setAbierto(false);
                  }}
                  className={`flex w-full flex-col items-start rounded-md px-3 py-2 text-xs transition-colors ${
                    proyectoActivo === proyecto.id
                      ? 'bg-[#C9A84C]/10 text-[#C9A84C]'
                      : 'text-[#9AA0A6] hover:bg-[#243044] hover:text-[#E8EAED]'
                  }`}
                >
                  <span className="font-medium">{proyecto.nombre}</span>
                  <span className="text-[10px] text-[#5F6368]">{proyecto.entidad}</span>
                </button>
              ))}
              <div className="my-1 border-t border-[#2D3748]" />
              <button className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-xs text-[#9AA0A6] hover:bg-[#243044] hover:text-[#E8EAED] transition-colors">
                <Plus className="h-3.5 w-3.5" />
                Nuevo proyecto
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default SelectorProyecto;
