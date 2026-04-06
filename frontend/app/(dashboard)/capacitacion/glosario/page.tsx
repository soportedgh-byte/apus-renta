'use client';

/**
 * CecilIA v2 — Glosario Interactivo de Control Fiscal
 * Busqueda instantanea, filtrado por categoria, definiciones simples y tecnicas
 * Sprint: Capacitacion 2.0
 */

import React, { useState, useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft, Search, BookMarked, Scale, Building2,
  FileText, ShoppingCart, ChevronDown, ChevronUp, ExternalLink,
  Loader2, Tag,
} from 'lucide-react';
import { apiCliente } from '@/lib/api';
import type { EntradaGlosario } from '@/lib/types';

const CATEGORIAS = [
  { id: 'todas', nombre: 'Todas', icono: BookMarked, color: '#C9A84C' },
  { id: 'auditoria', nombre: 'Auditoria', icono: Search, color: '#1A5276' },
  { id: 'normativa', nombre: 'Normativa', icono: Scale, color: '#8E44AD' },
  { id: 'financiero', nombre: 'Financiero', icono: FileText, color: '#27AE60' },
  { id: 'institucional', nombre: 'Institucional', icono: Building2, color: '#2471A3' },
  { id: 'contratacion', nombre: 'Contratacion', icono: ShoppingCart, color: '#E74C3C' },
];

function TarjetaGlosario({ entrada }: { entrada: EntradaGlosario }) {
  const [expandida, setExpandida] = useState(false);

  const cat = CATEGORIAS.find((c) => c.id === entrada.categoria) || CATEGORIAS[0];

  return (
    <div className="rounded-lg border border-[#2D3748]/50 bg-[#1A2332]/40 overflow-hidden">
      <button
        onClick={() => setExpandida(!expandida)}
        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-[#1A2332]/70 transition-colors"
      >
        <div className="flex items-center gap-3 min-w-0">
          <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[9px] font-semibold" style={{ backgroundColor: `${cat.color}15`, color: cat.color }}>
            <Tag className="h-2.5 w-2.5" />
            {cat.nombre}
          </span>
          <h3 className="text-sm font-semibold text-[#E8EAED] truncate">{entrada.termino}</h3>
        </div>
        {expandida ? <ChevronUp className="h-4 w-4 text-[#5F6368] flex-shrink-0" /> : <ChevronDown className="h-4 w-4 text-[#5F6368] flex-shrink-0" />}
      </button>

      {!expandida && (
        <div className="px-4 pb-3">
          <p className="text-xs text-[#9AA0A6] line-clamp-2">{entrada.definicion_simple}</p>
        </div>
      )}

      {expandida && (
        <div className="px-4 pb-4 space-y-3 border-t border-[#2D3748]/30 pt-3">
          <div>
            <p className="text-[10px] font-semibold text-[#C9A84C] mb-1">Definicion simple</p>
            <p className="text-xs text-[#E8EAED] leading-relaxed">{entrada.definicion_simple}</p>
          </div>
          <div>
            <p className="text-[10px] font-semibold text-[#2471A3] mb-1">Definicion tecnica</p>
            <p className="text-xs text-[#9AA0A6] leading-relaxed">{entrada.definicion_tecnica}</p>
          </div>
          {entrada.ejemplo && (
            <div className="rounded-lg bg-[#0A0F14]/60 p-3 border border-[#2D3748]/30">
              <p className="text-[10px] font-semibold text-[#27AE60] mb-1">Ejemplo</p>
              <p className="text-xs text-[#9AA0A6] leading-relaxed italic">{entrada.ejemplo}</p>
            </div>
          )}
          {entrada.norma_aplicable && (
            <div className="flex items-start gap-2">
              <Scale className="h-3.5 w-3.5 text-[#8E44AD] mt-0.5 flex-shrink-0" />
              <p className="text-[10px] text-[#8E44AD]">{entrada.norma_aplicable}</p>
            </div>
          )}
          {entrada.terminos_relacionados.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[10px] text-[#5F6368]">Relacionados:</span>
              {entrada.terminos_relacionados.map((t) => (
                <span key={t} className="rounded-full bg-[#2D3748]/30 px-2 py-0.5 text-[9px] text-[#9AA0A6]">
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function PaginaGlosario() {
  const router = useRouter();
  const [entradas, setEntradas] = useState<EntradaGlosario[]>([]);
  const [busqueda, setBusqueda] = useState('');
  const [categoriaActiva, setCategoriaActiva] = useState('todas');
  const [cargando, setCargando] = useState(true);

  useEffect(() => { cargarGlosario(); }, []);

  const cargarGlosario = async () => {
    setCargando(true);
    try {
      const resp = await apiCliente.get<EntradaGlosario[]>('/capacitacion/glosario');
      setEntradas(resp);
    } catch {
      setEntradas([]);
    } finally {
      setCargando(false);
    }
  };

  const entradasFiltradas = useMemo(() => {
    let resultado = entradas;
    if (categoriaActiva !== 'todas') {
      resultado = resultado.filter((e) => e.categoria === categoriaActiva);
    }
    if (busqueda.trim()) {
      const q = busqueda.toLowerCase();
      resultado = resultado.filter(
        (e) => e.termino.toLowerCase().includes(q) || e.definicion_simple.toLowerCase().includes(q)
      );
    }
    return resultado;
  }, [entradas, categoriaActiva, busqueda]);

  return (
    <div className="flex flex-col h-full bg-[#0F1419] text-[#E8EAED] overflow-y-auto">
      {/* Header */}
      <div className="border-b border-[#2D3748]/30 px-6 py-4 space-y-3">
        <div className="flex items-center gap-3">
          <button onClick={() => router.push('/capacitacion')} className="flex items-center gap-1 text-[10px] text-[#5F6368] hover:text-[#9AA0A6]">
            <ArrowLeft className="h-3 w-3" />
          </button>
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#27AE60]/10 border border-[#27AE60]/20">
            <BookMarked className="h-5 w-5 text-[#27AE60]" />
          </div>
          <div>
            <h1 className="text-base font-bold text-[#27AE60]">Glosario de Control Fiscal</h1>
            <p className="text-[10px] text-[#5F6368]">{entradas.length} terminos disponibles</p>
          </div>
        </div>

        {/* Barra de busqueda */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#5F6368]" />
          <input
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            placeholder="Buscar termino..."
            className="w-full rounded-lg bg-[#1A2332] border border-[#2D3748]/50 pl-9 pr-4 py-2.5 text-xs text-[#E8EAED] placeholder-[#5F6368] outline-none focus:border-[#27AE60]/50"
          />
        </div>

        {/* Filtros de categoria */}
        <div className="flex gap-2 overflow-x-auto pb-1">
          {CATEGORIAS.map((cat) => {
            const Icono = cat.icono;
            const activa = categoriaActiva === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setCategoriaActiva(cat.id)}
                className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-[10px] font-medium whitespace-nowrap transition-colors ${
                  activa
                    ? 'border text-white'
                    : 'border border-[#2D3748]/50 text-[#5F6368] hover:text-[#9AA0A6]'
                }`}
                style={activa ? { backgroundColor: `${cat.color}20`, borderColor: `${cat.color}40`, color: cat.color } : {}}
              >
                <Icono className="h-3 w-3" />
                {cat.nombre}
              </button>
            );
          })}
        </div>
      </div>

      {/* Lista */}
      <div className="flex-1 p-6 space-y-2">
        {cargando ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 text-[#27AE60] animate-spin" />
          </div>
        ) : entradasFiltradas.length === 0 ? (
          <div className="text-center py-12">
            <BookMarked className="h-10 w-10 text-[#2D3748] mx-auto mb-3" />
            <p className="text-sm text-[#5F6368]">
              {busqueda ? `No se encontraron terminos para "${busqueda}"` : 'El glosario esta vacio. Ejecuta el seed para poblarlo.'}
            </p>
          </div>
        ) : (
          entradasFiltradas.map((entrada) => (
            <TarjetaGlosario key={entrada.id} entrada={entrada} />
          ))
        )}
      </div>

      <div className="border-t border-[#2D3748]/30 px-6 py-3 text-center">
        <p className="text-[10px] text-[#5F6368]">
          Definiciones con fines educativos — Consulte siempre la norma vigente — Circular 023 CGR
        </p>
      </div>
    </div>
  );
}
