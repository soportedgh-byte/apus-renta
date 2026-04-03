'use client';

import * as React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Propiedades del componente de entrada de texto
 */
export interface PropiedadesInput extends React.InputHTMLAttributes<HTMLInputElement> {
  icono?: React.ReactNode;
  iconoDerecha?: React.ReactNode;
  error?: string;
}

/**
 * Componente Input reutilizable con soporte para iconos y errores
 */
const Input = React.forwardRef<HTMLInputElement, PropiedadesInput>(
  ({ className, type, icono, iconoDerecha, error, ...props }, ref) => {
    return (
      <div className="w-full">
        <div className="relative">
          {icono && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-[#5F6368]">
              {icono}
            </div>
          )}
          <input
            type={type}
            className={twMerge(
              clsx(
                'flex h-11 w-full rounded-lg border bg-[#0A0F14] px-4 py-2 text-sm text-[#E8EAED] placeholder:text-[#5F6368] transition-all duration-200',
                'border-[#2D3748] focus:border-[#C9A84C] focus:outline-none focus:ring-1 focus:ring-[#C9A84C]/50',
                'disabled:cursor-not-allowed disabled:opacity-50',
                icono && 'pl-10',
                iconoDerecha && 'pr-10',
                error && 'border-red-500 focus:border-red-500 focus:ring-red-500/50',
                className,
              ),
            )}
            ref={ref}
            {...props}
          />
          {iconoDerecha && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-[#5F6368]">
              {iconoDerecha}
            </div>
          )}
        </div>
        {error && (
          <p className="mt-1.5 text-xs text-red-400">{error}</p>
        )}
      </div>
    );
  },
);

Input.displayName = 'Input';

export { Input };
