import React from 'react';

const statusColorMap = {
  // Green
  APROBADO: 'bg-green-100 text-green-800',
  PAGADO: 'bg-green-100 text-green-800',
  ACTIVO: 'bg-green-100 text-green-800',
  DISPONIBLE: 'bg-green-100 text-green-800',
  RESUELTA: 'bg-green-100 text-green-800',

  // Yellow / Amber
  PENDIENTE: 'bg-amber-100 text-amber-800',
  RADICADA: 'bg-amber-100 text-amber-800',
  EN_PROCESO: 'bg-amber-100 text-amber-800',
  BORRADOR: 'bg-amber-100 text-amber-800',

  // Red
  RECHAZADO: 'bg-red-100 text-red-800',
  VENCIDO: 'bg-red-100 text-red-800',
  MORA: 'bg-red-100 text-red-800',
  BLOQUEADO: 'bg-red-100 text-red-800',

  // Blue
  OCUPADO: 'bg-blue-100 text-blue-800',
  MANTENIMIENTO: 'bg-blue-100 text-blue-800',
};

export default function StatusBadge({ status, type }) {
  const key = (status || type || '').toUpperCase().replace(/\s+/g, '_');
  const colorClasses = statusColorMap[key] || 'bg-gray-100 text-gray-800';
  const label = (status || type || '').replace(/_/g, ' ');

  return (
    <span
      className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${colorClasses}`}
    >
      {label.toLowerCase()}
    </span>
  );
}
