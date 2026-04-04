'use client';

import React, { useState } from 'react';
import { BookOpen, CheckCircle, XCircle, User, HelpCircle, ChevronDown, ChevronUp, AlertTriangle, Shield } from 'lucide-react';

interface SeccionProps {
  titulo: string;
  icono: React.ReactNode;
  children: React.ReactNode;
  abierta?: boolean;
}

function Seccion({ titulo, icono, children, abierta = false }: SeccionProps) {
  const [expandida, setExpandida] = useState(abierta);
  return (
    <div className="rounded-xl border border-[#2D3748]/30 bg-[#1A2332]/40 overflow-hidden">
      <button
        onClick={() => setExpandida(!expandida)}
        className="flex w-full items-center gap-3 px-6 py-4 hover:bg-[#1A2332]/60 transition-colors"
      >
        <span className="text-[#C9A84C]">{icono}</span>
        <h2 className="text-sm font-semibold text-[#E8EAED] flex-1 text-left">{titulo}</h2>
        {expandida ? <ChevronUp className="h-4 w-4 text-[#5F6368]" /> : <ChevronDown className="h-4 w-4 text-[#5F6368]" />}
      </button>
      {expandida && <div className="px-6 pb-5 pt-1">{children}</div>}
    </div>
  );
}

function FAQ({ pregunta, respuesta }: { pregunta: string; respuesta: string }) {
  const [abierta, setAbierta] = useState(false);
  return (
    <div className="border-b border-[#2D3748]/20 last:border-0">
      <button onClick={() => setAbierta(!abierta)} className="flex w-full items-start gap-2 py-3 text-left">
        <HelpCircle className="h-3.5 w-3.5 text-[#C9A84C] mt-0.5 flex-shrink-0" />
        <span className="text-xs font-medium text-[#E8EAED] flex-1">{pregunta}</span>
        {abierta ? <ChevronUp className="h-3 w-3 text-[#5F6368]" /> : <ChevronDown className="h-3 w-3 text-[#5F6368]" />}
      </button>
      {abierta && <p className="text-xs text-[#9AA0A6] leading-relaxed pl-5.5 pb-3 ml-1">{respuesta}</p>}
    </div>
  );
}

/**
 * Guia de uso de CecilIA — Cumplimiento Principio 7 (Conocimiento) Circular 023
 */
export default function PaginaGuiaUso() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-8 space-y-4">
      <div className="text-center mb-6">
        <h1 className="font-titulo text-xl font-bold text-[#C9A84C] mb-2">
          Guia de uso de CecilIA
        </h1>
        <p className="text-xs text-[#5F6368]">
          Conforme al Principio 7 (Conocimiento) de la Circular 023 de la CGR
        </p>
      </div>

      <Seccion titulo="1. Que es CecilIA?" icono={<BookOpen className="h-5 w-5" />} abierta={true}>
        <p className="text-sm text-[#9AA0A6] leading-relaxed">
          CecilIA es el sistema de inteligencia artificial de la Contraloria General de la Republica
          de Colombia, disenado para asistir a los auditores y analistas de la Contraloria Delegada
          para el Sector TIC (CD-TIC-CGR) en sus procesos de control fiscal.
        </p>
        <p className="text-sm text-[#9AA0A6] leading-relaxed mt-2">
          Utiliza modelos de lenguaje avanzados combinados con un sistema de Recuperacion Aumentada
          por Generacion (RAG) que consulta el corpus normativo, jurisprudencial e institucional de
          la CGR para fundamentar sus respuestas con fuentes verificables.
        </p>
        <div className="mt-3 rounded-lg border border-[#C9A84C]/20 bg-[#C9A84C]/5 px-3 py-2">
          <p className="text-[11px] text-[#C9A84C]/80">
            CecilIA es una herramienta de APOYO. No reemplaza el juicio profesional del auditor
            ni exonera de responsabilidad por los productos generados con su asistencia.
          </p>
        </div>
      </Seccion>

      <Seccion titulo="2. Que puede hacer CecilIA? (Usos permitidos)" icono={<CheckCircle className="h-5 w-5" />}>
        <p className="text-xs text-[#5F6368] mb-3">Seccion V de la Circular 023 — Usos aprobados:</p>
        <ul className="space-y-2">
          {[
            'Buscar y citar normativa aplicable (leyes, decretos, resoluciones, NIA)',
            'Asistir en la estructuracion de hallazgos con sus 4 atributos (condicion, criterio, causa, efecto)',
            'Generar BORRADORES de documentos de auditoria para revision del auditor',
            'Realizar analisis de datos financieros e indicadores sectoriales',
            'Consultar guias de auditoria (GAF) y metodologias institucionales',
            'Asistir en la planeacion de auditorias y estudios sectoriales',
            'Aplicar analisis de Ley de Benford para deteccion de anomalias',
            'Generar formatos CGR (1-30) como borradores editables',
            'Buscar jurisprudencia de control fiscal y responsabilidad fiscal',
            'Calcular indicadores de materialidad, muestreo y riesgo de auditoria',
          ].map((uso) => (
            <li key={uso} className="flex items-start gap-2">
              <CheckCircle className="h-3.5 w-3.5 text-green-500 mt-0.5 flex-shrink-0" />
              <span className="text-xs text-[#9AA0A6]">{uso}</span>
            </li>
          ))}
        </ul>
      </Seccion>

      <Seccion titulo="3. Que NO puede hacer CecilIA? (Usos limitados)" icono={<XCircle className="h-5 w-5" />}>
        <p className="text-xs text-[#5F6368] mb-3">Seccion VI de la Circular 023 — Usos con restricciones:</p>
        <ul className="space-y-2">
          {[
            'Generar dictamenes u opiniones FINALES sobre estados contables — solo borradores',
            'Redactar hallazgos DEFINITIVOS — solo propuestas para revision del auditor',
            'Producir diagnosticos sectoriales COMPLETOS sin revision — solo analisis preliminares',
            'Generar informes finales de EPP listos para publicacion — solo borradores',
            'Sustituir la evaluacion y juicio profesional del auditor',
            'Procesar datos personales identificables sin previa anonimizacion',
            'Tomar decisiones autonomas sobre traslados fiscales, disciplinarios o penales',
            'Generar contenido oficial de la CGR sin revision y aprobacion humana',
          ].map((uso) => (
            <li key={uso} className="flex items-start gap-2">
              <XCircle className="h-3.5 w-3.5 text-red-400 mt-0.5 flex-shrink-0" />
              <span className="text-xs text-[#9AA0A6]">{uso}</span>
            </li>
          ))}
        </ul>
        <div className="mt-3 rounded-lg border border-red-500/20 bg-red-500/5 px-3 py-2">
          <p className="text-[11px] text-red-400/80">
            La redaccion final de hallazgos, dictamenes, informes y diagnosticos es
            responsabilidad exclusiva del servidor publico. CecilIA solo genera borradores y sugerencias.
          </p>
        </div>
      </Seccion>

      <Seccion titulo="4. Tu responsabilidad como usuario" icono={<User className="h-5 w-5" />}>
        <p className="text-xs text-[#5F6368] mb-3">Principio 2 — Responsabilidad del servidor publico:</p>
        <div className="space-y-3">
          {[
            { titulo: 'Verificar siempre', texto: 'Todas las fuentes, datos, cifras y conclusiones generadas por CecilIA deben ser verificadas antes de su uso oficial.' },
            { titulo: 'Declarar el uso de IA', texto: 'Todo documento en cuya construccion se haya incorporado CecilIA debe hacerlo explicito, conforme a la Circular 023.' },
            { titulo: 'No delegar responsabilidad', texto: 'Usted es siempre responsable de la exactitud y pertinencia del contenido, independientemente de que haya sido asistido por IA.' },
            { titulo: 'Proteger datos personales', texto: 'Anonimice datos personales antes de compartirlos con CecilIA. Nunca ingrese cedulas, nombres propios de personas naturales, NIT personales o direcciones particulares.' },
            { titulo: 'Revisar antes de aprobar', texto: 'Lea cuidadosamente cada borrador generado. Modifique, ajuste y apruebe con su criterio profesional.' },
          ].map((item) => (
            <div key={item.titulo} className="rounded-lg bg-[#0A0F14]/40 px-4 py-3 border border-[#2D3748]/20">
              <p className="text-xs font-medium text-[#E8EAED] mb-1">{item.titulo}</p>
              <p className="text-xs text-[#9AA0A6] leading-relaxed">{item.texto}</p>
            </div>
          ))}
        </div>
      </Seccion>

      <Seccion titulo="5. Preguntas frecuentes" icono={<HelpCircle className="h-5 w-5" />}>
        <div>
          <FAQ pregunta="CecilIA puede equivocarse?" respuesta="Si. La IA puede presentar errores, sesgos, desactualizacion de datos o generar contenido impreciso. Todos los resultados deben verificarse por el auditor responsable." />
          <FAQ pregunta="Mis datos estan seguros?" respuesta="Si. Los datos se procesan exclusivamente en servidores institucionales de la CGR. No se comparten con terceros ni se usan para entrenar modelos de IA." />
          <FAQ pregunta="Puedo usar CecilIA para redactar hallazgos?" respuesta="CecilIA puede asistir con BORRADORES de hallazgos. La redaccion final es responsabilidad del auditor conforme a la Seccion VI.1.4 de la Circular 023." />
          <FAQ pregunta="Que modelos de IA utiliza CecilIA?" respuesta="CecilIA privilegia modelos de codigo abierto (Qwen3, Llama 3.3) y puede usar Gemini como alternativa. Todos tienen arquitectura publicamente auditable." />
          <FAQ pregunta="Debo declarar que use CecilIA?" respuesta="Si. La Circular 023 exige que todo documento generado con asistencia de IA debe declararlo explicitamente." />
          <FAQ pregunta="CecilIA puede generar formatos CGR?" respuesta="Si, puede generar borradores de los formatos 1 al 30 del proceso auditor. Siempre deben ser revisados y aprobados por el equipo auditor." />
          <FAQ pregunta="Puedo ingresar datos personales?" respuesta="No sin anonimizacion previa. Conforme a la Ley 1581/2012 y la Circular 023, los datos personales deben ser anonimizados antes de procesarlos con IA." />
          <FAQ pregunta="Que pasa si CecilIA no tiene informacion?" respuesta="CecilIA indicara: 'No cuento con informacion suficiente para responder con precision esta consulta.' Nunca inventa normas, cifras o hallazgos." />
          <FAQ pregunta="Quien supervisa el uso de CecilIA?" respuesta="Conforme al Principio 10, cada dependencia tiene un responsable que reporta trimestralmente al Jefe de DIARI sobre el uso de herramientas de IA." />
          <FAQ pregunta="Donde puedo reportar un problema?" respuesta="Puede reportar incidentes o sugerencias a traves del modulo de Administracion o directamente al Lider Tecnico de la CD-TIC-CGR." />
        </div>
      </Seccion>

      <div className="text-center py-4">
        <p className="text-[10px] text-[#5F6368]">
          Guia elaborada conforme a la Circular 023 de 2025 (2025IE0146473) de la CGR
        </p>
      </div>
    </div>
  );
}
