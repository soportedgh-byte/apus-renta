'use client';

/**
 * CecilIA v2 — Biblioteca de Recursos Generados
 * Podcasts, flashcards, infografias, manuales generados con IA
 * Sprint: Capacitacion 2.0
 */

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft, Headphones, BookOpen, Image, FileText,
  Loader2, Download, Play, Sparkles, Layers,
} from 'lucide-react';
import { apiCliente } from '@/lib/api';

type Tab = 'podcast' | 'flashcards' | 'infografia' | 'manual';

const TABS: Array<{ id: Tab; nombre: string; icono: any; color: string }> = [
  { id: 'podcast', nombre: 'Podcast', icono: Headphones, color: '#2471A3' },
  { id: 'flashcards', nombre: 'Flashcards', icono: Layers, color: '#27AE60' },
  { id: 'infografia', nombre: 'Infografia', icono: Image, color: '#8E44AD' },
  { id: 'manual', nombre: 'Manual', icono: FileText, color: '#C9A84C' },
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
      <div className="border-b border-[#2D3748]/30 px-6 py-4">
        <div className="flex items-center gap-3 mb-3">
          <button onClick={() => router.push('/capacitacion')} className="flex items-center gap-1 text-[10px] text-[#5F6368] hover:text-[#9AA0A6]">
            <ArrowLeft className="h-3 w-3" />
          </button>
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#8E44AD]/10 border border-[#8E44AD]/20">
            <Sparkles className="h-5 w-5 text-[#8E44AD]" />
          </div>
          <div>
            <h1 className="text-base font-bold text-[#8E44AD]">Biblioteca de Recursos</h1>
            <p className="text-[10px] text-[#5F6368]">Genera contenido educativo con IA sobre cualquier tema fiscal</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          {TABS.map((tab) => {
            const Icono = tab.icono;
            const activa = tabActiva === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => { setTabActiva(tab.id); setResultado(null); }}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-[10px] font-medium transition-colors ${
                  activa ? 'border text-white' : 'border border-[#2D3748]/50 text-[#5F6368] hover:text-[#9AA0A6]'
                }`}
                style={activa ? { backgroundColor: `${tab.color}15`, borderColor: `${tab.color}40`, color: tab.color } : {}}
              >
                <Icono className="h-3.5 w-3.5" />
                {tab.nombre}
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
              className="flex-1 rounded-lg bg-[#1A2332] border border-[#2D3748]/50 px-4 py-2.5 text-xs text-[#E8EAED] placeholder-[#5F6368] outline-none focus:border-[#C9A84C]/50"
            />
            <button
              onClick={generar}
              disabled={!tema.trim() || cargando}
              className="flex items-center gap-2 rounded-lg px-4 py-2.5 text-xs font-medium transition-colors disabled:opacity-30"
              style={{ backgroundColor: `${tabInfo.color}15`, border: `1px solid ${tabInfo.color}40`, color: tabInfo.color }}
            >
              {cargando ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Sparkles className="h-3.5 w-3.5" />}
              Generar
            </button>
          </div>

          {/* Temas sugeridos */}
          <div className="flex flex-wrap gap-1.5 mt-3">
            {TEMAS_SUGERIDOS.map((t) => (
              <button
                key={t}
                onClick={() => setTema(t)}
                className="rounded-full bg-[#2D3748]/30 px-2.5 py-1 text-[9px] text-[#5F6368] hover:text-[#9AA0A6] hover:bg-[#2D3748]/50 transition-colors"
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Resultado */}
        {resultado && !resultado.error && (
          <div className="space-y-4">
            {/* Podcast */}
            {tabActiva === 'podcast' && (
              <div className="rounded-xl border border-[#2471A3]/30 bg-[#2471A3]/5 p-5 space-y-3">
                <div className="flex items-center gap-2">
                  <Headphones className="h-5 w-5 text-[#2471A3]" />
                  <h3 className="text-sm font-semibold text-[#2471A3]">Podcast: {resultado.tema}</h3>
                </div>
                {resultado.audio_base64 ? (
                  <audio controls className="w-full" src={`data:audio/mp3;base64,${resultado.audio_base64}`} />
                ) : (
                  <p className="text-[10px] text-[#5F6368]">{resultado.nota || 'Audio no disponible'}</p>
                )}
                {resultado.script && (
                  <details className="text-xs">
                    <summary className="cursor-pointer text-[#2471A3] hover:underline">Ver script del podcast</summary>
                    <pre className="mt-2 rounded-lg bg-[#0A0F14] p-3 text-[#9AA0A6] whitespace-pre-wrap text-[10px] max-h-60 overflow-y-auto">{resultado.script}</pre>
                  </details>
                )}
              </div>
            )}

            {/* Flashcards */}
            {tabActiva === 'flashcards' && resultado.tarjetas && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-[#27AE60] flex items-center gap-2">
                    <Layers className="h-4 w-4" /> Flashcards ({resultado.total})
                  </h3>
                  <span className="text-xs text-[#5F6368]">{flashcardIdx + 1} / {resultado.tarjetas.length}</span>
                </div>
                <div
                  onClick={() => setFlashcardVolteada(!flashcardVolteada)}
                  className="cursor-pointer rounded-xl border border-[#27AE60]/30 bg-[#27AE60]/5 p-8 text-center min-h-[180px] flex flex-col items-center justify-center transition-all hover:bg-[#27AE60]/10"
                >
                  {flashcardVolteada ? (
                    <>
                      <p className="text-[10px] text-[#27AE60] mb-2 font-semibold">RESPUESTA</p>
                      <p className="text-sm text-[#E8EAED] leading-relaxed">{resultado.tarjetas[flashcardIdx]?.reverso}</p>
                      <p className="text-[9px] text-[#5F6368] mt-3">Bloom: {resultado.tarjetas[flashcardIdx]?.nivel_bloom} | {resultado.tarjetas[flashcardIdx]?.dificultad}</p>
                    </>
                  ) : (
                    <>
                      <p className="text-[10px] text-[#27AE60] mb-2 font-semibold">PREGUNTA</p>
                      <p className="text-sm text-[#E8EAED] leading-relaxed">{resultado.tarjetas[flashcardIdx]?.frente}</p>
                      <p className="text-[10px] text-[#5F6368] mt-4">Toca para ver la respuesta</p>
                    </>
                  )}
                </div>
                <div className="flex gap-2 justify-center">
                  <button
                    onClick={() => { setFlashcardIdx(Math.max(0, flashcardIdx - 1)); setFlashcardVolteada(false); }}
                    disabled={flashcardIdx === 0}
                    className="rounded-lg border border-[#2D3748]/50 px-4 py-2 text-xs text-[#5F6368] hover:text-[#E8EAED] disabled:opacity-30"
                  >
                    Anterior
                  </button>
                  <button
                    onClick={() => { setFlashcardIdx(Math.min(resultado.tarjetas.length - 1, flashcardIdx + 1)); setFlashcardVolteada(false); }}
                    disabled={flashcardIdx >= resultado.tarjetas.length - 1}
                    className="rounded-lg bg-[#27AE60]/10 border border-[#27AE60]/30 px-4 py-2 text-xs text-[#27AE60] disabled:opacity-30"
                  >
                    Siguiente
                  </button>
                </div>
              </div>
            )}

            {/* Infografia Mermaid */}
            {tabActiva === 'infografia' && resultado.mermaid && (
              <div className="rounded-xl border border-[#8E44AD]/30 bg-[#8E44AD]/5 p-5 space-y-3">
                <div className="flex items-center gap-2">
                  <Image className="h-5 w-5 text-[#8E44AD]" />
                  <h3 className="text-sm font-semibold text-[#8E44AD]">Infografia: {resultado.tema}</h3>
                </div>
                <pre className="rounded-lg bg-[#0A0F14] p-4 text-[10px] text-[#9AA0A6] whitespace-pre-wrap overflow-x-auto border border-[#2D3748]/30">
                  {resultado.mermaid}
                </pre>
                <p className="text-[10px] text-[#5F6368]">Copia el codigo Mermaid en un visor como mermaid.live para ver el diagrama renderizado</p>
              </div>
            )}

            {/* Manual DOCX */}
            {tabActiva === 'manual' && resultado.contenido_base64 && (
              <div className="rounded-xl border border-[#C9A84C]/30 bg-[#C9A84C]/5 p-5 text-center space-y-3">
                <FileText className="h-12 w-12 text-[#C9A84C] mx-auto" />
                <h3 className="text-sm font-semibold text-[#C9A84C]">Manual generado</h3>
                <p className="text-xs text-[#9AA0A6]">{resultado.nombre_archivo}</p>
                <button
                  onClick={() => descargarDocx(resultado.contenido_base64, resultado.nombre_archivo)}
                  className="flex items-center gap-2 mx-auto rounded-lg bg-[#C9A84C]/10 border border-[#C9A84C]/30 px-5 py-2.5 text-xs font-medium text-[#C9A84C] hover:bg-[#C9A84C]/20"
                >
                  <Download className="h-4 w-4" /> Descargar DOCX
                </button>
              </div>
            )}
          </div>
        )}

        {resultado?.error && (
          <div className="rounded-lg border border-[#E74C3C]/30 bg-[#E74C3C]/5 p-4 text-center">
            <p className="text-xs text-[#E74C3C]">{resultado.error}</p>
          </div>
        )}

        <div className="rounded-lg border border-[#C9A84C]/20 bg-[#C9A84C]/5 p-3 text-center">
          <p className="text-[10px] text-[#C9A84C]/80">
            Contenido generado con IA — Requiere validacion humana — Circular 023 CGR
          </p>
        </div>
      </div>
    </div>
  );
}
