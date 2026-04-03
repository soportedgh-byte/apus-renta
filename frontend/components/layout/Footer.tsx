'use client';

import React from 'react';
import { ShieldCheck } from 'lucide-react';

/**
 * Pie de pagina con banner de privacidad institucional
 * Muestra el texto exacto requerido sobre proteccion de datos
 */
export function PiePrivacidad() {
  return (
    <footer className="border-t border-[#2D3748]/30 bg-[#0A0F14] px-4 py-2.5">
      <div className="flex items-start gap-2">
        <ShieldCheck className="h-3.5 w-3.5 flex-shrink-0 text-[#C9A84C] mt-0.5" />
        <p className="text-[10px] leading-relaxed text-[#5F6368]">
          Los datos de su auditoria se almacenan como contexto de sesion en servidores de la CGR.
          No se utilizan para entrenar modelos de IA. CecilIA es un asistente: todas las conclusiones
          requieren validacion del auditor. Los archivos locales se procesan en streaming sin copiarse
          permanentemente al servidor.
        </p>
      </div>
    </footer>
  );
}

export default PiePrivacidad;
