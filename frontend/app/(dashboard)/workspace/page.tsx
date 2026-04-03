'use client';

import React, { useState, useEffect } from 'react';
import { FolderOpen, Upload, HardDrive, RefreshCw } from 'lucide-react';
import { Pestanas, ListaPestanas, DisparadorPestana, ContenidoPestana } from '@/components/ui/tabs';
import { Boton } from '@/components/ui/button';
import { CargadorArchivos } from '@/components/workspace/FileUploader';
import { ListaDocumentos } from '@/components/workspace/DocumentList';
import { NavegadorArchivosLocal } from '@/components/workspace/LocalFileBrowser';
import { VisorDocumento } from '@/components/workspace/DocumentViewer';
import type { Documento } from '@/lib/types';

/**
 * Pagina de Workspace
 * Gestiona documentos cargados, carga de nuevos archivos y
 * navegacion de archivos locales via Desktop Agent
 */
export default function PaginaWorkspace() {
  const [documentos, setDocumentos] = useState<Documento[]>([]);
  const [documentoSeleccionado, setDocumentoSeleccionado] = useState<Documento | null>(null);

  // Datos de ejemplo (en produccion se cargarian del API)
  useEffect(() => {
    setDocumentos([
      {
        id: '1',
        nombre: 'Ley_42_1993_Control_Fiscal.pdf',
        tipo_archivo: 'application/pdf',
        tamano_bytes: 2456789,
        coleccion: 'normativo',
        usuario_id: 'user1',
        estado_procesamiento: 'completado',
        chunks_totales: 145,
        fecha_carga: '2025-12-01T10:30:00Z',
      },
      {
        id: '2',
        nombre: 'Guia_Auditoria_Financiera_CGR.pdf',
        tipo_archivo: 'application/pdf',
        tamano_bytes: 5123456,
        coleccion: 'metodologico',
        usuario_id: 'user1',
        estado_procesamiento: 'completado',
        chunks_totales: 320,
        fecha_carga: '2025-12-05T14:20:00Z',
      },
      {
        id: '3',
        nombre: 'Ejecucion_Presupuestal_MinTIC_2025.xlsx',
        tipo_archivo: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        tamano_bytes: 876543,
        coleccion: 'sectorial',
        usuario_id: 'user1',
        estado_procesamiento: 'procesando',
        fecha_carga: '2026-01-15T09:00:00Z',
      },
    ]);
  }, []);

  return (
    <div className="flex h-full">
      {/* Panel izquierdo: Documentos y carga */}
      <div className="flex w-96 flex-col border-r border-[#2D3748]/30">
        <div className="border-b border-[#2D3748]/30 p-4">
          <h2 className="font-titulo text-lg font-semibold text-[#E8EAED] flex items-center gap-2">
            <FolderOpen className="h-5 w-5 text-[#C9A84C]" />
            Workspace
          </h2>
          <p className="mt-1 text-xs text-[#5F6368]">
            Gestione documentos y archivos de auditoria
          </p>
        </div>

        <Pestanas defaultValue="documentos" className="flex flex-1 flex-col overflow-hidden">
          <ListaPestanas className="mx-4 mt-3 w-auto">
            <DisparadorPestana value="documentos" className="flex-1 text-xs">
              Documentos
            </DisparadorPestana>
            <DisparadorPestana value="subir" className="flex-1 text-xs">
              Subir
            </DisparadorPestana>
            <DisparadorPestana value="local" className="flex-1 text-xs">
              Local
            </DisparadorPestana>
          </ListaPestanas>

          <ContenidoPestana value="documentos" className="flex-1 overflow-y-auto p-4">
            <ListaDocumentos
              documentos={documentos}
              alSeleccionar={setDocumentoSeleccionado}
              alEliminar={(id) => setDocumentos((prev) => prev.filter((d) => d.id !== id))}
            />
          </ContenidoPestana>

          <ContenidoPestana value="subir" className="flex-1 overflow-y-auto p-4">
            <CargadorArchivos
              alSubirCompleto={() => {
                // Recargar documentos
              }}
            />
          </ContenidoPestana>

          <ContenidoPestana value="local" className="flex-1 overflow-y-auto p-4">
            <NavegadorArchivosLocal />
          </ContenidoPestana>
        </Pestanas>
      </div>

      {/* Panel derecho: Visor de documento */}
      <div className="flex-1">
        <VisorDocumento
          documento={documentoSeleccionado}
          alCerrar={() => setDocumentoSeleccionado(null)}
        />
      </div>
    </div>
  );
}
