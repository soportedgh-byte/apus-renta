import type { Metadata } from 'next';
import './globals.css';

/**
 * Metadatos globales de CecilIA v2
 * Contraloria General de la Republica de Colombia
 */
export const metadata: Metadata = {
  title: 'CecilIA v2 — Control Fiscal',
  description:
    'Sistema de Inteligencia Artificial para Control Fiscal - Contraloria General de la Republica de Colombia',
  keywords: ['CecilIA', 'control fiscal', 'contraloria', 'auditoria', 'inteligencia artificial'],
  authors: [{ name: 'Contraloria General de la Republica de Colombia' }],
};

/**
 * Layout raiz de la aplicacion.
 * Configura la fuente Inter como fuente base de interfaz.
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className="dark">
      <head>
        {/* Fuentes de Google Fonts */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
        <link rel="icon" href="/logo-cecilia.png" />
      </head>
      <body className="font-interfaz bg-fondo text-[#E8EAED] antialiased">
        {children}
      </body>
    </html>
  );
}
