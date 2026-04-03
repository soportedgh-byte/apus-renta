'use client';

import React from 'react';

interface PropiedadesCarga {
  /** Tamano del spinner */
  tamano?: 'sm' | 'md' | 'lg';
  /** Texto opcional debajo del spinner */
  texto?: string;
  /** Color personalizado */
  color?: string;
}

/**
 * Spinner de carga animado con estilo institucional
 */
export function SpinnerCarga({ tamano = 'md', texto, color }: PropiedadesCarga) {
  const dimensiones = {
    sm: 'h-5 w-5',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  const colorBorde = color || '#C9A84C';

  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div
        className={`${dimensiones[tamano]} animate-spin rounded-full border-2 border-transparent`}
        style={{
          borderTopColor: colorBorde,
          borderRightColor: `${colorBorde}40`,
        }}
        role="status"
        aria-label="Cargando"
      />
      {texto && (
        <p className="text-sm text-[#9AA0A6] animate-pulse">{texto}</p>
      )}
    </div>
  );
}

/**
 * Pantalla completa de carga
 */
export function PantallaCarga({ texto = 'Cargando CecilIA...' }: { texto?: string }) {
  return (
    <div className="flex h-screen w-full items-center justify-center bg-[#0F1419]">
      <div className="flex flex-col items-center gap-6">
        {/* Logo animado */}
        <div className="relative">
          <div className="h-16 w-16 rounded-full border-2 border-[#C9A84C]/20" />
          <div className="absolute inset-0 h-16 w-16 animate-spin rounded-full border-2 border-transparent border-t-[#C9A84C]" />
          <div className="absolute inset-2 h-12 w-12 animate-spin rounded-full border-2 border-transparent border-t-[#D4B96A]" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }} />
        </div>
        <div className="text-center">
          <h2 className="font-titulo text-lg text-[#C9A84C]">CecilIA v2</h2>
          <p className="mt-1 text-sm text-[#9AA0A6]">{texto}</p>
        </div>
      </div>
    </div>
  );
}

export default SpinnerCarga;
