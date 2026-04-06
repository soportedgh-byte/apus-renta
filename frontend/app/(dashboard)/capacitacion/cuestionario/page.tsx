'use client';

/**
 * CecilIA v2 — Cuestionario de Estilo de Aprendizaje (VARK)
 * 5 preguntas para determinar estilo predominante: lector/auditivo/visual/kinestesico
 * Sprint: Capacitacion 2.0
 */

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  BookOpen, Headphones, Eye, Hand, ChevronRight,
  CheckCircle, ArrowLeft, Sparkles, Loader2,
} from 'lucide-react';
import { obtenerUsuario } from '@/lib/auth';
import { apiCliente } from '@/lib/api';

const PREGUNTAS = [
  {
    id: 'pregunta_1',
    texto: 'Cuando necesitas aprender un nuevo procedimiento de auditoria, prefieres:',
    opciones: [
      { valor: 'a', texto: 'Leer el manual o la guia escrita paso a paso', icono: BookOpen },
      { valor: 'b', texto: 'Que un colega experimentado te lo explique verbalmente', icono: Headphones },
      { valor: 'c', texto: 'Ver un diagrama de flujo o un video demostrativo', icono: Eye },
      { valor: 'd', texto: 'Practicar directamente con un caso de ejemplo', icono: Hand },
    ],
  },
  {
    id: 'pregunta_2',
    texto: 'Para recordar las normas del control fiscal (Ley 42, Ley 610, etc.) te funciona mejor:',
    opciones: [
      { valor: 'a', texto: 'Subrayar y tomar notas del texto de la ley', icono: BookOpen },
      { valor: 'b', texto: 'Escuchar una explicacion o podcast sobre el tema', icono: Headphones },
      { valor: 'c', texto: 'Crear un mapa mental o tabla comparativa', icono: Eye },
      { valor: 'd', texto: 'Resolver ejercicios aplicando la norma a casos practicos', icono: Hand },
    ],
  },
  {
    id: 'pregunta_3',
    texto: 'Si te piden preparar una presentacion sobre hallazgos de auditoria:',
    opciones: [
      { valor: 'a', texto: 'Escribes un documento detallado y lo lees en la presentacion', icono: BookOpen },
      { valor: 'b', texto: 'Preparas puntos clave y los expones conversacionalmente', icono: Headphones },
      { valor: 'c', texto: 'Creas diapositivas con graficos, tablas y diagramas', icono: Eye },
      { valor: 'd', texto: 'Demuestras con un ejemplo en vivo del sistema', icono: Hand },
    ],
  },
  {
    id: 'pregunta_4',
    texto: 'Cuando te explican como usar CecilIA para generar un formato CGR:',
    opciones: [
      { valor: 'a', texto: 'Pides la documentacion escrita para leerla tranquilamente', icono: BookOpen },
      { valor: 'b', texto: 'Prefieres que te narren los pasos mientras lo haces', icono: Headphones },
      { valor: 'c', texto: 'Necesitas ver una captura de pantalla o video de cada paso', icono: Eye },
      { valor: 'd', texto: 'Abres CecilIA directamente y pruebas haciendo clic', icono: Hand },
    ],
  },
  {
    id: 'pregunta_5',
    texto: 'Para entender que es el "detrimento patrimonial" en una auditoria:',
    opciones: [
      { valor: 'a', texto: 'Lees la definicion de la Ley 610 y tomas notas', icono: BookOpen },
      { valor: 'b', texto: 'Escuchas a Don Carlos explicarlo con una analogia', icono: Headphones },
      { valor: 'c', texto: 'Ves una infografia que muestra el flujo condicion-criterio-causa-efecto', icono: Eye },
      { valor: 'd', texto: 'Analizas un caso real anonimizado y encuentras el detrimento', icono: Hand },
    ],
  },
];

const ESTILOS_INFO: Record<string, { nombre: string; icono: any; color: string; descripcion: string }> = {
  lector: {
    nombre: 'Lector/Escritor',
    icono: BookOpen,
    color: '#C9A84C',
    descripcion: 'Aprendes mejor leyendo textos detallados, tomando notas y revisando documentos escritos. CecilIA te mostrara contenido en formato de lectura enriquecida con citas normativas.',
  },
  auditivo: {
    nombre: 'Auditivo',
    icono: Headphones,
    color: '#2471A3',
    descripcion: 'Aprendes mejor escuchando explicaciones, podcasts y discusiones. CecilIA priorizara los podcasts de Sofia y Don Carlos y explicaciones narrativas.',
  },
  visual: {
    nombre: 'Visual',
    icono: Eye,
    color: '#27AE60',
    descripcion: 'Aprendes mejor con diagramas, tablas, infografias y organizadores visuales. CecilIA te mostrara mas infografias Mermaid y tablas comparativas.',
  },
  kinestesico: {
    nombre: 'Kinestesico',
    icono: Hand,
    color: '#E74C3C',
    descripcion: 'Aprendes mejor haciendo ejercicios practicos, simulaciones y actividades interactivas. CecilIA priorizara simulaciones y ejercicios paso a paso.',
  },
};

export default function PaginaCuestionario() {
  const router = useRouter();
  const usuario = obtenerUsuario();
  const [pasoActual, setPasoActual] = useState(0);
  const [respuestas, setRespuestas] = useState<Record<string, string>>({});
  const [resultado, setResultado] = useState<any>(null);
  const [cargando, setCargando] = useState(false);

  const preguntaActual = PREGUNTAS[pasoActual];
  const totalPreguntas = PREGUNTAS.length;
  const progreso = ((pasoActual) / totalPreguntas) * 100;

  const seleccionarOpcion = async (valor: string) => {
    const nuevasRespuestas = { ...respuestas, [preguntaActual.id]: valor };
    setRespuestas(nuevasRespuestas);

    if (pasoActual < totalPreguntas - 1) {
      setPasoActual(pasoActual + 1);
    } else {
      // Enviar al backend
      setCargando(true);
      try {
        const resp = await apiCliente.post<any>('/capacitacion/perfil-aprendizaje', {
          usuario_id: usuario?.id || 0,
          respuestas: nuevasRespuestas,
        });
        setResultado(resp);
      } catch {
        // Calcular localmente como fallback
        const conteo: Record<string, number> = { lector: 0, auditivo: 0, visual: 0, kinestesico: 0 };
        const mapa: Record<string, string> = { a: 'lector', b: 'auditivo', c: 'visual', d: 'kinestesico' };
        Object.values(nuevasRespuestas).forEach((v) => { conteo[mapa[v] || 'lector']++; });
        const estilo = Object.entries(conteo).sort((a, b) => b[1] - a[1])[0][0];
        setResultado({
          estilo_predominante: estilo,
          puntajes: conteo,
          descripcion: ESTILOS_INFO[estilo]?.descripcion,
        });
      } finally {
        setCargando(false);
      }
    }
  };

  // Pantalla de resultado
  if (resultado) {
    const estilo = ESTILOS_INFO[resultado.estilo_predominante] || ESTILOS_INFO.lector;
    const IconoEstilo = estilo.icono;

    return (
      <div className="flex flex-col h-full bg-[#0F1419] text-[#E8EAED] overflow-y-auto">
        <div className="border-b border-[#2D3748]/30 px-6 py-4">
          <button onClick={() => router.push('/capacitacion')} className="flex items-center gap-1 text-[10px] text-[#5F6368] hover:text-[#9AA0A6]">
            <ArrowLeft className="h-3 w-3" /> Volver a Capacitacion
          </button>
        </div>
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-lg w-full text-center space-y-6">
            <div className="flex justify-center">
              <div className="flex h-20 w-20 items-center justify-center rounded-2xl border-2" style={{ backgroundColor: `${estilo.color}15`, borderColor: `${estilo.color}40` }}>
                <IconoEstilo className="h-10 w-10" style={{ color: estilo.color }} />
              </div>
            </div>
            <div>
              <h1 className="text-2xl font-bold" style={{ color: estilo.color }}>Tu estilo: {estilo.nombre}</h1>
              <p className="mt-3 text-sm text-[#9AA0A6] leading-relaxed">{estilo.descripcion}</p>
            </div>

            {/* Barras de puntaje */}
            <div className="space-y-2 text-left">
              {Object.entries(resultado.puntajes || {}).sort((a: any, b: any) => b[1] - a[1]).map(([key, val]: [string, any]) => {
                const info = ESTILOS_INFO[key];
                const porcentaje = (val / totalPreguntas) * 100;
                return (
                  <div key={key} className="flex items-center gap-3">
                    <span className="text-xs text-[#9AA0A6] w-24">{info?.nombre || key}</span>
                    <div className="flex-1 h-2 rounded-full bg-[#2D3748]/50 overflow-hidden">
                      <div className="h-full rounded-full transition-all duration-700" style={{ width: `${porcentaje}%`, backgroundColor: info?.color }} />
                    </div>
                    <span className="text-xs font-semibold w-8 text-right" style={{ color: info?.color }}>{val}</span>
                  </div>
                );
              })}
            </div>

            <div className="flex gap-3 justify-center pt-4">
              <button
                onClick={() => router.push('/capacitacion')}
                className="flex items-center gap-2 rounded-lg bg-[#C9A84C]/10 border border-[#C9A84C]/30 px-5 py-2.5 text-sm font-medium text-[#C9A84C] hover:bg-[#C9A84C]/20 transition-colors"
              >
                <Sparkles className="h-4 w-4" />
                Comenzar a aprender
              </button>
            </div>

            <p className="text-[10px] text-[#5F6368]">
              Tu contenido se adaptara automaticamente a tu estilo de aprendizaje
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Cuestionario
  return (
    <div className="flex flex-col h-full bg-[#0F1419] text-[#E8EAED] overflow-y-auto">
      <div className="border-b border-[#2D3748]/30 px-6 py-4">
        <div className="flex items-center justify-between">
          <button onClick={() => router.push('/capacitacion')} className="flex items-center gap-1 text-[10px] text-[#5F6368] hover:text-[#9AA0A6]">
            <ArrowLeft className="h-3 w-3" /> Volver
          </button>
          <span className="text-xs text-[#5F6368]">Pregunta {pasoActual + 1} de {totalPreguntas}</span>
        </div>
        <div className="mt-3 h-1.5 rounded-full bg-[#2D3748]/50 overflow-hidden">
          <div className="h-full rounded-full bg-[#C9A84C] transition-all duration-500" style={{ width: `${progreso}%` }} />
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-6">
        {cargando ? (
          <div className="text-center space-y-4">
            <Loader2 className="h-10 w-10 text-[#C9A84C] animate-spin mx-auto" />
            <p className="text-sm text-[#9AA0A6]">Analizando tu estilo de aprendizaje...</p>
          </div>
        ) : (
          <div className="max-w-2xl w-full space-y-6">
            <h2 className="text-lg font-semibold text-center text-[#E8EAED]">{preguntaActual.texto}</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {preguntaActual.opciones.map((op) => {
                const Icono = op.icono;
                const seleccionada = respuestas[preguntaActual.id] === op.valor;
                return (
                  <button
                    key={op.valor}
                    onClick={() => seleccionarOpcion(op.valor)}
                    className={`flex items-start gap-3 rounded-xl border p-4 text-left transition-all hover:bg-[#1A2332]/80 ${
                      seleccionada ? 'border-[#C9A84C]/60 bg-[#C9A84C]/10' : 'border-[#2D3748]/50 bg-[#1A2332]/40'
                    }`}
                  >
                    <Icono className={`h-5 w-5 mt-0.5 flex-shrink-0 ${seleccionada ? 'text-[#C9A84C]' : 'text-[#5F6368]'}`} />
                    <span className="text-xs text-[#E8EAED] leading-relaxed">{op.texto}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-[#2D3748]/30 px-6 py-3 text-center">
        <p className="text-[10px] text-[#5F6368]">
          Cuestionario basado en el modelo VARK — Tu estilo de aprendizaje adaptara el contenido de CecilIA
        </p>
      </div>
    </div>
  );
}
