import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Salida standalone para Docker
  output: 'standalone',

  // Configuracion de imagenes para logos institucionales
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },

  // Las peticiones /api/* son manejadas por el catch-all route handler
  // en app/api/[...proxy]/route.ts que lee BACKEND_URL en runtime

  // Cabeceras de seguridad
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ];
  },
};

export default nextConfig;
