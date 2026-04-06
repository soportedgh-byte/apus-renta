'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Brain,
  Cpu,
  Database,
  Play,
  Download,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  BarChart3,
  Layers,
  Zap,
  FileText,
  Settings,
  TrendingUp,
  AlertTriangle,
  Loader2,
} from 'lucide-react';
import { Tarjeta } from '@/components/ui/card';
import { Insignia } from '@/components/ui/badge';
import { Boton } from '@/components/ui/button';
import { Pestanas, ListaPestanas, DisparadorPestana, ContenidoPestana } from '@/components/ui/tabs';
import { esAdmin } from '@/lib/auth';

/**
 * Panel de gestion de modelos y fine-tuning
 * Permite construir datasets, entrenar modelos LoRA, ejecutar benchmarks
 * y comparar resultados entre proveedores.
 * Sprint 9 — CecilIA v2
 */

interface DependenciasInfo {
  torch: boolean;
  cuda_disponible: boolean;
  gpu_nombre?: string;
  gpu_memoria_gb?: number;
  transformers: boolean;
  peft: boolean;
  bitsandbytes: boolean;
  datasets: boolean;
  todas_disponibles: boolean;
}

interface ResumenFinetuning {
  dependencias_listas: boolean;
  cuda_disponible: boolean;
  gpu: string;
  tiene_modelo_entrenado: boolean;
  benchmarks_ejecutados: number;
  tareas_activas: number;
  tareas_resumen: Record<string, number>;
}

interface ResultadoBenchmark {
  archivo: string;
  modelo: string;
  tipo: string;
  fecha: string;
  promedio: number;
}

interface PreguntaBenchmark {
  id: string;
  categoria: string;
  pregunta: string;
  criterios: string;
}

const API_BASE = '/api/modelos';

async function apiFetch(ruta: string, opciones?: RequestInit) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  const res = await fetch(`${API_BASE}${ruta}`, {
    ...opciones,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...opciones?.headers,
    },
  });
  if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);
  return res.json();
}

export default function PaginaModelos() {
  const [tieneAcceso, setTieneAcceso] = useState(true);
  const [cargando, setCargando] = useState(true);
  const [resumen, setResumen] = useState<ResumenFinetuning | null>(null);
  const [dependencias, setDependencias] = useState<DependenciasInfo | null>(null);
  const [resultados, setResultados] = useState<ResultadoBenchmark[]>([]);
  const [preguntas, setPreguntas] = useState<PreguntaBenchmark[]>([]);
  const [categorias, setCategorias] = useState<string[]>([]);
  const [ejecutando, setEjecutando] = useState<string | null>(null);
  const [mensajeExito, setMensajeExito] = useState('');
  const [mensajeError, setMensajeError] = useState('');

  useEffect(() => {
    setTieneAcceso(esAdmin());
  }, []);

  const cargarDatos = useCallback(async () => {
    setCargando(true);
    try {
      const [res, deps, bench, pregs] = await Promise.allSettled([
        apiFetch('/resumen'),
        apiFetch('/train/dependencias'),
        apiFetch('/benchmark/resultados'),
        apiFetch('/benchmark/preguntas'),
      ]);

      if (res.status === 'fulfilled') setResumen(res.value);
      if (deps.status === 'fulfilled') setDependencias(deps.value.dependencias);
      if (bench.status === 'fulfilled') setResultados(bench.value.resultados || []);
      if (pregs.status === 'fulfilled') {
        setPreguntas(pregs.value.preguntas || []);
        setCategorias(pregs.value.categorias || []);
      }
    } catch (err) {
      console.error('Error cargando datos:', err);
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    if (tieneAcceso) cargarDatos();
  }, [tieneAcceso, cargarDatos]);

  const construirDataset = async () => {
    setEjecutando('dataset');
    setMensajeError('');
    try {
      const resp = await apiFetch('/dataset/construir', {
        method: 'POST',
        body: JSON.stringify({ categorias: null }),
      });
      setMensajeExito(`Dataset generado: ${resp.estadisticas?.total_ejemplos || 0} ejemplos`);
      setTimeout(() => setMensajeExito(''), 5000);
    } catch (err: any) {
      setMensajeError(err.message);
    } finally {
      setEjecutando(null);
    }
  };

  const ejecutarBenchmark = async () => {
    setEjecutando('benchmark');
    setMensajeError('');
    try {
      const resp = await apiFetch('/benchmark/ejecutar', {
        method: 'POST',
        body: JSON.stringify({ proveedores: ['base'], categorias: null, usar_evaluador_llm: false }),
      });
      setMensajeExito(`Benchmark iniciado: ${resp.tarea_id}`);
      setTimeout(() => {
        setMensajeExito('');
        cargarDatos();
      }, 5000);
    } catch (err: any) {
      setMensajeError(err.message);
    } finally {
      setEjecutando(null);
    }
  };

  const descargarInforme = async () => {
    setEjecutando('informe');
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/benchmark/informe`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error('No hay informes disponibles');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `informe_benchmark_${new Date().toISOString().slice(0, 10)}.docx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setMensajeError(err.message);
    } finally {
      setEjecutando(null);
    }
  };

  if (!tieneAcceso) {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <div className="text-center max-w-md">
          <AlertTriangle className="mx-auto h-16 w-16 text-[#2D3748] mb-4" />
          <h2 className="font-titulo text-xl font-semibold text-[#E8EAED] mb-2">Acceso restringido</h2>
          <p className="text-sm text-[#9AA0A6]">Solo administradores pueden acceder a la gestion de modelos.</p>
        </div>
      </div>
    );
  }

  const categoriaNombre: Record<string, string> = {
    normativo: 'Normativo y Legal',
    hallazgos: 'Hallazgos de Auditoria',
    materialidad: 'Materialidad y Muestreo',
    financiero: 'Auditoria Financiera',
    contratacion: 'Contratacion Publica',
  };

  const preguntasPorCategoria = categorias.reduce((acc, cat) => {
    acc[cat] = preguntas.filter(p => p.categoria === cat);
    return acc;
  }, {} as Record<string, PreguntaBenchmark[]>);

  return (
    <div className="p-6">
      {/* Encabezado */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-titulo text-xl font-bold text-[#E8EAED] flex items-center gap-2">
            <Brain className="h-6 w-6 text-[#C9A84C]" />
            Gestion de Modelos IA
          </h1>
          <p className="mt-1 text-xs text-[#5F6368]">
            Fine-tuning LoRA, benchmark y comparativa de modelos — Sprint 9
          </p>
        </div>
        <Boton variante="secundario" onClick={cargarDatos} disabled={cargando}>
          <RefreshCw className={`h-4 w-4 ${cargando ? 'animate-spin' : ''}`} />
          Actualizar
        </Boton>
      </div>

      {/* Mensajes */}
      {mensajeExito && (
        <div className="mb-4 flex items-center gap-2 rounded-lg bg-green-500/10 border border-green-500/20 p-3 text-xs text-green-400">
          <CheckCircle className="h-4 w-4" />
          {mensajeExito}
        </div>
      )}
      {mensajeError && (
        <div className="mb-4 flex items-center gap-2 rounded-lg bg-red-500/10 border border-red-500/20 p-3 text-xs text-red-400">
          <XCircle className="h-4 w-4" />
          {mensajeError}
          <button onClick={() => setMensajeError('')} className="ml-auto text-red-400 hover:text-red-300">&times;</button>
        </div>
      )}

      {/* Contadores */}
      <div className="mb-6 grid grid-cols-2 md:grid-cols-4 gap-3">
        <Tarjeta className="p-4">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-[#C9A84C]/10 p-2.5">
              <Cpu className="h-5 w-5 text-[#C9A84C]" />
            </div>
            <div>
              <p className="text-[10px] text-[#5F6368] uppercase tracking-wider">GPU</p>
              <p className="text-sm font-semibold text-[#E8EAED]">{resumen?.gpu || 'N/A'}</p>
              <Insignia variante={resumen?.cuda_disponible ? 'exito' : 'gris'}>
                {resumen?.cuda_disponible ? 'CUDA activo' : 'Sin CUDA'}
              </Insignia>
            </div>
          </div>
        </Tarjeta>

        <Tarjeta className="p-4">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-[#2471A3]/10 p-2.5">
              <Layers className="h-5 w-5 text-[#2471A3]" />
            </div>
            <div>
              <p className="text-[10px] text-[#5F6368] uppercase tracking-wider">Dependencias</p>
              <p className="text-sm font-semibold text-[#E8EAED]">
                {resumen?.dependencias_listas ? 'Listas' : 'Incompletas'}
              </p>
              <Insignia variante={resumen?.dependencias_listas ? 'exito' : 'rojo'}>
                {resumen?.dependencias_listas ? 'OK' : 'Faltan paquetes'}
              </Insignia>
            </div>
          </div>
        </Tarjeta>

        <Tarjeta className="p-4">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-[#9B59B6]/10 p-2.5">
              <Brain className="h-5 w-5 text-[#9B59B6]" />
            </div>
            <div>
              <p className="text-[10px] text-[#5F6368] uppercase tracking-wider">Modelo LoRA</p>
              <p className="text-sm font-semibold text-[#E8EAED]">
                {resumen?.tiene_modelo_entrenado ? 'Entrenado' : 'Sin modelo'}
              </p>
              <Insignia variante={resumen?.tiene_modelo_entrenado ? 'exito' : 'gris'}>
                {resumen?.tiene_modelo_entrenado ? 'Disponible' : 'Pendiente'}
              </Insignia>
            </div>
          </div>
        </Tarjeta>

        <Tarjeta className="p-4">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-[#27AE60]/10 p-2.5">
              <BarChart3 className="h-5 w-5 text-[#27AE60]" />
            </div>
            <div>
              <p className="text-[10px] text-[#5F6368] uppercase tracking-wider">Benchmarks</p>
              <p className="text-sm font-semibold text-[#E8EAED]">{resumen?.benchmarks_ejecutados || 0}</p>
              <p className="text-[10px] text-[#5F6368]">{resumen?.tareas_activas || 0} tareas activas</p>
            </div>
          </div>
        </Tarjeta>
      </div>

      {/* Tabs principales */}
      <Pestanas defaultValue="resumen">
        <ListaPestanas className="w-auto mb-4">
          <DisparadorPestana value="resumen" className="text-xs">
            <TrendingUp className="h-3.5 w-3.5 mr-1.5" />
            Resumen
          </DisparadorPestana>
          <DisparadorPestana value="dataset" className="text-xs">
            <Database className="h-3.5 w-3.5 mr-1.5" />
            Dataset
          </DisparadorPestana>
          <DisparadorPestana value="benchmark" className="text-xs">
            <BarChart3 className="h-3.5 w-3.5 mr-1.5" />
            Benchmark
          </DisparadorPestana>
          <DisparadorPestana value="preguntas" className="text-xs">
            <FileText className="h-3.5 w-3.5 mr-1.5" />
            Preguntas (50)
          </DisparadorPestana>
          <DisparadorPestana value="config" className="text-xs">
            <Settings className="h-3.5 w-3.5 mr-1.5" />
            Configuracion
          </DisparadorPestana>
        </ListaPestanas>

        {/* Tab: Resumen */}
        <ContenidoPestana value="resumen">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Pipeline status */}
            <Tarjeta className="p-5">
              <h3 className="text-sm font-medium text-[#E8EAED] mb-4 flex items-center gap-2">
                <Zap className="h-4 w-4 text-[#C9A84C]" />
                Pipeline de Fine-tuning
              </h3>
              <div className="space-y-3">
                {[
                  { paso: '1. Construir dataset JSONL', estado: 'listo', accion: construirDataset },
                  { paso: '2. Entrenar modelo LoRA', estado: resumen?.tiene_modelo_entrenado ? 'completado' : 'pendiente', accion: null },
                  { paso: '3. Ejecutar benchmark', estado: (resumen?.benchmarks_ejecutados || 0) > 0 ? 'completado' : 'pendiente', accion: ejecutarBenchmark },
                  { paso: '4. Merge y despliegue', estado: 'pendiente', accion: null },
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between rounded-lg bg-[#0A0F14]/60 p-3 border border-[#2D3748]/30">
                    <div className="flex items-center gap-2">
                      {item.estado === 'completado' ? (
                        <CheckCircle className="h-4 w-4 text-green-400" />
                      ) : item.estado === 'listo' ? (
                        <Play className="h-4 w-4 text-[#C9A84C]" />
                      ) : (
                        <Clock className="h-4 w-4 text-[#5F6368]" />
                      )}
                      <span className="text-xs text-[#E8EAED]">{item.paso}</span>
                    </div>
                    {item.accion && (
                      <button
                        onClick={item.accion}
                        disabled={ejecutando !== null}
                        className="rounded px-2 py-1 text-[10px] bg-[#C9A84C]/10 text-[#C9A84C] hover:bg-[#C9A84C]/20 transition-colors disabled:opacity-50"
                      >
                        {ejecutando ? <Loader2 className="h-3 w-3 animate-spin" /> : 'Ejecutar'}
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </Tarjeta>

            {/* Dependencias */}
            <Tarjeta className="p-5">
              <h3 className="text-sm font-medium text-[#E8EAED] mb-4 flex items-center gap-2">
                <Layers className="h-4 w-4 text-[#2471A3]" />
                Dependencias de Entrenamiento
              </h3>
              <div className="space-y-2">
                {dependencias && Object.entries(dependencias)
                  .filter(([k]) => ['torch', 'transformers', 'peft', 'bitsandbytes', 'datasets', 'trl', 'cuda_disponible'].includes(k))
                  .map(([nombre, estado]) => (
                    <div key={nombre} className="flex items-center justify-between text-xs">
                      <span className="text-[#9AA0A6] font-codigo">{nombre}</span>
                      <div className="flex items-center gap-1.5">
                        <span className={`h-1.5 w-1.5 rounded-full ${estado ? 'bg-green-400' : 'bg-red-400'}`} />
                        <span className={estado ? 'text-green-400' : 'text-red-400'}>
                          {estado ? 'Disponible' : 'No instalado'}
                        </span>
                      </div>
                    </div>
                  ))}
                {dependencias?.gpu_nombre && (
                  <div className="mt-3 pt-3 border-t border-[#2D3748]/30 text-xs">
                    <span className="text-[#5F6368]">GPU: </span>
                    <span className="text-[#E8EAED] font-codigo">{dependencias.gpu_nombre}</span>
                    {dependencias.gpu_memoria_gb && (
                      <span className="text-[#5F6368]"> ({dependencias.gpu_memoria_gb} GB)</span>
                    )}
                  </div>
                )}
              </div>
            </Tarjeta>
          </div>
        </ContenidoPestana>

        {/* Tab: Dataset */}
        <ContenidoPestana value="dataset">
          <div className="space-y-4">
            <Tarjeta className="p-5">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-[#E8EAED] flex items-center gap-2">
                  <Database className="h-4 w-4 text-[#C9A84C]" />
                  Construccion de Dataset JSONL
                </h3>
                <Boton
                  variante="primario"
                  onClick={construirDataset}
                  disabled={ejecutando === 'dataset'}
                >
                  {ejecutando === 'dataset' ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                  Construir Dataset
                </Boton>
              </div>

              <p className="text-xs text-[#9AA0A6] mb-4">
                Genera un archivo JSONL con ejemplos de entrenamiento anonimizados (Ley 1581/2012)
                en 5 categorias de control fiscal colombiano.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                {[
                  { cat: 'hallazgos', desc: 'Redaccion de hallazgos con 4 elementos', ejemplo: 3, color: '#E74C3C' },
                  { cat: 'preguntas_frecuentes', desc: 'Conceptos basicos de control fiscal', ejemplo: 4, color: '#3498DB' },
                  { cat: 'interpretaciones_normativas', desc: 'Analisis de leyes y decretos', ejemplo: 3, color: '#9B59B6' },
                  { cat: 'calculos_materialidad', desc: 'NIA 320, 450, muestreo', ejemplo: 2, color: '#F39C12' },
                  { cat: 'contratacion', desc: 'Ley 80/1993, modalidades', ejemplo: 2, color: '#27AE60' },
                ].map((item) => (
                  <div key={item.cat} className="rounded-lg bg-[#0A0F14]/60 p-3 border border-[#2D3748]/30">
                    <div className="flex items-center gap-1.5 mb-1">
                      <span className="h-2 w-2 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="text-[10px] font-medium text-[#E8EAED] uppercase">{item.cat.replace('_', ' ')}</span>
                    </div>
                    <p className="text-[10px] text-[#5F6368] mb-1">{item.desc}</p>
                    <p className="text-xs text-[#C9A84C] font-semibold">{item.ejemplo} ejemplos</p>
                  </div>
                ))}
              </div>
            </Tarjeta>

            <Tarjeta className="p-5">
              <h3 className="text-sm font-medium text-[#E8EAED] mb-3">Formato JSONL</h3>
              <pre className="rounded-lg bg-[#0A0F14] p-4 text-[10px] text-[#9AA0A6] font-codigo overflow-x-auto border border-[#2D3748]/30">
{`{
  "instruction": "Redacta un hallazgo de auditoria...",
  "input": "La Entidad ABC suscribio 12 contratos...",
  "output": "HALLAZGO: Sobrecosto en contratacion...\\nCONDICION: ...\\nCRITERIO: ...",
  "metadata": {"categoria": "hallazgos", "anonimizado": true}
}`}
              </pre>
            </Tarjeta>
          </div>
        </ContenidoPestana>

        {/* Tab: Benchmark */}
        <ContenidoPestana value="benchmark">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-[#E8EAED]">Resultados de Benchmarks</h3>
              <div className="flex gap-2">
                <Boton
                  variante="secundario"
                  onClick={descargarInforme}
                  disabled={ejecutando === 'informe' || resultados.length === 0}
                >
                  {ejecutando === 'informe' ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Download className="h-4 w-4" />
                  )}
                  Descargar Informe DOCX
                </Boton>
                <Boton
                  variante="primario"
                  onClick={ejecutarBenchmark}
                  disabled={ejecutando === 'benchmark'}
                >
                  {ejecutando === 'benchmark' ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                  Ejecutar Benchmark
                </Boton>
              </div>
            </div>

            {resultados.length === 0 ? (
              <Tarjeta className="p-8 text-center">
                <BarChart3 className="mx-auto h-12 w-12 text-[#2D3748] mb-3" />
                <p className="text-sm text-[#9AA0A6]">No hay resultados de benchmark aun.</p>
                <p className="text-xs text-[#5F6368] mt-1">
                  Ejecute un benchmark para comparar modelos en las 50 preguntas de control fiscal.
                </p>
              </Tarjeta>
            ) : (
              <Tarjeta>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-[#2D3748]">
                        <th className="p-3 text-left font-medium text-[#9AA0A6]">Modelo</th>
                        <th className="p-3 text-left font-medium text-[#9AA0A6]">Tipo</th>
                        <th className="p-3 text-center font-medium text-[#9AA0A6]">Promedio</th>
                        <th className="p-3 text-left font-medium text-[#9AA0A6]">Fecha</th>
                      </tr>
                    </thead>
                    <tbody>
                      {resultados.map((r, i) => (
                        <tr key={i} className="border-b border-[#2D3748]/30 hover:bg-[#1A2332]/50">
                          <td className="p-3 font-medium text-[#E8EAED]">{r.modelo || r.archivo}</td>
                          <td className="p-3">
                            <Insignia variante={
                              r.tipo === 'finetuned' ? 'oro' :
                              r.tipo === 'claude' ? 'info' :
                              r.tipo === 'gemini' ? 'exito' : 'gris'
                            }>
                              {r.tipo}
                            </Insignia>
                          </td>
                          <td className="p-3 text-center">
                            <span className={`font-semibold ${
                              r.promedio >= 7 ? 'text-green-400' :
                              r.promedio >= 5 ? 'text-yellow-400' : 'text-red-400'
                            }`}>
                              {r.promedio.toFixed(1)}/10
                            </span>
                          </td>
                          <td className="p-3 text-[#5F6368]">{r.fecha?.slice(0, 10) || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Tarjeta>
            )}

            {/* Info sobre proveedores */}
            <Tarjeta className="p-5">
              <h3 className="text-sm font-medium text-[#E8EAED] mb-3">Proveedores disponibles</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {[
                  { id: 'base', nombre: 'Modelo Base', desc: 'LLM principal (OpenAI/vLLM)', icono: Cpu, color: '#5F6368' },
                  { id: 'finetuned', nombre: 'Fine-tuned', desc: 'CecilIA v2 LoRA', icono: Brain, color: '#C9A84C' },
                  { id: 'claude', nombre: 'Claude', desc: 'Anthropic Claude Sonnet 4', icono: Zap, color: '#2471A3' },
                  { id: 'gemini', nombre: 'Gemini', desc: 'Google Gemini 2.0 Flash', icono: TrendingUp, color: '#27AE60' },
                ].map((prov) => (
                  <div key={prov.id} className="rounded-lg bg-[#0A0F14]/60 p-3 border border-[#2D3748]/30">
                    <div className="flex items-center gap-2 mb-1">
                      <prov.icono className="h-4 w-4" style={{ color: prov.color }} />
                      <span className="text-xs font-medium text-[#E8EAED]">{prov.nombre}</span>
                    </div>
                    <p className="text-[10px] text-[#5F6368]">{prov.desc}</p>
                  </div>
                ))}
              </div>
            </Tarjeta>
          </div>
        </ContenidoPestana>

        {/* Tab: Preguntas */}
        <ContenidoPestana value="preguntas">
          <div className="space-y-4">
            <p className="text-xs text-[#9AA0A6]">
              50 preguntas de evaluacion en 5 categorias del dominio de control fiscal colombiano.
            </p>

            {categorias.map((cat) => (
              <Tarjeta key={cat} className="p-4">
                <h3 className="text-sm font-medium text-[#E8EAED] mb-3 flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-[#C9A84C]" />
                  {categoriaNombre[cat] || cat}
                  <Insignia variante="gris">{preguntasPorCategoria[cat]?.length || 0}</Insignia>
                </h3>
                <div className="space-y-2">
                  {(preguntasPorCategoria[cat] || []).map((p) => (
                    <div key={p.id} className="rounded-lg bg-[#0A0F14]/60 p-3 border border-[#2D3748]/30">
                      <div className="flex items-start gap-2">
                        <span className="text-[10px] font-codigo text-[#C9A84C] mt-0.5">{p.id}</span>
                        <div>
                          <p className="text-xs text-[#E8EAED]">{p.pregunta}</p>
                          <p className="text-[10px] text-[#5F6368] mt-1 italic">
                            Criterios: {p.criterios}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Tarjeta>
            ))}
          </div>
        </ContenidoPestana>

        {/* Tab: Configuracion */}
        <ContenidoPestana value="config">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Tarjeta className="p-5">
              <h3 className="text-sm font-medium text-[#E8EAED] mb-4 flex items-center gap-2">
                <Settings className="h-4 w-4 text-[#C9A84C]" />
                Parametros LoRA por defecto
              </h3>
              <div className="space-y-2">
                {[
                  { param: 'Modelo base', valor: 'Qwen/Qwen2.5-7B-Instruct' },
                  { param: 'LoRA rank', valor: '16' },
                  { param: 'LoRA alpha', valor: '32' },
                  { param: 'Target modules', valor: 'q_proj, v_proj' },
                  { param: 'Dropout', valor: '0.05' },
                  { param: 'Cuantizacion', valor: 'QLoRA 4-bit NF4' },
                  { param: 'Epochs', valor: '3' },
                  { param: 'Learning rate', valor: '2e-4' },
                  { param: 'Batch size', valor: '4' },
                  { param: 'Max seq length', valor: '2048' },
                  { param: 'Checkpoints cada', valor: '100 pasos' },
                ].map((item) => (
                  <div key={item.param} className="flex items-center justify-between text-xs">
                    <span className="text-[#9AA0A6]">{item.param}</span>
                    <span className="font-codigo text-[#E8EAED]">{item.valor}</span>
                  </div>
                ))}
              </div>
            </Tarjeta>

            <Tarjeta className="p-5">
              <h3 className="text-sm font-medium text-[#E8EAED] mb-4 flex items-center gap-2">
                <Brain className="h-4 w-4 text-[#2471A3]" />
                Modelos compatibles
              </h3>
              <div className="space-y-3">
                {[
                  { modelo: 'Qwen/Qwen2.5-7B-Instruct', params: '7B', vram: '~6GB', rec: true },
                  { modelo: 'meta-llama/Llama-3.1-8B-Instruct', params: '8B', vram: '~7GB', rec: false },
                  { modelo: 'mistralai/Mistral-7B-Instruct-v0.3', params: '7B', vram: '~6GB', rec: false },
                  { modelo: 'Qwen/Qwen2.5-14B-Instruct', params: '14B', vram: '~12GB', rec: false },
                ].map((m) => (
                  <div key={m.modelo} className="flex items-center justify-between rounded-lg bg-[#0A0F14]/60 p-3 border border-[#2D3748]/30">
                    <div>
                      <p className="text-xs font-medium text-[#E8EAED] font-codigo">{m.modelo}</p>
                      <p className="text-[10px] text-[#5F6368]">{m.params} params | QLoRA: {m.vram}</p>
                    </div>
                    {m.rec && <Insignia variante="oro">Recomendado</Insignia>}
                  </div>
                ))}
              </div>
            </Tarjeta>
          </div>
        </ContenidoPestana>
      </Pestanas>
    </div>
  );
}
