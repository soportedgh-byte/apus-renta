'use client';

import React from 'react';
import {
  FileSearch,
  AlertTriangle,
  BarChart3,
  FileText,
  Scale,
  TrendingUp,
  DollarSign,
  ClipboardList,
} from 'lucide-react';
import type { Direccion } from '@/lib/types';

interface PropiedadesAccionesRapidas {
  direccion: Direccion;
  alSeleccionar: (prompt: string) => void;
}

/** Acciones rapidas DVF — 4 botones principales */
const accionesDVF = [
  {
    etiqueta: 'Iniciar pre-planeacion',
    emoji: '📝',
    prompt: 'Ayudame a iniciar la fase de pre-planeacion de una auditoria. Necesito definir el universo auditable, identificar la entidad y los criterios de seleccion.',
    icono: ClipboardList,
  },
  {
    etiqueta: 'Calcular materialidad',
    emoji: '🧮',
    prompt: 'Necesito calcular la materialidad para una auditoria financiera. Explicame los metodos disponibles y ayudame a determinar el nivel adecuado.',
    icono: Scale,
  },
  {
    etiqueta: 'Configurar hallazgo',
    emoji: '🔎',
    prompt: 'Ayudame a redactar un hallazgo fiscal con sus 5 elementos obligatorios: condicion, criterio, causa, efecto y recomendacion.',
    icono: AlertTriangle,
  },
  {
    etiqueta: 'Generar formato CGR',
    emoji: '📄',
    prompt: 'Necesito generar un formato de auditoria CGR. Listame los formatos disponibles (F1 al F30) para seleccionar el que necesito.',
    icono: FileText,
  },
];

/** Acciones rapidas DES — 4 botones principales */
const accionesDES = [
  {
    etiqueta: 'Analisis presupuestal',
    emoji: '📈',
    prompt: 'Realiza un analisis de la ejecucion presupuestal del sector, identificando los principales rubros, tendencias y alertas fiscales.',
    icono: BarChart3,
  },
  {
    etiqueta: 'Seguimiento regalias',
    emoji: '💰',
    prompt: 'Analiza el estado del Sistema General de Regalias, identificando la ejecucion por departamento y los principales riesgos.',
    icono: DollarSign,
  },
  {
    etiqueta: 'Evaluacion politica',
    emoji: '📋',
    prompt: 'Ayudame a disenar una evaluacion de politica publica. Necesito definir el marco de evaluacion, la cadena de valor y los indicadores.',
    icono: FileSearch,
  },
  {
    etiqueta: 'Alerta temprana',
    emoji: '⚠️',
    prompt: 'Identifica posibles alertas tempranas en el sector basandose en los indicadores disponibles y genera un borrador de pronunciamiento.',
    icono: TrendingUp,
  },
];

/**
 * Acciones rapidas contextuales por direccion
 * Visibles solo cuando no hay mensajes en el chat
 */
export function AccionesRapidas({ direccion, alSeleccionar }: PropiedadesAccionesRapidas) {
  const acciones = direccion === 'DES' ? accionesDES : accionesDVF;
  const colorBorde = direccion === 'DES' ? '#1A5276' : '#1E8449';
  const colorTexto = direccion === 'DES' ? '#2471A3' : '#27AE60';

  return (
    <div className="px-4 py-3 border-t border-[#2D3748]/20">
      <div className="mx-auto max-w-3xl">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {acciones.map((accion) => (
            <button
              key={accion.etiqueta}
              onClick={() => alSeleccionar(accion.prompt)}
              className="group flex flex-col items-center gap-2 rounded-xl border bg-[#1A2332]/30 p-3 text-center transition-all hover:bg-[#1A2332] hover:-translate-y-0.5"
              style={{
                borderColor: `${colorBorde}25`,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = `${colorBorde}60`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = `${colorBorde}25`;
              }}
            >
              <span className="text-xl">{accion.emoji}</span>
              <span className="text-[11px] font-medium text-[#9AA0A6] group-hover:text-[#E8EAED] transition-colors leading-tight">
                {accion.etiqueta}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default AccionesRapidas;
