import { redirect } from 'next/navigation';

/**
 * Pagina raiz: redirige automaticamente al inicio de sesion.
 */
export default function PaginaInicio() {
  redirect('/login');
}
