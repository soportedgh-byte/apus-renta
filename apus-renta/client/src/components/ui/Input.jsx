import React from 'react';

export default function Input({
  label,
  error,
  icon: Icon,
  type = 'text',
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
      <div className="relative">
        {Icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Icon className="w-4 h-4 text-gray-400" />
          </div>
        )}
        <input
          type={type}
          className={`
            w-full rounded-lg border bg-white px-3 py-2 text-sm text-[#2C3E50]
            placeholder:text-gray-400
            focus:outline-none focus:ring-2 focus:ring-[#2E86C1] focus:border-transparent
            disabled:bg-gray-100 disabled:cursor-not-allowed
            ${Icon ? 'pl-10' : ''}
            ${error ? 'border-[#E74C3C]' : 'border-gray-300'}
          `}
          {...rest}
        />
      </div>
      {error && (
        <p className="mt-1 text-xs text-[#E74C3C]">{error}</p>
      )}
    </div>
  );
}
