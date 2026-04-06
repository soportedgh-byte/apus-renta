'use client';

/**
 * CecilIA v2 — Simulador de Auditorias Guiado
 * Escenarios paso a paso con IA: primera auditoria, estudio sectorial, hallazgo completo
 * Sprint: Capacitacion 2.0
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft, Play, CheckCircle, XCircle, ChevronRight,
  Loader2, Target, Lightbulb, AlertTriangle, Award, RotateCcw,
  MapPin,
} from 'lucide-react';
import { apiCliente } from '@/lib/api';
import type { Simulacion, PasoSimulacion } from '@/lib/types';

export default function PaginaSimulador() {
  const router = useRouter();
  const [simulaciones, setSimulaciones] = useState<Simulacion[]>([]);
  const [simulacionActiva, setSimulacionActiva] = useState<string | null>(null);
  const [pasoActual, setPasoActual] = useState<PasoSimulacion | null>(null);
  const [respuestaSeleccionada, setRespuestaSeleccionada] = useState<number | null>(null);
  const [pasoNum, setPasoNum] = useState(1);
  const [puntaje, setPuntaje] = useState(0);
  const [totalRespondido, setTotalRespondido] = useState(0);
  const [cargando, setCargando] = useState(false);
  const [terminado, setTerminado] = useState(false);

  useEffect(() => { cargarSimulaciones(); }, []);

  const cargarSimulaciones = async () => {
    try {
      const resp = await apiCliente.get<Simulacion[]>('/capacitacion/simulaciones');
      setSimulaciones(resp);
    } catch {
      setSimulaciones([
        { id: 'primera_auditoria', nombre: 'Tu primera auditoria', descripcion: 'Guia paso a paso por las 5 fases del proceso auditor DVF.', direccion: 'DVF', total_pasos: 5 },
        { id: 'estudio_sectorial', nombre: 'Construye un estudio sectorial', descripcion: 'Caso del sector TIC para aprender la metodologia DES.', direccion: 'DES', total_pasos: 4 },
        { id: 'hallazgo_completo', nombre: 'Configura un hallazgo completo', descripcion: 'Estructura un hallazgo con sus 4 elementos.', direccion: 'DVF', total_pasos: 4 },
      ]);
    }
  };

  const iniciarSimulacion = async (id: string) => {
    setSimulacionActiva(id);
    setPasoNum(1);
    setPuntaje(0);
    setTotalRespondido(0);
    setTerminado(false);
    await cargarPaso(id, 1);
  };

  const cargarPaso = async (simId: string, paso: number) => {
    setCargando(true);
    setRespuestaSeleccionada(null);
    try {
      const resp = await apiCliente.post<PasoSimulacion>('/capacitacion/simulaciones/paso', {
        simulacion_id: simId,
        paso,
        contexto_previo: '',
      });
      setPasoActual(resp);
    } catch {
      setPasoActual(null);
    } finally {
      setCargando(false);
    }
  };

  const seleccionarRespuesta = (idx: number) => {
    if (respuestaSeleccionada !== null) return;
    setRespuestaSeleccionada(idx);
    setTotalRespondido((p) => p + 1);
    if (pasoActual?.opciones[idx]?.correcta) {
      setPuntaje((p) => p + 1);
    }
  };

  const siguientePaso = async () => {
    if (!simulacionActiva || !pasoActual) return;
    if (pasoNum >= pasoActual.total_pasos) {
      setTerminado(true);
    } else {
      const siguiente = pasoNum + 1;
      setPasoNum(siguiente);
      await cargarPaso(simulacionActiva, siguiente);
    }
  };

  const reiniciar = () => {
    setSimulacionActiva(null);
    setPasoActual(null);
    setPasoNum(1);
    setPuntaje(0);
    setTotalRespondido(0);
    setTerminado(false);
    setRespuestaSeleccionada(null);
  };

  // Pantalla de resultado
  if (terminado && pasoActual) {
    const porcentaje = totalRespondido > 0 ? Math.round((puntaje / totalRespondido) * 100) : 0;
    const aprobado = porcentaje >= 70;

    return (
      <div className="flex flex-col h-full bg-[#0F1419] text-[#E8EAED] overflow-y-auto">
        <div className="border-b border-[#2D3748]/30 px-6 py-4">
          <button onClick={reiniciar} className="flex items-center gap-1 text-[10px] text-[#5F6368] hover:text-[#9AA0A6]">
            <ArrowLeft className="h-3 w-3" /> Volver a simulaciones
          </button>
        </div>
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-md w-full text-center space-y-6">
            <div className={`flex h-20 w-20 items-center justify-center rounded-full mx-auto border-2 ${aprobado ? 'bg-[#27AE60]/10 border-[#27AE60]/40' : 'bg-[#E74C3C]/10 border-[#E74C3C]/40'}`}>
              {aprobado ? <Award className="h-10 w-10 text-[#27AE60]" /> : <AlertTriangle className="h-10 w-10 text-[#E74C3C]" />}
            </div>
            <div>
              <h2 className={`text-2xl font-bold ${aprobado ? 'text-[#27AE60]' : 'text-[#E74C3C]'}`}>
                {aprobado ? 'Simulacion aprobada!' : 'Sigue practicando'}
              </h2>
              <p className="text-lg font-semibold text-[#E8EAED] mt-2">{puntaje}/{totalRespondido} correctas ({porcentaje}%)</p>
              <p className="text-xs text-[#5F6368] mt-1">Umbral de aprobacion: 70%</p>
            </div>
            <div className="flex gap-3 justify-center">
              <button onClick={reiniciar} className="flex items-center gap-2 rounded-lg border border-[#2D3748]/50 bg-[#1A2332] px-4 py-2 text-xs text-[#9AA0A6] hover:text-[#E8EAED]">
                <RotateCcw className="h-3.5 w-3.5" /> Otra simulacion
              </button>
              <button onClick={() => router.push('/capacitacion')} className="flex items-center gap-2 rounded-lg bg-[#C9A84C]/10 border border-[#C9A84C]/30 px-4 py-2 text-xs text-[#C9A84C]">
                Volver a capacitacion
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Simulacion en progreso
  if (simulacionActiva && pasoActual) {
    return (
      <div className="flex flex-col h-full bg-[#0F1419] text-[#E8EAED] overflow-y-auto">
        <div className="border-b border-[#2D3748]/30 px-6 py-4">
          <div className="flex items-center justify-between mb-2">
            <button onClick={reiniciar} className="flex items-center gap-1 text-[10px] text-[#5F6368] hover:text-[#9AA0A6]">
              <ArrowLeft className="h-3 w-3" /> Salir
            </button>
            <span className="text-xs text-[#5F6368]">Paso {pasoActual.paso} de {pasoActual.total_pasos}</span>
            <span className="text-xs font-semibold text-[#C9A84C]">{puntaje}/{totalRespondido} correctas</span>
          </div>
          <div className="h-1.5 rounded-full bg-[#2D3748]/50 overflow-hidden">
            <div className="h-full rounded-full bg-[#C9A84C] transition-all duration-500" style={{ width: `${(pasoActual.paso / pasoActual.total_pasos) * 100}%` }} />
          </div>
        </div>

        <div className="flex-1 p-6 space-y-5">
          {cargando ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="h-8 w-8 text-[#C9A84C] animate-spin" />
            </div>
          ) : (
            <>
              <div>
                <h2 className="text-base font-bold text-[#C9A84C] flex items-center gap-2">
                  <MapPin className="h-4 w-4" /> {pasoActual.titulo}
                </h2>
              </div>

              {/* Escenario */}
              <div className="rounded-lg border border-[#2D3748]/50 bg-[#1A2332]/60 p-4">
                <p className="text-xs text-[#E8EAED] leading-relaxed">{pasoActual.escenario}</p>
              </div>

              {/* Datos */}
              {pasoActual.datos.length > 0 && (
                <div className="rounded-lg border border-[#1A5276]/30 bg-[#1A5276]/5 p-3">
                  <p className="text-[10px] font-semibold text-[#1A5276] mb-2">Datos del caso</p>
                  <ul className="space-y-1">
                    {pasoActual.datos.map((d, i) => (
                      <li key={i} className="text-xs text-[#9AA0A6] flex items-start gap-2">
                        <span className="text-[#1A5276] mt-0.5">-</span> {d}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Pregunta */}
              <div>
                <h3 className="text-sm font-semibold text-[#E8EAED] mb-3 flex items-center gap-2">
                  <Target className="h-4 w-4 text-[#C9A84C]" /> {pasoActual.pregunta}
                </h3>
                <div className="space-y-2">
                  {pasoActual.opciones.map((op, idx) => {
                    const seleccionada = respuestaSeleccionada === idx;
                    const respondido = respuestaSeleccionada !== null;
                    let estilo = 'border-[#2D3748]/50 bg-[#1A2332]/40';
                    if (respondido && op.correcta) estilo = 'border-[#27AE60]/50 bg-[#27AE60]/10';
                    else if (seleccionada && !op.correcta) estilo = 'border-[#E74C3C]/50 bg-[#E74C3C]/10';

                    return (
                      <button
                        key={idx}
                        onClick={() => seleccionarRespuesta(idx)}
                        disabled={respondido}
                        className={`w-full flex items-start gap-3 rounded-lg border p-3 text-left transition-all ${estilo} ${!respondido ? 'hover:bg-[#1A2332]/70 cursor-pointer' : ''}`}
                      >
                        <div className="flex-shrink-0 mt-0.5">
                          {respondido && op.correcta ? (
                            <CheckCircle className="h-4 w-4 text-[#27AE60]" />
                          ) : seleccionada && !op.correcta ? (
                            <XCircle className="h-4 w-4 text-[#E74C3C]" />
                          ) : (
                            <div className="h-4 w-4 rounded-full border border-[#5F6368]" />
                          )}
                        </div>
                        <div>
                          <p className="text-xs text-[#E8EAED]">{op.texto}</p>
                          {respondido && (seleccionada || op.correcta) && (
                            <p className={`text-[10px] mt-1 ${op.correcta ? 'text-[#27AE60]' : 'text-[#E74C3C]'}`}>
                              {op.retroalimentacion}
                            </p>
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Tip */}
              {respuestaSeleccionada !== null && pasoActual.tip && (
                <div className="rounded-lg border border-[#C9A84C]/30 bg-[#C9A84C]/5 p-3 flex gap-2">
                  <Lightbulb className="h-4 w-4 text-[#C9A84C] flex-shrink-0 mt-0.5" />
                  <p className="text-[10px] text-[#C9A84C]">{pasoActual.tip}</p>
                </div>
              )}

              {/* Boton siguiente */}
              {respuestaSeleccionada !== null && (
                <button
                  onClick={siguientePaso}
                  className="flex w-full items-center justify-center gap-2 rounded-lg bg-[#C9A84C]/10 border border-[#C9A84C]/30 px-4 py-3 text-sm font-medium text-[#C9A84C] hover:bg-[#C9A84C]/20 transition-colors"
                >
                  {pasoNum >= pasoActual.total_pasos ? 'Ver resultados' : 'Siguiente paso'}
                  <ChevronRight className="h-4 w-4" />
                </button>
              )}
            </>
          )}
        </div>
      </div>
    );
  }

  // Lista de simulaciones
  const COLORES_DIRECCION: Record<string, string> = { DVF: '#1E8449', DES: '#1A5276' };

  return (
    <div className="flex flex-col h-full bg-[#0F1419] text-[#E8EAED] overflow-y-auto">
      <div className="border-b border-[#2D3748]/30 px-6 py-4">
        <div className="flex items-center gap-3">
          <button onClick={() => router.push('/capacitacion')} className="flex items-center gap-1 text-[10px] text-[#5F6368] hover:text-[#9AA0A6]">
            <ArrowLeft className="h-3 w-3" />
          </button>
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#E74C3C]/10 border border-[#E74C3C]/20">
            <Target className="h-5 w-5 text-[#E74C3C]" />
          </div>
          <div>
            <h1 className="text-base font-bold text-[#E74C3C]">Simulador de Auditorias</h1>
            <p className="text-[10px] text-[#5F6368]">Escenarios guiados paso a paso con retroalimentacion de IA</p>
          </div>
        </div>
      </div>

      <div className="flex-1 p-6 space-y-4">
        {simulaciones.map((sim) => {
          const color = COLORES_DIRECCION[sim.direccion] || '#C9A84C';
          return (
            <button
              key={sim.id}
              onClick={() => iniciarSimulacion(sim.id)}
              className="w-full flex items-center gap-4 rounded-xl border border-[#2D3748]/50 bg-[#1A2332]/40 p-5 text-left hover:bg-[#1A2332]/70 transition-all group"
              style={{ borderColor: `${color}20` }}
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-xl" style={{ backgroundColor: `${color}10`, border: `1px solid ${color}25` }}>
                <Play className="h-6 w-6" style={{ color }} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-[#E8EAED]">{sim.nombre}</h3>
                  <span className="rounded-full px-2 py-0.5 text-[9px] font-semibold" style={{ backgroundColor: `${color}15`, color }}>{sim.direccion}</span>
                </div>
                <p className="text-xs text-[#9AA0A6] mt-1">{sim.descripcion}</p>
                <p className="text-[10px] text-[#5F6368] mt-1">{sim.total_pasos} pasos</p>
              </div>
              <ChevronRight className="h-5 w-5 text-[#5F6368] group-hover:text-[#E8EAED] transition-colors flex-shrink-0" />
            </button>
          );
        })}

        <div className="rounded-lg border border-[#C9A84C]/20 bg-[#C9A84C]/5 p-3 text-center mt-6">
          <p className="text-[10px] text-[#C9A84C]/80">
            Datos ficticios con fines educativos — CecilIA Modo Tutor — Circular 023 CGR
          </p>
        </div>
      </div>
    </div>
  );
}
