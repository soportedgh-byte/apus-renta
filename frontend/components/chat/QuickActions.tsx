'use client';

import React from 'react';
import {
  FileSearch,
  AlertTriangle,
  BarChart3,
  FileText,
  Scale,
  Eye,
  TrendingUp,
  ClipboardList,
} from 'lucide-react';
import type { Direccion } from '@/lib/types';

interface PropiedadesAccionesRapidas {
  direccion: Direccion;
  alSeleccionar: (prompt: string) => void;
}

/** Acciones rapidas segun la direccion */
const accionesDES = [
  {
    etiqueta: 'Analisis sectorial',
    prompt: 'Realiza un analisis sectorial del sector TIC identificando los principales riesgos fiscales y tendencias.',
    icono: BarChart3,
  },
  {
    etiqueta: 'Indicadores macro',
    prompt: 'Genera un resumen de los indicadores macroeconomicos relevantes para el control fiscal del sector.',
    icono: TrendingUp,
  },
  {
    etiqueta: 'Alertas sectoriales',
    prompt: 'Identifica posibles alertas tempranas en el sector basandose en los datos disponibles.',
    icono: AlertTriangle,
  },
  {
    etiqueta: 'Estudio transversal',
    prompt: 'Elabora un estudio transversal comparando la ejecucion presupuestal de las entidades del sector.',
    icono: Eye,
  },
];

const accionesDVF = [
  {
    etiqueta: 'Redactar hallazgo',
    prompt: 'Ayudame a redactar un hallazgo fiscal con sus 5 elementos: condicion, criterio, causa, efecto y recomendacion.',
    icono: AlertTriangle,
  },
  {
    etiqueta: 'Revisar normativa',
    prompt: 'Busca la normativa aplicable y los criterios legales relevantes para el hallazgo que estoy documentando.',
    icono: Scale,
  },
  {
    etiqueta: 'Generar formato',
    prompt: 'Necesito generar un formato de auditoria. Listame los formatos disponibles para seleccionar.',
    icono: FileText,
  },
  {
    etiqueta: 'Analizar documento',
    prompt: 'Analiza el documento cargado y extrae los hallazgos potenciales con sus evidencias.',
    icono: FileSearch,
  },
  {
    etiqueta: 'Plan de auditoria',
    prompt: 'Ayudame a elaborar el plan de auditoria con objetivos, alcance, criterios y cronograma.',
    icono: ClipboardList,
  },
];

/**
 * Barra de acciones rapidas contextual segun la direccion del usuario
 */
export function AccionesRapidas({ direccion, alSeleccionar }: PropiedadesAccionesRapidas) {
  const acciones = direccion === 'DES' ? accionesDES : accionesDVF;
  const colorBorde = direccion === 'DES' ? 'border-[#1A5276]/30 hover:border-[#1A5276]/60' : 'border-[#1E8449]/30 hover:border-[#1E8449]/60';
  const colorTexto = direccion === 'DES' ? 'text-[#2471A3]' : 'text-[#27AE60]';

  return (
    <div className="flex flex-wrap gap-2 px-4 py-3 border-t border-[#2D3748]/30">
      <span className="self-center text-[10px] text-[#5F6368] mr-1">Acciones rapidas:</span>
      {acciones.map((accion) => {
        const Icono = accion.icono;
        return (
          <button
            key={accion.etiqueta}
            onClick={() => alSeleccionar(accion.prompt)}
            className={`flex items-center gap-1.5 rounded-lg border bg-[#1A2332]/40 px-2.5 py-1.5 text-xs transition-all ${colorBorde} hover:bg-[#1A2332]`}
          >
            <Icono className={`h-3 w-3 ${colorTexto}`} />
            <span className="text-[#9AA0A6]">{accion.etiqueta}</span>
          </button>
        );
      })}
    </div>
  );
}

export default AccionesRapidas;
