/**
 * Cliente WebSocket para comunicacion con el Desktop Agent de CecilIA
 * Permite acceso a archivos locales del equipo del auditor
 */

/** Tipos de mensajes del Desktop Agent */
export type TipoMensajeWS =
  | 'conectar'
  | 'desconectar'
  | 'listar_archivos'
  | 'leer_archivo'
  | 'escribir_archivo'
  | 'estado'
  | 'error';

/** Mensaje enviado o recibido por WebSocket */
export interface MensajeWS {
  tipo: TipoMensajeWS;
  datos?: unknown;
  id_peticion?: string;
}

/** Archivo local del Desktop Agent */
export interface ArchivoLocal {
  nombre: string;
  ruta: string;
  tipo: 'archivo' | 'directorio';
  tamano?: number;
  fecha_modificacion?: string;
  extension?: string;
}

/** Estado del Desktop Agent */
export interface EstadoDesktopAgent {
  conectado: boolean;
  version?: string;
  directorio_base?: string;
  archivos_cargados?: number;
}

/** Callbacks para eventos del WebSocket */
export interface CallbacksWS {
  alConectar?: () => void;
  alDesconectar?: () => void;
  alRecibirMensaje?: (mensaje: MensajeWS) => void;
  alError?: (error: Event) => void;
}

/**
 * Clase que gestiona la conexion WebSocket con el Desktop Agent
 */
export class ClienteDesktopAgent {
  private ws: WebSocket | null = null;
  private callbacks: CallbacksWS;
  private url: string;
  private intentosReconexion = 0;
  private maxIntentos = 5;
  private temporizadorReconexion: ReturnType<typeof setTimeout> | null = null;

  constructor(callbacks: CallbacksWS) {
    this.url = process.env.NEXT_PUBLIC_WS_AGENT_URL || 'ws://localhost:9000/ws/agent';
    this.callbacks = callbacks;
  }

  /** Conectar al Desktop Agent */
  conectar(): void {
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.intentosReconexion = 0;
        this.enviar({ tipo: 'conectar' });
        this.callbacks.alConectar?.();
      };

      this.ws.onclose = () => {
        this.callbacks.alDesconectar?.();
        this.intentarReconexion();
      };

      this.ws.onmessage = (evento) => {
        try {
          const mensaje: MensajeWS = JSON.parse(evento.data);
          this.callbacks.alRecibirMensaje?.(mensaje);
        } catch {
          console.error('[CecilIA WS] Error al parsear mensaje:', evento.data);
        }
      };

      this.ws.onerror = (error) => {
        this.callbacks.alError?.(error);
      };
    } catch (error) {
      console.error('[CecilIA WS] Error al conectar:', error);
    }
  }

  /** Desconectar del Desktop Agent */
  desconectar(): void {
    if (this.temporizadorReconexion) {
      clearTimeout(this.temporizadorReconexion);
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /** Enviar un mensaje al Desktop Agent */
  enviar(mensaje: MensajeWS): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(mensaje));
    }
  }

  /** Solicitar listado de archivos de un directorio */
  listarArchivos(ruta: string): void {
    this.enviar({
      tipo: 'listar_archivos',
      datos: { ruta },
      id_peticion: crypto.randomUUID(),
    });
  }

  /** Solicitar lectura de un archivo */
  leerArchivo(ruta: string): void {
    this.enviar({
      tipo: 'leer_archivo',
      datos: { ruta },
      id_peticion: crypto.randomUUID(),
    });
  }

  /** Verificar si esta conectado */
  get estaConectado(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /** Intentar reconexion automatica */
  private intentarReconexion(): void {
    if (this.intentosReconexion >= this.maxIntentos) return;

    this.intentosReconexion++;
    const espera = Math.min(1000 * Math.pow(2, this.intentosReconexion), 30000);

    this.temporizadorReconexion = setTimeout(() => {
      this.conectar();
    }, espera);
  }
}
