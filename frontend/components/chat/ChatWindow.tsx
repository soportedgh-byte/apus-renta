'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { BurbujaMensaje } from './MessageBubble';
import { AreaEntrada } from './InputArea';
import { AccionesRapidas } from './QuickActions';
import { SpinnerCarga } from '@/components/shared/LoadingSpinner';
import { iniciarStreaming, type CallbacksStreaming } from '@/lib/sse';
import { apiCliente } from '@/lib/api';
import { obtenerDireccionActiva } from '@/lib/auth';
import type { Mensaje, Direccion, CitaFuente } from '@/lib/types';

interface PropiedadesChat {
  conversacionId?: string;
}

/**
 * Ventana principal de chat
 * Contiene historial de mensajes, area de entrada y acciones rapidas
 */
export function VentanaChat({ conversacionId }: PropiedadesChat) {
  const [mensajes, setMensajes] = useState<Mensaje[]>([]);
  const [cargando, setCargando] = useState(false);
  const [enStreaming, setEnStreaming] = useState(false);
  const [mensajeStreaming, setMensajeStreaming] = useState('');
  const [citasStreaming, setCitasStreaming] = useState<CitaFuente[]>([]);
  const [direccion, setDireccion] = useState<Direccion>('DES');
  const [idConversacion, setIdConversacion] = useState(conversacionId);

  const refFinal = useRef<HTMLDivElement>(null);
  const refCancelarStreaming = useRef<(() => void) | null>(null);

  // Cargar direccion activa
  useEffect(() => {
    const dir = obtenerDireccionActiva();
    if (dir) setDireccion(dir);
  }, []);

  // Cargar historial si hay conversacion
  useEffect(() => {
    if (idConversacion) {
      cargarHistorial();
    }
  }, [idConversacion]);

  // Scroll automatico al final
  useEffect(() => {
    refFinal.current?.scrollIntoView({ behavior: 'smooth' });
  }, [mensajes, mensajeStreaming]);

  const cargarHistorial = async () => {
    if (!idConversacion) return;
    setCargando(true);
    try {
      const datos = await apiCliente.get<{ mensajes: Mensaje[] }>(`/chat/${idConversacion}`);
      setMensajes(datos.mensajes || []);
    } catch (error) {
      console.error('[CecilIA] Error al cargar historial:', error);
    } finally {
      setCargando(false);
    }
  };

  const enviarMensaje = useCallback(async (texto: string) => {
    // Crear mensaje de usuario
    const mensajeUsuario: Mensaje = {
      id: `tmp-${Date.now()}`,
      conversacion_id: idConversacion || '',
      rol: 'user',
      contenido: texto,
      fecha_creacion: new Date().toISOString(),
    };

    setMensajes((prev) => [...prev, mensajeUsuario]);
    setEnStreaming(true);
    setMensajeStreaming('');
    setCitasStreaming([]);

    // Si no hay conversacion, crear una nueva
    let idConv = idConversacion;
    if (!idConv) {
      try {
        const nueva = await apiCliente.post<{ id: string }>('/chat/conversaciones', {
          direccion,
          mensaje_inicial: texto,
        });
        idConv = nueva.id;
        setIdConversacion(idConv);
      } catch (error) {
        console.error('[CecilIA] Error al crear conversacion:', error);
        setEnStreaming(false);
        return;
      }
    }

    // Iniciar streaming
    const callbacks: CallbacksStreaming = {
      alRecibirToken: (token) => {
        setMensajeStreaming((prev) => prev + token);
      },
      alRecibirCita: (cita) => {
        setCitasStreaming((prev) => [...prev, cita]);
      },
      alCompletar: () => {
        setEnStreaming(false);
        // Agregar el mensaje completo del asistente
        setMensajes((prev) => [
          ...prev,
          {
            id: `resp-${Date.now()}`,
            conversacion_id: idConv || '',
            rol: 'assistant',
            contenido: '',  // Se actualiza abajo
            citas: [],
            modelo_llm: 'claude-sonnet-4-20250514',
            fecha_creacion: new Date().toISOString(),
          },
        ]);
        // Mover el contenido del streaming al ultimo mensaje
        setMensajes((prev) => {
          const actualizados = [...prev];
          const ultimo = actualizados[actualizados.length - 1];
          if (ultimo && ultimo.rol === 'assistant') {
            // Se actualizara con el estado actual
          }
          return actualizados;
        });
        setMensajeStreaming('');
        setCitasStreaming([]);
      },
      alError: (error) => {
        setEnStreaming(false);
        setMensajes((prev) => [
          ...prev,
          {
            id: `error-${Date.now()}`,
            conversacion_id: idConv || '',
            rol: 'assistant',
            contenido: `Error: ${error}. Por favor intente nuevamente.`,
            fecha_creacion: new Date().toISOString(),
          },
        ]);
        setMensajeStreaming('');
      },
    };

    refCancelarStreaming.current = iniciarStreaming(idConv!, texto, callbacks);
  }, [idConversacion, direccion]);

  const detenerStreaming = () => {
    refCancelarStreaming.current?.();
    setEnStreaming(false);
    if (mensajeStreaming) {
      setMensajes((prev) => [
        ...prev,
        {
          id: `parcial-${Date.now()}`,
          conversacion_id: idConversacion || '',
          rol: 'assistant',
          contenido: mensajeStreaming + '\n\n[Respuesta interrumpida por el usuario]',
          citas: citasStreaming,
          fecha_creacion: new Date().toISOString(),
        },
      ]);
    }
    setMensajeStreaming('');
    setCitasStreaming([]);
  };

  const manejarFeedback = async (mensajeId: string, tipo: 'positivo' | 'negativo') => {
    try {
      await apiCliente.post(`/chat/mensajes/${mensajeId}/feedback`, { tipo });
    } catch (error) {
      console.error('[CecilIA] Error al enviar feedback:', error);
    }
  };

  return (
    <div className="flex h-full flex-col">
      {/* Area de mensajes */}
      <div className="flex-1 overflow-y-auto">
        {cargando ? (
          <div className="flex h-full items-center justify-center">
            <SpinnerCarga texto="Cargando conversacion..." />
          </div>
        ) : mensajes.length === 0 && !enStreaming ? (
          /* Pantalla de bienvenida */
          <div className="flex h-full flex-col items-center justify-center px-4">
            <div className="max-w-lg text-center">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-[#C9A84C]/10 border border-[#C9A84C]/20">
                <span className="font-titulo text-2xl text-[#C9A84C]">C</span>
              </div>
              <h2 className="font-titulo text-xl text-[#E8EAED] mb-2">
                Bienvenido a CecilIA
              </h2>
              <p className="text-sm text-[#9AA0A6] mb-1">
                Asistente de Inteligencia Artificial para Control Fiscal
              </p>
              <p className="text-xs text-[#5F6368]">
                {direccion === 'DES'
                  ? 'Modo: Estudios Sectoriales — Control Macro'
                  : 'Modo: Vigilancia Fiscal — Control Micro'}
              </p>
            </div>
          </div>
        ) : (
          <div className="mx-auto max-w-3xl">
            {mensajes.map((mensaje) => (
              <BurbujaMensaje
                key={mensaje.id}
                mensaje={mensaje}
                direccion={direccion}
                alEnviarFeedback={manejarFeedback}
              />
            ))}

            {/* Mensaje en streaming */}
            {enStreaming && mensajeStreaming && (
              <BurbujaMensaje
                mensaje={{
                  id: 'streaming',
                  conversacion_id: '',
                  rol: 'assistant',
                  contenido: mensajeStreaming,
                  citas: citasStreaming,
                  modelo_llm: 'claude-sonnet-4-20250514',
                  fecha_creacion: new Date().toISOString(),
                }}
                direccion={direccion}
                enStreaming={true}
              />
            )}

            <div ref={refFinal} />
          </div>
        )}
      </div>

      {/* Acciones rapidas (solo si no hay mensajes) */}
      {mensajes.length === 0 && !enStreaming && (
        <AccionesRapidas direccion={direccion} alSeleccionar={enviarMensaje} />
      )}

      {/* Area de entrada */}
      <AreaEntrada
        alEnviar={enviarMensaje}
        direccion={direccion}
        deshabilitado={cargando}
        enStreaming={enStreaming}
        alDetenerStreaming={detenerStreaming}
      />
    </div>
  );
}

export default VentanaChat;
