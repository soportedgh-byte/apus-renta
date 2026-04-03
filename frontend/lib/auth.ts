/**
 * Utilidades de autenticacion para CecilIA v2
 * Manejo de JWT, sesion y permisos
 */

import { apiCliente } from './api';
import type { CredencialesLogin, RespuestaAuth, Usuario, Direccion } from './types';

const CLAVE_TOKEN = 'cecilia_token';
const CLAVE_USUARIO = 'cecilia_usuario';
const CLAVE_DIRECCION = 'cecilia_direccion_activa';

/**
 * Inicia sesion con credenciales y almacena el token JWT
 */
export async function iniciarSesion(credenciales: CredencialesLogin): Promise<Usuario> {
  const respuesta = await apiCliente.post<RespuestaAuth>('/auth/login', credenciales);

  if (typeof window !== 'undefined') {
    localStorage.setItem(CLAVE_TOKEN, respuesta.access_token);
    localStorage.setItem(CLAVE_USUARIO, JSON.stringify(respuesta.usuario));
  }

  return respuesta.usuario;
}

/**
 * Cierra la sesion del usuario
 */
export function cerrarSesion(): void {
  if (typeof window === 'undefined') return;

  localStorage.removeItem(CLAVE_TOKEN);
  localStorage.removeItem(CLAVE_USUARIO);
  localStorage.removeItem(CLAVE_DIRECCION);
  window.location.href = '/login';
}

/**
 * Obtiene el token JWT actual
 */
export function obtenerToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(CLAVE_TOKEN);
}

/**
 * Obtiene los datos del usuario actual desde localStorage
 */
export function obtenerUsuario(): Usuario | null {
  if (typeof window === 'undefined') return null;

  const datos = localStorage.getItem(CLAVE_USUARIO);
  if (!datos) return null;

  try {
    return JSON.parse(datos) as Usuario;
  } catch {
    return null;
  }
}

/**
 * Verifica si el usuario esta autenticado
 */
export function estaAutenticado(): boolean {
  return !!obtenerToken() && !!obtenerUsuario();
}

/**
 * Establece la direccion activa (DES o DVF)
 */
export function establecerDireccionActiva(direccion: Direccion): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(CLAVE_DIRECCION, direccion);
}

/**
 * Obtiene la direccion activa actual
 */
export function obtenerDireccionActiva(): Direccion | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(CLAVE_DIRECCION) as Direccion | null;
}

/**
 * Verifica si el usuario puede ver una direccion especifica
 */
export function puedeVerDireccion(direccion: Direccion): boolean {
  const usuario = obtenerUsuario();
  if (!usuario) return false;
  return usuario.puede_ver.includes(direccion);
}

/**
 * Verifica si el usuario tiene un rol especifico
 */
export function tieneRol(rol: string): boolean {
  const usuario = obtenerUsuario();
  if (!usuario) return false;
  return usuario.rol === rol;
}

/**
 * Verifica si el usuario es administrador
 */
export function esAdmin(): boolean {
  const usuario = obtenerUsuario();
  if (!usuario) return false;
  return usuario.rol === 'admin' || usuario.rol === 'superadmin';
}

/**
 * Verifica si el usuario es director
 */
export function esDirector(): boolean {
  const usuario = obtenerUsuario();
  if (!usuario) return false;
  return usuario.rol === 'director_des' || usuario.rol === 'director_dvf';
}
