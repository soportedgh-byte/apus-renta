'use client';

import React from 'react';
import { Building2, Eye } from 'lucide-react';
import type { Direccion } from '@/lib/types';

interface PropiedadesSelectorRol {
  direccionActiva: Direccion | null;
  puedeVerDES: boolean;
  puedeVerDVF: boolean;
  alSeleccionar: (direccion: Direccion) => void;
}

/**
 * Selector de direccion DES/DVF
 * Permite cambiar entre las dos direcciones disponibles
 */
export function SelectorRol({
  direccionActiva,
  puedeVerDES,
  puedeVerDVF,
  alSeleccionar,
}: PropiedadesSelectorRol) {
  return (
    <div className="flex items-center gap-2">
      {puedeVerDES && (
        <button
          onClick={() => alSeleccionar('DES')}
          className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
            direccionActiva === 'DES'
              ? 'bg-[#1A5276] text-white shadow-md shadow-[#1A5276]/30'
              : 'text-[#9AA0A6] hover:bg-[#1A5276]/20 hover:text-[#2471A3]'
          }`}
        >
          <Eye className="h-3.5 w-3.5" />
          DES
        </button>
      )}
      {puedeVerDVF && (
        <button
          onClick={() => alSeleccionar('DVF')}
          className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
            direccionActiva === 'DVF'
              ? 'bg-[#1E8449] text-white shadow-md shadow-[#1E8449]/30'
              : 'text-[#9AA0A6] hover:bg-[#1E8449]/20 hover:text-[#27AE60]'
          }`}
        >
          <Building2 className="h-3.5 w-3.5" />
          DVF
        </button>
      )}
    </div>
  );
}

export default SelectorRol;
