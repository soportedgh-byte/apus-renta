'use client';

import React, { useState } from 'react';
import { FileText, Search, Filter, Trash2, Eye, Clock, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { Insignia } from '@/components/ui/badge';
import type { Documento, ColeccionDocumento } from '@/lib/types';

interface PropiedadesListaDocumentos {
  documentos: Documento[];
  alSeleccionar?: (documento: Documento) => void;
  alEliminar?: (id: string) => void;
}

/** Mapa de colecciones a variantes de insignia */
const varianteColeccion: Record<ColeccionDocumento, 'des' | 'dvf' | 'oro' | 'info' | 'gris'> = {
  normativo: 'oro',
  metodologico: 'des',
  sectorial: 'info',
  auditoria: 'dvf',
  hallazgo: 'rojo' as 'des',
};

/** Iconos de estado de procesamiento */
const iconoEstado = {
  pendiente: <Clock className="h-3 w-3 text-yellow-400" />,
  procesando: <Loader className="h-3 w-3 text-blue-400 animate-spin" />,
  completado: <CheckCircle className="h-3 w-3 text-green-400" />,
  error: <AlertCircle className="h-3 w-3 text-red-400" />,
};

/**
 * Lista de documentos con filtros y busqueda
 */
export function ListaDocumentos({ documentos, alSeleccionar, alEliminar }: PropiedadesListaDocumentos) {
  const [busqueda, setBusqueda] = useState('');
  const [filtroColeccion, setFiltroColeccion] = useState<ColeccionDocumento | 'todas'>('todas');

  const documentosFiltrados = documentos.filter((doc) => {
    const coincideBusqueda = doc.nombre.toLowerCase().includes(busqueda.toLowerCase());
    const coincideColeccion = filtroColeccion === 'todas' || doc.coleccion === filtroColeccion;
    return coincideBusqueda && coincideColeccion;
  });

  const formatearTamano = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const colecciones: { valor: ColeccionDocumento | 'todas'; etiqueta: string }[] = [
    { valor: 'todas', etiqueta: 'Todas' },
    { valor: 'normativo', etiqueta: 'Normativo' },
    { valor: 'metodologico', etiqueta: 'Metodologico' },
    { valor: 'sectorial', etiqueta: 'Sectorial' },
    { valor: 'auditoria', etiqueta: 'Auditoria' },
    { valor: 'hallazgo', etiqueta: 'Hallazgo' },
  ];

  return (
    <div className="space-y-3">
      {/* Barra de busqueda y filtros */}
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[#5F6368]" />
          <input
            type="text"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            placeholder="Buscar documentos..."
            className="w-full rounded-lg border border-[#2D3748] bg-[#0A0F14] py-2 pl-9 pr-4 text-xs text-[#E8EAED] placeholder:text-[#5F6368] focus:border-[#C9A84C] focus:outline-none"
          />
        </div>
      </div>

      {/* Filtros de coleccion */}
      <div className="flex flex-wrap gap-1.5">
        {colecciones.map((col) => (
          <button
            key={col.valor}
            onClick={() => setFiltroColeccion(col.valor)}
            className={`rounded-full px-2.5 py-1 text-[10px] transition-colors ${
              filtroColeccion === col.valor
                ? 'bg-[#C9A84C]/20 text-[#C9A84C] border border-[#C9A84C]/40'
                : 'bg-[#1A2332] text-[#9AA0A6] border border-[#2D3748] hover:border-[#4A5568]'
            }`}
          >
            {col.etiqueta}
          </button>
        ))}
      </div>

      {/* Lista */}
      <div className="space-y-1.5">
        {documentosFiltrados.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <FileText className="h-8 w-8 text-[#2D3748] mb-2" />
            <p className="text-xs text-[#5F6368]">No se encontraron documentos</p>
          </div>
        ) : (
          documentosFiltrados.map((doc) => (
            <div
              key={doc.id}
              onClick={() => alSeleccionar?.(doc)}
              className="flex items-center gap-3 rounded-lg border border-[#2D3748]/30 bg-[#1A2332]/40 p-3 hover:bg-[#1A2332] transition-colors cursor-pointer group"
            >
              <FileText className="h-5 w-5 flex-shrink-0 text-[#5F6368]" />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-xs font-medium text-[#E8EAED] truncate">
                    {doc.nombre}
                  </p>
                  {iconoEstado[doc.estado_procesamiento]}
                </div>
                <div className="flex items-center gap-2 mt-0.5">
                  <Insignia variante={varianteColeccion[doc.coleccion] || 'gris'} className="text-[8px]">
                    {doc.coleccion}
                  </Insignia>
                  <span className="text-[10px] text-[#5F6368]">
                    {formatearTamano(doc.tamano_bytes)}
                  </span>
                  {doc.chunks_totales && (
                    <span className="text-[10px] text-[#5F6368]">
                      {doc.chunks_totales} chunks
                    </span>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={(e) => { e.stopPropagation(); alSeleccionar?.(doc); }}
                  className="p-1 rounded text-[#5F6368] hover:text-[#9AA0A6]"
                >
                  <Eye className="h-3.5 w-3.5" />
                </button>
                <button
                  onClick={(e) => { e.stopPropagation(); alEliminar?.(doc.id); }}
                  className="p-1 rounded text-[#5F6368] hover:text-red-400"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default ListaDocumentos;
