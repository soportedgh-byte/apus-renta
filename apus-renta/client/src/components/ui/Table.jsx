import React from 'react';
import { ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';

export default function Table({
  columns = [],
  data = [],
  loading = false,
  emptyMessage = 'No hay datos disponibles',
  page,
  totalPages,
  onPageChange,
}) {
  return (
    <div className="w-full overflow-x-auto rounded-xl border border-gray-200">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-[#1B4F72] text-white">
            {columns.map((col) => (
              <th
                key={col.key}
                className="px-4 py-3 text-left font-medium whitespace-nowrap"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {loading ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-12 text-center">
                <Loader2 className="w-6 h-6 animate-spin mx-auto text-[#2E86C1]" />
              </td>
            </tr>
          ) : data.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                className="px-4 py-12 text-center text-gray-500"
              >
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, idx) => (
              <tr
                key={row.id || idx}
                className={`
                  border-t border-gray-100 hover:bg-[#D6EAF8]/30 transition-colors
                  ${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                `}
              >
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-3 whitespace-nowrap">
                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-white">
          <span className="text-sm text-gray-600">
            Pagina {page} de {totalPages}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1}
              className="p-1.5 rounded-lg hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages}
              className="p-1.5 rounded-lg hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
