'use client';

import React, { useState, useEffect } from 'react';
import { Shield, ExternalLink } from 'lucide-react';

const CLAVE_ACEPTACION = 'cecilia_responsabilidad_aceptada';

/**
 * Modal de aceptacion de responsabilidad — Circular 023 CGR
 * Se muestra una sola vez al primer login de cada usuario.
 * Principio 2: Responsabilidad del servidor publico
 * Principio 9: Declaracion de riesgos
 */
export function ModalResponsabilidad() {
  const [visible, setVisible] = useState(false);
  const [aceptando, setAceptando] = useState(false);

  useEffect(() => {
    // Verificar si ya fue aceptado
    if (typeof window !== 'undefined') {
      const aceptado = localStorage.getItem(CLAVE_ACEPTACION);
      if (!aceptado) {
        setVisible(true);
      }
    }
  }, []);

  const aceptar = async () => {
    setAceptando(true);
    try {
      // Intentar registrar en el backend
      const urlBase = process.env.NEXT_PUBLIC_API_URL || '/api';
      await fetch(`${urlBase}/auth/aceptar-responsabilidad`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          version_circular: '023-2025',
          timestamp: new Date().toISOString(),
        }),
      }).catch(() => {
        // Si falla el backend, no bloquear al usuario
      });
    } finally {
      localStorage.setItem(CLAVE_ACEPTACION, new Date().toISOString());
      setVisible(false);
      setAceptando(false);
    }
  };

  const cancelar = () => {
    // No dejar entrar — redirigir a login
    if (typeof window !== 'undefined') {
      localStorage.removeItem('cecilia_token');
      localStorage.removeItem('cecilia_usuario');
      window.location.href = '/login';
    }
  };

  if (!visible) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="mx-4 w-full max-w-lg rounded-2xl border border-[#2D3748]/40 bg-[#1A2332] shadow-2xl">
        {/* Header */}
        <div className="flex items-center gap-3 border-b border-[#2D3748]/30 px-6 py-4">
          <Shield className="h-6 w-6 text-[#C9A84C]" />
          <div>
            <h2 className="text-sm font-bold text-[#E8EAED]">
              Declaracion de Responsabilidad
            </h2>
            <p className="text-[10px] text-[#5F6368]">Circular 023 CGR — Obligatorio</p>
          </div>
        </div>

        {/* Contenido */}
        <div className="px-6 py-5 space-y-4">
          <p className="text-xs text-[#9AA0A6] leading-relaxed">
            Al utilizar CecilIA, usted reconoce que:
          </p>

          <ol className="space-y-3">
            {[
              'Es responsable de la exactitud y pertinencia de los documentos generados con asistencia de IA.',
              'Debe verificar todas las fuentes, datos y conclusiones antes de su uso oficial.',
              'La IA no sustituye su juicio profesional ni exonera de responsabilidad por errores.',
              'Se compromete a declarar el uso de IA en los documentos producidos.',
            ].map((item, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[#C9A84C]/10 text-[10px] font-bold text-[#C9A84C] flex-shrink-0 mt-0.5">
                  {i + 1}
                </span>
                <p className="text-xs text-[#E8EAED] leading-relaxed">{item}</p>
              </li>
            ))}
          </ol>

          {/* Declaracion de riesgos — Principio 9 */}
          <div className="rounded-lg border border-[#C9A84C]/20 bg-[#C9A84C]/5 px-4 py-3">
            <p className="text-[11px] text-[#C9A84C]/80 leading-relaxed">
              Conforme al principio de declaracion de riesgos de la Circular 023:
              La IA puede presentar errores, sesgos, desactualizacion de datos o generar
              contenido impreciso. Los resultados deben someterse a verificaciones adicionales
              por profesionales competentes.
            </p>
          </div>

          <p className="text-[10px] text-[#5F6368] leading-relaxed">
            Conforme a la Circular 023 de la CGR y la Sentencia T-323 de 2024 de la Corte Constitucional.
          </p>
        </div>

        {/* Acciones */}
        <div className="flex items-center justify-between border-t border-[#2D3748]/30 px-6 py-4">
          <a href="/guia-uso" className="flex items-center gap-1 text-[10px] text-[#2471A3] hover:underline">
            <ExternalLink className="h-3 w-3" />
            Ver guia de uso completa
          </a>
          <div className="flex gap-2">
            <button
              onClick={cancelar}
              className="rounded-lg px-4 py-2 text-xs text-[#9AA0A6] hover:text-[#E8EAED] hover:bg-[#2D3748]/30 transition-colors"
            >
              Cancelar
            </button>
            <button
              onClick={aceptar}
              disabled={aceptando}
              className="rounded-lg bg-gradient-to-r from-[#C9A84C] to-[#D4B96A] px-5 py-2 text-xs font-semibold text-[#0F1419] hover:from-[#D4B96A] hover:to-[#C9A84C] disabled:opacity-50 transition-all"
            >
              {aceptando ? 'Registrando...' : 'Acepto y comprendo'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ModalResponsabilidad;
