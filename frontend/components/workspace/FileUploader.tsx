'use client';

import React, { useState, useRef, useCallback } from 'react';
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react';
import { Boton } from '@/components/ui/button';
import { SpinnerCarga } from '@/components/shared/LoadingSpinner';
import { apiCliente } from '@/lib/api';

interface PropiedadesUploader {
  alSubirCompleto?: () => void;
  coleccion?: string;
  auditoriaId?: string;
}

interface ArchivoEnCola {
  archivo: File;
  estado: 'pendiente' | 'subiendo' | 'completado' | 'error';
  progreso: number;
  error?: string;
}

/**
 * Componente de carga de archivos con drag & drop
 * Soporta multiples archivos y muestra progreso
 */
export function CargadorArchivos({ alSubirCompleto, coleccion, auditoriaId }: PropiedadesUploader) {
  const [archivos, setArchivos] = useState<ArchivoEnCola[]>([]);
  const [arrastrando, setArrastrando] = useState(false);
  const refInput = useRef<HTMLInputElement>(null);

  const agregarArchivos = useCallback((nuevos: FileList | null) => {
    if (!nuevos) return;
    const lista = Array.from(nuevos).map((archivo) => ({
      archivo,
      estado: 'pendiente' as const,
      progreso: 0,
    }));
    setArchivos((prev) => [...prev, ...lista]);
  }, []);

  const manejarDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setArrastrando(false);
    agregarArchivos(e.dataTransfer.files);
  }, [agregarArchivos]);

  const manejarDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setArrastrando(true);
  }, []);

  const eliminarArchivo = (indice: number) => {
    setArchivos((prev) => prev.filter((_, i) => i !== indice));
  };

  const subirTodos = async () => {
    for (let i = 0; i < archivos.length; i++) {
      if (archivos[i].estado !== 'pendiente') continue;

      setArchivos((prev) =>
        prev.map((a, idx) => (idx === i ? { ...a, estado: 'subiendo' } : a)),
      );

      try {
        await apiCliente.subirArchivo('/documentos/subir', archivos[i].archivo, {
          ...(coleccion ? { coleccion } : {}),
          ...(auditoriaId ? { auditoria_id: auditoriaId } : {}),
        });

        setArchivos((prev) =>
          prev.map((a, idx) =>
            idx === i ? { ...a, estado: 'completado', progreso: 100 } : a,
          ),
        );
      } catch (error) {
        setArchivos((prev) =>
          prev.map((a, idx) =>
            idx === i
              ? { ...a, estado: 'error', error: 'Error al subir archivo' }
              : a,
          ),
        );
      }
    }
    alSubirCompleto?.();
  };

  const formatearTamano = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-4">
      {/* Zona de arrastrar y soltar */}
      <div
        onDrop={manejarDrop}
        onDragOver={manejarDragOver}
        onDragLeave={() => setArrastrando(false)}
        onClick={() => refInput.current?.click()}
        className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 transition-all cursor-pointer ${
          arrastrando
            ? 'border-[#C9A84C] bg-[#C9A84C]/5'
            : 'border-[#2D3748] hover:border-[#4A5568] hover:bg-[#1A2332]/30'
        }`}
      >
        <Upload
          className={`h-10 w-10 mb-3 ${arrastrando ? 'text-[#C9A84C]' : 'text-[#5F6368]'}`}
        />
        <p className="text-sm text-[#E8EAED] mb-1">
          Arrastre archivos aqui o haga clic para seleccionar
        </p>
        <p className="text-xs text-[#5F6368]">
          PDF, DOCX, XLSX, CSV, TXT — Maximo 50 MB por archivo
        </p>
        <input
          ref={refInput}
          type="file"
          multiple
          accept=".pdf,.docx,.xlsx,.csv,.txt,.doc,.xls"
          onChange={(e) => agregarArchivos(e.target.files)}
          className="hidden"
        />
      </div>

      {/* Lista de archivos */}
      {archivos.length > 0 && (
        <div className="space-y-2">
          {archivos.map((item, indice) => (
            <div
              key={indice}
              className="flex items-center gap-3 rounded-lg border border-[#2D3748]/50 bg-[#1A2332] p-3"
            >
              <FileText className="h-5 w-5 flex-shrink-0 text-[#5F6368]" />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-[#E8EAED] truncate">{item.archivo.name}</p>
                <p className="text-[10px] text-[#5F6368]">
                  {formatearTamano(item.archivo.size)}
                </p>
              </div>
              {item.estado === 'subiendo' && <SpinnerCarga tamano="sm" />}
              {item.estado === 'completado' && <CheckCircle className="h-4 w-4 text-green-400" />}
              {item.estado === 'error' && <AlertCircle className="h-4 w-4 text-red-400" />}
              {item.estado === 'pendiente' && (
                <button
                  onClick={(e) => { e.stopPropagation(); eliminarArchivo(indice); }}
                  className="text-[#5F6368] hover:text-red-400 transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          ))}

          {/* Boton de subir */}
          {archivos.some((a) => a.estado === 'pendiente') && (
            <Boton variante="primario" tamano="md" onClick={subirTodos} className="w-full">
              <Upload className="h-4 w-4" />
              Subir {archivos.filter((a) => a.estado === 'pendiente').length} archivo(s)
            </Boton>
          )}
        </div>
      )}
    </div>
  );
}

export default CargadorArchivos;
