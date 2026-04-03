'use client';

import * as React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Componente Tarjeta - contenedor principal con efecto vidrio
 */
const Tarjeta = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={twMerge(
      clsx(
        'rounded-xl border border-[#2D3748]/50 bg-[#1A2332] shadow-lg',
        'transition-all duration-200',
        className,
      ),
    )}
    {...props}
  />
));
Tarjeta.displayName = 'Tarjeta';

/**
 * Encabezado de la tarjeta
 */
const EncabezadoTarjeta = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={twMerge(clsx('flex flex-col space-y-1.5 p-6', className))}
    {...props}
  />
));
EncabezadoTarjeta.displayName = 'EncabezadoTarjeta';

/**
 * Titulo de la tarjeta
 */
const TituloTarjeta = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={twMerge(
      clsx('font-titulo text-xl font-semibold leading-none tracking-tight text-[#E8EAED]', className),
    )}
    {...props}
  />
));
TituloTarjeta.displayName = 'TituloTarjeta';

/**
 * Descripcion de la tarjeta
 */
const DescripcionTarjeta = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={twMerge(clsx('text-sm text-[#9AA0A6]', className))}
    {...props}
  />
));
DescripcionTarjeta.displayName = 'DescripcionTarjeta';

/**
 * Contenido principal de la tarjeta
 */
const ContenidoTarjeta = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={twMerge(clsx('p-6 pt-0', className))} {...props} />
));
ContenidoTarjeta.displayName = 'ContenidoTarjeta';

/**
 * Pie de la tarjeta
 */
const PieTarjeta = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={twMerge(clsx('flex items-center p-6 pt-0', className))}
    {...props}
  />
));
PieTarjeta.displayName = 'PieTarjeta';

export {
  Tarjeta,
  EncabezadoTarjeta,
  TituloTarjeta,
  DescripcionTarjeta,
  ContenidoTarjeta,
  PieTarjeta,
};
