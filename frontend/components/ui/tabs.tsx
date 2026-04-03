'use client';

import * as React from 'react';
import * as TabsPrimitivo from '@radix-ui/react-tabs';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Contenedor raiz de pestanas
 */
const Pestanas = TabsPrimitivo.Root;

/**
 * Lista de pestanas (barra de navegacion)
 */
const ListaPestanas = React.forwardRef<
  React.ComponentRef<typeof TabsPrimitivo.List>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitivo.List>
>(({ className, ...props }, ref) => (
  <TabsPrimitivo.List
    ref={ref}
    className={twMerge(
      clsx(
        'inline-flex h-10 items-center justify-center rounded-lg bg-[#0A0F14] p-1 text-[#9AA0A6]',
        className,
      ),
    )}
    {...props}
  />
));
ListaPestanas.displayName = 'ListaPestanas';

/**
 * Disparador individual de pestana
 */
const DisparadorPestana = React.forwardRef<
  React.ComponentRef<typeof TabsPrimitivo.Trigger>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitivo.Trigger>
>(({ className, ...props }, ref) => (
  <TabsPrimitivo.Trigger
    ref={ref}
    className={twMerge(
      clsx(
        'inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium transition-all',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C9A84C]',
        'disabled:pointer-events-none disabled:opacity-50',
        'data-[state=active]:bg-[#1A2332] data-[state=active]:text-[#E8EAED] data-[state=active]:shadow-sm',
        'hover:text-[#E8EAED]',
        className,
      ),
    )}
    {...props}
  />
));
DisparadorPestana.displayName = 'DisparadorPestana';

/**
 * Contenido de la pestana
 */
const ContenidoPestana = React.forwardRef<
  React.ComponentRef<typeof TabsPrimitivo.Content>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitivo.Content>
>(({ className, ...props }, ref) => (
  <TabsPrimitivo.Content
    ref={ref}
    className={twMerge(
      clsx(
        'mt-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C9A84C]',
        className,
      ),
    )}
    {...props}
  />
));
ContenidoPestana.displayName = 'ContenidoPestana';

export { Pestanas, ListaPestanas, DisparadorPestana, ContenidoPestana };
