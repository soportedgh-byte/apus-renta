'use client';

import React from 'react';
import { FileText, Download, ExternalLink, X } from 'lucide-react';
import { Insignia } from '@/components/ui/badge';
import { Boton } from '@/components/ui/button';
import type { Documento } from '@/lib/types';

interface PropiedadesVisor {
  documento: Documento | null;
  alCerrar: () => void;
}

/**
 * Panel de previsualizacion de documentos
 * Muestra metadatos y contenido del documento seleccionado
 */
export function VisorDocumento({ documento, alCerrar }: PropiedadesVisor) {
  if (!documento) {
    return (
      <div className="flex h-full flex-col items-center justify-center text-center p-8">
        <FileText className="h-12 w-12 text-[#2D3748] mb-3" />
        <p className="text-sm text-[#5F6368]">
          Seleccione un documento para previsualizarlo
        </p>
      </div>
    );
  }

  const formatearFecha = (fecha: string): string => {
    return new Date(fecha).toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatearTamano = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="flex h-full flex-col">
      {/* Encabezado */}
      <div className="flex items-center justify-between border-b border-[#2D3748]/30 p-4">
        <div className="flex items-center gap-3 min-w-0">
          <FileText className="h-5 w-5 flex-shrink-0 text-[#C9A84C]" />
          <div className="min-w-0">
            <h3 className="text-sm font-medium text-[#E8EAED] truncate">{documento.nombre}</h3>
            <p className="text-[10px] text-[#5F6368]">{documento.tipo_archivo}</p>
          </div>
        </div>
        <button onClick={alCerrar} className="p-1 text-[#5F6368] hover:text-[#9AA0A6]">
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Metadatos */}
      <div className="border-b border-[#2D3748]/30 p-4 space-y-3">
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div>
            <span className="text-[#5F6368]">Coleccion</span>
            <div className="mt-1">
              <Insignia variante="oro">{documento.coleccion}</Insignia>
            </div>
          </div>
          <div>
            <span className="text-[#5F6368]">Tamano</span>
            <p className="mt-1 text-[#E8EAED]">{formatearTamano(documento.tamano_bytes)}</p>
          </div>
          <div>
            <span className="text-[#5F6368]">Estado</span>
            <p className="mt-1 text-[#E8EAED] capitalize">{documento.estado_procesamiento}</p>
          </div>
          <div>
            <span className="text-[#5F6368]">Chunks</span>
            <p className="mt-1 text-[#E8EAED]">{documento.chunks_totales || '-'}</p>
          </div>
          <div className="col-span-2">
            <span className="text-[#5F6368]">Fecha de carga</span>
            <p className="mt-1 text-[#E8EAED]">{formatearFecha(documento.fecha_carga)}</p>
          </div>
        </div>
      </div>

      {/* Area de previsualizacion */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center">
          <FileText className="mx-auto h-16 w-16 text-[#2D3748] mb-4" />
          <p className="text-sm text-[#9AA0A6] mb-4">
            Previsualizacion no disponible para este tipo de archivo
          </p>
          <div className="flex items-center justify-center gap-2">
            <Boton variante="secundario" tamano="sm">
              <Download className="h-3.5 w-3.5" />
              Descargar
            </Boton>
            <Boton variante="fantasma" tamano="sm">
              <ExternalLink className="h-3.5 w-3.5" />
              Abrir externo
            </Boton>
          </div>
        </div>
      </div>
    </div>
  );
}

export default VisorDocumento;
