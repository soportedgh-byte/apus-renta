'use client';

import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  Cpu,
  Clock,
  MessageSquare,
  Users,
  TrendingUp,
  Activity,
  Database,
  ShieldAlert,
} from 'lucide-react';
import { Tarjeta } from '@/components/ui/card';
import { Insignia } from '@/components/ui/badge';
import { esDirector, esAdmin } from '@/lib/auth';

/**
 * Pagina de analitica y metricas del sistema
 * Accesible solo para directores y administradores
 */
export default function PaginaAnalytics() {
  const [tieneAcceso, setTieneAcceso] = useState(true);

  useEffect(() => {
    setTieneAcceso(esDirector() || esAdmin());
  }, []);

  if (!tieneAcceso) {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <div className="text-center max-w-md">
          <ShieldAlert className="mx-auto h-16 w-16 text-[#2D3748] mb-4" />
          <h2 className="font-titulo text-xl font-semibold text-[#E8EAED] mb-2">
            Acceso restringido
          </h2>
          <p className="text-sm text-[#9AA0A6]">
            Las metricas y analitica estan disponibles unicamente para directores y administradores.
          </p>
        </div>
      </div>
    );
  }

  /** Metricas de ejemplo */
  const metricas = [
    { titulo: 'Consultas totales', valor: '12,847', cambio: '+18%', icono: MessageSquare, color: '#C9A84C' },
    { titulo: 'Usuarios activos', valor: '156', cambio: '+5%', icono: Users, color: '#2471A3' },
    { titulo: 'Tiempo promedio', valor: '2.3s', cambio: '-12%', icono: Clock, color: '#27AE60' },
    { titulo: 'Tokens consumidos', valor: '45.2M', cambio: '+22%', icono: Activity, color: '#9B59B6' },
  ];

  const modelos = [
    { nombre: 'claude-sonnet-4-20250514', consultas: 8420, tiempo: 1800, tokens: 32100000, satisfaccion: 94 },
    { nombre: 'claude-3.5-haiku', consultas: 3127, tiempo: 850, tokens: 8900000, satisfaccion: 88 },
    { nombre: 'gpt-4o', consultas: 1300, tiempo: 2400, tokens: 4200000, satisfaccion: 91 },
  ];

  const registrosTraza = [
    { fecha: '2026-04-02 14:32:15', usuario: 'Dr. Rodriguez', accion: 'Consulta chat', modelo: 'claude-sonnet-4-20250514', tokens: 4250 },
    { fecha: '2026-04-02 14:28:03', usuario: 'Ana Gomez', accion: 'Generacion hallazgo', modelo: 'claude-sonnet-4-20250514', tokens: 6800 },
    { fecha: '2026-04-02 14:15:42', usuario: 'Luis Martinez', accion: 'Analisis documento', modelo: 'claude-3.5-haiku', tokens: 2100 },
    { fecha: '2026-04-02 13:55:21', usuario: 'Dra. Ruiz', accion: 'Generacion formato', modelo: 'claude-sonnet-4-20250514', tokens: 8500 },
    { fecha: '2026-04-02 13:40:10', usuario: 'Jorge Perez', accion: 'Consulta normativa', modelo: 'claude-3.5-haiku', tokens: 1800 },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Encabezado */}
      <div>
        <h1 className="font-titulo text-xl font-bold text-[#E8EAED] flex items-center gap-2">
          <BarChart3 className="h-6 w-6 text-[#C9A84C]" />
          Analitica del Sistema
        </h1>
        <p className="mt-1 text-xs text-[#5F6368]">
          Metricas de uso, rendimiento de modelos y trazabilidad
        </p>
      </div>

      {/* Tarjetas de metricas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {metricas.map((metrica) => (
          <Tarjeta key={metrica.titulo} className="p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg"
                style={{ backgroundColor: `${metrica.color}15` }}>
                <metrica.icono className="h-4.5 w-4.5" style={{ color: metrica.color }} />
              </div>
              <span className={`text-xs font-medium ${
                metrica.cambio.startsWith('+') ? 'text-green-400' : 'text-red-400'
              }`}>
                {metrica.cambio}
              </span>
            </div>
            <p className="text-2xl font-bold text-[#E8EAED]">{metrica.valor}</p>
            <p className="text-[10px] text-[#5F6368] mt-1">{metrica.titulo}</p>
          </Tarjeta>
        ))}
      </div>

      {/* Rendimiento de modelos */}
      <Tarjeta>
        <div className="p-5">
          <h2 className="font-titulo text-base font-semibold text-[#E8EAED] mb-4 flex items-center gap-2">
            <Cpu className="h-4 w-4 text-[#C9A84C]" />
            Rendimiento de Modelos
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-[#2D3748]">
                  <th className="pb-2 text-left font-medium text-[#9AA0A6]">Modelo</th>
                  <th className="pb-2 text-right font-medium text-[#9AA0A6]">Consultas</th>
                  <th className="pb-2 text-right font-medium text-[#9AA0A6]">Tiempo prom.</th>
                  <th className="pb-2 text-right font-medium text-[#9AA0A6]">Tokens</th>
                  <th className="pb-2 text-right font-medium text-[#9AA0A6]">Satisfaccion</th>
                </tr>
              </thead>
              <tbody>
                {modelos.map((modelo) => (
                  <tr key={modelo.nombre} className="border-b border-[#2D3748]/30">
                    <td className="py-3 font-codigo text-[#E8EAED]">{modelo.nombre}</td>
                    <td className="py-3 text-right text-[#E8EAED]">{modelo.consultas.toLocaleString()}</td>
                    <td className="py-3 text-right text-[#E8EAED]">{modelo.tiempo}ms</td>
                    <td className="py-3 text-right text-[#E8EAED]">{(modelo.tokens / 1000000).toFixed(1)}M</td>
                    <td className="py-3 text-right">
                      <span className={`font-medium ${
                        modelo.satisfaccion >= 90 ? 'text-green-400' : 'text-yellow-400'
                      }`}>
                        {modelo.satisfaccion}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </Tarjeta>

      {/* Grafico placeholder */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Tarjeta className="p-5">
          <h3 className="text-sm font-medium text-[#E8EAED] mb-4 flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-[#27AE60]" />
            Consultas por dia (ultimos 30 dias)
          </h3>
          <div className="flex h-40 items-center justify-center rounded-lg bg-[#0A0F14]/60 border border-[#2D3748]/30">
            <p className="text-xs text-[#5F6368]">Grafico de tendencia — Disponible con datos reales</p>
          </div>
        </Tarjeta>

        <Tarjeta className="p-5">
          <h3 className="text-sm font-medium text-[#E8EAED] mb-4 flex items-center gap-2">
            <Database className="h-4 w-4 text-[#2471A3]" />
            Distribucion de tokens por modelo
          </h3>
          <div className="flex h-40 items-center justify-center rounded-lg bg-[#0A0F14]/60 border border-[#2D3748]/30">
            <p className="text-xs text-[#5F6368]">Grafico circular — Disponible con datos reales</p>
          </div>
        </Tarjeta>
      </div>

      {/* Registros de trazabilidad */}
      <Tarjeta>
        <div className="p-5">
          <h2 className="font-titulo text-base font-semibold text-[#E8EAED] mb-4">
            Registros de trazabilidad recientes
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-[#2D3748]">
                  <th className="pb-2 text-left font-medium text-[#9AA0A6]">Fecha/Hora</th>
                  <th className="pb-2 text-left font-medium text-[#9AA0A6]">Usuario</th>
                  <th className="pb-2 text-left font-medium text-[#9AA0A6]">Accion</th>
                  <th className="pb-2 text-left font-medium text-[#9AA0A6]">Modelo</th>
                  <th className="pb-2 text-right font-medium text-[#9AA0A6]">Tokens</th>
                </tr>
              </thead>
              <tbody>
                {registrosTraza.map((reg, idx) => (
                  <tr key={idx} className="border-b border-[#2D3748]/30">
                    <td className="py-2.5 font-codigo text-[#5F6368]">{reg.fecha}</td>
                    <td className="py-2.5 text-[#E8EAED]">{reg.usuario}</td>
                    <td className="py-2.5 text-[#9AA0A6]">{reg.accion}</td>
                    <td className="py-2.5 font-codigo text-[#5F6368]">{reg.modelo}</td>
                    <td className="py-2.5 text-right text-[#E8EAED]">{reg.tokens.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </Tarjeta>
    </div>
  );
}
