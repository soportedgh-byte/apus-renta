import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  Building2,
  ShieldCheck,
  BarChart3,
  FileText,
} from 'lucide-react';

const FEATURES = [
  {
    icon: Building2,
    text: 'Administre todas sus propiedades desde un solo lugar',
  },
  {
    icon: ShieldCheck,
    text: 'Control total de contratos, pagos y PQRS',
  },
  {
    icon: BarChart3,
    text: 'Reportes financieros en tiempo real',
  },
  {
    icon: FileText,
    text: 'Facturacion y recaudos automatizados',
  },
];

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      if (rememberMe) {
        localStorage.setItem('rememberEmail', email);
      } else {
        localStorage.removeItem('rememberEmail');
      }
      navigate('/dashboard');
    } catch (err) {
      setError(
        err.response?.data?.message || 'Credenciales invalidas. Intente de nuevo.'
      );
    } finally {
      setLoading(false);
    }
  };

  // On mount, check if we had a remembered email
  React.useEffect(() => {
    const saved = localStorage.getItem('rememberEmail');
    if (saved) {
      setEmail(saved);
      setRememberMe(true);
    }
  }, []);

  return (
    <div className="min-h-screen flex flex-col lg:flex-row">
      {/* ---- LEFT BRANDING PANEL ---- */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-[#1B4F72] to-[#2E86C1] text-white flex-col justify-center px-16 py-12 relative overflow-hidden">
        {/* Decorative circles */}
        <div className="absolute -top-24 -left-24 w-80 h-80 rounded-full bg-white/5" />
        <div className="absolute -bottom-32 -right-32 w-96 h-96 rounded-full bg-white/5" />

        <div className="relative z-10">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-8">
            <div className="w-14 h-14 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center text-white font-bold text-2xl">
              A
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">APUS Renta</h1>
              <p className="text-sm text-white/70">by APUS Software</p>
            </div>
          </div>

          <h2 className="text-xl font-semibold leading-snug mb-3 max-w-md">
            Sistema Integral de Gestion de Propiedades en Arriendo
          </h2>

          <p className="text-white/80 mb-10 max-w-md leading-relaxed">
            Optimice la administracion de su portafolio inmobiliario con
            herramientas de gestion de contratos, pagos, servicios publicos y
            atencion a inquilinos.
          </p>

          <ul className="space-y-5">
            {FEATURES.map(({ icon: Icon, text }, idx) => (
              <li key={idx} className="flex items-start gap-4">
                <div className="mt-0.5 flex-shrink-0 w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center">
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <span className="text-sm text-white/90 leading-snug pt-2">
                  {text}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* ---- RIGHT LOGIN FORM ---- */}
      <div className="flex-1 flex flex-col">
        {/* Mobile header */}
        <div className="lg:hidden bg-gradient-to-r from-[#1B4F72] to-[#2E86C1] px-6 py-8 text-white text-center">
          <div className="w-12 h-12 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center text-white font-bold text-xl mx-auto mb-3">
            A
          </div>
          <h1 className="text-2xl font-bold">APUS Renta</h1>
          <p className="text-sm text-white/70 mt-1">
            Sistema Integral de Gestion de Propiedades
          </p>
        </div>

        {/* Form body */}
        <div className="flex-1 flex items-center justify-center px-6 py-12 bg-gray-50">
          <div className="w-full max-w-md">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-[#2C3E50]">
                Bienvenido de nuevo
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                Ingrese sus credenciales para acceder al sistema
              </p>
            </div>

            {/* Error banner */}
            {error && (
              <div className="mb-6 rounded-lg bg-red-50 border border-[#E74C3C]/20 px-4 py-3 flex items-start gap-3">
                <div className="flex-shrink-0 w-5 h-5 rounded-full bg-[#E74C3C] flex items-center justify-center mt-0.5">
                  <span className="text-white text-xs font-bold">!</span>
                </div>
                <p className="text-sm text-[#E74C3C]">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Email */}
              <Input
                label="Correo electronico"
                type="email"
                icon={Mail}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="correo@ejemplo.com"
                autoComplete="email"
                required
              />

              {/* Password with show/hide */}
              <div className="w-full">
                <label className="block text-sm font-medium text-[#2C3E50] mb-1">
                  Contrasena
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="w-4 h-4 text-gray-400" />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="********"
                    autoComplete="current-password"
                    required
                    className="w-full rounded-lg border border-gray-300 bg-white pl-10 pr-10 py-2 text-sm text-[#2C3E50] placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#2E86C1] focus:border-transparent"
                  />
                  <button
                    type="button"
                    tabIndex={-1}
                    onClick={() => setShowPassword((v) => !v)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
                    aria-label={showPassword ? 'Ocultar contrasena' : 'Mostrar contrasena'}
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Remember / Forgot */}
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded border-gray-300 text-[#1B4F72] focus:ring-[#2E86C1]"
                  />
                  <span className="text-sm text-gray-600">Recordar sesion</span>
                </label>
                <Link
                  to="/forgot-password"
                  className="text-sm text-[#2E86C1] hover:text-[#1B4F72] font-medium transition-colors"
                >
                  Olvido su contrasena?
                </Link>
              </div>

              {/* Submit */}
              <Button
                type="submit"
                loading={loading}
                className="w-full"
                size="lg"
              >
                Iniciar sesion
              </Button>
            </form>

            {/* Footer */}
            <p className="mt-10 text-center text-xs text-gray-400">
              APUS Renta v1.0 &middot; &copy; {new Date().getFullYear()} APUS
              Software
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
