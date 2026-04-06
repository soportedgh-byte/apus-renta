'use client';

/**
 * CecilIA v2 — Vista de Leccion Premium con Tutor IA Streaming
 * Renderizado Markdown completo, navegacion entre lecciones, mini-chat SSE
 * Sprint: Capacitacion 2.0 — Reestructuracion UX/UI completa
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft, ChevronLeft, ChevronRight, CheckCircle,
  Send, Clock, MessageSquare, Award, Star,
  Loader2, Bot, BookOpen, Sparkles, Eye, EyeOff,
  Zap, Brain, Volume2, Palette,
} from 'lucide-react';
import { obtenerUsuario } from '@/lib/auth';
import { apiCliente } from '@/lib/api';

// ── Tipos locales ───────────────────────────────────────────────────────────

interface LeccionData {
  id: string;
  ruta_id: string;
  numero: number;
  titulo: string;
  descripcion: string;
  contenido_md: string;
  duracion_minutos: number;
  orden?: number;
}

interface LeccionResumen {
  id: string;
  numero: number;
  titulo: string;
  orden?: number;
}

interface MensajeChat {
  rol: 'user' | 'assistant';
  contenido: string;
  timestamp: string;
  streaming?: boolean;
}

// ── Iconos de estilo de aprendizaje ─────────────────────────────────────────

const ESTILOS_INFO: Record<string, { icono: any; nombre: string; color: string }> = {
  lector: { icono: BookOpen, nombre: 'Lector', color: '#2471A3' },
  auditivo: { icono: Volume2, nombre: 'Auditivo', color: '#27AE60' },
  visual: { icono: Palette, nombre: 'Visual', color: '#8E44AD' },
  kinestesico: { icono: Brain, nombre: 'Kinestesico', color: '#E67E22' },
};

// ── Markdown Renderer ───────────────────────────────────────────────────────

function renderizarInline(texto: string): React.ReactNode[] {
  const nodos: React.ReactNode[] = [];
  // Patron para: **bold**, *italic*, `code`, [link](url)
  const regex = /(\*\*(.+?)\*\*)|(\*(.+?)\*)|(`(.+?)`)|(\[(.+?)\]\((.+?)\))/g;
  let ultimoIdx = 0;
  let match: RegExpExecArray | null;
  let key = 0;

  while ((match = regex.exec(texto)) !== null) {
    // Texto antes del match
    if (match.index > ultimoIdx) {
      nodos.push(texto.slice(ultimoIdx, match.index));
    }

    if (match[1]) {
      // **bold**
      nodos.push(<strong key={key++} className="text-[#E8EAED] font-semibold">{match[2]}</strong>);
    } else if (match[3]) {
      // *italic*
      nodos.push(<em key={key++} className="text-[#C9A84C]/90 italic">{match[4]}</em>);
    } else if (match[5]) {
      // `code`
      nodos.push(
        <code key={key++} className="rounded bg-[#C9A84C]/10 border border-[#C9A84C]/20 px-1.5 py-0.5 text-[10px] font-mono text-[#C9A84C]">
          {match[6]}
        </code>
      );
    } else if (match[7]) {
      // [link](url)
      nodos.push(
        <a key={key++} href={match[9]} target="_blank" rel="noopener noreferrer"
          className="text-[#C9A84C] underline underline-offset-2 decoration-[#C9A84C]/40 hover:decoration-[#C9A84C] transition-colors">
          {match[8]}
        </a>
      );
    }
    ultimoIdx = match.index + match[0].length;
  }

  if (ultimoIdx < texto.length) {
    nodos.push(texto.slice(ultimoIdx));
  }

  return nodos.length > 0 ? nodos : [texto];
}

function MarkdownTabla({ lineas }: { lineas: string[] }) {
  if (lineas.length < 2) return null;

  const parsearFila = (linea: string) =>
    linea.split('|').map((c) => c.trim()).filter((c) => c.length > 0);

  const encabezados = parsearFila(lineas[0]);
  // Saltar linea separadora (|---|---|)
  const filas = lineas.slice(2).map(parsearFila);

  return (
    <div className="my-4 overflow-x-auto rounded-xl border border-[#2D3748]/40">
      <table className="w-full text-xs">
        <thead>
          <tr className="bg-[#C9A84C]/8 border-b border-[#2D3748]/40">
            {encabezados.map((h, i) => (
              <th key={i} className="px-4 py-2.5 text-left font-semibold text-[#C9A84C] text-[11px]">
                {renderizarInline(h)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filas.map((fila, i) => (
            <tr key={i} className={`border-b border-[#2D3748]/20 ${i % 2 === 0 ? 'bg-[#1A2332]/30' : 'bg-[#0F1419]/50'} hover:bg-[#C9A84C]/5 transition-colors`}>
              {fila.map((celda, j) => (
                <td key={j} className="px-4 py-2.5 text-[#9AA0A6]">
                  {renderizarInline(celda)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ContenidoMarkdown({ md }: { md: string }) {
  const lineas = md.split('\n');
  const bloques: React.ReactNode[] = [];
  let i = 0;
  let key = 0;

  while (i < lineas.length) {
    const linea = lineas[i];

    // Tabla: multiples lineas que empiezan con |
    if (linea.startsWith('|')) {
      const lineasTabla: string[] = [];
      while (i < lineas.length && lineas[i].startsWith('|')) {
        lineasTabla.push(lineas[i]);
        i++;
      }
      bloques.push(<MarkdownTabla key={key++} lineas={lineasTabla} />);
      continue;
    }

    // Headers
    if (linea.startsWith('# ')) {
      bloques.push(
        <h1 key={key++} className="text-xl font-bold text-[#C9A84C] mb-4 mt-8 first:mt-0 pb-2 border-b border-[#C9A84C]/20">
          {renderizarInline(linea.slice(2))}
        </h1>
      );
      i++; continue;
    }
    if (linea.startsWith('## ')) {
      bloques.push(
        <h2 key={key++} className="text-base font-bold text-[#E8EAED] mb-3 mt-6 flex items-center gap-2">
          <div className="h-1 w-1 rounded-full bg-[#C9A84C]" />
          {renderizarInline(linea.slice(3))}
        </h2>
      );
      i++; continue;
    }
    if (linea.startsWith('### ')) {
      bloques.push(
        <h3 key={key++} className="text-sm font-semibold text-[#E8EAED] mb-2 mt-5">
          {renderizarInline(linea.slice(4))}
        </h3>
      );
      i++; continue;
    }

    // Blockquote
    if (linea.startsWith('> ')) {
      bloques.push(
        <blockquote key={key++} className="my-4 rounded-r-lg border-l-3 border-[#C9A84C] bg-[#C9A84C]/5 px-4 py-3 text-xs text-[#C9A84C]/90 italic leading-relaxed">
          <div className="flex items-start gap-2">
            <Sparkles className="h-3.5 w-3.5 text-[#C9A84C] mt-0.5 shrink-0" />
            <span>{renderizarInline(linea.slice(2))}</span>
          </div>
        </blockquote>
      );
      i++; continue;
    }

    // Horizontal rule
    if (linea.trim() === '---' || linea.trim() === '***') {
      bloques.push(
        <div key={key++} className="my-6 flex items-center gap-3">
          <div className="flex-1 h-px bg-gradient-to-r from-transparent via-[#C9A84C]/30 to-transparent" />
          <Star className="h-3 w-3 text-[#C9A84C]/30" />
          <div className="flex-1 h-px bg-gradient-to-r from-transparent via-[#C9A84C]/30 to-transparent" />
        </div>
      );
      i++; continue;
    }

    // Unordered list items
    if (linea.startsWith('- ') || linea.startsWith('* ')) {
      const items: string[] = [];
      while (i < lineas.length && (lineas[i].startsWith('- ') || lineas[i].startsWith('* '))) {
        items.push(lineas[i].slice(2));
        i++;
      }
      bloques.push(
        <ul key={key++} className="my-3 space-y-1.5 ml-1">
          {items.map((item, idx) => (
            <li key={idx} className="flex items-start gap-2.5 text-xs text-[#9AA0A6] leading-relaxed">
              <div className="mt-1.5 h-1.5 w-1.5 rounded-full bg-[#C9A84C]/60 shrink-0" />
              <span>{renderizarInline(item)}</span>
            </li>
          ))}
        </ul>
      );
      continue;
    }

    // Ordered list
    if (/^\d+\.\s/.test(linea)) {
      const items: string[] = [];
      while (i < lineas.length && /^\d+\.\s/.test(lineas[i])) {
        items.push(lineas[i].replace(/^\d+\.\s*/, ''));
        i++;
      }
      bloques.push(
        <ol key={key++} className="my-3 space-y-1.5 ml-1">
          {items.map((item, idx) => (
            <li key={idx} className="flex items-start gap-2.5 text-xs text-[#9AA0A6] leading-relaxed">
              <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[#C9A84C]/10 border border-[#C9A84C]/20 text-[9px] font-bold text-[#C9A84C]">
                {idx + 1}
              </span>
              <span>{renderizarInline(item)}</span>
            </li>
          ))}
        </ol>
      );
      continue;
    }

    // Empty line
    if (linea.trim() === '') {
      bloques.push(<div key={key++} className="h-2" />);
      i++; continue;
    }

    // Paragraph
    bloques.push(
      <p key={key++} className="text-[13px] text-[#9AA0A6] leading-[1.8] mb-2">
        {renderizarInline(linea)}
      </p>
    );
    i++;
  }

  return <>{bloques}</>;
}

// ── Mini-Chat Tutor con SSE Streaming ───────────────────────────────────────

function MiniChatTutor({ leccionTitulo, rutaNombre }: { leccionTitulo: string; rutaNombre: string }) {
  const [mensajes, setMensajes] = useState<MensajeChat[]>([
    {
      rol: 'assistant',
      contenido: `Hola! Soy CecilIA, tu tutora virtual. Estamos en la leccion "${leccionTitulo}" de la ruta ${rutaNombre}.\n\nPreguntame lo que quieras sobre este tema. Puedo explicarte conceptos, hacer mini-quizzes o simular escenarios practicos.`,
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [cargando, setCargando] = useState(false);
  const refScroll = useRef<HTMLDivElement>(null);
  const cancelarRef = useRef<(() => void) | null>(null);

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

    // Agregar mensaje placeholder para streaming
    const idxRespuesta = mensajes.length + 1;
    setMensajes((prev) => [...prev, {
      rol: 'assistant',
      contenido: '',
      timestamp: new Date().toISOString(),
      streaming: true,
    }]);

    const token = typeof window !== 'undefined' ? localStorage.getItem('cecilia_token') : null;
    const urlBase = process.env.NEXT_PUBLIC_API_URL || '/api';

    // Prefijar contexto de leccion al mensaje
    const mensajeConContexto = `[Contexto: soy un aprendiz en la leccion "${leccionTitulo}" de la ruta "${rutaNombre}". Actua como tutor educativo experto en control fiscal colombiano. Responde de forma clara y pedagogica.]\n\n${texto}`;

    try {
      const respuesta = await fetch(`${urlBase}/chat/enviar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ mensaje: mensajeConContexto }),
      });

      if (!respuesta.ok) {
        throw new Error(`Error ${respuesta.status}`);
      }

      const lector = respuesta.body?.getReader();
      if (!lector) throw new Error('No se pudo iniciar streaming');

      const decodificador = new TextDecoder();
      let buffer = '';
      let contenidoAcumulado = '';

      while (true) {
        const { done, value } = await lector.read();
        if (done) break;

        buffer += decodificador.decode(value, { stream: true });
        const lineas = buffer.split('\n');
        buffer = lineas.pop() || '';

        for (const linea of lineas) {
          if (linea.startsWith('data: ')) {
            const datos = linea.slice(6).trim();
            if (datos === '[DONE]') break;

            try {
              const evento = JSON.parse(datos);
              if (evento.tipo === 'token' && evento.contenido) {
                contenidoAcumulado += evento.contenido;
                setMensajes((prev) => {
                  const copia = [...prev];
                  const ultimo = copia[copia.length - 1];
                  if (ultimo && ultimo.rol === 'assistant' && ultimo.streaming) {
                    copia[copia.length - 1] = { ...ultimo, contenido: contenidoAcumulado };
                  }
                  return copia;
                });
              } else if (evento.tipo === 'fin') {
                if (evento.respuesta_completa) {
                  contenidoAcumulado = evento.respuesta_completa;
                }
              }
            } catch {
              // Ignorar datos no-JSON
            }
          }
        }
      }

      // Finalizar streaming
      setMensajes((prev) => {
        const copia = [...prev];
        const ultimo = copia[copia.length - 1];
        if (ultimo && ultimo.rol === 'assistant') {
          copia[copia.length - 1] = {
            ...ultimo,
            contenido: contenidoAcumulado || 'No se pudo obtener una respuesta. Intenta de nuevo.',
            streaming: false,
          };
        }
        return copia;
      });
    } catch {
      setMensajes((prev) => {
        const copia = [...prev];
        const ultimo = copia[copia.length - 1];
        if (ultimo && ultimo.rol === 'assistant' && ultimo.streaming) {
          copia[copia.length - 1] = {
            ...ultimo,
            contenido: 'No puedo conectarme al servicio en este momento. Intenta de nuevo en unos minutos.',
            streaming: false,
          };
        }
        return copia;
      });
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0A0F14] border-l border-[#2D3748]/30">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-[#2D3748]/30 bg-gradient-to-r from-[#C9A84C]/5 to-transparent">
        <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-[#C9A84C]/20 to-[#C9A84C]/5 border border-[#C9A84C]/20 shadow-lg shadow-[#C9A84C]/5">
          <Bot className="h-4 w-4 text-[#C9A84C]" />
        </div>
        <div>
          <p className="text-xs font-bold text-[#C9A84C]">CecilIA Tutor</p>
          <p className="text-[9px] text-[#5F6368]">Modo educativo en tiempo real</p>
        </div>
        <div className="ml-auto flex h-2 w-2 rounded-full bg-[#27AE60] shadow-lg shadow-[#27AE60]/50 animate-pulse" />
      </div>

      {/* Mensajes */}
      <div ref={refScroll} className="flex-1 overflow-y-auto p-3 space-y-3">
        {mensajes.map((msg, i) => (
          <div key={i} className={`flex ${msg.rol === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[88%] rounded-xl px-3.5 py-2.5 text-xs leading-relaxed ${
              msg.rol === 'user'
                ? 'bg-gradient-to-br from-[#1A5276]/50 to-[#1A5276]/30 text-[#E8EAED] border border-[#1A5276]/30 rounded-br-sm'
                : 'bg-gradient-to-br from-[#1A2332]/80 to-[#1A2332]/50 text-[#E8EAED] border border-[#2D3748]/30 rounded-bl-sm'
            }`}>
              <div className="whitespace-pre-wrap">{msg.contenido}</div>
              {msg.streaming && (
                <span className="inline-block w-1.5 h-4 bg-[#C9A84C] ml-0.5 animate-pulse rounded-sm" />
              )}
            </div>
          </div>
        ))}
        {cargando && mensajes[mensajes.length - 1]?.contenido === '' && (
          <div className="flex justify-start">
            <div className="bg-[#1A2332]/60 border border-[#2D3748]/30 rounded-xl px-4 py-3">
              <div className="flex items-center gap-1.5">
                <div className="h-1.5 w-1.5 rounded-full bg-[#C9A84C] animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="h-1.5 w-1.5 rounded-full bg-[#C9A84C] animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="h-1.5 w-1.5 rounded-full bg-[#C9A84C] animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-[#2D3748]/30 p-3 bg-[#0A0F14]">
        <div className="flex items-center gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && enviar()}
            placeholder="Pregunta al tutor..."
            className="flex-1 rounded-xl bg-[#1A2332] border border-[#2D3748]/50 px-4 py-2.5 text-xs text-[#E8EAED] placeholder-[#5F6368] outline-none focus:border-[#C9A84C]/40 focus:ring-1 focus:ring-[#C9A84C]/20 transition-all"
          />
          <button
            onClick={enviar}
            disabled={!input.trim() || cargando}
            className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-[#C9A84C]/20 to-[#C9A84C]/10 border border-[#C9A84C]/20 text-[#C9A84C] hover:from-[#C9A84C]/30 hover:to-[#C9A84C]/15 disabled:opacity-30 transition-all"
          >
            <Send className="h-3.5 w-3.5" />
          </button>
        </div>
        <p className="mt-2 text-[9px] text-[#5F6368] text-center">
          Asistido por IA — Requiere validacion humana — Circular 023 CGR
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

  const [leccion, setLeccion] = useState<LeccionData | null>(null);
  const [lecciones, setLecciones] = useState<LeccionResumen[]>([]);
  const [rutaNombre, setRutaNombre] = useState('');
  const [estiloUsuario, setEstiloUsuario] = useState<string | null>(null);
  const [completada, setCompletada] = useState(false);
  const [mostrarChat, setMostrarChat] = useState(true);
  const [cargando, setCargando] = useState(true);
  const [xpGanada, setXpGanada] = useState(false);

  useEffect(() => {
    cargarDatos();
  }, [leccionId, rutaId]);

  const cargarDatos = async () => {
    setCargando(true);
    setCompletada(false);
    setXpGanada(false);

    try {
      // Cargar en paralelo: leccion adaptativa, lista de lecciones, info ruta
      const promesas: Promise<any>[] = [];

      // 1. Leccion con contenido adaptativo
      if (usuario?.id) {
        promesas.push(
          apiCliente.get<any>(`/capacitacion/lecciones/${leccionId}/contenido-adaptativo?usuario_id=${usuario.id}`)
            .catch(() => apiCliente.get<any>(`/capacitacion/lecciones/${leccionId}`))
            .catch(() => null)
        );
      } else {
        promesas.push(
          apiCliente.get<any>(`/capacitacion/lecciones/${leccionId}`)
            .catch(() => null)
        );
      }

      // 2. Lista de lecciones de la ruta
      promesas.push(
        apiCliente.get<any>(`/capacitacion/rutas/${rutaId}/lecciones`).catch(() => [])
      );

      // 3. Info de la ruta
      promesas.push(
        apiCliente.get<any>(`/capacitacion/rutas/${rutaId}`).catch(() => null)
      );

      const [leccionData, leccionesData, rutaData] = await Promise.all(promesas);

      if (leccionData) {
        setLeccion(leccionData);
        if (leccionData.estilo_usuario) {
          setEstiloUsuario(leccionData.estilo_usuario);
        }
      }

      if (Array.isArray(leccionesData)) {
        const lista = leccionesData.map((l: any) => ({
          id: l.id,
          numero: l.numero,
          titulo: l.titulo,
          orden: l.orden,
        }));
        lista.sort((a: LeccionResumen, b: LeccionResumen) => (a.orden ?? a.numero) - (b.orden ?? b.numero));
        setLecciones(lista);
      }

      if (rutaData?.nombre) {
        setRutaNombre(rutaData.nombre);
      }
    } catch {
      // Estado de error manejado por leccion === null
    } finally {
      setCargando(false);
    }
  };

  const idxActual = lecciones.findIndex((l) => l.id === leccionId);
  const leccionAnterior = idxActual > 0 ? lecciones[idxActual - 1] : null;
  const leccionSiguiente = idxActual >= 0 && idxActual < lecciones.length - 1 ? lecciones[idxActual + 1] : null;

  const navegarLeccion = (leccion: LeccionResumen) => {
    router.push(`/capacitacion/${rutaId}/${leccion.id}`);
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
      // Marcar localmente igualmente
    }
    setCompletada(true);

    // Otorgar XP
    if (!xpGanada) {
      try {
        await apiCliente.post('/capacitacion/gamificacion/xp', {
          usuario_id: usuario.id,
          puntos: 100,
          motivo: `Leccion completada: ${leccion?.titulo || leccionId}`,
        });
        setXpGanada(true);
      } catch {
        // XP no critico
      }
    }
  };

  // ── Estado de carga ─────────────────────────────────────────────────────

  if (cargando) {
    return (
      <div className="flex items-center justify-center h-full bg-[#0F1419]">
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-[#C9A84C]/20 to-[#C9A84C]/5 border border-[#C9A84C]/20 flex items-center justify-center">
              <Loader2 className="h-6 w-6 text-[#C9A84C] animate-spin" />
            </div>
            <div className="absolute -inset-2 rounded-3xl bg-[#C9A84C]/5 animate-pulse" />
          </div>
          <p className="text-xs text-[#5F6368]">Cargando leccion...</p>
        </div>
      </div>
    );
  }

  // ── Estado de error ─────────────────────────────────────────────────────

  if (!leccion) {
    return (
      <div className="flex items-center justify-center h-full bg-[#0F1419]">
        <div className="flex flex-col items-center gap-4 text-center max-w-sm">
          <div className="h-12 w-12 rounded-2xl bg-[#E74C3C]/10 border border-[#E74C3C]/20 flex items-center justify-center">
            <BookOpen className="h-6 w-6 text-[#E74C3C]" />
          </div>
          <h2 className="text-sm font-semibold text-[#E8EAED]">Leccion no disponible</h2>
          <p className="text-xs text-[#5F6368]">No se pudo cargar el contenido de esta leccion. Verifica que la leccion existe e intenta nuevamente.</p>
          <Link
            href="/capacitacion"
            className="flex items-center gap-2 rounded-xl bg-[#C9A84C]/10 border border-[#C9A84C]/20 px-4 py-2.5 text-xs font-medium text-[#C9A84C] hover:bg-[#C9A84C]/20 transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Volver a capacitacion
          </Link>
        </div>
      </div>
    );
  }

  // ── Render principal ────────────────────────────────────────────────────

  const totalLecciones = lecciones.length;
  const progreso = totalLecciones > 0 ? ((idxActual + 1) / totalLecciones) * 100 : 0;
  const estiloInfo = estiloUsuario ? ESTILOS_INFO[estiloUsuario] : null;

  return (
    <div className="flex h-full bg-[#0F1419]">
      {/* Panel principal: contenido de la leccion */}
      <div className={`flex flex-col ${mostrarChat ? 'w-[62%]' : 'w-full'} transition-all duration-300`}>
        {/* Header */}
        <div className="border-b border-[#2D3748]/30 px-6 py-4 bg-gradient-to-r from-[#0F1419] to-[#1A2332]/30">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 mb-3">
            <Link
              href="/capacitacion"
              className="flex items-center gap-1.5 text-[10px] text-[#5F6368] hover:text-[#C9A84C] transition-colors"
            >
              <ArrowLeft className="h-3 w-3" />
              Capacitacion
            </Link>
            <ChevronRight className="h-2.5 w-2.5 text-[#2D3748]" />
            <span className="text-[10px] text-[#C9A84C] font-medium">{rutaNombre || 'Ruta'}</span>
          </div>

          {/* Titulo y meta */}
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-lg font-bold text-[#E8EAED] leading-tight">
                {leccion.numero && <span className="text-[#C9A84C] mr-1">{leccion.numero}.</span>}
                {leccion.titulo}
              </h1>
              <div className="flex items-center gap-4 mt-2">
                <span className="flex items-center gap-1.5 text-[10px] text-[#5F6368]">
                  <Clock className="h-3 w-3" />
                  {leccion.duracion_minutos} min
                </span>
                {totalLecciones > 0 && (
                  <span className="text-[10px] text-[#5F6368]">
                    {idxActual + 1} de {totalLecciones} lecciones
                  </span>
                )}
                {estiloInfo && (
                  <span className="flex items-center gap-1.5 text-[10px] font-medium rounded-full px-2.5 py-0.5 border"
                    style={{ color: estiloInfo.color, borderColor: `${estiloInfo.color}30`, backgroundColor: `${estiloInfo.color}08` }}>
                    {React.createElement(estiloInfo.icono, { className: 'h-3 w-3' })}
                    Adaptado: {estiloInfo.nombre}
                  </span>
                )}
                {completada && (
                  <span className="flex items-center gap-1 text-[10px] font-medium text-[#27AE60]">
                    <CheckCircle className="h-3 w-3" />
                    Completada
                  </span>
                )}
              </div>
            </div>

            <button
              onClick={() => setMostrarChat(!mostrarChat)}
              className={`flex items-center gap-1.5 rounded-xl px-3.5 py-2 text-[10px] font-medium border transition-all ${
                mostrarChat
                  ? 'bg-gradient-to-br from-[#C9A84C]/15 to-[#C9A84C]/5 border-[#C9A84C]/30 text-[#C9A84C] shadow-lg shadow-[#C9A84C]/5'
                  : 'bg-[#1A2332] border-[#2D3748]/50 text-[#9AA0A6] hover:text-[#E8EAED] hover:border-[#C9A84C]/30'
              }`}
            >
              <MessageSquare className="h-3 w-3" />
              {mostrarChat ? 'Ocultar' : 'Tutor IA'}
            </button>
          </div>

          {/* Barra de progreso */}
          {totalLecciones > 0 && (
            <div className="mt-3 flex items-center gap-3">
              <div className="flex-1 h-1 rounded-full bg-[#2D3748]/30 overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-[#C9A84C] to-[#E8D48B] transition-all duration-500"
                  style={{ width: `${progreso}%` }}
                />
              </div>
              <span className="text-[9px] text-[#5F6368] font-medium tabular-nums">{Math.round(progreso)}%</span>
            </div>
          )}
        </div>

        {/* Contenido Markdown */}
        <div className="flex-1 overflow-y-auto px-6 py-6">
          <div className="max-w-3xl mx-auto">
            <ContenidoMarkdown md={leccion.contenido_md || ''} />

            {/* Acciones al final */}
            <div className="mt-10 space-y-4">
              {/* Marcar completada / XP */}
              {!completada ? (
                <button
                  onClick={marcarCompletada}
                  className="group flex w-full items-center justify-center gap-2.5 rounded-xl bg-gradient-to-r from-[#27AE60]/10 to-[#27AE60]/5 border border-[#27AE60]/30 px-5 py-3.5 text-sm font-semibold text-[#27AE60] hover:from-[#27AE60]/20 hover:to-[#27AE60]/10 hover:shadow-lg hover:shadow-[#27AE60]/10 transition-all"
                >
                  <CheckCircle className="h-4.5 w-4.5 group-hover:scale-110 transition-transform" />
                  Marcar como completada
                </button>
              ) : (
                <div className="flex flex-col items-center gap-3 rounded-xl bg-gradient-to-r from-[#27AE60]/10 to-[#C9A84C]/5 border border-[#27AE60]/30 px-5 py-4">
                  <div className="flex items-center gap-2 text-sm font-semibold text-[#27AE60]">
                    <Award className="h-5 w-5" />
                    Leccion completada!
                  </div>
                  {xpGanada && (
                    <div className="flex items-center gap-1.5 rounded-full bg-[#C9A84C]/10 border border-[#C9A84C]/20 px-3 py-1">
                      <Zap className="h-3 w-3 text-[#C9A84C]" />
                      <span className="text-[10px] font-bold text-[#C9A84C]">+100 XP</span>
                    </div>
                  )}
                </div>
              )}

              {/* Navegacion prev/next */}
              <div className="flex items-center justify-between pt-2">
                {leccionAnterior ? (
                  <button
                    onClick={() => navegarLeccion(leccionAnterior)}
                    className="group flex items-center gap-2 rounded-xl bg-[#1A2332]/60 border border-[#2D3748]/40 px-4 py-3 hover:border-[#C9A84C]/30 hover:bg-[#1A2332] transition-all max-w-[45%]"
                  >
                    <ChevronLeft className="h-4 w-4 text-[#5F6368] group-hover:text-[#C9A84C] transition-colors shrink-0" />
                    <div className="text-left min-w-0">
                      <p className="text-[9px] text-[#5F6368] group-hover:text-[#9AA0A6]">Anterior</p>
                      <p className="text-[11px] text-[#9AA0A6] group-hover:text-[#E8EAED] truncate transition-colors">
                        {leccionAnterior.titulo}
                      </p>
                    </div>
                  </button>
                ) : (
                  <div />
                )}

                <Link
                  href="/capacitacion"
                  className="text-[10px] text-[#5F6368] hover:text-[#C9A84C] transition-colors shrink-0 px-2"
                >
                  Ver todas las rutas
                </Link>

                {leccionSiguiente ? (
                  <button
                    onClick={() => navegarLeccion(leccionSiguiente)}
                    className="group flex items-center gap-2 rounded-xl bg-gradient-to-r from-[#C9A84C]/8 to-[#C9A84C]/3 border border-[#C9A84C]/20 px-4 py-3 hover:from-[#C9A84C]/15 hover:to-[#C9A84C]/8 hover:shadow-lg hover:shadow-[#C9A84C]/5 transition-all max-w-[45%]"
                  >
                    <div className="text-right min-w-0">
                      <p className="text-[9px] text-[#C9A84C]/70">Siguiente</p>
                      <p className="text-[11px] text-[#C9A84C] truncate">
                        {leccionSiguiente.titulo}
                      </p>
                    </div>
                    <ChevronRight className="h-4 w-4 text-[#C9A84C] shrink-0" />
                  </button>
                ) : (
                  <div />
                )}
              </div>

              {/* Disclaimer Circular 023 */}
              <div className="mt-4 rounded-lg border border-[#C9A84C]/15 bg-[#C9A84C]/3 p-3 text-center">
                <p className="text-[9px] text-[#C9A84C]/60">
                  Contenido asistido por IA — Requiere validacion humana — Circular 023 CGR
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Panel lateral: Mini-Chat Tutor */}
      {mostrarChat && (
        <div className="w-[38%] border-l border-[#2D3748]/30">
          <MiniChatTutor
            leccionTitulo={leccion.titulo}
            rutaNombre={rutaNombre || 'Ruta de aprendizaje'}
          />
        </div>
      )}
    </div>
  );
}
