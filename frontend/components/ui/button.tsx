'use client';

import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Variantes del componente Boton
 * Incluye estilos institucionales DES/DVF y acento dorado
 */
const variantesBoton = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C9A84C] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0F1419] disabled:pointer-events-none disabled:opacity-50 cursor-pointer',
  {
    variants: {
      variante: {
        primario:
          'bg-gradient-to-r from-[#C9A84C] to-[#D4B96A] text-[#0F1419] font-semibold hover:from-[#D4B96A] hover:to-[#C9A84C] shadow-lg shadow-[#C9A84C]/20',
        des:
          'bg-[#1A5276] text-white hover:bg-[#2471A3] shadow-md',
        dvf:
          'bg-[#1E8449] text-white hover:bg-[#27AE60] shadow-md',
        secundario:
          'bg-[#1A2332] text-[#E8EAED] border border-[#2D3748] hover:bg-[#243044] hover:border-[#4A5568]',
        fantasma:
          'text-[#9AA0A6] hover:text-[#E8EAED] hover:bg-[#1A2332]',
        enlace:
          'text-[#C9A84C] underline-offset-4 hover:underline',
        destructivo:
          'bg-red-600 text-white hover:bg-red-700 shadow-md',
        contorno:
          'border border-[#2D3748] text-[#E8EAED] hover:bg-[#1A2332] hover:border-[#C9A84C]',
      },
      tamano: {
        sm: 'h-8 px-3 text-xs rounded-md',
        md: 'h-10 px-4 text-sm',
        lg: 'h-12 px-6 text-base',
        xl: 'h-14 px-8 text-lg',
        icono: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variante: 'primario',
      tamano: 'md',
    },
  },
);

export interface PropiedadesBoton
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof variantesBoton> {
  cargando?: boolean;
}

/**
 * Componente Boton reutilizable con variantes institucionales
 */
const Boton = React.forwardRef<HTMLButtonElement, PropiedadesBoton>(
  ({ className, variante, tamano, cargando, children, disabled, ...props }, ref) => {
    return (
      <button
        className={twMerge(clsx(variantesBoton({ variante, tamano }), className))}
        ref={ref}
        disabled={disabled || cargando}
        {...props}
      >
        {cargando && (
          <svg
            className="h-4 w-4 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        )}
        {children}
      </button>
    );
  },
);

Boton.displayName = 'Boton';

export { Boton, variantesBoton };
