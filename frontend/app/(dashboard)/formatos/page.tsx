'use client';

import React, { useState, useEffect } from 'react';
import {
  FileCheck,
  Download,
  Eye,
  Bot,
  CheckCircle,
  Clock,
  ChevronDown,
  ChevronRight,
  Sparkles,
  X,
  AlertTriangle,
  FileText,
  History,
  LayoutGrid,
} from 'lucide-react';
import { Tarjeta } from '@/components/ui/card';
import { Insignia } from '@/components/ui/badge';
import { Boton } from '@/components/ui/button';
import { obtenerDireccionActiva } from '@/lib/auth';
import type { Direccion } from '@/lib/types';

/** Tipo de plantilla del catalogo */
interface Plantilla {
  numero: number;
  nombre: string;
  fase: string;
  implementado: boolean;
}

/** Formato generado en historial */
interface FormatoHistorial {
  id: string;
  numero_formato: number;
  nombre_formato: string;
  estado: string;
  generado_con_ia: boolean;
  creado_en: string;
}

/** Fases del proceso auditor */
const FASES = [
  {
    id: 'pre-planeacion',
    nombre: 'Pre-planeacion',
    emoji: '📋',
    rango: 'F01 — F10',
    descripcion: 'Conocimiento de la entidad, analisis previo y preparacion',
    color: '#2471A3',
  },
  {
    id: 'planeacion',
    nombre: 'Planeacion',
    emoji: '📐',
    rango: 'F11 — F20',
    descripcion: 'Evaluacion de riesgos, materialidad y programas de auditoria',
    color: '#C9A84C',
  },
  {
    id: 'ejecucion',
    nombre: 'Ejecucion',
    emoji: '🔍',
    rango: 'F21 — F30',
    descripcion: 'Pruebas de detalle, hallazgos e informes finales',
    color: '#27AE60',
  },
];

/**
 * Pagina de Formatos de Auditoria CGR (1-30)
 * 3 secciones colapsables por fase, modal de generacion, checkbox Circular 023
 */
export default function PaginaFormatos() {
  const [direccion, setDireccion] = useState<Direccion>('DVF');
  const [pestana, setPestana] = useState<'catalogo' | 'historial'>('catalogo');
  const [plantillas, setPlantillas] = useState<Plantilla[]>([]);
  const [historial, setHistorial] = useState<FormatoHistorial[]>([]);
  const [fasesAbiertas, setFasesAbiertas] = useState<Record<string, boolean>>({
    'pre-planeacion': true,
    planeacion: false,
    ejecucion: false,
  });

  // Modal
  const [modalAbierto, setModalAbierto] = useState(false);
  const [formatoSeleccionado, setFormatoSeleccionado] = useState<Plantilla | null>(null);
  const [entidad, setEntidad] = useState('');
  const [vigencia, setVigencia] = useState('2025');
  const [tipoAuditoria, setTipoAuditoria] = useState('Financiera y de Gestion');
  const [aceptoCircular, setAceptoCircular] = useState(false);
  const [generando, setGenerando] = useState(false);
  const [previewHtml, setPreviewHtml] = useState<string | null>(null);

  const colorDir = direccion === 'DES' ? '#1A5276' : '#1E8449';

  useEffect(() => {
    const dir = obtenerDireccionActiva();
    if (dir) setDireccion(dir);
    cargarPlantillas();
    cargarHistorial();
  }, []);

  const cargarPlantillas = async () => {
    try {
      const urlBase = process.env.NEXT_PUBLIC_API_URL || '/api';
      const resp = await fetch(`${urlBase}/formatos/plantillas`);
      if (resp.ok) {
        const data = await resp.json();
        setPlantillas(data);
      } else {
        // Fallback con datos locales
        setPlantillas(generarPlantillasLocal());
      }
    } catch {
      setPlantillas(generarPlantillasLocal());
    }
  };

  const cargarHistorial = async () => {
    try {
      const urlBase = process.env.NEXT_PUBLIC_API_URL || '/api';
      const resp = await fetch(`${urlBase}/formatos/historial`);
      if (resp.ok) {
        setHistorial(await resp.json());
      }
    } catch {
      // Silenciar error
    }
  };

  const abrirModal = (plantilla: Plantilla) => {
    setFormatoSeleccionado(plantilla);
    setAceptoCircular(false);
    setPreviewHtml(null);
    setModalAbierto(true);
  };

  const previsualizar = async () => {
    if (!formatoSeleccionado) return;
    try {
      const urlBase = process.env.NEXT_PUBLIC_API_URL || '/api';
      const resp = await fetch(`${urlBase}/formatos/previsualizar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          numero_formato: formatoSeleccionado.numero,
          parametros: {
            nombre_entidad: entidad || '[COMPLETAR]',
            vigencia: vigencia || '[COMPLETAR]',
            tipo_auditoria: tipoAuditoria,
          },
        }),
      });
      if (resp.ok) {
        const data = await resp.json();
        setPreviewHtml(data.html);
      }
    } catch {
      // Silenciar
    }
  };

  const generarFormato = async () => {
    if (!formatoSeleccionado || !aceptoCircular) return;
    setGenerando(true);
    try {
      const urlBase = process.env.NEXT_PUBLIC_API_URL || '/api';
      const resp = await fetch(`${urlBase}/formatos/generar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          numero_formato: formatoSeleccionado.numero,
          auditoria_id: '',
          parametros: {
            nombre_entidad: entidad || '[COMPLETAR]',
            vigencia: vigencia || '[COMPLETAR]',
            tipo_auditoria: tipoAuditoria,
          },
          generar_con_ia: true,
        }),
      });

      if (resp.ok) {
        // Descargar el DOCX
        const blob = await resp.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `F${formatoSeleccionado.numero.toString().padStart(2, '0')}_${formatoSeleccionado.nombre.replace(/ /g, '_')}.docx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        setModalAbierto(false);
        cargarHistorial();
      }
    } catch {
      // Error silencioso
    } finally {
      setGenerando(false);
    }
  };

  const toggleFase = (faseId: string) => {
    setFasesAbiertas((prev) => ({ ...prev, [faseId]: !prev[faseId] }));
  };

  const plantillasPorFase = (faseId: string) =>
    plantillas.filter((p) => p.fase === faseId);

  return (
    <div className="p-6">
      {/* Encabezado */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-titulo text-xl font-bold text-[#E8EAED] flex items-center gap-2">
            <FileCheck className="h-6 w-6 text-[#C9A84C]" />
            Formatos de Auditoria CGR
          </h1>
          <p className="mt-1 text-xs text-[#5F6368]">
            30 formatos del proceso auditor — Genere documentos DOCX profesionales con encabezado institucional
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Insignia variante="oro" className="text-[10px]">
            <Sparkles className="h-3 w-3 mr-1" />
            {plantillas.filter((p) => p.implementado).length} implementados
          </Insignia>
        </div>
      </div>

      {/* Pestanas */}
      <div className="flex gap-1 mb-6 border-b border-[#2D3748]/30">
        <button
          onClick={() => setPestana('catalogo')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-medium transition-all border-b-2 ${
            pestana === 'catalogo'
              ? 'text-[#C9A84C] border-[#C9A84C]'
              : 'text-[#5F6368] border-transparent hover:text-[#9AA0A6]'
          }`}
        >
          <LayoutGrid className="h-3.5 w-3.5" />
          Catalogo de Formatos
        </button>
        <button
          onClick={() => setPestana('historial')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-medium transition-all border-b-2 ${
            pestana === 'historial'
              ? 'text-[#C9A84C] border-[#C9A84C]'
              : 'text-[#5F6368] border-transparent hover:text-[#9AA0A6]'
          }`}
        >
          <History className="h-3.5 w-3.5" />
          Historial ({historial.length})
        </button>
      </div>

      {/* Contenido por pestana */}
      {pestana === 'catalogo' ? (
        <div className="space-y-4">
          {FASES.map((fase) => {
            const formatosFase = plantillasPorFase(fase.id);
            const implementados = formatosFase.filter((f) => f.implementado).length;
            const abierta = fasesAbiertas[fase.id];

            return (
              <Tarjeta key={fase.id} className="overflow-hidden">
                {/* Header colapsable */}
                <button
                  onClick={() => toggleFase(fase.id)}
                  className="flex items-center justify-between w-full p-4 hover:bg-[#1A2332]/30 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{fase.emoji}</span>
                    <div className="text-left">
                      <div className="flex items-center gap-2">
                        <h3 className="text-sm font-semibold text-[#E8EAED]">
                          {fase.nombre}
                        </h3>
                        <span
                          className="rounded-full px-2 py-0.5 text-[9px] font-mono"
                          style={{
                            backgroundColor: `${fase.color}15`,
                            color: fase.color,
                            border: `1px solid ${fase.color}30`,
                          }}
                        >
                          {fase.rango}
                        </span>
                        <Insignia variante="gris" className="text-[9px]">
                          {implementados}/{formatosFase.length} implementados
                        </Insignia>
                      </div>
                      <p className="text-[10px] text-[#5F6368] mt-0.5">
                        {fase.descripcion}
                      </p>
                    </div>
                  </div>
                  {abierta ? (
                    <ChevronDown className="h-4 w-4 text-[#5F6368]" />
                  ) : (
                    <ChevronRight className="h-4 w-4 text-[#5F6368]" />
                  )}
                </button>

                {/* Contenido de la fase */}
                {abierta && (
                  <div className="border-t border-[#2D3748]/20 p-3">
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-2">
                      {formatosFase.map((plantilla) => (
                        <button
                          key={plantilla.numero}
                          onClick={() => abrirModal(plantilla)}
                          className="group flex flex-col items-start gap-1.5 rounded-lg border border-[#2D3748] bg-[#0A0F14]/60 p-3 text-left transition-all hover:border-[#C9A84C]/40 hover:bg-[#C9A84C]/5 hover:-translate-y-0.5"
                        >
                          <div className="flex items-center justify-between w-full">
                            <span className="flex h-7 w-7 items-center justify-center rounded bg-[#1A2332] text-[11px] font-mono font-bold text-[#C9A84C] border border-[#2D3748]">
                              {plantilla.numero.toString().padStart(2, '0')}
                            </span>
                            {plantilla.implementado ? (
                              <Insignia variante="exito" className="text-[8px] px-1.5">
                                Implementado
                              </Insignia>
                            ) : (
                              <Insignia variante="gris" className="text-[8px] px-1.5">
                                Proximamente
                              </Insignia>
                            )}
                          </div>
                          <span className="text-[11px] text-[#9AA0A6] group-hover:text-[#E8EAED] transition-colors leading-tight line-clamp-2">
                            {plantilla.nombre}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </Tarjeta>
            );
          })}
        </div>
      ) : (
        /* Historial */
        <div className="space-y-3">
          {historial.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <FileText className="h-12 w-12 text-[#2D3748] mb-3" />
              <p className="text-sm text-[#5F6368]">No hay formatos generados aun</p>
              <p className="text-[10px] text-[#5F6368] mt-1">
                Seleccione un formato del catalogo para comenzar
              </p>
            </div>
          ) : (
            historial.map((formato) => (
              <Tarjeta key={formato.id} className="hover:border-[#4A5568] transition-all">
                <div className="flex items-center p-4">
                  <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-[#C9A84C]/10 border border-[#C9A84C]/20 mr-4">
                    <span className="font-mono text-sm font-bold text-[#C9A84C]">
                      {formato.numero_formato.toString().padStart(2, '0')}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h4 className="text-sm font-medium text-[#E8EAED] truncate">
                        {formato.nombre_formato}
                      </h4>
                      <span
                        className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px]"
                        style={{
                          backgroundColor: '#27AE6020',
                          color: '#27AE60',
                          border: '1px solid #27AE6040',
                        }}
                      >
                        <CheckCircle className="h-3 w-3" />
                        {formato.estado}
                      </span>
                      {formato.generado_con_ia && (
                        <Insignia variante="oro" className="text-[9px]">
                          <Bot className="h-2.5 w-2.5 mr-0.5" />
                          IA
                        </Insignia>
                      )}
                    </div>
                    <p className="text-[10px] text-[#5F6368] mt-0.5">
                      Generado el{' '}
                      {new Date(formato.creado_en).toLocaleDateString('es-CO', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                </div>
              </Tarjeta>
            ))
          )}
        </div>
      )}

      {/* Modal de generacion */}
      {modalAbierto && formatoSeleccionado && (
        <>
          <div
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
            onClick={() => setModalAbierto(false)}
          />
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="w-full max-w-xl rounded-xl border border-[#2D3748] bg-[#0F1419] shadow-2xl">
              {/* Header modal */}
              <div className="flex items-center justify-between border-b border-[#2D3748]/30 px-6 py-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#C9A84C]/10 border border-[#C9A84C]/20">
                    <span className="font-mono text-sm font-bold text-[#C9A84C]">
                      {formatoSeleccionado.numero.toString().padStart(2, '0')}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-[#E8EAED]">
                      Generar Formato F{formatoSeleccionado.numero.toString().padStart(2, '0')}
                    </h3>
                    <p className="text-[10px] text-[#5F6368]">
                      {formatoSeleccionado.nombre}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setModalAbierto(false)}
                  className="rounded-lg p-1.5 text-[#5F6368] hover:bg-[#1A2332] hover:text-[#9AA0A6] transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Body modal */}
              <div className="p-6 space-y-4">
                {/* Entidad */}
                <div>
                  <label className="block text-[11px] font-medium text-[#9AA0A6] mb-1.5">
                    Entidad auditada
                  </label>
                  <input
                    type="text"
                    value={entidad}
                    onChange={(e) => setEntidad(e.target.value)}
                    placeholder="Ej: Ministerio de Tecnologias de la Informacion"
                    className="w-full rounded-lg border border-[#2D3748] bg-[#1A2332] px-3 py-2 text-sm text-[#E8EAED] placeholder:text-[#5F6368] focus:outline-none focus:border-[#C9A84C]/40"
                  />
                </div>

                {/* Vigencia y tipo */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-medium text-[#9AA0A6] mb-1.5">
                      Vigencia
                    </label>
                    <input
                      type="text"
                      value={vigencia}
                      onChange={(e) => setVigencia(e.target.value)}
                      placeholder="2025"
                      className="w-full rounded-lg border border-[#2D3748] bg-[#1A2332] px-3 py-2 text-sm text-[#E8EAED] placeholder:text-[#5F6368] focus:outline-none focus:border-[#C9A84C]/40"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-medium text-[#9AA0A6] mb-1.5">
                      Tipo de auditoria
                    </label>
                    <select
                      value={tipoAuditoria}
                      onChange={(e) => setTipoAuditoria(e.target.value)}
                      className="w-full rounded-lg border border-[#2D3748] bg-[#1A2332] px-3 py-2 text-sm text-[#E8EAED] focus:outline-none focus:border-[#C9A84C]/40"
                    >
                      <option>Financiera y de Gestion</option>
                      <option>Financiera</option>
                      <option>De Cumplimiento</option>
                      <option>De Desempeno</option>
                    </select>
                  </div>
                </div>

                {/* Preview */}
                <div className="flex justify-end">
                  <button
                    onClick={previsualizar}
                    className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-[10px] text-[#9AA0A6] hover:text-[#E8EAED] hover:bg-[#1A2332] border border-[#2D3748] transition-colors"
                  >
                    <Eye className="h-3 w-3" />
                    Vista previa
                  </button>
                </div>

                {previewHtml && (
                  <div
                    className="rounded-lg border border-[#2D3748] bg-white p-4 max-h-48 overflow-y-auto"
                    dangerouslySetInnerHTML={{ __html: previewHtml }}
                  />
                )}

                {/* Checkbox Circular 023 */}
                <div className="flex items-start gap-3 rounded-lg border border-[#C9A84C]/20 bg-[#C9A84C]/5 p-3">
                  <input
                    type="checkbox"
                    id="circular023"
                    checked={aceptoCircular}
                    onChange={(e) => setAceptoCircular(e.target.checked)}
                    className="mt-0.5 h-4 w-4 rounded border-[#2D3748] bg-[#1A2332] accent-[#C9A84C]"
                  />
                  <label htmlFor="circular023" className="text-[10px] text-[#9AA0A6] leading-relaxed cursor-pointer">
                    <span className="flex items-center gap-1 text-[#C9A84C] font-semibold mb-0.5">
                      <AlertTriangle className="h-3 w-3" />
                      Circular 023 — CGR
                    </span>
                    Declaro que este documento generado con asistencia de inteligencia artificial
                    sera revisado, verificado y validado por el equipo auditor antes de su
                    uso oficial. Los datos y conclusiones deben ser contrastados con la evidencia
                    de auditoria correspondiente.
                  </label>
                </div>
              </div>

              {/* Footer modal */}
              <div className="flex items-center justify-end gap-2 border-t border-[#2D3748]/30 px-6 py-4">
                <Boton variante="fantasma" onClick={() => setModalAbierto(false)}>
                  Cancelar
                </Boton>
                <button
                  onClick={generarFormato}
                  disabled={!aceptoCircular || generando}
                  className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all disabled:opacity-30"
                  style={{
                    background: aceptoCircular
                      ? 'linear-gradient(135deg, #C9A84C 0%, #B8963F 100%)'
                      : '#2D3748',
                    color: aceptoCircular ? '#0F1419' : '#5F6368',
                  }}
                >
                  {generando ? (
                    <>
                      <Clock className="h-4 w-4 animate-spin" />
                      Generando...
                    </>
                  ) : (
                    <>
                      <Download className="h-4 w-4" />
                      Generar y Descargar DOCX
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

/** Genera plantillas locales como fallback */
function generarPlantillasLocal(): Plantilla[] {
  const implementados = new Set([1, 3, 5, 7, 12, 14, 17, 18, 20, 22, 25]);
  const nombres: Record<number, string> = {
    1: 'Declaracion de Independencia',
    2: 'Comunicacion de Inicio',
    3: 'Datos Generales de la Entidad',
    4: 'Carta de Representacion',
    5: 'Analisis Financiero',
    6: 'Solicitud de Informacion',
    7: 'Analisis Presupuestal',
    8: 'Conocimiento de la Entidad',
    9: 'Identificacion de Procesos',
    10: 'Memorando de Pre-planeacion',
    11: 'Memorando de Planeacion',
    12: 'Evaluacion Control Interno (COSO)',
    13: 'Evaluacion Riesgo de Fraude',
    14: 'Matriz de Riesgos',
    15: 'Determinacion de la Muestra',
    16: 'Procedimientos Analiticos',
    17: 'Calculo de Materialidad',
    18: 'Plan de Trabajo',
    19: 'Comunicaciones con Direccion',
    20: 'Programa de Auditoria',
    21: 'Cedula de Hallazgo',
    22: 'Pruebas de Detalle',
    23: 'Pruebas de Cumplimiento',
    24: 'Cedula Sumaria',
    25: 'Resumen de Diferencias',
    26: 'Evaluacion de Estimaciones',
    27: 'Hechos Posteriores',
    28: 'Empresa en Funcionamiento',
    29: 'Informe Preliminar',
    30: 'Informe Final de Auditoria',
  };

  return Array.from({ length: 30 }, (_, i) => {
    const num = i + 1;
    const fase =
      num <= 10 ? 'pre-planeacion' : num <= 20 ? 'planeacion' : 'ejecucion';
    return {
      numero: num,
      nombre: nombres[num] || `Formato ${num}`,
      fase,
      implementado: implementados.has(num),
    };
  });
}
