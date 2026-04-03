'use client';

import React, { useState, useEffect } from 'react';
import {
  ClipboardList,
  Plus,
  Search,
  Filter,
  Calendar,
  Building2,
  Users,
  AlertTriangle,
  ChevronRight,
} from 'lucide-react';
import { Tarjeta } from '@/components/ui/card';
import { Insignia } from '@/components/ui/badge';
import { Boton } from '@/components/ui/button';
import { obtenerDireccionActiva } from '@/lib/auth';
import type { Auditoria, EstadoAuditoria, Direccion } from '@/lib/types';

/** Configuracion visual de estados de auditoria */
const configEstado: Record<EstadoAuditoria, { color: string; etiqueta: string }> = {
  planeacion: { color: '#2471A3', etiqueta: 'Planeacion' },
  ejecucion: { color: '#C9A84C', etiqueta: 'Ejecucion' },
  informe: { color: '#F39C12', etiqueta: 'Informe' },
  cierre: { color: '#27AE60', etiqueta: 'Cierre' },
  seguimiento: { color: '#9B59B6', etiqueta: 'Seguimiento' },
};

/**
 * Pagina de listado de auditorias
 * Muestra tabla/tarjetas con informacion de auditorias
 */
export default function PaginaAuditorias() {
  const [auditorias, setAuditorias] = useState<Auditoria[]>([]);
  const [busqueda, setBusqueda] = useState('');
  const [filtroEstado, setFiltroEstado] = useState<EstadoAuditoria | 'todos'>('todos');
  const [direccion, setDireccion] = useState<Direccion>('DES');

  useEffect(() => {
    const dir = obtenerDireccionActiva();
    if (dir) setDireccion(dir);

    // Datos de ejemplo
    setAuditorias([
      {
        id: '1',
        nombre: 'Auditoria Financiera MinTIC 2025',
        entidad_auditada: 'Ministerio de Tecnologias de la Informacion',
        sector: 'TIC',
        direccion: 'DVF',
        estado: 'ejecucion',
        responsable_id: 'user1',
        responsable_nombre: 'Dr. Carlos Rodriguez',
        fecha_inicio: '2025-03-01',
        descripcion: 'Auditoria financiera y de gestion a la ejecucion presupuestal del MinTIC.',
        equipo: ['Ana Gomez', 'Luis Martinez', 'Maria Lopez'],
        hallazgos_count: 3,
        fecha_creacion: '2025-02-15T10:00:00Z',
      },
      {
        id: '2',
        nombre: 'Auditoria de Cumplimiento DIAN',
        entidad_auditada: 'Direccion de Impuestos y Aduanas Nacionales',
        sector: 'Hacienda',
        direccion: 'DVF',
        estado: 'planeacion',
        responsable_id: 'user2',
        responsable_nombre: 'Dra. Patricia Ruiz',
        fecha_inicio: '2025-06-01',
        equipo: ['Jorge Perez', 'Sandra Torres'],
        hallazgos_count: 0,
        fecha_creacion: '2025-05-01T08:00:00Z',
      },
      {
        id: '3',
        nombre: 'Estudio Sectorial Transporte 2025',
        entidad_auditada: 'Sector Transporte',
        sector: 'Transporte',
        direccion: 'DES',
        estado: 'informe',
        responsable_id: 'user3',
        responsable_nombre: 'Dr. Fernando Diaz',
        fecha_inicio: '2025-01-15',
        fecha_fin: '2025-12-31',
        equipo: ['Carolina Vargas', 'Andres Mejia', 'Laura Hernandez', 'Pedro Sanchez'],
        hallazgos_count: 12,
        fecha_creacion: '2025-01-10T14:00:00Z',
      },
    ]);
  }, []);

  const auditoriasFiltradas = auditorias.filter((a) => {
    const coincideBusqueda =
      a.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
      a.entidad_auditada.toLowerCase().includes(busqueda.toLowerCase());
    const coincideEstado = filtroEstado === 'todos' || a.estado === filtroEstado;
    return coincideBusqueda && coincideEstado;
  });

  return (
    <div className="p-6">
      {/* Encabezado */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-titulo text-xl font-bold text-[#E8EAED] flex items-center gap-2">
            <ClipboardList className="h-6 w-6 text-[#C9A84C]" />
            Auditorias
          </h1>
          <p className="mt-1 text-xs text-[#5F6368]">
            Gestione las auditorias y estudios asignados
          </p>
        </div>
        <Boton variante="primario">
          <Plus className="h-4 w-4" />
          Nueva auditoria
        </Boton>
      </div>

      {/* Barra de busqueda y filtros */}
      <div className="flex items-center gap-3 mb-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#5F6368]" />
          <input
            type="text"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            placeholder="Buscar auditoria o entidad..."
            className="w-full rounded-lg border border-[#2D3748] bg-[#1A2332] py-2.5 pl-10 pr-4 text-sm text-[#E8EAED] placeholder:text-[#5F6368] focus:border-[#C9A84C] focus:outline-none"
          />
        </div>
        <div className="flex gap-1.5">
          {(['todos', 'planeacion', 'ejecucion', 'informe', 'cierre', 'seguimiento'] as const).map((estado) => (
            <button
              key={estado}
              onClick={() => setFiltroEstado(estado)}
              className={`rounded-lg px-3 py-2 text-xs transition-colors ${
                filtroEstado === estado
                  ? 'bg-[#C9A84C]/20 text-[#C9A84C] border border-[#C9A84C]/40'
                  : 'bg-[#1A2332] text-[#9AA0A6] border border-[#2D3748] hover:border-[#4A5568]'
              }`}
            >
              {estado === 'todos' ? 'Todos' : configEstado[estado].etiqueta}
            </button>
          ))}
        </div>
      </div>

      {/* Lista de auditorias */}
      <div className="space-y-3">
        {auditoriasFiltradas.map((auditoria) => {
          const estado = configEstado[auditoria.estado];
          return (
            <Tarjeta key={auditoria.id} className="hover:border-[#4A5568] transition-all cursor-pointer">
              <div className="flex items-center p-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-sm font-medium text-[#E8EAED] truncate">
                      {auditoria.nombre}
                    </h3>
                    <Insignia
                      variante={auditoria.direccion === 'DES' ? 'des' : 'dvf'}
                      className="text-[9px]"
                    >
                      {auditoria.direccion}
                    </Insignia>
                    <span
                      className="inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium"
                      style={{
                        backgroundColor: `${estado.color}20`,
                        color: estado.color,
                        border: `1px solid ${estado.color}40`,
                      }}
                    >
                      {estado.etiqueta}
                    </span>
                  </div>

                  <div className="flex items-center gap-4 text-[10px] text-[#5F6368]">
                    <span className="flex items-center gap-1">
                      <Building2 className="h-3 w-3" />
                      {auditoria.entidad_auditada}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {new Date(auditoria.fecha_inicio).toLocaleDateString('es-CO')}
                    </span>
                    <span className="flex items-center gap-1">
                      <Users className="h-3 w-3" />
                      {auditoria.equipo.length} miembros
                    </span>
                    <span className="flex items-center gap-1">
                      <AlertTriangle className="h-3 w-3" />
                      {auditoria.hallazgos_count} hallazgos
                    </span>
                  </div>
                </div>

                <ChevronRight className="h-4 w-4 text-[#5F6368] flex-shrink-0" />
              </div>
            </Tarjeta>
          );
        })}
      </div>
    </div>
  );
}
