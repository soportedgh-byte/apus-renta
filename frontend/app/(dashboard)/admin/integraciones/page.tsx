'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Plug,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  Activity,
  Shield,
  ExternalLink,
  Search,
  Key,
  Save,
  Settings,
  Eye,
  EyeOff,
} from 'lucide-react';
import { apiCliente } from '@/lib/api';

interface EstadoConector {
  servicio: string;
  estado: string;
  latencia_ms: number | null;
  ultimo_chequeo: string;
  mensaje: string | null;
  circuit_breaker?: {
    estado: string;
    fallos_consecutivos: number;
    umbral_fallos?: number;
    cooldown_segundos?: number;
  };
}

const iconoEstado = (estado: string) => {
  switch (estado) {
    case 'disponible':
      return <CheckCircle className="h-5 w-5 text-green-400" />;
    case 'degradado':
      return <AlertTriangle className="h-5 w-5 text-yellow-400" />;
    case 'no_disponible':
      return <XCircle className="h-5 w-5 text-red-400" />;
    case 'circuito_abierto':
      return <Shield className="h-5 w-5 text-red-400" />;
    case 'pendiente':
      return <Clock className="h-5 w-5 text-yellow-400" />;
    default:
      return <Activity className="h-5 w-5 text-[#5F6368]" />;
  }
};

const colorEstado = (estado: string): string => {
  switch (estado) {
    case 'disponible': return 'border-green-500/30 bg-green-500/5';
    case 'degradado': return 'border-yellow-500/30 bg-yellow-500/5';
    case 'no_disponible': return 'border-red-500/30 bg-red-500/5';
    case 'circuito_abierto': return 'border-red-500/30 bg-red-500/5';
    case 'pendiente': return 'border-yellow-500/30 bg-yellow-500/5';
    default: return 'border-[#2D3748]/30 bg-[#1A2332]/40';
  }
};

const etiquetaEstado = (estado: string): string => {
  switch (estado) {
    case 'disponible': return 'Disponible';
    case 'degradado': return 'Degradado';
    case 'no_disponible': return 'No disponible';
    case 'circuito_abierto': return 'Circuit Breaker Abierto';
    case 'pendiente': return 'Pendiente de configuracion';
    default: return estado;
  }
};

interface ConfigAPI {
  nombre: string;
  clave: string;
  url_base: string;
  activo: boolean;
  descripcion: string;
  tipo: 'publica' | 'interna';
}

const CONFIG_APIS_DEFECTO: ConfigAPI[] = [
  {
    nombre: 'SECOP II',
    clave: '',
    url_base: 'https://www.datos.gov.co',
    activo: true,
    descripcion: 'Sistema Electronico de Contratacion Publica — Datos abiertos de contratacion',
    tipo: 'publica',
  },
  {
    nombre: 'DANE',
    clave: '',
    url_base: 'https://www.datos.gov.co',
    activo: true,
    descripcion: 'Departamento Administrativo Nacional de Estadistica — Indicadores economicos',
    tipo: 'publica',
  },
  {
    nombre: 'Congreso',
    clave: '',
    url_base: 'https://www.datos.gov.co',
    activo: true,
    descripcion: 'Congreso de la Republica — Normatividad y proyectos de ley',
    tipo: 'publica',
  },
  {
    nombre: 'SIRECI',
    clave: '',
    url_base: '',
    activo: false,
    descripcion: 'Sistema de Rendicion Electronica de Cuenta e Informes — Requiere VPN CGR',
    tipo: 'interna',
  },
  {
    nombre: 'SIGECI',
    clave: '',
    url_base: '',
    activo: false,
    descripcion: 'Sistema de Gestion del Control Fiscal — Requiere VPN CGR',
    tipo: 'interna',
  },
  {
    nombre: 'APA',
    clave: '',
    url_base: '',
    activo: false,
    descripcion: 'Plan de Vigilancia y Control Fiscal — Requiere VPN CGR',
    tipo: 'interna',
  },
  {
    nombre: 'DIARI',
    clave: '',
    url_base: '',
    activo: false,
    descripcion: 'Deposito Integrado de Informes — Requiere VPN CGR',
    tipo: 'interna',
  },
];

export default function PaginaAdminIntegraciones() {
  const [conectores, setConectores] = useState<EstadoConector[]>([]);
  const [cargando, setCargando] = useState(true);
  const [consultaRapida, setConsultaRapida] = useState('');
  const [conectorSeleccionado, setConectorSeleccionado] = useState<string | null>(null);
  const [resultadoConsulta, setResultadoConsulta] = useState<any>(null);
  const [consultando, setConsultando] = useState(false);

  // Configuracion de APIs
  const [pestana, setPestana] = useState<'estado' | 'configuracion'>('estado');
  const [configAPIs, setConfigAPIs] = useState<ConfigAPI[]>(CONFIG_APIS_DEFECTO);
  const [mostrarClaves, setMostrarClaves] = useState<Record<string, boolean>>({});
  const [configGuardada, setConfigGuardada] = useState(false);

  const cargarEstado = useCallback(async () => {
    setCargando(true);
    try {
      const datos = await apiCliente.get<EstadoConector[]>('/integraciones/estado');
      if (datos && Array.isArray(datos)) {
        setConectores(datos);
      }
    } catch (error) {
      console.error('[CecilIA] Error al cargar estado de integraciones:', error);
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    cargarEstado();
    // Cargar config guardada
    const guardada = localStorage.getItem('cecilia_config_apis');
    if (guardada) {
      try {
        setConfigAPIs(JSON.parse(guardada));
      } catch { /* silenciar */ }
    }
  }, [cargarEstado]);

  const actualizarConfigAPI = (nombre: string, campo: keyof ConfigAPI, valor: any) => {
    setConfigAPIs((prev) =>
      prev.map((api) => (api.nombre === nombre ? { ...api, [campo]: valor } : api))
    );
    setConfigGuardada(false);
  };

  const guardarConfigAPIs = async () => {
    localStorage.setItem('cecilia_config_apis', JSON.stringify(configAPIs));
    try {
      await apiCliente.post('/integraciones/configurar', { apis: configAPIs });
    } catch {
      // El backend puede no tener este endpoint aun — guardar solo local
    }
    setConfigGuardada(true);
    setTimeout(() => setConfigGuardada(false), 3000);
  };

  const ejecutarConsultaRapida = async () => {
    if (!conectorSeleccionado || !consultaRapida.trim()) return;
    setConsultando(true);
    setResultadoConsulta(null);
    try {
      const datos = await apiCliente.post<any>(`/integraciones/${conectorSeleccionado.toLowerCase()}/consultar`, {
        parametros: { termino_busqueda: consultaRapida, limite: 5 },
      });
      setResultadoConsulta(datos);
    } catch (error: any) {
      setResultadoConsulta({ error: true, mensaje: error.message || 'Error desconocido' });
    } finally {
      setConsultando(false);
    }
  };

  const serviciosPublicos = conectores.filter((c) =>
    ['SECOP II', 'DANE', 'Congreso'].includes(c.servicio)
  );
  const serviciosInternos = conectores.filter((c) =>
    ['SIRECI', 'SIGECI', 'APA', 'DIARI'].includes(c.servicio)
  );

  return (
    <div className="min-h-full bg-[#0F1419] p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-[#E8EAED] flex items-center gap-2">
            <Plug className="h-6 w-6 text-[#C9A84C]" />
            Integraciones Externas
          </h1>
          <p className="text-sm text-[#9AA0A6] mt-1">
            Administre conectores, API keys y parametros de integracion
          </p>
        </div>
        <div className="flex items-center gap-2">
          {pestana === 'configuracion' && (
            <button
              onClick={guardarConfigAPIs}
              className="flex items-center gap-2 rounded-lg bg-[#C9A84C] px-4 py-2 text-sm font-medium text-[#0F1419] hover:bg-[#D4B84F] transition-colors"
            >
              {configGuardada ? <CheckCircle className="h-4 w-4" /> : <Save className="h-4 w-4" />}
              {configGuardada ? 'Guardado' : 'Guardar configuracion'}
            </button>
          )}
          <button
            onClick={cargarEstado}
            disabled={cargando}
            className="flex items-center gap-2 rounded-lg bg-[#1A2332] border border-[#2D3748] px-4 py-2 text-sm text-[#E8EAED] hover:bg-[#2D3748] transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${cargando ? 'animate-spin' : ''}`} />
            Verificar estado
          </button>
        </div>
      </div>

      {/* Pestanas */}
      <div className="flex gap-1 mb-6 border-b border-[#2D3748]/30">
        <button
          onClick={() => setPestana('estado')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-medium transition-all border-b-2 ${
            pestana === 'estado'
              ? 'text-[#C9A84C] border-[#C9A84C]'
              : 'text-[#5F6368] border-transparent hover:text-[#9AA0A6]'
          }`}
        >
          <Activity className="h-3.5 w-3.5" />
          Estado y Monitoreo
        </button>
        <button
          onClick={() => setPestana('configuracion')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-medium transition-all border-b-2 ${
            pestana === 'configuracion'
              ? 'text-[#C9A84C] border-[#C9A84C]'
              : 'text-[#5F6368] border-transparent hover:text-[#9AA0A6]'
          }`}
        >
          <Settings className="h-3.5 w-3.5" />
          Configuracion de APIs
        </button>
      </div>

      {pestana === 'estado' ? (
      <>
      {/* KPIs */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="rounded-lg bg-[#1A2332] border border-[#2D3748]/30 p-4">
          <p className="text-[10px] text-[#5F6368] uppercase tracking-wider">Total conectores</p>
          <p className="text-2xl font-bold text-[#E8EAED] mt-1">{conectores.length}</p>
        </div>
        <div className="rounded-lg bg-[#1A2332] border border-green-500/20 p-4">
          <p className="text-[10px] text-[#5F6368] uppercase tracking-wider">Disponibles</p>
          <p className="text-2xl font-bold text-green-400 mt-1">
            {conectores.filter((c) => c.estado === 'disponible').length}
          </p>
        </div>
        <div className="rounded-lg bg-[#1A2332] border border-yellow-500/20 p-4">
          <p className="text-[10px] text-[#5F6368] uppercase tracking-wider">Pendientes</p>
          <p className="text-2xl font-bold text-yellow-400 mt-1">
            {conectores.filter((c) => c.estado === 'pendiente').length}
          </p>
        </div>
        <div className="rounded-lg bg-[#1A2332] border border-red-500/20 p-4">
          <p className="text-[10px] text-[#5F6368] uppercase tracking-wider">No disponibles</p>
          <p className="text-2xl font-bold text-red-400 mt-1">
            {conectores.filter((c) => ['no_disponible', 'circuito_abierto'].includes(c.estado)).length}
          </p>
        </div>
      </div>

      {/* APIs Publicas */}
      <div className="mb-6">
        <h2 className="text-sm font-semibold text-[#C9A84C] mb-3 flex items-center gap-2">
          <ExternalLink className="h-4 w-4" />
          APIs Publicas (datos.gov.co)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {serviciosPublicos.map((conector) => (
            <div
              key={conector.servicio}
              className={`rounded-lg border p-4 ${colorEstado(conector.estado)} cursor-pointer hover:opacity-90 transition-opacity`}
              onClick={() => setConectorSeleccionado(conector.servicio)}
            >
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-[#E8EAED]">{conector.servicio}</h3>
                {iconoEstado(conector.estado)}
              </div>
              <p className="text-[10px] text-[#9AA0A6]">{etiquetaEstado(conector.estado)}</p>
              {conector.latencia_ms != null && conector.latencia_ms > 0 && (
                <p className="text-[10px] text-[#5F6368] mt-1">
                  Latencia: {conector.latencia_ms.toFixed(0)}ms
                </p>
              )}
              {conector.circuit_breaker && (
                <p className="text-[9px] text-[#5F6368] mt-1">
                  CB: {conector.circuit_breaker.estado} ({conector.circuit_breaker.fallos_consecutivos} fallos)
                </p>
              )}
              {conector.mensaje && (
                <p className="text-[9px] text-[#5F6368] mt-1 truncate" title={conector.mensaje}>
                  {conector.mensaje}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Sistemas Internos CGR */}
      <div className="mb-6">
        <h2 className="text-sm font-semibold text-[#C9A84C] mb-3 flex items-center gap-2">
          <Shield className="h-4 w-4" />
          Sistemas Internos CGR (requieren VPN)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {serviciosInternos.map((conector) => (
            <div
              key={conector.servicio}
              className={`rounded-lg border p-4 ${colorEstado(conector.estado)}`}
            >
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-[#E8EAED]">{conector.servicio}</h3>
                {iconoEstado(conector.estado)}
              </div>
              <p className="text-[10px] text-[#9AA0A6]">{etiquetaEstado(conector.estado)}</p>
              {conector.mensaje && (
                <p className="text-[9px] text-[#5F6368] mt-1 line-clamp-2">
                  {conector.mensaje}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Consulta rapida */}
      <div className="rounded-lg bg-[#1A2332] border border-[#2D3748]/30 p-4">
        <h2 className="text-sm font-semibold text-[#C9A84C] mb-3 flex items-center gap-2">
          <Search className="h-4 w-4" />
          Consulta rapida
        </h2>
        <div className="flex gap-2 mb-3">
          <select
            value={conectorSeleccionado || ''}
            onChange={(e) => setConectorSeleccionado(e.target.value || null)}
            className="rounded-lg bg-[#0F1419] border border-[#2D3748] px-3 py-2 text-xs text-[#E8EAED] outline-none"
          >
            <option value="">Seleccionar conector</option>
            {serviciosPublicos.map((c) => (
              <option key={c.servicio} value={c.servicio}>{c.servicio}</option>
            ))}
          </select>
          <input
            value={consultaRapida}
            onChange={(e) => setConsultaRapida(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && ejecutarConsultaRapida()}
            placeholder="Termino de busqueda..."
            className="flex-1 rounded-lg bg-[#0F1419] border border-[#2D3748] px-3 py-2 text-xs text-[#E8EAED] outline-none focus:border-[#C9A84C]/50"
          />
          <button
            onClick={ejecutarConsultaRapida}
            disabled={consultando || !conectorSeleccionado || !consultaRapida.trim()}
            className="rounded-lg bg-[#C9A84C] px-4 py-2 text-xs font-medium text-[#0F1419] hover:bg-[#D4B84F] transition-colors disabled:opacity-50"
          >
            {consultando ? 'Consultando...' : 'Consultar'}
          </button>
        </div>

        {resultadoConsulta && (
          <div className="rounded-lg bg-[#0F1419] border border-[#2D3748] p-3 max-h-[300px] overflow-auto">
            <pre className="text-[10px] text-[#9AA0A6] whitespace-pre-wrap">
              {JSON.stringify(resultadoConsulta, null, 2)}
            </pre>
          </div>
        )}
      </div>
      </>
      ) : (
      /* Pestana de Configuracion de APIs */
      <div className="space-y-4">
        <div className="rounded-lg bg-[#1A2332] border border-[#C9A84C]/20 p-4 mb-4">
          <div className="flex items-start gap-3">
            <Key className="h-5 w-5 text-[#C9A84C] mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-[#E8EAED]">Configuracion de API Keys y Parametros</h3>
              <p className="text-[10px] text-[#9AA0A6] mt-1">
                Configure las claves de acceso y URLs base para cada integracion.
                Las APIs publicas (datos.gov.co) funcionan sin clave. Las APIs internas CGR
                requieren configuracion por la Oficina de Sistemas cuando esten disponibles.
              </p>
            </div>
          </div>
        </div>

        {/* APIs Publicas */}
        <div>
          <h3 className="text-sm font-semibold text-[#C9A84C] mb-3 flex items-center gap-2">
            <ExternalLink className="h-4 w-4" />
            APIs Publicas
          </h3>
          <div className="space-y-3">
            {configAPIs.filter((a) => a.tipo === 'publica').map((api) => (
              <div key={api.nombre} className="rounded-lg border border-[#2D3748]/30 bg-[#1A2332] p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <h4 className="text-sm font-medium text-[#E8EAED]">{api.nombre}</h4>
                    <span className={`rounded-full px-2 py-0.5 text-[9px] font-medium ${
                      api.activo
                        ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                        : 'bg-red-500/10 text-red-400 border border-red-500/20'
                    }`}>
                      {api.activo ? 'Activa' : 'Inactiva'}
                    </span>
                  </div>
                  <button
                    onClick={() => actualizarConfigAPI(api.nombre, 'activo', !api.activo)}
                    className={`relative h-5 w-9 rounded-full transition-colors ${
                      api.activo ? 'bg-[#C9A84C]' : 'bg-[#2D3748]'
                    }`}
                  >
                    <div className={`absolute top-0.5 h-4 w-4 rounded-full bg-white transition-transform ${
                      api.activo ? 'translate-x-4' : 'translate-x-0.5'
                    }`} />
                  </button>
                </div>
                <p className="text-[10px] text-[#5F6368] mb-3">{api.descripcion}</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="text-[10px] text-[#5F6368] uppercase tracking-wider block mb-1">URL Base</label>
                    <input
                      value={api.url_base}
                      onChange={(e) => actualizarConfigAPI(api.nombre, 'url_base', e.target.value)}
                      className="w-full rounded-md border border-[#2D3748] bg-[#0F1419] px-3 py-2 text-xs text-[#E8EAED] focus:border-[#C9A84C] focus:outline-none"
                      placeholder="https://..."
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-[#5F6368] uppercase tracking-wider block mb-1">API Key (opcional)</label>
                    <div className="relative">
                      <input
                        type={mostrarClaves[api.nombre] ? 'text' : 'password'}
                        value={api.clave}
                        onChange={(e) => actualizarConfigAPI(api.nombre, 'clave', e.target.value)}
                        className="w-full rounded-md border border-[#2D3748] bg-[#0F1419] px-3 py-2 pr-8 text-xs text-[#E8EAED] focus:border-[#C9A84C] focus:outline-none"
                        placeholder="Dejar vacio si no requiere"
                      />
                      <button
                        onClick={() => setMostrarClaves((prev) => ({ ...prev, [api.nombre]: !prev[api.nombre] }))}
                        className="absolute right-2 top-1/2 -translate-y-1/2 text-[#5F6368] hover:text-[#9AA0A6]"
                      >
                        {mostrarClaves[api.nombre] ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* APIs Internas CGR */}
        <div>
          <h3 className="text-sm font-semibold text-[#C9A84C] mb-3 flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Sistemas Internos CGR
          </h3>
          <div className="space-y-3">
            {configAPIs.filter((a) => a.tipo === 'interna').map((api) => (
              <div key={api.nombre} className="rounded-lg border border-[#2D3748]/30 bg-[#1A2332] p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <h4 className="text-sm font-medium text-[#E8EAED]">{api.nombre}</h4>
                    <span className="rounded-full px-2 py-0.5 text-[9px] font-medium bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
                      Pendiente
                    </span>
                  </div>
                  <button
                    onClick={() => actualizarConfigAPI(api.nombre, 'activo', !api.activo)}
                    className={`relative h-5 w-9 rounded-full transition-colors ${
                      api.activo ? 'bg-[#C9A84C]' : 'bg-[#2D3748]'
                    }`}
                  >
                    <div className={`absolute top-0.5 h-4 w-4 rounded-full bg-white transition-transform ${
                      api.activo ? 'translate-x-4' : 'translate-x-0.5'
                    }`} />
                  </button>
                </div>
                <p className="text-[10px] text-[#5F6368] mb-3">{api.descripcion}</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="text-[10px] text-[#5F6368] uppercase tracking-wider block mb-1">URL Base</label>
                    <input
                      value={api.url_base}
                      onChange={(e) => actualizarConfigAPI(api.nombre, 'url_base', e.target.value)}
                      className="w-full rounded-md border border-[#2D3748] bg-[#0F1419] px-3 py-2 text-xs text-[#E8EAED] focus:border-[#C9A84C] focus:outline-none"
                      placeholder="URL proporcionada por la Oficina de Sistemas"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-[#5F6368] uppercase tracking-wider block mb-1">API Key / Token</label>
                    <div className="relative">
                      <input
                        type={mostrarClaves[api.nombre] ? 'text' : 'password'}
                        value={api.clave}
                        onChange={(e) => actualizarConfigAPI(api.nombre, 'clave', e.target.value)}
                        className="w-full rounded-md border border-[#2D3748] bg-[#0F1419] px-3 py-2 pr-8 text-xs text-[#E8EAED] focus:border-[#C9A84C] focus:outline-none"
                        placeholder="Credencial proporcionada por CD-TIC-CGR"
                      />
                      <button
                        onClick={() => setMostrarClaves((prev) => ({ ...prev, [api.nombre]: !prev[api.nombre] }))}
                        className="absolute right-2 top-1/2 -translate-y-1/2 text-[#5F6368] hover:text-[#9AA0A6]"
                      >
                        {mostrarClaves[api.nombre] ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Nota informativa */}
        <div className="rounded-lg border border-[#2D3748]/30 bg-[#0F1419]/50 p-4">
          <p className="text-[10px] text-[#5F6368] leading-relaxed">
            <strong className="text-[#9AA0A6]">Nota:</strong> Las APIs publicas (SECOP, DANE, Congreso)
            utilizan datos abiertos de datos.gov.co y no requieren credenciales. Los sistemas internos
            de la CGR (SIRECI, SIGECI, APA, DIARI) seran habilitados cuando la Oficina de Sistemas
            proporcione los accesos correspondientes. Para solicitar acceso, contacte a:
            <strong className="text-[#C9A84C]"> CD-TIC-CGR — sistemas@contraloria.gov.co</strong>
          </p>
        </div>
      </div>
      )}
    </div>
  );
}
