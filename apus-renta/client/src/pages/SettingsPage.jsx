import React, { useState, useEffect, useCallback } from 'react';
import {
  User, Bell, Building2, Save, Upload, Lock, Mail, Phone,
  Eye, EyeOff, Check, ToggleLeft, ToggleRight, Palette, Crown,
} from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';

const ALERT_TYPES = [
  { key: 'paymentDue', label: 'Vencimiento de Pago', description: 'Notificar cuando se acerca el vencimiento de un pago de arriendo' },
  { key: 'utilityDue', label: 'Vencimiento de Servicios', description: 'Notificar cuando se acercan vencimientos de agua, luz o gas' },
  { key: 'leaseExpiry', label: 'Vencimiento de Contrato', description: 'Notificar cuando un contrato de arrendamiento esta por vencer' },
  { key: 'pqrsNew', label: 'Nueva PQRS', description: 'Notificar cuando se recibe una nueva solicitud PQRS' },
];

function TabButton({ active, onClick, icon: Icon, children }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
        active
          ? 'bg-white text-[#1B4F72] shadow-sm'
          : 'text-gray-600 hover:text-[#1B4F72]'
      }`}
    >
      <Icon className="w-4 h-4" />
      {children}
    </button>
  );
}

function Toggle({ enabled, onToggle }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className="focus:outline-none"
    >
      {enabled ? (
        <ToggleRight className="w-8 h-8 text-[#27AE60]" />
      ) : (
        <ToggleLeft className="w-8 h-8 text-gray-400" />
      )}
    </button>
  );
}

export default function SettingsPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('perfil');
  const [saving, setSaving] = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState('');

  const isPropietario = user?.role === 'PROPIETARIO' || user?.role === 'ADMIN';

  // PROFILE
  const [profile, setProfile] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    avatar: null,
    avatarPreview: '',
  });

  const [passwords, setPasswords] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  // ALERTS
  const [alertConfig, setAlertConfig] = useState({});

  // TENANT
  const [tenant, setTenant] = useState({
    name: '',
    logo: null,
    logoPreview: '',
    plan: '',
    planLimits: {},
    primaryColor: '#1B4F72',
  });

  const fetchProfile = useCallback(async () => {
    try {
      const { data } = await api.get('/auth/me');
      const u = data.data || data;
      setProfile({
        firstName: u.firstName || '',
        lastName: u.lastName || '',
        email: u.email || '',
        phone: u.phone || '',
        avatar: null,
        avatarPreview: u.avatarUrl || u.avatar || '',
      });
    } catch {
      // Use context user as fallback
      if (user) {
        setProfile({
          firstName: user.firstName || '',
          lastName: user.lastName || '',
          email: user.email || '',
          phone: user.phone || '',
          avatar: null,
          avatarPreview: user.avatarUrl || user.avatar || '',
        });
      }
    }
  }, [user]);

  const fetchAlerts = useCallback(async () => {
    if (!isPropietario) return;
    try {
      const { data } = await api.get('/settings/alerts');
      const config = data.data || data;
      const mapped = {};
      ALERT_TYPES.forEach(({ key }) => {
        mapped[key] = config[key] || {
          enabled: false,
          daysBefore: 3,
          channels: { email: true, whatsapp: false, push: false },
        };
      });
      setAlertConfig(mapped);
    } catch {
      const defaults = {};
      ALERT_TYPES.forEach(({ key }) => {
        defaults[key] = {
          enabled: false,
          daysBefore: 3,
          channels: { email: true, whatsapp: false, push: false },
        };
      });
      setAlertConfig(defaults);
    }
  }, [isPropietario]);

  const fetchTenant = useCallback(async () => {
    if (!isPropietario) return;
    try {
      const { data } = await api.get('/settings/tenant');
      const t = data.data || data;
      setTenant({
        name: t.name || '',
        logo: null,
        logoPreview: t.logoUrl || t.logo || '',
        plan: t.plan || t.planName || 'Basico',
        planLimits: t.planLimits || t.limits || {},
        primaryColor: t.primaryColor || '#1B4F72',
      });
    } catch {
      // keep defaults
    }
  }, [isPropietario]);

  useEffect(() => {
    fetchProfile();
    fetchAlerts();
    fetchTenant();
  }, [fetchProfile, fetchAlerts, fetchTenant]);

  const showTemporarySuccess = (message) => {
    setSaveSuccess(message);
    setTimeout(() => setSaveSuccess(''), 3000);
  };

  // PROFILE HANDLERS
  const handleProfileChange = (key, value) => {
    setProfile((prev) => ({ ...prev, [key]: value }));
  };

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setProfile((prev) => ({
        ...prev,
        avatar: file,
        avatarPreview: URL.createObjectURL(file),
      }));
    }
  };

  const saveProfile = async () => {
    setSaving(true);
    try {
      const formData = new FormData();
      formData.append('firstName', profile.firstName);
      formData.append('lastName', profile.lastName);
      formData.append('phone', profile.phone);
      if (profile.avatar) {
        formData.append('avatar', profile.avatar);
      }
      await api.put('/auth/profile', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      showTemporarySuccess('Perfil actualizado correctamente');
    } catch {
      // Error handled by interceptor
    } finally {
      setSaving(false);
    }
  };

  const changePassword = async () => {
    if (passwords.newPassword !== passwords.confirmPassword) return;
    if (!passwords.currentPassword || !passwords.newPassword) return;
    setSaving(true);
    try {
      await api.put('/auth/password', {
        currentPassword: passwords.currentPassword,
        newPassword: passwords.newPassword,
      });
      setPasswords({ currentPassword: '', newPassword: '', confirmPassword: '' });
      showTemporarySuccess('Contrasena actualizada correctamente');
    } catch {
      // Error handled by interceptor
    } finally {
      setSaving(false);
    }
  };

  // ALERTS HANDLERS
  const updateAlertConfig = (key, field, value) => {
    setAlertConfig((prev) => ({
      ...prev,
      [key]: { ...prev[key], [field]: value },
    }));
  };

  const updateAlertChannel = (key, channel, value) => {
    setAlertConfig((prev) => ({
      ...prev,
      [key]: {
        ...prev[key],
        channels: { ...prev[key].channels, [channel]: value },
      },
    }));
  };

  const saveAlerts = async () => {
    setSaving(true);
    try {
      await api.put('/settings/alerts', alertConfig);
      showTemporarySuccess('Configuracion de alertas guardada');
    } catch {
      // Error handled by interceptor
    } finally {
      setSaving(false);
    }
  };

  // TENANT HANDLERS
  const handleLogoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setTenant((prev) => ({
        ...prev,
        logo: file,
        logoPreview: URL.createObjectURL(file),
      }));
    }
  };

  const saveTenant = async () => {
    setSaving(true);
    try {
      const formData = new FormData();
      formData.append('name', tenant.name);
      formData.append('primaryColor', tenant.primaryColor);
      if (tenant.logo) {
        formData.append('logo', tenant.logo);
      }
      await api.put('/settings/tenant', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      showTemporarySuccess('Configuracion de tenant guardada');
    } catch {
      // Error handled by interceptor
    } finally {
      setSaving(false);
    }
  };

  const passwordsMatch = passwords.newPassword && passwords.newPassword === passwords.confirmPassword;
  const passwordError = passwords.confirmPassword && !passwordsMatch ? 'Las contrasenas no coinciden' : '';

  return (
    <div>
      <h2 className="text-2xl font-bold text-[#2C3E50] mb-6">Configuracion</h2>

      {/* Success Toast */}
      {saveSuccess && (
        <div className="fixed top-4 right-4 z-50 flex items-center gap-2 bg-[#27AE60] text-white px-4 py-3 rounded-lg shadow-lg animate-in fade-in">
          <Check className="w-4 h-4" />
          <span className="text-sm font-medium">{saveSuccess}</span>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 rounded-lg p-1 w-fit">
        <TabButton active={activeTab === 'perfil'} onClick={() => setActiveTab('perfil')} icon={User}>
          Perfil
        </TabButton>
        {isPropietario && (
          <TabButton active={activeTab === 'alertas'} onClick={() => setActiveTab('alertas')} icon={Bell}>
            Alertas
          </TabButton>
        )}
        {isPropietario && (
          <TabButton active={activeTab === 'tenant'} onClick={() => setActiveTab('tenant')} icon={Building2}>
            Tenant
          </TabButton>
        )}
      </div>

      {/* PERFIL TAB */}
      {activeTab === 'perfil' && (
        <div className="space-y-6 max-w-2xl">
          <Card title="Informacion Personal">
            <div className="space-y-4">
              {/* Avatar */}
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-[#D6EAF8] flex items-center justify-center overflow-hidden border-2 border-[#2E86C1]">
                  {profile.avatarPreview ? (
                    <img src={profile.avatarPreview} alt="Avatar" className="w-full h-full object-cover" />
                  ) : (
                    <User className="w-8 h-8 text-[#1B4F72]" />
                  )}
                </div>
                <label className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-gray-300 cursor-pointer hover:bg-gray-50 text-sm text-gray-600 transition-colors">
                  <Upload className="w-4 h-4" />
                  Cambiar foto
                  <input type="file" className="hidden" accept=".jpg,.jpeg,.png" onChange={handleAvatarChange} />
                </label>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  label="Nombre"
                  value={profile.firstName}
                  onChange={(e) => handleProfileChange('firstName', e.target.value)}
                />
                <Input
                  label="Apellido"
                  value={profile.lastName}
                  onChange={(e) => handleProfileChange('lastName', e.target.value)}
                />
              </div>
              <Input
                label="Email"
                type="email"
                icon={Mail}
                value={profile.email}
                disabled
                className="opacity-70"
              />
              <Input
                label="Telefono"
                type="tel"
                icon={Phone}
                value={profile.phone}
                onChange={(e) => handleProfileChange('phone', e.target.value)}
                placeholder="+57 300 000 0000"
              />
              <div className="flex justify-end pt-2">
                <Button onClick={saveProfile} loading={saving}>
                  <Save className="w-4 h-4" />
                  Guardar Perfil
                </Button>
              </div>
            </div>
          </Card>

          <Card title="Cambiar Contrasena">
            <div className="space-y-4">
              <div className="relative">
                <Input
                  label="Contrasena Actual"
                  type={showCurrentPassword ? 'text' : 'password'}
                  icon={Lock}
                  value={passwords.currentPassword}
                  onChange={(e) => setPasswords((p) => ({ ...p, currentPassword: e.target.value }))}
                />
                <button
                  type="button"
                  onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                  className="absolute right-3 top-8 text-gray-400 hover:text-gray-600"
                >
                  {showCurrentPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              <div className="relative">
                <Input
                  label="Nueva Contrasena"
                  type={showNewPassword ? 'text' : 'password'}
                  icon={Lock}
                  value={passwords.newPassword}
                  onChange={(e) => setPasswords((p) => ({ ...p, newPassword: e.target.value }))}
                />
                <button
                  type="button"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  className="absolute right-3 top-8 text-gray-400 hover:text-gray-600"
                >
                  {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              <Input
                label="Confirmar Contrasena"
                type="password"
                icon={Lock}
                value={passwords.confirmPassword}
                onChange={(e) => setPasswords((p) => ({ ...p, confirmPassword: e.target.value }))}
                error={passwordError}
              />
              <div className="flex justify-end pt-2">
                <Button
                  onClick={changePassword}
                  loading={saving}
                  disabled={!passwordsMatch || !passwords.currentPassword}
                >
                  <Lock className="w-4 h-4" />
                  Cambiar Contrasena
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* ALERTAS TAB */}
      {activeTab === 'alertas' && isPropietario && (
        <div className="space-y-4 max-w-2xl">
          {ALERT_TYPES.map(({ key, label, description }) => {
            const config = alertConfig[key] || { enabled: false, daysBefore: 3, channels: { email: true, whatsapp: false, push: false } };
            return (
              <Card key={key}>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-[#2C3E50]">{label}</h4>
                    <p className="text-xs text-gray-500 mt-0.5">{description}</p>
                  </div>
                  <Toggle
                    enabled={config.enabled}
                    onToggle={() => updateAlertConfig(key, 'enabled', !config.enabled)}
                  />
                </div>
                {config.enabled && (
                  <div className="space-y-3 pt-3 border-t border-gray-100">
                    <div className="flex items-center gap-3">
                      <label className="text-xs text-gray-600 whitespace-nowrap">Dias antes:</label>
                      <input
                        type="number"
                        min="1"
                        max="30"
                        value={config.daysBefore}
                        onChange={(e) => updateAlertConfig(key, 'daysBefore', parseInt(e.target.value) || 3)}
                        className="w-20 rounded-lg border border-gray-300 px-2 py-1 text-sm text-[#2C3E50] focus:outline-none focus:ring-2 focus:ring-[#2E86C1] focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-600 block mb-2">Canales de notificacion:</label>
                      <div className="flex gap-4">
                        {[
                          { key: 'email', label: 'Email' },
                          { key: 'whatsapp', label: 'WhatsApp' },
                          { key: 'push', label: 'Push' },
                        ].map((ch) => (
                          <label key={ch.key} className="flex items-center gap-1.5 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={config.channels?.[ch.key] || false}
                              onChange={(e) => updateAlertChannel(key, ch.key, e.target.checked)}
                              className="w-4 h-4 rounded border-gray-300 text-[#2E86C1] focus:ring-[#2E86C1]"
                            />
                            <span className="text-sm text-gray-700">{ch.label}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </Card>
            );
          })}
          <div className="flex justify-end pt-2">
            <Button onClick={saveAlerts} loading={saving}>
              <Save className="w-4 h-4" />
              Guardar Configuracion
            </Button>
          </div>
        </div>
      )}

      {/* TENANT TAB */}
      {activeTab === 'tenant' && isPropietario && (
        <div className="space-y-6 max-w-2xl">
          <Card title="Informacion del Tenant">
            <div className="space-y-4">
              <Input
                label="Nombre de la Organizacion"
                value={tenant.name}
                onChange={(e) => setTenant((p) => ({ ...p, name: e.target.value }))}
              />
              <div>
                <label className="block text-sm font-medium text-[#2C3E50] mb-1">Logo</label>
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-lg bg-gray-100 flex items-center justify-center overflow-hidden border border-gray-200">
                    {tenant.logoPreview ? (
                      <img src={tenant.logoPreview} alt="Logo" className="w-full h-full object-contain" />
                    ) : (
                      <Building2 className="w-8 h-8 text-gray-400" />
                    )}
                  </div>
                  <label className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-gray-300 cursor-pointer hover:bg-gray-50 text-sm text-gray-600 transition-colors">
                    <Upload className="w-4 h-4" />
                    Subir logo
                    <input type="file" className="hidden" accept=".jpg,.jpeg,.png,.svg" onChange={handleLogoChange} />
                  </label>
                </div>
              </div>
            </div>
          </Card>

          <Card title="Marca / Branding">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[#2C3E50] mb-1">
                  <span className="flex items-center gap-1.5">
                    <Palette className="w-4 h-4" />
                    Color Primario
                  </span>
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={tenant.primaryColor}
                    onChange={(e) => setTenant((p) => ({ ...p, primaryColor: e.target.value }))}
                    className="w-10 h-10 rounded-lg border border-gray-300 cursor-pointer p-0.5"
                  />
                  <input
                    type="text"
                    value={tenant.primaryColor}
                    onChange={(e) => setTenant((p) => ({ ...p, primaryColor: e.target.value }))}
                    className="w-28 rounded-lg border border-gray-300 px-3 py-2 text-sm font-mono text-[#2C3E50] focus:outline-none focus:ring-2 focus:ring-[#2E86C1] focus:border-transparent"
                    placeholder="#1B4F72"
                  />
                  <div
                    className="w-10 h-10 rounded-lg border border-gray-200"
                    style={{ backgroundColor: tenant.primaryColor }}
                  />
                </div>
              </div>
            </div>
          </Card>

          <Card title="Plan Actual">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-lg bg-amber-100">
                <Crown className="w-5 h-5 text-[#F39C12]" />
              </div>
              <div>
                <span className="text-lg font-bold text-[#2C3E50]">{tenant.plan}</span>
                <span className="text-xs text-gray-500 block">Plan activo</span>
              </div>
            </div>
            {Object.keys(tenant.planLimits).length > 0 && (
              <div className="space-y-2 border-t border-gray-100 pt-3">
                {Object.entries(tenant.planLimits).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between text-sm">
                    <span className="text-gray-600 capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                    <span className="font-medium text-[#2C3E50]">{value}</span>
                  </div>
                ))}
              </div>
            )}
            {Object.keys(tenant.planLimits).length === 0 && (
              <div className="text-sm text-gray-500 border-t border-gray-100 pt-3">
                Los limites del plan se mostraran aqui cuando esten configurados.
              </div>
            )}
          </Card>

          <div className="flex justify-end pt-2">
            <Button onClick={saveTenant} loading={saving}>
              <Save className="w-4 h-4" />
              Guardar Configuracion
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
