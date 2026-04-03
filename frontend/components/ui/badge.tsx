'use client';

import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Variantes de la insignia (badge)
 */
const variantesInsignia = cva(
  'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors',
  {
    variants: {
      variante: {
        des: 'bg-[#1A5276]/20 text-[#2471A3] border border-[#1A5276]/40',
        dvf: 'bg-[#1E8449]/20 text-[#27AE60] border border-[#1E8449]/40',
        oro: 'bg-[#C9A84C]/20 text-[#D4B96A] border border-[#C9A84C]/40',
        gris: 'bg-[#2D3748]/40 text-[#9AA0A6] border border-[#2D3748]',
        rojo: 'bg-red-500/20 text-red-400 border border-red-500/40',
        amarillo: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/40',
        exito: 'bg-green-500/20 text-green-400 border border-green-500/40',
        info: 'bg-blue-500/20 text-blue-400 border border-blue-500/40',
        fiscal: 'bg-red-600/20 text-red-300 border border-red-600/40',
        disciplinario: 'bg-orange-500/20 text-orange-300 border border-orange-500/40',
        penal: 'bg-purple-500/20 text-purple-300 border border-purple-500/40',
        administrativo: 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40',
      },
    },
    defaultVariants: {
      variante: 'gris',
    },
  },
);

export interface PropiedadesInsignia
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof variantesInsignia> {}

/**
 * Componente Insignia para etiquetas y estados
 */
function Insignia({ className, variante, ...props }: PropiedadesInsignia) {
  return (
    <div
      className={twMerge(clsx(variantesInsignia({ variante }), className))}
      {...props}
    />
  );
}

export { Insignia, variantesInsignia };
