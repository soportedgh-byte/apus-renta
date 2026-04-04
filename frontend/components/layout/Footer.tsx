'use client';

import React from 'react';
import { ShieldCheck } from 'lucide-react';

/**
 * Pie de pagina con banner de privacidad institucional
 * Actualizado para cumplimiento de la Circular 023 de la CGR
 */
export function PiePrivacidad() {
  return (
    <footer className="border-t border-[#2D3748]/30 bg-[#0A0F14] px-4 py-2.5">
      <div className="flex items-start gap-2">
        <ShieldCheck className="h-3.5 w-3.5 flex-shrink-0 text-[#C9A84C] mt-0.5" />
        <div>
          <p className="text-[10px] leading-relaxed text-[#5F6368]">
            <span className="text-[#9AA0A6] font-medium">CecilIA v2</span> — Sistema de IA para Control Fiscal — Contraloria Delegada TIC
          </p>
          <p className="text-[10px] leading-relaxed text-[#5F6368]">
            Conforme a la Circular 023 de la CGR: Los datos se procesan en servidores institucionales.
            No se utilizan para entrenar modelos de IA. Toda respuesta requiere validacion del servidor publico responsable.
            <span className="text-[#5F6368]/70"> Ley 1581/2012 · CONPES 4144/2025 · Sentencia T-323/2024</span>
          </p>
          <p className="text-[9px] leading-relaxed text-[#5F6368]/60 mt-0.5">
            Proyecto impulsado por el Dr. Omar Javier Contreras Socarras, Contralor Delegado TIC
          </p>
        </div>
      </div>
    </footer>
  );
}

export default PiePrivacidad;
