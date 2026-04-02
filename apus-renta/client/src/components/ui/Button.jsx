import React from 'react';
import { Loader2 } from 'lucide-react';

const variants = {
  primary: 'bg-[#1B4F72] hover:bg-[#154360] text-white',
  secondary: 'bg-gray-200 hover:bg-gray-300 text-[#2C3E50]',
  success: 'bg-[#27AE60] hover:bg-[#219A52] text-white',
  danger: 'bg-[#E74C3C] hover:bg-[#CB4335] text-white',
  outline: 'border-2 border-[#1B4F72] text-[#1B4F72] hover:bg-[#D6EAF8] bg-transparent',
};

const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-base',
};

export default function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  children,
  className = '',
  ...rest
}) {
  return (
    <button
      className={`
        inline-flex items-center justify-center gap-2 font-medium rounded-lg
        transition-colors duration-150 focus:outline-none focus:ring-2
        focus:ring-[#2E86C1] focus:ring-offset-2
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variants[variant] || variants.primary}
        ${sizes[size] || sizes.md}
        ${className}
      `}
      disabled={disabled || loading}
      {...rest}
    >
      {loading && <Loader2 className="w-4 h-4 animate-spin" />}
      {children}
    </button>
  );
}
