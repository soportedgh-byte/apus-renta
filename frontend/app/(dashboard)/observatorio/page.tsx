'use client';

import React, { useState, useEffect } from 'react';
import {
  Eye,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Minus,
  BarChart3,
  Activity,
  ShieldAlert,
} from 'lucide-react';
import { Tarjeta } from '@/components/ui/card';
import { Insignia } from '@/components/ui/badge';
import { obtenerDireccionActiva } from '@/lib/auth';
import type { AlertaObservatorio, IndicadorSectorial } from '@/lib/types';

/**
 * Pagina del Observatorio Sectorial (solo DES)
 * Muestra alertas, indicadores sectoriales y analisis macro
 */
export default function PaginaObservatorio() {
  const [direccion, setDireccion] = useState<string | null>(null);
  const [alertas, setAlertas] = useState<AlertaObservatorio[]>([]);

  useEffect(() => {
    setDireccion(obtenerDireccionActiva());

    // Datos de ejemplo
    setAlertas([
      {
        id: '1',
        titulo: 'Subejecucion presupuestal critica en el sector TIC',
        sector: 'Tecnologias de la Informacion',
        severidad: 'alta',
        descripcion: 'Se detecta una subejecucion del 45% en el presupuesto de inversion del sector TIC al corte del tercer trimestre, significativamente por debajo del promedio historico del 28%.',
        indicadores: [
          { nombre: 'Ejecucion presupuestal', valor_actual: 55, valor_anterior: 72, unidad: '%', tendencia: 'baja' },
          { nombre: 'Contratos en ejecucion', valor_actual: 23, valor_anterior: 45, unidad: 'contratos', tendencia: 'baja' },
        ],
        fecha_deteccion: '2025-10-15T08:00:00Z',
        estado: 'en_analisis',
      },
      {
        id: '2',
        titulo: 'Incremento atipico en contratacion directa - Sector Salud',
        sector: 'Salud',
        severidad: 'media',
        descripcion: 'La contratacion directa en el sector salud aumento un 30% respecto al mismo periodo del ano anterior, superando los umbrales normales establecidos.',
        indicadores: [
          { nombre: 'Contratacion directa', valor_actual: 892, valor_anterior: 686, unidad: 'contratos', tendencia: 'alza' },
          { nombre: 'Valor promedio contrato', valor_actual: 450, valor_anterior: 320, unidad: 'M COP', tendencia: 'alza' },
        ],
        fecha_deteccion: '2025-10-10T14:00:00Z',
        estado: 'nueva',
      },
      {
        id: '3',
        titulo: 'Mejora sostenida en rendicion de cuentas - Sector Educacion',
        sector: 'Educacion',
        severidad: 'baja',
        descripcion: 'El indice de rendicion de cuentas del sector educacion ha mejorado consistentemente en los ultimos 3 trimestres, alcanzando un nivel satisfactorio.',
        indicadores: [
          { nombre: 'Indice rendicion de cuentas', valor_actual: 87, valor_anterior: 78, unidad: '%', tendencia: 'alza' },
        ],
        fecha_deteccion: '2025-10-08T10:00:00Z',
        estado: 'resuelta',
      },
    ]);
  }, []);

  // Verificar acceso DES
  if (direccion && direccion !== 'DES') {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <div className="text-center max-w-md">
          <ShieldAlert className="mx-auto h-16 w-16 text-[#2D3748] mb-4" />
          <h2 className="font-titulo text-xl font-semibold text-[#E8EAED] mb-2">
            Acceso restringido
          </h2>
          <p className="text-sm text-[#9AA0A6] mb-1">
            El Observatorio Sectorial esta disponible unicamente para la
            Direccion de Estudios Sectoriales (DES).
          </p>
          <p className="text-xs text-[#5F6368]">
            Si necesita acceso, contacte al administrador del sistema.
          </p>
        </div>
      </div>
    );
  }

  const colorSeveridad = {
    baja: { bg: 'bg-green-500/10', texto: 'text-green-400', borde: 'border-green-500/30' },
    media: { bg: 'bg-yellow-500/10', texto: 'text-yellow-400', borde: 'border-yellow-500/30' },
    alta: { bg: 'bg-orange-500/10', texto: 'text-orange-400', borde: 'border-orange-500/30' },
    critica: { bg: 'bg-red-500/10', texto: 'text-red-400', borde: 'border-red-500/30' },
  };

  const iconoTendencia = {
    alza: <TrendingUp className="h-3 w-3 text-green-400" />,
    baja: <TrendingDown className="h-3 w-3 text-red-400" />,
    estable: <Minus className="h-3 w-3 text-[#5F6368]" />,
  };

  return (
    <div className="p-6">
      {/* Encabezado */}
      <div className="mb-6">
        <h1 className="font-titulo text-xl font-bold text-[#E8EAED] flex items-center gap-2">
          <Eye className="h-6 w-6 text-[#1A5276]" />
          Observatorio Sectorial
        </h1>
        <p className="mt-1 text-xs text-[#5F6368]">
          Alertas tempranas, indicadores macroeconomicos y vigilancia sectorial — DES
        </p>
      </div>

      {/* Resumen de indicadores */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {[
          { titulo: 'Alertas activas', valor: '5', icono: AlertTriangle, color: '#C9A84C' },
          { titulo: 'Sectores monitoreados', valor: '18', icono: BarChart3, color: '#2471A3' },
          { titulo: 'Indicadores rastreados', valor: '142', icono: Activity, color: '#27AE60' },
          { titulo: 'Riesgo promedio', valor: 'Medio', icono: ShieldAlert, color: '#F39C12' },
        ].map((indicador) => (
          <Tarjeta key={indicador.titulo} className="p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg"
                style={{ backgroundColor: `${indicador.color}15` }}>
                <indicador.icono className="h-5 w-5" style={{ color: indicador.color }} />
              </div>
              <div>
                <p className="text-[10px] text-[#5F6368]">{indicador.titulo}</p>
                <p className="text-lg font-bold text-[#E8EAED]">{indicador.valor}</p>
              </div>
            </div>
          </Tarjeta>
        ))}
      </div>

      {/* Alertas */}
      <h2 className="font-titulo text-lg font-semibold text-[#E8EAED] mb-4">
        Alertas recientes
      </h2>
      <div className="space-y-4">
        {alertas.map((alerta) => {
          const sev = colorSeveridad[alerta.severidad];
          return (
            <Tarjeta key={alerta.id} className={`${sev.borde} border hover:border-opacity-60 transition-all`}>
              <div className="p-5">
                <div className="flex items-start justify-between gap-4 mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <AlertTriangle className={`h-4 w-4 ${sev.texto}`} />
                      <h3 className="text-sm font-medium text-[#E8EAED]">
                        {alerta.titulo}
                      </h3>
                    </div>
                    <p className="text-xs text-[#9AA0A6] leading-relaxed">
                      {alerta.descripcion}
                    </p>
                  </div>
                  <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
                    <Insignia
                      variante={
                        alerta.severidad === 'critica' || alerta.severidad === 'alta' ? 'rojo'
                          : alerta.severidad === 'media' ? 'amarillo' : 'exito'
                      }
                    >
                      {alerta.severidad.charAt(0).toUpperCase() + alerta.severidad.slice(1)}
                    </Insignia>
                    <Insignia variante="gris">{alerta.sector}</Insignia>
                  </div>
                </div>

                {/* Indicadores */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4 pt-3 border-t border-[#2D3748]/30">
                  {alerta.indicadores.map((ind, idx) => (
                    <div key={idx} className="rounded-lg bg-[#0A0F14]/60 p-2.5">
                      <p className="text-[10px] text-[#5F6368] mb-1">{ind.nombre}</p>
                      <div className="flex items-center gap-1.5">
                        <span className="text-sm font-bold text-[#E8EAED]">
                          {ind.valor_actual}
                        </span>
                        <span className="text-[10px] text-[#5F6368]">{ind.unidad}</span>
                        {iconoTendencia[ind.tendencia]}
                      </div>
                      <p className="text-[9px] text-[#5F6368] mt-0.5">
                        Anterior: {ind.valor_anterior} {ind.unidad}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </Tarjeta>
          );
        })}
      </div>
    </div>
  );
}
