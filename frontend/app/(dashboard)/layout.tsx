'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { BarraLateral } from '@/components/layout/Sidebar';
import { Encabezado } from '@/components/layout/Header';
import { PiePrivacidad } from '@/components/layout/Footer';
import { PantallaCarga } from '@/components/shared/LoadingSpinner';
import { LimiteError } from '@/components/shared/ErrorBoundary';
import { ModalResponsabilidad } from '@/components/shared/ResponsibilityModal';
import { estaAutenticado } from '@/lib/auth';

/**
 * Layout principal del dashboard
 * Incluye sidebar, header, area de contenido y footer de privacidad
 * Verifica autenticacion antes de renderizar
 */
export default function LayoutDashboard({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [verificando, setVerificando] = useState(true);

  useEffect(() => {
    // Verificar si el usuario esta autenticado
    if (!estaAutenticado()) {
      router.push('/login');
      return;
    }
    setVerificando(false);
  }, [router]);

  // Mostrar pantalla de carga mientras se verifica
  if (verificando) {
    return <PantallaCarga texto="Verificando sesion..." />;
  }

  return (
    <div className="flex h-screen overflow-hidden bg-[#0F1419]">
      {/* Barra lateral */}
      <BarraLateral />

      {/* Area principal */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Encabezado */}
        <Encabezado />

        {/* Contenido principal */}
        <main className="flex-1 overflow-y-auto">
          <LimiteError>
            {children}
          </LimiteError>
        </main>

        {/* Pie de privacidad */}
        <PiePrivacidad />
      </div>

      {/* Modal de aceptacion de responsabilidad — Circular 023 */}
      <ModalResponsabilidad />
    </div>
  );
}
