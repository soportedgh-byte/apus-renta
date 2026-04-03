/**
 * Tipos TypeScript para CecilIA v2
 * Contraloria General de la Republica de Colombia
 */

// === AUTENTICACION Y USUARIOS ===

/** Roles disponibles en el sistema */
export type RolUsuario = 'auditor' | 'director_des' | 'director_dvf' | 'admin' | 'superadmin';

/** Direcciones de la CGR */
export type Direccion = 'DES' | 'DVF';

/** Informacion de usuario autenticado */
export interface Usuario {
  id: number;
  usuario: string;
  nombre_completo: string;
  email: string;
  rol: string;
  direccion: Direccion | null;
  modulos: string[];
  permisos: string[];
  acciones_rapidas: string[];
}

/** Respuesta del endpoint de autenticacion */
export interface RespuestaAuth {
  token_acceso: string;
  token_refresco: string;
  tipo_token: string;
  expira_en_minutos: number;
  usuario: Usuario;
}

/** Credenciales de inicio de sesion */
export interface CredencialesLogin {
  usuario: string;
  contrasena: string;
}

// === CONVERSACIONES Y MENSAJES ===

/** Rol del mensaje en la conversacion */
export type RolMensaje = 'user' | 'assistant' | 'system';

/** Tipo de connotacion de hallazgo */
export type TipoConnotacion =
  | 'fiscal'
  | 'disciplinario'
  | 'penal'
  | 'administrativo'
  | 'fiscal_disciplinario';

/** Estado de un hallazgo en el flujo de trabajo */
export type EstadoHallazgo =
  | 'borrador'
  | 'en_revision'
  | 'aprobado'
  | 'rechazado'
  | 'trasladado'
  | 'archivado';

/** Estado de una auditoria */
export type EstadoAuditoria =
  | 'planeacion'
  | 'ejecucion'
  | 'informe'
  | 'cierre'
  | 'seguimiento';

/** Citacion de fuente en respuesta de IA */
export interface CitaFuente {
  documento: string;
  pagina?: number;
  seccion?: string;
  fragmento: string;
  confianza: number;
  coleccion: string;
}

/** Mensaje individual en una conversacion */
export interface Mensaje {
  id: string;
  conversacion_id: string;
  rol: RolMensaje;
  contenido: string;
  citas?: CitaFuente[];
  modelo_llm?: string;
  tokens_entrada?: number;
  tokens_salida?: number;
  tiempo_respuesta_ms?: number;
  feedback?: 'positivo' | 'negativo' | null;
  fecha_creacion: string;
}

/** Conversacion completa */
export interface Conversacion {
  id: string;
  titulo: string;
  usuario_id: string;
  direccion: Direccion;
  auditoria_id?: string;
  mensajes: Mensaje[];
  modelo_activo: string;
  fecha_creacion: string;
  fecha_actualizacion: string;
}

/** Resumen de conversacion para la lista del sidebar */
export interface ResumenConversacion {
  id: string;
  titulo: string;
  direccion: Direccion;
  ultimo_mensaje?: string;
  fecha_actualizacion: string;
}

// === DOCUMENTOS ===

/** Coleccion a la que pertenece un documento */
export type ColeccionDocumento =
  | 'normativo'
  | 'metodologico'
  | 'sectorial'
  | 'auditoria'
  | 'hallazgo';

/** Documento cargado al sistema */
export interface Documento {
  id: string;
  nombre: string;
  tipo_archivo: string;
  tamano_bytes: number;
  coleccion: ColeccionDocumento;
  auditoria_id?: string;
  usuario_id: string;
  estado_procesamiento: 'pendiente' | 'procesando' | 'completado' | 'error';
  chunks_totales?: number;
  fecha_carga: string;
  metadatos?: Record<string, unknown>;
}

// === AUDITORIAS ===

/** Auditoria registrada en el sistema */
export interface Auditoria {
  id: string;
  nombre: string;
  entidad_auditada: string;
  sector: string;
  direccion: Direccion;
  estado: EstadoAuditoria;
  responsable_id: string;
  responsable_nombre: string;
  fecha_inicio: string;
  fecha_fin?: string;
  descripcion?: string;
  equipo: string[];
  hallazgos_count: number;
  fecha_creacion: string;
}

// === HALLAZGOS ===

/** Los 5 elementos de un hallazgo fiscal */
export interface ElementosHallazgo {
  condicion: string;
  criterio: string;
  causa: string;
  efecto: string;
  recomendacion: string;
}

/** Hallazgo de auditoria */
export interface Hallazgo {
  id: string;
  auditoria_id: string;
  titulo: string;
  connotacion: TipoConnotacion;
  estado: EstadoHallazgo;
  elementos: ElementosHallazgo;
  cuantia?: number;
  responsables?: string[];
  evidencias: string[];
  generado_por_ia: boolean;
  validado_por?: string;
  fecha_creacion: string;
  fecha_actualizacion: string;
  historial_flujo: EventoFlujo[];
}

/** Evento en el flujo de trabajo de un hallazgo */
export interface EventoFlujo {
  estado_anterior: EstadoHallazgo;
  estado_nuevo: EstadoHallazgo;
  usuario: string;
  comentario?: string;
  fecha: string;
}

// === FORMATOS ===

/** Formato generado por el sistema */
export interface Formato {
  id: string;
  numero: number;
  nombre: string;
  auditoria_id: string;
  estado: 'borrador' | 'generado' | 'aprobado';
  url_descarga?: string;
  generado_por_ia: boolean;
  fecha_generacion: string;
}

// === OBSERVATORIO (DES) ===

/** Alerta del observatorio sectorial */
export interface AlertaObservatorio {
  id: string;
  titulo: string;
  sector: string;
  severidad: 'baja' | 'media' | 'alta' | 'critica';
  descripcion: string;
  indicadores: IndicadorSectorial[];
  fecha_deteccion: string;
  estado: 'nueva' | 'en_analisis' | 'resuelta';
}

/** Indicador sectorial para el observatorio */
export interface IndicadorSectorial {
  nombre: string;
  valor_actual: number;
  valor_anterior: number;
  unidad: string;
  tendencia: 'alza' | 'baja' | 'estable';
}

// === ANALYTICS ===

/** Registro de uso del sistema */
export interface RegistroUso {
  fecha: string;
  consultas_totales: number;
  tokens_consumidos: number;
  modelo: string;
  tiempo_promedio_ms: number;
  usuario_id: string;
}

/** Metricas de rendimiento de modelo */
export interface MetricasModelo {
  modelo: string;
  consultas: number;
  tiempo_promedio_ms: number;
  tokens_promedio: number;
  satisfaccion: number;
}

// === ACCIONES RAPIDAS ===

/** Accion rapida disponible segun el rol */
export interface AccionRapida {
  id: string;
  etiqueta: string;
  icono: string;
  prompt_base: string;
  direccion: Direccion;
  categoria: string;
}

// === CONFIGURACION DEL SISTEMA ===

/** Estado de conexion del sistema */
export interface EstadoSistema {
  cecilia_conectada: boolean;
  modelo_activo: string;
  version: string;
  workspace_activo?: string;
  desktop_agent_conectado: boolean;
}

/** Respuesta paginada generica */
export interface RespuestaPaginada<T> {
  items: T[];
  total: number;
  pagina: number;
  tamano_pagina: number;
  paginas_totales: number;
}

/** Evento de streaming SSE */
export interface EventoSSE {
  tipo: 'token' | 'cita' | 'error' | 'fin';
  contenido?: string;
  cita?: CitaFuente;
  error?: string;
}
