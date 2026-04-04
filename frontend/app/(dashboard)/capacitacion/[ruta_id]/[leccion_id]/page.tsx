'use client';

/**
 * CecilIA v2 — Vista de Leccion con Mini-Chat Tutor
 * Muestra contenido Markdown de la leccion + sidebar con chat tutor
 * Sprint 6
 */

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft, ChevronLeft, ChevronRight, CheckCircle,
  Send, BookOpen, Clock, MessageSquare, Award,
  Loader2, Bot,
} from 'lucide-react';
import { obtenerUsuario } from '@/lib/auth';
import { apiCliente } from '@/lib/api';

// ── Datos demo de lecciones ─────────────────────────────────────────────────
const LECCIONES_DEMO: Record<string, {
  id: string; ruta_id: string; numero: number; titulo: string;
  descripcion: string; contenido_md: string; duracion_minutos: number;
}> = {
  'ruta-001-1': {
    id: 'ruta-001-1', ruta_id: 'ruta-001', numero: 1,
    titulo: 'Que es la Contraloria General de la Republica',
    descripcion: 'Origen, mision y estructura de la CGR',
    duracion_minutos: 20,
    contenido_md: `# Que es la Contraloria General de la Republica

## Origen constitucional

La **Contraloria General de la Republica (CGR)** es el maximo organo de control fiscal del Estado colombiano, establecido por los **articulos 267 y 268** de la Constitucion Politica de 1991.

## Mision

Vigilar y controlar la gestion fiscal del Estado, contribuyendo a la generacion de una cultura de responsabilidad en el manejo de los recursos publicos.

## Estructura organizacional

| Nivel | Dependencia | Funcion |
|-------|-------------|---------|
| Estrategico | Despacho del Contralor | Direccion general |
| Misional | DVF — Direccion de Vigilancia Fiscal | Control fiscal micro (auditorias) |
| Misional | DES — Direccion de Estudios Sectoriales | Control fiscal macro (estudios) |
| Apoyo | CD-TIC-CGR | Tecnologia e innovacion |
| Apoyo | Secretaria General | Gestion administrativa |

## Tipos de control fiscal

1. **Control Fiscal Micro (DVF):** Auditorias individuales a entidades del Estado
2. **Control Fiscal Macro (DES):** Estudios sectoriales, alertas tempranas, analisis transversales
3. **Responsabilidad Fiscal:** Procesos sancionatorios por dano al patrimonio publico
4. **GIA:** Gestoria e Investigacion de Asuntos Especiales

## Datos clave para recordar

- La CGR fue reorganizada por los **Decretos 2037 y 2038 de 2019**
- El Contralor General es elegido por el Congreso para un periodo de 4 anos
- La CGR es autonoma e independiente — no pertenece a ninguna rama del poder publico

---

> **Tip del tutor:** Para la proxima leccion, es util que revises el organigrama completo de la CGR. Lo encontraras en la seccion de documentos institucionales.
`,
  },
};

const RUTAS_NOMBRES: Record<string, string> = {
  'ruta-001': 'Conoce la CGR',
  'ruta-002': 'Auditoria DVF - Paso a paso',
  'ruta-003': 'Estudios Sectoriales DES',
  'ruta-004': 'Normativa Esencial',
};

// ── Componente: Mini-Chat Tutor ─────────────────────────────────────────────
interface MensajeChat {
  rol: 'user' | 'assistant';
  contenido: string;
  timestamp: string;
}

function MiniChatTutor({ leccionTitulo, rutaNombre }: { leccionTitulo: string; rutaNombre: string }) {
  const [mensajes, setMensajes] = useState<MensajeChat[]>([
    {
      rol: 'assistant',
      contenido: `Hola! 👋 Soy CecilIA, tu tutora virtual. Estamos en la leccion **"${leccionTitulo}"** de la ruta **${rutaNombre}**.\n\nPreguntame lo que quieras sobre este tema. Puedo:\n- Explicarte conceptos con ejemplos\n- Hacer mini-quizzes\n- Simular escenarios practicos\n\nQue te gustaria saber?`,
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [cargando, setCargando] = useState(false);
  const refScroll = useRef<HTMLDivElement>(null);

  useEffect(() => {
    refScroll.current?.scrollTo({ top: refScroll.current.scrollHeight, behavior: 'smooth' });
  }, [mensajes]);

  const enviar = async () => {
    if (!input.trim() || cargando) return;
    const texto = input.trim();
    setInput('');

    const nuevoMensaje: MensajeChat = { rol: 'user', contenido: texto, timestamp: new Date().toISOString() };
    setMensajes((prev) => [...prev, nuevoMensaje]);
    setCargando(true);

    try {
      const resp = await apiCliente.post<any>('/chat/mensaje', {
        mensaje: texto,
        modo: 'tutor',
        contexto: { leccion_titulo: leccionTitulo, ruta_nombre: rutaNombre },
      });

      setMensajes((prev) => [
        ...prev,
        {
          rol: 'assistant',
          contenido: resp.respuesta || resp.contenido || 'Excelente pregunta! Lamentablemente no puedo procesar tu consulta en este momento. Intenta nuevamente en unos minutos.',
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch {
      setMensajes((prev) => [
        ...prev,
        {
          rol: 'assistant',
          contenido: '📚 Lo siento, no puedo conectarme al servicio en este momento. Intenta de nuevo en unos minutos. Mientras tanto, revisa el contenido de la leccion!',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0A0F14] border-l border-[#2D3748]/30">
      {/* Header chat */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-[#2D3748]/30">
        <div className="flex h-7 w-7 items-center justify-center rounded-full bg-[#C9A84C]/10 border border-[#C9A84C]/20">
          <Bot className="h-4 w-4 text-[#C9A84C]" />
        </div>
        <div>
          <p className="text-xs font-semibold text-[#C9A84C]">CecilIA Tutor</p>
          <p className="text-[9px] text-[#5F6368]">Modo educativo</p>
        </div>
      </div>

      {/* Mensajes */}
      <div ref={refScroll} className="flex-1 overflow-y-auto p-3 space-y-3">
        {mensajes.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.rol === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-lg px-3 py-2 text-xs ${
                msg.rol === 'user'
                  ? 'bg-[#1A5276]/40 text-[#E8EAED] border border-[#1A5276]/30'
                  : 'bg-[#1A2332]/60 text-[#E8EAED] border border-[#2D3748]/30'
              }`}
            >
              <div className="whitespace-pre-wrap leading-relaxed">{msg.contenido}</div>
            </div>
          </div>
        ))}
        {cargando && (
          <div className="flex justify-start">
            <div className="bg-[#1A2332]/60 border border-[#2D3748]/30 rounded-lg px-3 py-2">
              <Loader2 className="h-4 w-4 text-[#C9A84C] animate-spin" />
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-[#2D3748]/30 p-3">
        <div className="flex items-center gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && enviar()}
            placeholder="Pregunta al tutor..."
            className="flex-1 rounded-lg bg-[#1A2332] border border-[#2D3748]/50 px-3 py-2 text-xs text-[#E8EAED] placeholder-[#5F6368] outline-none focus:border-[#C9A84C]/50"
          />
          <button
            onClick={enviar}
            disabled={!input.trim() || cargando}
            className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#C9A84C]/10 border border-[#C9A84C]/20 text-[#C9A84C] hover:bg-[#C9A84C]/20 disabled:opacity-30 transition-colors"
          >
            <Send className="h-3.5 w-3.5" />
          </button>
        </div>
        <p className="mt-1.5 text-[9px] text-[#5F6368] text-center">
          📚 Respuestas con fines educativos — Datos ficticios — Circular 023 CGR
        </p>
      </div>
    </div>
  );
}

// ── Pagina de Leccion ───────────────────────────────────────────────────────
export default function PaginaLeccion() {
  const params = useParams();
  const router = useRouter();
  const rutaId = params?.ruta_id as string;
  const leccionId = params?.leccion_id as string;
  const usuario = obtenerUsuario();

  const [leccion, setLeccion] = useState<any>(null);
  const [completada, setCompletada] = useState(false);
  const [mostrarChat, setMostrarChat] = useState(true);

  useEffect(() => {
    cargarLeccion();
  }, [leccionId]);

  const cargarLeccion = async () => {
    // Intentar API primero
    try {
      const leccionApi = await apiCliente.get<any>(`/capacitacion/lecciones/${leccionId}`);
      if (leccionApi) {
        setLeccion(leccionApi);
        return;
      }
    } catch {
      // Fallback a demo
    }

    // Usar datos demo
    const demo = LECCIONES_DEMO[leccionId];
    if (demo) {
      setLeccion(demo);
    } else {
      // Leccion generica
      setLeccion({
        id: leccionId,
        ruta_id: rutaId,
        numero: 1,
        titulo: 'Leccion en desarrollo',
        descripcion: 'Esta leccion estara disponible proximamente.',
        contenido_md: '# Leccion en desarrollo\n\nEsta leccion estara disponible proximamente. Mientras tanto, usa el chat tutor para hacer preguntas sobre el tema.',
        duracion_minutos: 15,
      });
    }
  };

  const marcarCompletada = async () => {
    if (!usuario?.id) return;
    try {
      await apiCliente.post('/capacitacion/progreso/completar', {
        usuario_id: usuario.id,
        ruta_id: rutaId,
        leccion_id: leccionId,
      });
    } catch {
      // Marcar localmente
    }
    setCompletada(true);
  };

  const rutaNombre = RUTAS_NOMBRES[rutaId] || rutaId;

  if (!leccion) {
    return (
      <div className="flex items-center justify-center h-full bg-[#0F1419]">
        <Loader2 className="h-8 w-8 text-[#C9A84C] animate-spin" />
      </div>
    );
  }

  return (
    <div className="flex h-full bg-[#0F1419]">
      {/* Panel principal: contenido de la leccion */}
      <div className={`flex flex-col ${mostrarChat ? 'w-[60%]' : 'w-full'} transition-all`}>
        {/* Header leccion */}
        <div className="border-b border-[#2D3748]/30 px-6 py-4">
          <div className="flex items-center gap-2 mb-2">
            <Link
              href="/capacitacion"
              className="flex items-center gap-1 text-[10px] text-[#5F6368] hover:text-[#9AA0A6] transition-colors"
            >
              <ArrowLeft className="h-3 w-3" />
              Volver
            </Link>
            <span className="text-[10px] text-[#2D3748]">/</span>
            <span className="text-[10px] text-[#C9A84C]">{rutaNombre}</span>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-base font-semibold text-[#E8EAED]">
                Leccion {leccion.numero}: {leccion.titulo}
              </h1>
              <div className="flex items-center gap-3 mt-1 text-[10px] text-[#5F6368]">
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {leccion.duracion_minutos} min
                </span>
                {completada && (
                  <span className="flex items-center gap-1 text-green-400">
                    <CheckCircle className="h-3 w-3" />
                    Completada
                  </span>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setMostrarChat(!mostrarChat)}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-[10px] border transition-colors ${
                  mostrarChat
                    ? 'bg-[#C9A84C]/10 border-[#C9A84C]/30 text-[#C9A84C]'
                    : 'bg-[#1A2332] border-[#2D3748]/50 text-[#9AA0A6] hover:text-[#E8EAED]'
                }`}
              >
                <MessageSquare className="h-3 w-3" />
                Tutor IA
              </button>
            </div>
          </div>
        </div>

        {/* Contenido Markdown */}
        <div className="flex-1 overflow-y-auto px-6 py-5">
          <div className="max-w-3xl mx-auto prose prose-invert prose-sm prose-headings:text-[#E8EAED] prose-p:text-[#9AA0A6] prose-strong:text-[#E8EAED] prose-a:text-[#C9A84C] prose-code:text-[#C9A84C] prose-table:text-[#9AA0A6] prose-th:text-[#E8EAED] prose-th:border-[#2D3748] prose-td:border-[#2D3748]">
            {/* Renderizado simple de Markdown */}
            {leccion.contenido_md.split('\n').map((linea: string, i: number) => {
              if (linea.startsWith('# ')) return <h1 key={i} className="text-lg font-bold text-[#C9A84C] mb-4 mt-6">{linea.slice(2)}</h1>;
              if (linea.startsWith('## ')) return <h2 key={i} className="text-base font-semibold text-[#E8EAED] mb-3 mt-5">{linea.slice(3)}</h2>;
              if (linea.startsWith('### ')) return <h3 key={i} className="text-sm font-semibold text-[#E8EAED] mb-2 mt-4">{linea.slice(4)}</h3>;
              if (linea.startsWith('> ')) return <blockquote key={i} className="border-l-2 border-[#C9A84C]/50 pl-3 italic text-xs text-[#C9A84C]/80 my-3">{linea.slice(2)}</blockquote>;
              if (linea.startsWith('---')) return <hr key={i} className="border-[#2D3748]/50 my-4" />;
              if (linea.startsWith('- ') || linea.match(/^\d+\./)) return <li key={i} className="text-xs text-[#9AA0A6] ml-4 mb-1">{linea.replace(/^[-\d.]+\s*/, '')}</li>;
              if (linea.startsWith('|')) return <p key={i} className="text-xs text-[#9AA0A6] font-mono">{linea}</p>;
              if (linea.trim() === '') return <div key={i} className="h-2" />;
              return <p key={i} className="text-xs text-[#9AA0A6] leading-relaxed mb-2">{linea}</p>;
            })}
          </div>

          {/* Acciones al final */}
          <div className="max-w-3xl mx-auto mt-8 space-y-3">
            {!completada && (
              <button
                onClick={marcarCompletada}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-[#27AE60]/10 border border-[#27AE60]/30 px-4 py-3 text-sm font-medium text-[#27AE60] hover:bg-[#27AE60]/20 transition-colors"
              >
                <CheckCircle className="h-4 w-4" />
                Marcar como completada
              </button>
            )}

            {completada && (
              <div className="flex items-center justify-center gap-2 rounded-lg bg-[#27AE60]/10 border border-[#27AE60]/30 px-4 py-3 text-sm text-[#27AE60]">
                <Award className="h-4 w-4" />
                Leccion completada! Excelente trabajo.
              </div>
            )}

            {/* Navegacion prev/next */}
            <div className="flex items-center justify-between pt-4">
              <button
                onClick={() => router.back()}
                className="flex items-center gap-1 text-xs text-[#5F6368] hover:text-[#9AA0A6] transition-colors"
              >
                <ChevronLeft className="h-3 w-3" />
                Anterior
              </button>
              <Link
                href="/capacitacion"
                className="text-xs text-[#C9A84C] hover:text-[#E8D48B] transition-colors"
              >
                Ver todas las rutas
              </Link>
              <button
                onClick={() => {/* navigate to next lesson */}}
                className="flex items-center gap-1 text-xs text-[#5F6368] hover:text-[#9AA0A6] transition-colors"
              >
                Siguiente
                <ChevronRight className="h-3 w-3" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Panel lateral: Mini-Chat Tutor */}
      {mostrarChat && (
        <div className="w-[40%]">
          <MiniChatTutor
            leccionTitulo={leccion.titulo}
            rutaNombre={rutaNombre}
          />
        </div>
      )}
    </div>
  );
}
