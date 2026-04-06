'use client';

/**
 * CecilIA v2 — Biblioteca de Recursos Generados (Premium)
 * Podcasts con audio real, flashcards interactivas,
 * infografias renderizadas, manuales DOCX con logos CGR
 * Sprint: Capacitacion 2.0 — Reestructuracion UX/UI
 */

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft, Headphones, BookOpen, Image, FileText,
  Loader2, Download, Sparkles, Layers, ChevronLeft,
  ChevronRight, RotateCcw, Volume2, Eye,
} from 'lucide-react';
import { apiCliente } from '@/lib/api';

type Tab = 'podcast' | 'flashcards' | 'infografia' | 'manual';

const TABS: Array<{ id: Tab; nombre: string; icono: any; color: string; desc: string }> = [
  { id: 'podcast', nombre: 'Podcast', icono: Headphones, color: '#2471A3', desc: 'Audio educativo con 2 voces colombianas' },
  { id: 'flashcards', nombre: 'Flashcards', icono: Layers, color: '#27AE60', desc: 'Tarjetas con taxonomia de Bloom' },
  { id: 'infografia', nombre: 'Infografia', icono: Image, color: '#8E44AD', desc: 'Diagramas visuales renderizados' },
  { id: 'manual', nombre: 'Manual', icono: FileText, color: '#C9A84C', desc: 'Documento DOCX con logos CGR' },
];

const TEMAS_SUGERIDOS = [
  'Control fiscal en Colombia',
  'Hallazgos de auditoria',
  'Proceso de responsabilidad fiscal',
  'Materialidad en auditorias',
  'Circular 023 CGR sobre IA',
  'Fases del proceso auditor',
  'Contratacion publica y SECOP',
  'Detrimento patrimonial',
];

export default function PaginaBiblioteca() {
  const router = useRouter();
  const [tabActiva, setTabActiva] = useState<Tab>('podcast');
  const [tema, setTema] = useState('');
  const [resultado, setResultado] = useState<any>(null);
  const [cargando, setCargando] = useState(false);
  const [flashcardIdx, setFlashcardIdx] = useState(0);
  const [flashcardVolteada, setFlashcardVolteada] = useState(false);

  const generar = async () => {
    if (!tema.trim()) return;
    setCargando(true);
    setResultado(null);
    setFlashcardIdx(0);
    setFlashcardVolteada(false);

    try {
      let resp: any;
      switch (tabActiva) {
        case 'podcast':
          resp = await apiCliente.post<any>('/capacitacion/generar-audio', { tema, duracion: '5 minutos' });
          break;
        case 'flashcards':
          resp = await apiCliente.post<any>('/capacitacion/generar-flashcards', { tema, num_tarjetas: 10 });
          break;
        case 'infografia':
          resp = await apiCliente.post<any>('/capacitacion/generar-infografia', { tema, tipo_diagrama: 'flowchart' });
          break;
        case 'manual':
          resp = await apiCliente.post<any>('/capacitacion/generar-manual', { tema, nivel: 'basico' });
          break;
      }
      setResultado(resp);
    } catch (error) {
      setResultado({ error: 'No se pudo generar el recurso. Intenta nuevamente.' });
    } finally {
      setCargando(false);
    }
  };

  const descargarDocx = (base64: string, nombre: string) => {
    const byteChars = atob(base64);
    const byteNumbers = new Array(byteChars.length);
    for (let i = 0; i < byteChars.length; i++) byteNumbers[i] = byteChars.charCodeAt(i);
    const blob = new Blob([new Uint8Array(byteNumbers)], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = nombre; a.click();
    URL.revokeObjectURL(url);
  };

  const tabInfo = TABS.find((t) => t.id === tabActiva)!;

  return (
    <div className="flex flex-col h-full bg-[#0F1419] text-[#E8EAED] overflow-y-auto">
      {/* Header */}
      <div className="border-b border-[#2D3748]/30 px-6 py-4 bg-gradient-to-r from-[#0F1419] to-[#1A2332]/30">
        <div className="flex items-center gap-3 mb-4">
          <button onClick={() => router.push('/capacitacion')} className="flex items-center gap-1 text-[10px] text-[#5F6368] hover:text-[#C9A84C] transition-colors">
            <ArrowLeft className="h-3 w-3" />
          </button>
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#8E44AD]/20 to-[#8E44AD]/5 border border-[#8E44AD]/20 shadow-lg shadow-[#8E44AD]/5">
            <Sparkles className="h-5 w-5 text-[#8E44AD]" />
          </div>
          <div>
            <h1 className="text-base font-bold text-[#E8EAED]">Biblioteca de Recursos</h1>
            <p className="text-[10px] text-[#5F6368]">Genera contenido educativo con IA sobre cualquier tema fiscal</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="grid grid-cols-4 gap-2">
          {TABS.map((tab) => {
            const Icono = tab.icono;
            const activa = tabActiva === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => { setTabActiva(tab.id); setResultado(null); }}
                className={`flex flex-col items-center gap-1.5 rounded-xl px-3 py-3 text-[10px] font-medium transition-all ${
                  activa
                    ? 'border shadow-lg scale-[1.02]'
                    : 'border border-[#2D3748]/30 text-[#5F6368] hover:text-[#9AA0A6] hover:border-[#2D3748]/50'
                }`}
                style={activa ? {
                  backgroundColor: `${tab.color}12`,
                  borderColor: `${tab.color}40`,
                  color: tab.color,
                  boxShadow: `0 4px 15px ${tab.color}15`,
                } : {}}
              >
                <Icono className="h-4 w-4" />
                <span className="font-semibold">{tab.nombre}</span>
                <span className={`text-[8px] ${activa ? 'opacity-70' : 'opacity-0'} transition-opacity`}>
                  {tab.desc}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="flex-1 p-6 space-y-5">
        {/* Input tema */}
        <div>
          <label className="text-xs font-medium text-[#9AA0A6] mb-2 block">Tema para generar</label>
          <div className="flex gap-2">
            <input
              value={tema}
              onChange={(e) => setTema(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && generar()}
              placeholder="Ej: Proceso de responsabilidad fiscal"
              className="flex-1 rounded-xl bg-[#1A2332] border border-[#2D3748]/50 px-4 py-3 text-xs text-[#E8EAED] placeholder-[#5F6368] outline-none focus:border-[#C9A84C]/50 focus:ring-1 focus:ring-[#C9A84C]/20 transition-all"
            />
            <button
              onClick={generar}
              disabled={!tema.trim() || cargando}
              className="flex items-center gap-2 rounded-xl px-5 py-3 text-xs font-semibold transition-all disabled:opacity-30 hover:scale-[1.02] hover:shadow-lg"
              style={{
                backgroundColor: `${tabInfo.color}15`,
                border: `1px solid ${tabInfo.color}40`,
                color: tabInfo.color,
                boxShadow: `0 2px 10px ${tabInfo.color}10`,
              }}
            >
              {cargando ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
              {cargando ? 'Generando...' : 'Generar'}
            </button>
          </div>

          {/* Temas sugeridos */}
          <div className="flex flex-wrap gap-1.5 mt-3">
            {TEMAS_SUGERIDOS.map((t) => (
              <button
                key={t}
                onClick={() => setTema(t)}
                className="rounded-full bg-[#2D3748]/20 border border-[#2D3748]/30 px-3 py-1.5 text-[9px] text-[#5F6368] hover:text-[#C9A84C] hover:border-[#C9A84C]/30 hover:bg-[#C9A84C]/5 transition-all"
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Loading state */}
        {cargando && (
          <div className="flex flex-col items-center justify-center py-16 gap-4">
            <div className="relative">
              <div className="h-16 w-16 rounded-2xl flex items-center justify-center border"
                style={{ backgroundColor: `${tabInfo.color}10`, borderColor: `${tabInfo.color}30` }}>
                <Loader2 className="h-8 w-8 animate-spin" style={{ color: tabInfo.color }} />
              </div>
              <div className="absolute -inset-3 rounded-3xl animate-pulse" style={{ backgroundColor: `${tabInfo.color}05` }} />
            </div>
            <div className="text-center">
              <p className="text-sm font-medium" style={{ color: tabInfo.color }}>Generando {tabInfo.nombre.toLowerCase()}...</p>
              <p className="text-[10px] text-[#5F6368] mt-1">CecilIA esta procesando tu solicitud con IA</p>
            </div>
          </div>
        )}

        {/* Resultado */}
        {resultado && !resultado.error && !cargando && (
          <div className="space-y-4">
            {/* ═══ PODCAST ═══ */}
            {tabActiva === 'podcast' && (
              <div className="rounded-2xl border border-[#2471A3]/30 bg-gradient-to-br from-[#2471A3]/8 to-[#2471A3]/2 p-6 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#2471A3]/15 border border-[#2471A3]/25">
                    <Headphones className="h-5 w-5 text-[#2471A3]" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-[#2471A3]">Podcast: {resultado.tema}</h3>
                    <p className="text-[10px] text-[#5F6368]">
                      {resultado.audio_base64 ? `Audio MP3 — ${resultado.duracion_segundos}s` : 'Script del podcast generado'}
                    </p>
                  </div>
                </div>

                {resultado.audio_base64 ? (
                  <div className="rounded-xl bg-[#0A0F14]/80 p-4 border border-[#2D3748]/30">
                    <div className="flex items-center gap-2 mb-2">
                      <Volume2 className="h-3.5 w-3.5 text-[#2471A3]" />
                      <span className="text-[10px] font-medium text-[#2471A3]">Voces: Sofia (es-CO) y Don Carlos (es-CO)</span>
                    </div>
                    <audio
                      controls
                      className="w-full h-10"
                      src={`data:audio/mp3;base64,${resultado.audio_base64}`}
                      style={{ filter: 'hue-rotate(200deg) brightness(1.3)' }}
                    />
                  </div>
                ) : (
                  <div className="rounded-xl bg-[#C9A84C]/5 border border-[#C9A84C]/20 p-3">
                    <p className="text-[10px] text-[#C9A84C]">
                      {resultado.nota || 'El audio se genera con edge-tts en voces colombianas. Si no esta disponible, se muestra el script.'}
                    </p>
                  </div>
                )}

                {resultado.script && (
                  <details className="text-xs group">
                    <summary className="cursor-pointer text-[#2471A3] hover:text-[#5DADE2] font-medium flex items-center gap-1.5 py-1">
                      <Eye className="h-3 w-3" />
                      Ver script del podcast
                    </summary>
                    <pre className="mt-3 rounded-xl bg-[#0A0F14] p-4 text-[#9AA0A6] whitespace-pre-wrap text-[10px] max-h-60 overflow-y-auto border border-[#2D3748]/30 leading-relaxed">
                      {resultado.script}
                    </pre>
                  </details>
                )}
              </div>
            )}

            {/* ═══ FLASHCARDS ═══ */}
            {tabActiva === 'flashcards' && resultado.tarjetas && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-[#27AE60] flex items-center gap-2">
                    <Layers className="h-4 w-4" />
                    Flashcards — {resultado.total} tarjetas
                  </h3>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-[#5F6368] bg-[#1A2332] rounded-lg px-2.5 py-1 border border-[#2D3748]/30">
                      {flashcardIdx + 1} / {resultado.tarjetas.length}
                    </span>
                  </div>
                </div>

                {/* Flashcard interactiva */}
                <div
                  onClick={() => setFlashcardVolteada(!flashcardVolteada)}
                  className="group cursor-pointer rounded-2xl border border-[#27AE60]/30 p-8 text-center min-h-[220px] flex flex-col items-center justify-center transition-all duration-300 hover:shadow-xl relative overflow-hidden"
                  style={{
                    background: flashcardVolteada
                      ? 'linear-gradient(135deg, rgba(39,174,96,0.12) 0%, rgba(39,174,96,0.04) 100%)'
                      : 'linear-gradient(135deg, rgba(26,35,50,0.8) 0%, rgba(26,35,50,0.4) 100%)',
                    boxShadow: '0 4px 20px rgba(39,174,96,0.08)',
                  }}
                >
                  <div className="absolute top-0 left-0 right-0 h-1 rounded-t-2xl" style={{ backgroundColor: flashcardVolteada ? '#27AE60' : '#2D3748' }} />

                  {flashcardVolteada ? (
                    <>
                      <p className="text-[10px] text-[#27AE60] mb-3 font-bold tracking-wider uppercase">Respuesta</p>
                      <p className="text-sm text-[#E8EAED] leading-relaxed max-w-md">{resultado.tarjetas[flashcardIdx]?.reverso}</p>
                      <div className="flex items-center gap-3 mt-4">
                        <span className="text-[9px] px-2 py-0.5 rounded-full bg-[#27AE60]/10 border border-[#27AE60]/20 text-[#27AE60]">
                          Bloom: {resultado.tarjetas[flashcardIdx]?.nivel_bloom}
                        </span>
                        <span className="text-[9px] px-2 py-0.5 rounded-full bg-[#2D3748]/50 border border-[#2D3748]/30 text-[#5F6368]">
                          {resultado.tarjetas[flashcardIdx]?.dificultad}
                        </span>
                      </div>
                    </>
                  ) : (
                    <>
                      <p className="text-[10px] text-[#C9A84C] mb-3 font-bold tracking-wider uppercase">Pregunta</p>
                      <p className="text-sm text-[#E8EAED] leading-relaxed max-w-md font-medium">{resultado.tarjetas[flashcardIdx]?.frente}</p>
                      <p className="text-[10px] text-[#5F6368] mt-5 flex items-center gap-1.5">
                        <RotateCcw className="h-3 w-3" />
                        Toca para ver la respuesta
                      </p>
                    </>
                  )}
                </div>

                {/* Navegacion flashcards */}
                <div className="flex gap-2 justify-center">
                  <button
                    onClick={() => { setFlashcardIdx(Math.max(0, flashcardIdx - 1)); setFlashcardVolteada(false); }}
                    disabled={flashcardIdx === 0}
                    className="flex items-center gap-1.5 rounded-xl border border-[#2D3748]/50 px-4 py-2.5 text-xs text-[#5F6368] hover:text-[#E8EAED] hover:border-[#27AE60]/30 disabled:opacity-30 transition-all"
                  >
                    <ChevronLeft className="h-3.5 w-3.5" />
                    Anterior
                  </button>
                  <button
                    onClick={() => setFlashcardVolteada(!flashcardVolteada)}
                    className="flex items-center gap-1.5 rounded-xl bg-[#27AE60]/10 border border-[#27AE60]/30 px-4 py-2.5 text-xs text-[#27AE60] hover:bg-[#27AE60]/20 transition-all"
                  >
                    <RotateCcw className="h-3.5 w-3.5" />
                    Voltear
                  </button>
                  <button
                    onClick={() => { setFlashcardIdx(Math.min(resultado.tarjetas.length - 1, flashcardIdx + 1)); setFlashcardVolteada(false); }}
                    disabled={flashcardIdx >= resultado.tarjetas.length - 1}
                    className="flex items-center gap-1.5 rounded-xl bg-[#27AE60]/8 border border-[#27AE60]/20 px-4 py-2.5 text-xs text-[#27AE60] hover:bg-[#27AE60]/15 disabled:opacity-30 transition-all"
                  >
                    Siguiente
                    <ChevronRight className="h-3.5 w-3.5" />
                  </button>
                </div>

                {/* Indicador de progreso de tarjetas */}
                <div className="flex gap-1 justify-center">
                  {resultado.tarjetas.map((_: any, idx: number) => (
                    <button
                      key={idx}
                      onClick={() => { setFlashcardIdx(idx); setFlashcardVolteada(false); }}
                      className={`h-1.5 rounded-full transition-all ${
                        idx === flashcardIdx ? 'w-6 bg-[#27AE60]' : 'w-1.5 bg-[#2D3748]/50 hover:bg-[#2D3748]'
                      }`}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* ═══ INFOGRAFIA ═══ */}
            {tabActiva === 'infografia' && (
              <div className="rounded-2xl border border-[#8E44AD]/30 bg-gradient-to-br from-[#8E44AD]/8 to-[#8E44AD]/2 p-6 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#8E44AD]/15 border border-[#8E44AD]/25">
                    <Image className="h-5 w-5 text-[#8E44AD]" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-[#8E44AD]">Infografia: {resultado.tema}</h3>
                    <p className="text-[10px] text-[#5F6368]">Diagrama generado con IA — tipo {resultado.tipo_diagrama}</p>
                  </div>
                </div>

                {/* Imagen renderizada */}
                {resultado.imagen_url && (
                  <div className="rounded-xl bg-white p-6 border border-[#2D3748]/20 overflow-hidden">
                    <img
                      src={resultado.imagen_url}
                      alt={`Infografia: ${resultado.tema}`}
                      className="w-full h-auto max-h-[500px] object-contain mx-auto"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none';
                        const parent = (e.target as HTMLImageElement).parentElement;
                        if (parent) {
                          const fallback = document.createElement('div');
                          fallback.className = 'text-center py-8';
                          fallback.innerHTML = '<p class="text-sm text-gray-500">No se pudo renderizar la imagen. Ver codigo Mermaid abajo.</p>';
                          parent.appendChild(fallback);
                        }
                      }}
                    />
                  </div>
                )}

                {/* Codigo fuente Mermaid */}
                {resultado.mermaid && (
                  <details className="text-xs group">
                    <summary className="cursor-pointer text-[#8E44AD] hover:text-[#AF7AC5] font-medium flex items-center gap-1.5 py-1">
                      <Eye className="h-3 w-3" />
                      Ver codigo Mermaid
                    </summary>
                    <pre className="mt-3 rounded-xl bg-[#0A0F14] p-4 text-[10px] text-[#9AA0A6] whitespace-pre-wrap overflow-x-auto border border-[#2D3748]/30 leading-relaxed">
                      {resultado.mermaid}
                    </pre>
                  </details>
                )}
              </div>
            )}

            {/* ═══ MANUAL DOCX ═══ */}
            {tabActiva === 'manual' && resultado.contenido_base64 && (
              <div className="rounded-2xl border border-[#C9A84C]/30 bg-gradient-to-br from-[#C9A84C]/8 to-[#C9A84C]/2 p-8 text-center space-y-5">
                <div className="flex flex-col items-center gap-3">
                  <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-[#C9A84C]/20 to-[#C9A84C]/5 border border-[#C9A84C]/25 shadow-lg shadow-[#C9A84C]/10">
                    <FileText className="h-8 w-8 text-[#C9A84C]" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-[#C9A84C]">Manual Generado</h3>
                    <p className="text-[10px] text-[#5F6368] mt-1">Documento DOCX con formato institucional CGR</p>
                  </div>
                </div>

                <div className="rounded-xl bg-[#0A0F14]/60 border border-[#2D3748]/30 p-4 max-w-sm mx-auto">
                  <p className="text-xs text-[#9AA0A6] font-mono">{resultado.nombre_archivo}</p>
                  <div className="flex items-center justify-center gap-3 mt-2 text-[9px] text-[#5F6368]">
                    <span>Nivel: {resultado.nivel}</span>
                    <span>|</span>
                    <span>Formato: DOCX</span>
                    <span>|</span>
                    <span>Logos: CGR + CecilIA</span>
                  </div>
                </div>

                <button
                  onClick={() => descargarDocx(resultado.contenido_base64, resultado.nombre_archivo)}
                  className="group flex items-center gap-2.5 mx-auto rounded-xl bg-gradient-to-r from-[#C9A84C]/15 to-[#C9A84C]/8 border border-[#C9A84C]/30 px-6 py-3 text-sm font-semibold text-[#C9A84C] hover:from-[#C9A84C]/25 hover:to-[#C9A84C]/12 hover:shadow-lg hover:shadow-[#C9A84C]/10 transition-all"
                >
                  <Download className="h-4 w-4 group-hover:scale-110 transition-transform" />
                  Descargar Manual DOCX
                </button>
              </div>
            )}
          </div>
        )}

        {resultado?.error && !cargando && (
          <div className="rounded-xl border border-[#E74C3C]/30 bg-gradient-to-r from-[#E74C3C]/8 to-[#E74C3C]/3 p-5 text-center">
            <p className="text-xs text-[#E74C3C] font-medium">{resultado.error}</p>
            <p className="text-[10px] text-[#5F6368] mt-2">Verifica que el backend este corriendo y el LLM este configurado</p>
          </div>
        )}

        {/* Disclaimer */}
        <div className="rounded-xl border border-[#C9A84C]/15 bg-[#C9A84C]/3 p-3 text-center">
          <p className="text-[9px] text-[#C9A84C]/60">
            Contenido asistido por IA — Requiere validacion humana — Circular 023 CGR
          </p>
        </div>
      </div>
    </div>
  );
}
