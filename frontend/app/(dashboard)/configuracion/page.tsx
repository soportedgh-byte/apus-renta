'use client';

import React, { useState, useEffect } from 'react';
import {
  Settings,
  Sun,
  Moon,
  Volume2,
  VolumeX,
  Bell,
  BellOff,
  Globe,
  Shield,
  Save,
  CheckCircle,
  Cpu,
  Palette,
  MessageSquare,
  FileText,
  RotateCcw,
} from 'lucide-react';
import { Tarjeta } from '@/components/ui/card';
import { Boton } from '@/components/ui/button';
import { obtenerDireccionActiva } from '@/lib/auth';
import type { Direccion } from '@/lib/types';

interface ConfiguracionUsuario {
  tema: 'oscuro' | 'claro';
  notificaciones: boolean;
  sonido_notificaciones: boolean;
  formato_fecha: 'DD/MM/YYYY' | 'YYYY-MM-DD' | 'MM/DD/YYYY';
  idioma: 'es';
  max_tokens_respuesta: number;
  mostrar_fuentes: boolean;
  autoguardado: boolean;
  circular_023_advertencias: boolean;
}

const CONFIG_DEFECTO: ConfiguracionUsuario = {
  tema: 'oscuro',
  notificaciones: true,
  sonido_notificaciones: true,
  formato_fecha: 'DD/MM/YYYY',
  idioma: 'es',
  max_tokens_respuesta: 2048,
  mostrar_fuentes: true,
  autoguardado: true,
  circular_023_advertencias: true,
};

function InterruptorToggle({
  activo,
  onChange,
}: {
  activo: boolean;
  onChange: (val: boolean) => void;
}) {
  return (
    <button
      onClick={() => onChange(!activo)}
      className={`relative h-5 w-9 rounded-full transition-colors ${
        activo ? 'bg-[#C9A84C]' : 'bg-[#2D3748]'
      }`}
    >
      <div
        className={`absolute top-0.5 h-4 w-4 rounded-full bg-white transition-transform ${
          activo ? 'translate-x-4' : 'translate-x-0.5'
        }`}
      />
    </button>
  );
}

export default function PaginaConfiguracion() {
  const [config, setConfig] = useState<ConfiguracionUsuario>(CONFIG_DEFECTO);
  const [guardado, setGuardado] = useState(false);
  const [direccion, setDireccion] = useState<Direccion>('DES');

  useEffect(() => {
    const dir = obtenerDireccionActiva();
    if (dir) setDireccion(dir);

    // Cargar config guardada en localStorage
    const guardada = localStorage.getItem('cecilia_config');
    if (guardada) {
      try {
        setConfig({ ...CONFIG_DEFECTO, ...JSON.parse(guardada) });
      } catch {
        // Silenciar
      }
    }
  }, []);

  const actualizar = (campo: keyof ConfiguracionUsuario, valor: any) => {
    setConfig((prev) => ({ ...prev, [campo]: valor }));
    setGuardado(false);
  };

  const guardarConfiguracion = () => {
    localStorage.setItem('cecilia_config', JSON.stringify(config));
    setGuardado(true);
    setTimeout(() => setGuardado(false), 3000);
  };

  const restaurarDefecto = () => {
    setConfig(CONFIG_DEFECTO);
    localStorage.removeItem('cecilia_config');
    setGuardado(false);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Encabezado */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-titulo text-xl font-bold text-[#E8EAED] flex items-center gap-2">
            <Settings className="h-6 w-6 text-[#C9A84C]" />
            Configuracion
          </h1>
          <p className="mt-1 text-xs text-[#5F6368]">
            Personalice su experiencia en CecilIA
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Boton variante="fantasma" tamano="sm" onClick={restaurarDefecto} className="text-[10px]">
            <RotateCcw className="h-3 w-3 mr-1" />
            Restaurar
          </Boton>
          <Boton variante="primario" tamano="sm" onClick={guardarConfiguracion} className="text-[10px]">
            {guardado ? (
              <>
                <CheckCircle className="h-3 w-3 mr-1" />
                Guardado
              </>
            ) : (
              <>
                <Save className="h-3 w-3 mr-1" />
                Guardar cambios
              </>
            )}
          </Boton>
        </div>
      </div>

      <div className="space-y-4">
        {/* Apariencia */}
        <Tarjeta className="p-5">
          <h3 className="text-sm font-semibold text-[#E8EAED] mb-4 flex items-center gap-2">
            <Palette className="h-4 w-4 text-[#C9A84C]" />
            Apariencia
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-[#E8EAED]">Tema</p>
                <p className="text-[10px] text-[#5F6368]">El tema oscuro esta optimizado para CecilIA</p>
              </div>
              <div className="flex items-center gap-2 rounded-lg border border-[#2D3748] p-0.5">
                <button
                  onClick={() => actualizar('tema', 'oscuro')}
                  className={`flex items-center gap-1 rounded-md px-3 py-1.5 text-[10px] transition-colors ${
                    config.tema === 'oscuro'
                      ? 'bg-[#C9A84C]/20 text-[#D4B96A]'
                      : 'text-[#5F6368] hover:text-[#9AA0A6]'
                  }`}
                >
                  <Moon className="h-3 w-3" />
                  Oscuro
                </button>
                <button
                  onClick={() => actualizar('tema', 'claro')}
                  className={`flex items-center gap-1 rounded-md px-3 py-1.5 text-[10px] transition-colors ${
                    config.tema === 'claro'
                      ? 'bg-[#C9A84C]/20 text-[#D4B96A]'
                      : 'text-[#5F6368] hover:text-[#9AA0A6]'
                  }`}
                >
                  <Sun className="h-3 w-3" />
                  Claro
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-[#E8EAED]">Formato de fecha</p>
                <p className="text-[10px] text-[#5F6368]">Como se muestran las fechas en la interfaz</p>
              </div>
              <select
                value={config.formato_fecha}
                onChange={(e) => actualizar('formato_fecha', e.target.value)}
                className="rounded-md border border-[#2D3748] bg-[#0F1419] px-3 py-1.5 text-[10px] text-[#E8EAED] focus:border-[#C9A84C] focus:outline-none"
              >
                <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                <option value="MM/DD/YYYY">MM/DD/YYYY</option>
              </select>
            </div>
          </div>
        </Tarjeta>

        {/* Notificaciones */}
        <Tarjeta className="p-5">
          <h3 className="text-sm font-semibold text-[#E8EAED] mb-4 flex items-center gap-2">
            <Bell className="h-4 w-4 text-[#C9A84C]" />
            Notificaciones
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {config.notificaciones ? (
                  <Bell className="h-4 w-4 text-[#9AA0A6]" />
                ) : (
                  <BellOff className="h-4 w-4 text-[#5F6368]" />
                )}
                <div>
                  <p className="text-xs text-[#E8EAED]">Notificaciones del sistema</p>
                  <p className="text-[10px] text-[#5F6368]">Alertas de nuevas auditorias, hallazgos y actualizaciones</p>
                </div>
              </div>
              <InterruptorToggle activo={config.notificaciones} onChange={(v) => actualizar('notificaciones', v)} />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {config.sonido_notificaciones ? (
                  <Volume2 className="h-4 w-4 text-[#9AA0A6]" />
                ) : (
                  <VolumeX className="h-4 w-4 text-[#5F6368]" />
                )}
                <div>
                  <p className="text-xs text-[#E8EAED]">Sonido de notificaciones</p>
                  <p className="text-[10px] text-[#5F6368]">Alerta sonora al recibir notificaciones</p>
                </div>
              </div>
              <InterruptorToggle
                activo={config.sonido_notificaciones}
                onChange={(v) => actualizar('sonido_notificaciones', v)}
              />
            </div>
          </div>
        </Tarjeta>

        {/* Chat e IA */}
        <Tarjeta className="p-5">
          <h3 className="text-sm font-semibold text-[#E8EAED] mb-4 flex items-center gap-2">
            <MessageSquare className="h-4 w-4 text-[#C9A84C]" />
            Chat e Inteligencia Artificial
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-[#E8EAED]">Mostrar fuentes consultadas</p>
                <p className="text-[10px] text-[#5F6368]">Muestra las fuentes normativas y documentales en cada respuesta</p>
              </div>
              <InterruptorToggle activo={config.mostrar_fuentes} onChange={(v) => actualizar('mostrar_fuentes', v)} />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-[#E8EAED]">Longitud de respuestas</p>
                <p className="text-[10px] text-[#5F6368]">Tokens maximos por respuesta de CecilIA</p>
              </div>
              <select
                value={config.max_tokens_respuesta}
                onChange={(e) => actualizar('max_tokens_respuesta', Number(e.target.value))}
                className="rounded-md border border-[#2D3748] bg-[#0F1419] px-3 py-1.5 text-[10px] text-[#E8EAED] focus:border-[#C9A84C] focus:outline-none"
              >
                <option value={1024}>Corta (1024 tokens)</option>
                <option value={2048}>Estandar (2048 tokens)</option>
                <option value={4096}>Extendida (4096 tokens)</option>
              </select>
            </div>
          </div>
        </Tarjeta>

        {/* Privacidad y seguridad */}
        <Tarjeta className="p-5">
          <h3 className="text-sm font-semibold text-[#E8EAED] mb-4 flex items-center gap-2">
            <Shield className="h-4 w-4 text-[#C9A84C]" />
            Privacidad y Cumplimiento
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-[#E8EAED]">Advertencias Circular 023</p>
                <p className="text-[10px] text-[#5F6368]">
                  Alertas cuando se detectan datos personales (Ley 1581/2012)
                </p>
              </div>
              <InterruptorToggle
                activo={config.circular_023_advertencias}
                onChange={(v) => actualizar('circular_023_advertencias', v)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-[#E8EAED]">Autoguardado de formatos</p>
                <p className="text-[10px] text-[#5F6368]">Guarda borradores automaticamente mientras trabaja</p>
              </div>
              <InterruptorToggle activo={config.autoguardado} onChange={(v) => actualizar('autoguardado', v)} />
            </div>
          </div>
        </Tarjeta>

        {/* Info del sistema */}
        <Tarjeta className="p-5">
          <h3 className="text-sm font-semibold text-[#E8EAED] mb-4 flex items-center gap-2">
            <Cpu className="h-4 w-4 text-[#C9A84C]" />
            Informacion del Sistema
          </h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-lg border border-[#2D3748]/30 bg-[#0F1419]/50 px-3 py-2">
              <p className="text-[10px] text-[#5F6368]">Version</p>
              <p className="text-xs text-[#E8EAED]">CecilIA v2.0 — Sprint 7</p>
            </div>
            <div className="rounded-lg border border-[#2D3748]/30 bg-[#0F1419]/50 px-3 py-2">
              <p className="text-[10px] text-[#5F6368]">Marco Normativo</p>
              <p className="text-xs text-[#E8EAED]">Circular 023 CGR</p>
            </div>
            <div className="rounded-lg border border-[#2D3748]/30 bg-[#0F1419]/50 px-3 py-2">
              <p className="text-[10px] text-[#5F6368]">Entidad</p>
              <p className="text-xs text-[#E8EAED]">Contraloria General de la Republica</p>
            </div>
            <div className="rounded-lg border border-[#2D3748]/30 bg-[#0F1419]/50 px-3 py-2">
              <p className="text-[10px] text-[#5F6368]">Soporte</p>
              <p className="text-xs text-[#E8EAED]">CD-TIC-CGR</p>
            </div>
          </div>
        </Tarjeta>
      </div>
    </div>
  );
}
