'use client';

import React, { Component, type ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Boton } from '@/components/ui/button';

interface PropiedadesLimiteError {
  children: ReactNode;
  /** Componente alternativo personalizado */
  fallback?: ReactNode;
}

interface EstadoLimiteError {
  tieneError: boolean;
  error?: Error;
}

/**
 * Limite de error que captura errores en componentes hijos
 * y muestra una interfaz de recuperacion amigable
 */
export class LimiteError extends Component<PropiedadesLimiteError, EstadoLimiteError> {
  constructor(props: PropiedadesLimiteError) {
    super(props);
    this.state = { tieneError: false };
  }

  static getDerivedStateFromError(error: Error): EstadoLimiteError {
    return { tieneError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo): void {
    console.error('[CecilIA] Error capturado:', error, info);
  }

  private reintentar = () => {
    this.setState({ tieneError: false, error: undefined });
  };

  render(): ReactNode {
    if (this.state.tieneError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex min-h-[300px] items-center justify-center p-8">
          <div className="max-w-md text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-500/10 border border-red-500/20">
              <AlertTriangle className="h-8 w-8 text-red-400" />
            </div>
            <h3 className="font-titulo text-lg font-semibold text-[#E8EAED] mb-2">
              Ocurrio un error inesperado
            </h3>
            <p className="text-sm text-[#9AA0A6] mb-6">
              Se produjo un error al renderizar este componente.
              Por favor, intente nuevamente o contacte al equipo de soporte CD-TIC-CGR.
            </p>
            {this.state.error && (
              <details className="mb-4 text-left">
                <summary className="cursor-pointer text-xs text-[#5F6368] hover:text-[#9AA0A6]">
                  Detalles del error
                </summary>
                <pre className="mt-2 rounded-lg bg-[#0A0F14] p-3 text-xs text-red-400 overflow-auto max-h-32 font-codigo">
                  {this.state.error.message}
                </pre>
              </details>
            )}
            <Boton variante="secundario" onClick={this.reintentar}>
              <RefreshCw className="h-4 w-4" />
              Reintentar
            </Boton>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default LimiteError;
