import React from 'react';

export default function Card({ title, children, className = '' }) {
  return (
    <div className={`bg-white shadow-md rounded-xl p-6 ${className}`}>
      {title && (
        <h3 className="text-lg font-semibold text-[#2C3E50] mb-4">{title}</h3>
      )}
      {children}
    </div>
  );
}
