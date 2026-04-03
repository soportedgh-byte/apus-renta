'use client';

import React, { useState } from 'react';
import {
  FileCheck,
  Plus,
  Download,
  Eye,
  Bot,
  CheckCircle,
  Clock,
  FileText,
} from 'lucide-react';
import { Tarjeta } from '@/components/ui/card';
import { Insignia } from '@/components/ui/badge';
import { Boton } from '@/components/ui/button';

/** Definicion de formatos disponibles (1 a 30) */
const formatosDisponibles = [
  { numero: 1, nombre: 'Comunicacion de inicio de auditoria' },
  { numero: 2, nombre: 'Plan de trabajo de auditoria' },
  { numero: 3, nombre: 'Programa de auditoria' },
  { numero: 4, nombre: 'Papeles de trabajo' },
  { numero: 5, nombre: 'Acta de mesa de trabajo' },
  { numero: 6, nombre: 'Solicitud de informacion' },
  { numero: 7, nombre: 'Hallazgo de auditoria' },
  { numero: 8, nombre: 'Informe de auditoria' },
  { numero: 9, nombre: 'Plan de mejoramiento' },
  { numero: 10, nombre: 'Seguimiento plan de mejoramiento' },
  { numero: 11, nombre: 'Evaluacion de control interno' },
  { numero: 12, nombre: 'Analisis de cuentas' },
  { numero: 13, nombre: 'Cedula analitica' },
  { numero: 14, nombre: 'Cedula sumaria' },
  { numero: 15, nombre: 'Verificacion de cumplimiento' },
  { numero: 16, nombre: 'Analisis financiero' },
  { numero: 17, nombre: 'Cuestionario de control interno' },
  { numero: 18, nombre: 'Memorando de planeacion' },
  { numero: 19, nombre: 'Evaluacion de riesgos' },
  { numero: 20, nombre: 'Matriz de riesgos' },
  { numero: 21, nombre: 'Informe de gestion' },
  { numero: 22, nombre: 'Balance de auditoria' },
  { numero: 23, nombre: 'Comunicacion de hallazgos' },
  { numero: 24, nombre: 'Respuesta a hallazgos' },
  { numero: 25, nombre: 'Consolidado de hallazgos' },
  { numero: 26, nombre: 'Traslado a entes de control' },
  { numero: 27, nombre: 'Acta de cierre' },
  { numero: 28, nombre: 'Informe de seguimiento' },
  { numero: 29, nombre: 'Dictamen de estados financieros' },
  { numero: 30, nombre: 'Informe consolidado sectorial' },
];

interface FormatoGenerado {
  id: string;
  numero: number;
  nombre: string;
  estado: 'borrador' | 'generado' | 'aprobado';
  generado_por_ia: boolean;
  fecha: string;
}

/**
 * Pagina de formatos de auditoria
 * Permite generar y descargar los 30 formatos estandar de la CGR
 */
export default function PaginaFormatos() {
  const [formatosGenerados, setFormatosGenerados] = useState<FormatoGenerado[]>([
    {
      id: '1',
      numero: 1,
      nombre: 'Comunicacion de inicio de auditoria',
      estado: 'aprobado',
      generado_por_ia: false,
      fecha: '2025-08-01T10:00:00Z',
    },
    {
      id: '2',
      numero: 7,
      nombre: 'Hallazgo de auditoria',
      estado: 'generado',
      generado_por_ia: true,
      fecha: '2025-09-15T14:30:00Z',
    },
    {
      id: '3',
      numero: 8,
      nombre: 'Informe de auditoria',
      estado: 'borrador',
      generado_por_ia: true,
      fecha: '2025-10-01T09:00:00Z',
    },
  ]);

  const [mostrarCatalogo, setMostrarCatalogo] = useState(false);

  const estadoConfig = {
    borrador: { icono: Clock, color: '#5F6368', etiqueta: 'Borrador' },
    generado: { icono: FileCheck, color: '#C9A84C', etiqueta: 'Generado' },
    aprobado: { icono: CheckCircle, color: '#27AE60', etiqueta: 'Aprobado' },
  };

  return (
    <div className="p-6">
      {/* Encabezado */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-titulo text-xl font-bold text-[#E8EAED] flex items-center gap-2">
            <FileCheck className="h-6 w-6 text-[#C9A84C]" />
            Formatos de Auditoria
          </h1>
          <p className="mt-1 text-xs text-[#5F6368]">
            Genere y administre los 30 formatos estandar de la CGR
          </p>
        </div>
        <Boton variante="primario" onClick={() => setMostrarCatalogo(!mostrarCatalogo)}>
          <Plus className="h-4 w-4" />
          Generar formato
        </Boton>
      </div>

      {/* Catalogo de formatos (desplegable) */}
      {mostrarCatalogo && (
        <Tarjeta className="mb-6">
          <div className="p-4">
            <h3 className="text-sm font-medium text-[#E8EAED] mb-3">
              Seleccione un formato para generar
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 max-h-80 overflow-y-auto">
              {formatosDisponibles.map((formato) => (
                <button
                  key={formato.numero}
                  onClick={() => {
                    // En produccion se llamaria al API para generar
                    setFormatosGenerados((prev) => [
                      ...prev,
                      {
                        id: `new-${Date.now()}`,
                        numero: formato.numero,
                        nombre: formato.nombre,
                        estado: 'borrador',
                        generado_por_ia: true,
                        fecha: new Date().toISOString(),
                      },
                    ]);
                    setMostrarCatalogo(false);
                  }}
                  className="flex items-center gap-2 rounded-lg border border-[#2D3748] bg-[#0A0F14]/60 p-2.5 text-left text-xs hover:border-[#C9A84C]/40 hover:bg-[#C9A84C]/5 transition-all"
                >
                  <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded bg-[#1A2332] text-[10px] font-mono text-[#C9A84C] border border-[#2D3748]">
                    {formato.numero}
                  </span>
                  <span className="text-[#9AA0A6] line-clamp-1">{formato.nombre}</span>
                </button>
              ))}
            </div>
          </div>
        </Tarjeta>
      )}

      {/* Formatos generados */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-[#9AA0A6]">
          Formatos generados ({formatosGenerados.length})
        </h3>

        {formatosGenerados.map((formato) => {
          const config = estadoConfig[formato.estado];
          const Icono = config.icono;
          return (
            <Tarjeta key={formato.id} className="hover:border-[#4A5568] transition-all">
              <div className="flex items-center p-4">
                <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-[#C9A84C]/10 border border-[#C9A84C]/20 mr-4">
                  <span className="font-mono text-sm font-bold text-[#C9A84C]">
                    {formato.numero}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-medium text-[#E8EAED] truncate">
                      {formato.nombre}
                    </h4>
                    <span
                      className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px]"
                      style={{
                        backgroundColor: `${config.color}20`,
                        color: config.color,
                        border: `1px solid ${config.color}40`,
                      }}
                    >
                      <Icono className="h-3 w-3" />
                      {config.etiqueta}
                    </span>
                    {formato.generado_por_ia && (
                      <Insignia variante="oro" className="text-[9px]">
                        <Bot className="h-2.5 w-2.5 mr-0.5" />
                        IA
                      </Insignia>
                    )}
                  </div>
                  <p className="text-[10px] text-[#5F6368] mt-0.5">
                    Formato #{formato.numero} — Generado el{' '}
                    {new Date(formato.fecha).toLocaleDateString('es-CO')}
                  </p>
                </div>
                <div className="flex items-center gap-1.5 ml-4">
                  <Boton variante="fantasma" tamano="icono" className="h-8 w-8">
                    <Eye className="h-3.5 w-3.5" />
                  </Boton>
                  <Boton variante="fantasma" tamano="icono" className="h-8 w-8">
                    <Download className="h-3.5 w-3.5" />
                  </Boton>
                </div>
              </div>
            </Tarjeta>
          );
        })}
      </div>
    </div>
  );
}
