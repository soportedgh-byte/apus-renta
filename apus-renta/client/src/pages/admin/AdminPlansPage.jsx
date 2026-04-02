import React, { useState } from 'react';
import { Pencil, X, Check } from 'lucide-react';

const PLAN_BORDER = {
  FREE: 'border-gray-300',
  BASIC: 'border-[#2E86C1]',
  PRO: 'border-[#27AE60]',
  ENTERPRISE: 'border-[#8E44AD]',
};

const PLAN_HEADER_BG = {
  FREE: 'bg-gray-100 text-gray-700',
  BASIC: 'bg-blue-50 text-[#2E86C1]',
  PRO: 'bg-green-50 text-[#27AE60]',
  ENTERPRISE: 'bg-purple-50 text-[#8E44AD]',
};

function formatCOP(value) {
  if (value == null) return '$0';
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

const DEFAULT_PLANS = [
  {
    id: 'FREE',
    name: 'FREE',
    price: 0,
    maxProperties: 3,
    features: [
      'Hasta 3 propiedades',
      '1 usuario',
      'Reportes basicos',
      'Soporte por email',
    ],
  },
  {
    id: 'BASIC',
    name: 'BASIC',
    price: 89000,
    maxProperties: 15,
    features: [
      'Hasta 15 propiedades',
      '3 usuarios',
      'Reportes avanzados',
      'Soporte prioritario',
      'Facturacion electronica',
    ],
  },
  {
    id: 'PRO',
    name: 'PRO',
    price: 179000,
    maxProperties: 50,
    features: [
      'Hasta 50 propiedades',
      '10 usuarios',
      'Reportes personalizados',
      'Soporte 24/7',
      'Facturacion electronica',
      'API Access',
      'Integraciones',
    ],
  },
  {
    id: 'ENTERPRISE',
    name: 'ENTERPRISE',
    price: 399000,
    maxProperties: 999,
    features: [
      'Propiedades ilimitadas',
      'Usuarios ilimitados',
      'Reportes personalizados',
      'Soporte dedicado',
      'Facturacion electronica',
      'API Access',
      'Integraciones',
      'SLA garantizado',
      'Onboarding personalizado',
    ],
  },
];

// ─── Edit Modal ───
function EditPlanModal({ open, onClose, plan, onSave }) {
  const [maxProperties, setMaxProperties] = useState(plan?.maxProperties ?? 0);
  const [features, setFeatures] = useState(plan?.features?.join('\n') ?? '');

  React.useEffect(() => {
    if (plan) {
      setMaxProperties(plan.maxProperties ?? 0);
      setFeatures(plan.features?.join('\n') ?? '');
    }
  }, [plan]);

  if (!open || !plan) return null;

  const handleSave = () => {
    const featureList = features
      .split('\n')
      .map((f) => f.trim())
      .filter(Boolean);
    onSave({ ...plan, maxProperties, features: featureList });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-md mx-4">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-[#2C3E50]">Editar Plan - {plan.name}</h2>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-gray-100">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        <div className="px-6 py-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Precio (COP/mes)</label>
            <input
              type="text"
              value={formatCOP(plan.price)}
              readOnly
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 text-gray-500 cursor-not-allowed"
            />
            <p className="text-xs text-gray-400 mt-1">El precio no se puede modificar desde aqui</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Max Propiedades</label>
            <input
              type="number"
              min={1}
              value={maxProperties}
              onChange={(e) => setMaxProperties(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#2E86C1] focus:border-[#2E86C1] outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Caracteristicas (una por linea)
            </label>
            <textarea
              value={features}
              onChange={(e) => setFeatures(e.target.value)}
              rows={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#2E86C1] focus:border-[#2E86C1] outline-none resize-none"
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
            >
              Cancelar
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 text-sm font-medium text-white bg-[#1B4F72] rounded-lg hover:bg-[#1B4F72]/90"
            >
              Guardar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Main Page ───
export default function AdminPlansPage() {
  const [plans, setPlans] = useState(DEFAULT_PLANS);
  const [editPlan, setEditPlan] = useState(null);

  const handleSave = (updatedPlan) => {
    setPlans((prev) =>
      prev.map((p) => (p.id === updatedPlan.id ? updatedPlan : p))
    );
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#2C3E50]">Planes</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`bg-white rounded-xl border-2 ${PLAN_BORDER[plan.id]} overflow-hidden flex flex-col`}
          >
            {/* Header */}
            <div className={`px-5 py-4 ${PLAN_HEADER_BG[plan.id]}`}>
              <h3 className="text-lg font-bold">{plan.name}</h3>
              <p className="text-2xl font-bold mt-1">
                {plan.price === 0 ? 'Gratis' : formatCOP(plan.price)}
                {plan.price > 0 && <span className="text-sm font-normal opacity-70">/mes</span>}
              </p>
            </div>

            {/* Body */}
            <div className="px-5 py-4 flex-1 space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Max Propiedades</span>
                <span className="font-semibold text-[#2C3E50]">
                  {plan.maxProperties >= 999 ? 'Ilimitadas' : plan.maxProperties}
                </span>
              </div>

              <hr className="border-gray-100" />

              <ul className="space-y-2">
                {plan.features.map((feature, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                    <Check className="w-4 h-4 text-[#27AE60] shrink-0 mt-0.5" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Footer */}
            <div className="px-5 py-3 border-t border-gray-100">
              <button
                onClick={() => setEditPlan(plan)}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-[#1B4F72] bg-[#D6EAF8] rounded-lg hover:bg-[#D6EAF8]/80"
              >
                <Pencil className="w-4 h-4" />
                Editar Plan
              </button>
            </div>
          </div>
        ))}
      </div>

      <EditPlanModal
        open={!!editPlan}
        onClose={() => setEditPlan(null)}
        plan={editPlan}
        onSave={handleSave}
      />
    </div>
  );
}
