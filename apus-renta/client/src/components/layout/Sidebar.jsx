import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Building2,
  Users,
  FileText,
  CreditCard,
  Zap,
  MessageSquare,
  BarChart3,
  Shield,
  Settings,
  ChevronLeft,
  ChevronRight,
  X,
  UsersRound,
  Package,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/properties', label: 'Propiedades', icon: Building2 },
  { to: '/tenants', label: 'Inquilinos', icon: Users },
  { to: '/leases', label: 'Contratos', icon: FileText },
  { to: '/payments', label: 'Pagos', icon: CreditCard },
  { to: '/utilities', label: 'Servicios', icon: Zap },
  { to: '/pqrs', label: 'PQRS', icon: MessageSquare },
  { to: '/reports', label: 'Reportes', icon: BarChart3 },
  { to: '/audit', label: 'Auditoria', icon: Shield },
  { to: '/settings', label: 'Configuracion', icon: Settings },
];

const adminNavItems = [
  { to: '/admin', label: 'Admin Dashboard', icon: LayoutDashboard },
  { to: '/admin/tenants', label: 'Clientes', icon: UsersRound },
  { to: '/admin/plans', label: 'Planes', icon: Package },
];

export default function Sidebar({ collapsed, setCollapsed, mobileOpen, setMobileOpen }) {
  const { user } = useAuth();

  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-gray-200">
        <div className="w-8 h-8 rounded-lg bg-[#1B4F72] flex items-center justify-center text-white font-bold text-sm shrink-0">
          A
        </div>
        {!collapsed && (
          <span className="text-lg font-bold text-[#1B4F72] whitespace-nowrap">
            APUS Renta
          </span>
        )}
        {/* Mobile close */}
        <button
          onClick={() => setMobileOpen(false)}
          className="ml-auto p-1 rounded-lg hover:bg-gray-100 lg:hidden"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-[#D6EAF8] text-[#1B4F72]'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-[#2C3E50]'
              }`
            }
          >
            <Icon className="w-5 h-5 shrink-0" />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}

        {/* Admin section - SUPER_ADMIN only */}
        {user?.role === 'SUPER_ADMIN' && (
          <>
            <div className="pt-4 pb-2">
              {!collapsed ? (
                <p className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Administracion
                </p>
              ) : (
                <hr className="border-gray-200 mx-2" />
              )}
            </div>
            {adminNavItems.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/admin'}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-[#D6EAF8] text-[#1B4F72]'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-[#2C3E50]'
                  }`
                }
              >
                <Icon className="w-5 h-5 shrink-0" />
                {!collapsed && <span>{label}</span>}
              </NavLink>
            ))}
          </>
        )}
      </nav>

      {/* Collapse toggle (desktop only) */}
      <div className="hidden lg:block px-3 py-2 border-t border-gray-200">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full flex items-center justify-center p-2 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors"
        >
          {collapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <ChevronLeft className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* User info */}
      <div className="px-4 py-3 border-t border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-[#2E86C1] flex items-center justify-center text-white text-xs font-medium shrink-0">
            {user?.firstName?.[0] || user?.email?.[0] || 'U'}
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <p className="text-sm font-medium text-[#2C3E50] truncate">
                {user?.firstName ? `${user.firstName} ${user.lastName || ''}`.trim() : user?.email || 'Usuario'}
              </p>
              <p className="text-xs text-gray-500 truncate">
                {user?.role || 'Sin rol'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Mobile sidebar */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200
          transform transition-transform duration-200 lg:hidden
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {sidebarContent}
      </aside>

      {/* Desktop sidebar */}
      <aside
        className={`
          hidden lg:flex lg:flex-col lg:fixed lg:inset-y-0 lg:left-0 lg:z-30
          bg-white border-r border-gray-200 transition-all duration-200
          ${collapsed ? 'w-20' : 'w-64'}
        `}
      >
        {sidebarContent}
      </aside>
    </>
  );
}
