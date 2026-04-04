'use client';

import React from 'react';
import Image from 'next/image';
import { Shield, Users, Scale, BookOpen, Cpu, Award } from 'lucide-react';

/**
 * Pagina "Acerca de CecilIA" — Informacion institucional, equipo y marco normativo
 * Cumplimiento Circular 023 — Principio de Transparencia
 */
export default function PaginaAcerca() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-8 space-y-8">
      {/* Header con logos */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-6">
          <div className="relative h-16 w-16">
            <Image src="/logo-cgr.png" alt="CGR" fill className="object-contain" sizes="64px" />
          </div>
          <div className="relative h-16 w-16">
            <Image src="/logo-cecilia.png" alt="CecilIA" fill className="object-contain" sizes="64px" />
          </div>
        </div>
        <h1 className="font-titulo text-2xl font-bold text-[#C9A84C]">
          CecilIA v2
        </h1>
        <p className="text-sm text-[#9AA0A6]">
          Sistema de Inteligencia Artificial para Control Fiscal
        </p>
        <p className="text-xs text-[#5F6368]">
          Contraloria General de la Republica de Colombia
        </p>
      </div>

      {/* Origen del proyecto */}
      <section className="rounded-xl border border-[#2D3748]/30 bg-[#1A2332]/40 p-6">
        <div className="flex items-center gap-2 mb-3">
          <Award className="h-5 w-5 text-[#C9A84C]" />
          <h2 className="text-base font-semibold text-[#E8EAED]">Origen del proyecto</h2>
        </div>
        <p className="text-sm text-[#9AA0A6] leading-relaxed">
          CecilIA es una iniciativa concebida e impulsada por el Dr. Omar Javier Contreras Socarras,
          Contralor Delegado para el Sector TIC de la Contraloria General de la Republica, como parte
          de la estrategia de transformacion digital e innovacion en el control fiscal colombiano.
          El proyecto nacio de la vision de potenciar las capacidades de los auditores y analistas
          de la CD-TIC mediante inteligencia artificial responsable, etica y soberana.
        </p>
      </section>

      {/* Equipo */}
      <section className="rounded-xl border border-[#2D3748]/30 bg-[#1A2332]/40 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Users className="h-5 w-5 text-[#C9A84C]" />
          <h2 className="text-base font-semibold text-[#E8EAED]">Equipo</h2>
        </div>
        <div className="space-y-3">
          {[
            { cargo: 'Direccion del proyecto', nombre: 'Dr. Omar Javier Contreras Socarras', detalle: 'Contralor Delegado TIC' },
            { cargo: 'Direccion Operativa', nombre: 'Dr. Hector Hernan Gonzalez Naranjo', detalle: 'Contralor Delegado TIC (actual)' },
            { cargo: 'Direccion DES', nombre: 'Dr. Juan Carlos Cobo Gomez', detalle: 'Director de Estudios Sectoriales' },
            { cargo: 'Direccion DVF', nombre: 'Dr. Jose Fernando Ramirez Munoz', detalle: 'Director de Vigilancia Fiscal' },
            { cargo: 'Coordinacion Juridica', nombre: 'Dra. Karen Tatiana Suevis Gomez', detalle: 'Asesora Juridica' },
            { cargo: 'Lider Tecnico', nombre: 'Ing. Gustavo Adolfo Castillo Romero', detalle: 'Lider de Desarrollo e IA' },
          ].map((miembro) => (
            <div key={miembro.cargo} className="flex items-start gap-3 py-2 border-b border-[#2D3748]/20 last:border-0">
              <div className="h-2 w-2 rounded-full bg-[#C9A84C] mt-1.5 flex-shrink-0" />
              <div>
                <p className="text-xs text-[#5F6368]">{miembro.cargo}</p>
                <p className="text-sm font-medium text-[#E8EAED]">{miembro.nombre}</p>
                <p className="text-xs text-[#5F6368]">{miembro.detalle}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Marco normativo */}
      <section className="rounded-xl border border-[#2D3748]/30 bg-[#1A2332]/40 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Scale className="h-5 w-5 text-[#C9A84C]" />
          <h2 className="text-base font-semibold text-[#E8EAED]">Marco normativo</h2>
        </div>
        <div className="space-y-2">
          {[
            'Circular 023 de 2025 (2025IE0146473) — Directrices sobre uso de IA en la CGR',
            'CONPES 4144 de 2025 — Politica Nacional de Inteligencia Artificial',
            'Ley 1581 de 2012 — Proteccion de Datos Personales',
            'Ley 42 de 1993 — Organizacion del sistema de control fiscal',
            'Decreto 403 de 2020 — Reglamentacion del control fiscal',
            'Decreto Ley 267 de 2000 — Estructura de la CGR',
            'Sentencia T-323 de 2024 — Corte Constitucional sobre uso de IA',
            'NIA adoptadas en Colombia — Normas Internacionales de Auditoria',
            'Ley 610 de 2000 — Proceso de Responsabilidad Fiscal',
          ].map((norma) => (
            <div key={norma} className="flex items-start gap-2 py-1">
              <span className="text-[#C9A84C] text-xs mt-0.5">-</span>
              <p className="text-xs text-[#9AA0A6] leading-relaxed">{norma}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Transparencia algoritmica */}
      <section className="rounded-xl border border-[#2D3748]/30 bg-[#1A2332]/40 p-6">
        <div className="flex items-center gap-2 mb-3">
          <Cpu className="h-5 w-5 text-[#C9A84C]" />
          <h2 className="text-base font-semibold text-[#E8EAED]">Transparencia algoritmica</h2>
        </div>
        <p className="text-sm text-[#9AA0A6] leading-relaxed">
          CecilIA privilegia el uso de modelos de IA de codigo abierto conforme al principio de
          prevencion de riesgos de la Circular 023. Los modelos utilizados (Qwen3, Llama 3.3,
          Gemini) tienen arquitectura y pesos publicamente auditables. Los embeddings se generan
          localmente con modelos open-source (nomic-embed-text) y los datos se procesan
          exclusivamente en servidores institucionales de la CGR.
        </p>
      </section>

      {/* Version */}
      <div className="text-center py-4">
        <p className="text-xs text-[#5F6368]">
          CecilIA v2.0 · 2026 · Contraloria General de la Republica de Colombia
        </p>
        <p className="text-[10px] text-[#5F6368]/60 mt-1">
          Contraloria Delegada para el Sector TIC — CD-TIC-CGR
        </p>
      </div>
    </div>
  );
}
