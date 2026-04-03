'use client';

import React from 'react';
import { Insignia } from '@/components/ui/badge';
import type { TipoConnotacion } from '@/lib/types';

interface PropiedadesConnotacion {
  tipo: TipoConnotacion;
  className?: string;
}

/** Mapa de connotaciones a variantes y etiquetas */
const configuracion: Record<TipoConnotacion, { variante: 'fiscal' | 'disciplinario' | 'penal' | 'administrativo' | 'oro'; etiqueta: string }> = {
  fiscal: { variante: 'fiscal', etiqueta: 'Fiscal' },
  disciplinario: { variante: 'disciplinario', etiqueta: 'Disciplinario' },
  penal: { variante: 'penal', etiqueta: 'Penal' },
  administrativo: { variante: 'administrativo', etiqueta: 'Administrativo' },
  fiscal_disciplinario: { variante: 'oro', etiqueta: 'Fiscal y Disciplinario' },
};

/**
 * Insignia de tipo de connotacion para hallazgos
 * Muestra el color y etiqueta correspondiente al tipo
 */
export function InsigniaConnotacion({ tipo, className }: PropiedadesConnotacion) {
  const config = configuracion[tipo];
  // Usar 'gris' como fallback seguro si la variante no existe directamente
  return (
    <Insignia variante={config.variante as 'gris'} className={className}>
      {config.etiqueta}
    </Insignia>
  );
}

export default InsigniaConnotacion;
