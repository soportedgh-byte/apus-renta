import React from 'react';

export default function Select({
  label,
  error,
  options = [],
  className = '',
  ...rest
}) {
  return (
    <div className={`w-full ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-[#2C3E50] mb-1">
          {label}
        </label>
      )}
      <select
        className={`
          w-full rounded-lg border bg-white px-3 py-2 text-sm text-[#2C3E50]
          focus:outline-none focus:ring-2 focus:ring-[#2E86C1] focus:border-transparent
          disabled:bg-gray-100 disabled:cursor-not-allowed
          ${error ? 'border-[#E74C3C]' : 'border-gray-300'}
        `}
        {...rest}
      >
        <option value="">Seleccionar...</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && (
        <p className="mt-1 text-xs text-[#E74C3C]">{error}</p>
      )}
    </div>
  );
}
