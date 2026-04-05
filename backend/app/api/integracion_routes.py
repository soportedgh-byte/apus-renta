"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: app/api/integracion_routes.py
Proposito: Endpoints de integraciones externas — consulta SECOP, DANE, Congreso,
           verificacion de estado y gestion de conectores
Sprint: 7
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

logger = logging.getLogger("cecilia.api.integraciones")

enrutador = APIRouter()


# ── Esquemas ─────────────────────────────────────────────────────────────────


class ContratoSECOP(BaseModel):
    """Esquema de un contrato consultado en SECOP II."""
    id_contrato: str = ""
    numero_proceso: str = ""
    entidad_compradora: str = ""
    contratista: str = ""
    nit_contratista: str = ""
    objeto: str = ""
    valor_total: float = 0
    fecha_firma: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    estado: str = ""
    tipo_contrato: str = ""
    modalidad: str = ""
    departamento: str = ""
    municipio: str = ""
    url_secop: Optional[str] = None


class IndicadorDANE(BaseModel):
    """Esquema de un indicador estadistico del DANE."""
    codigo: str
    nombre: str
    valor: float
    unidad: str = ""
    periodo: str = ""
    fuente: str = ""
    fecha_publicacion: Optional[str] = None


class ProyectoLey(BaseModel):
    """Esquema de un proyecto de ley o acto legislativo."""
    numero: str = ""
    titulo: str = ""
    autores: list[str] = []
    estado: str = ""
    comision: str = ""
    fecha_radicacion: Optional[str] = None
    legislatura: str = ""
    tipo: str = ""
    url: Optional[str] = None


class EstadoIntegracion(BaseModel):
    """Estado de salud de un servicio externo integrado."""
    servicio: str
    estado: str  # disponible | degradado | no_disponible | pendiente | circuito_abierto
    latencia_ms: Optional[float] = None
    ultimo_chequeo: datetime
    mensaje: Optional[str] = None
    circuit_breaker: Optional[dict[str, Any]] = None


class ConsultaGenericaRequest(BaseModel):
    """Request para consulta generica a un conector."""
    parametros: dict[str, Any] = Field(default_factory=dict)


class ConsultaGenericaResponse(BaseModel):
    """Response de consulta generica."""
    servicio: str
    exito: bool
    datos: Any = None
    mensaje: Optional[str] = None
    duracion_ms: Optional[float] = None


# ── Dependencia temporal de usuario autenticado ──────────────────────────────


async def _obtener_usuario_actual_id() -> int:
    """Dependencia temporal — sera reemplazada por auth real."""
    return 1


# ── Endpoints de estado ────────────────────────────────────────────────────────


@enrutador.get(
    "/estado",
    response_model=list[EstadoIntegracion],
    summary="Verificar estado de todas las integraciones",
    description="Verifica el estado de conectividad de todos los servicios externos.",
)
async def verificar_estado_integraciones(
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> list[dict[str, Any]]:
    """Retorna el estado de salud de cada integracion externa.

    Realiza chequeo de conectividad contra servicios publicos (SECOP, DANE, Congreso)
    y reporta estado pendiente para los internos CGR (SIRECI, SIGECI, APA, DIARI).
    """
    import time

    ahora: datetime = datetime.now(timezone.utc)
    servicios: list[dict[str, Any]] = []

    # ── Servicios publicos: verificar salud real ──
    servicios_publicos = [
        ("SECOP II", "app.integraciones.secop", "ClienteSECOP"),
        ("DANE", "app.integraciones.dane", "ClienteDANE"),
        ("Congreso", "app.integraciones.congreso", "ClienteCongreso"),
    ]

    for nombre, modulo_path, clase_name in servicios_publicos:
        try:
            import importlib
            modulo = importlib.import_module(modulo_path)
            clase = getattr(modulo, clase_name)
            cliente = clase()
            inicio = time.monotonic()
            estado_servicio = await cliente.verificar_salud()
            await cliente.cerrar()

            servicios.append({
                "servicio": nombre,
                "estado": estado_servicio.get("estado", "no_disponible"),
                "latencia_ms": estado_servicio.get("latencia_ms"),
                "ultimo_chequeo": ahora,
                "mensaje": estado_servicio.get("error") or f"Servicio {estado_servicio.get('estado', 'desconocido')}",
                "circuit_breaker": estado_servicio.get("circuit_breaker"),
            })
        except Exception as exc:
            servicios.append({
                "servicio": nombre,
                "estado": "no_disponible",
                "latencia_ms": None,
                "ultimo_chequeo": ahora,
                "mensaje": f"Error al verificar: {exc}",
            })

    # ── Servicios internos CGR: estado pendiente ──
    servicios_cgr = [
        ("SIRECI", "Sistema de Rendicion Electronica de la Cuenta e Informes — requiere VPN CGR"),
        ("SIGECI", "Sistema de Gestion del Control e Investigacion — requiere VPN CGR"),
        ("APA", "Aplicativo de Planeacion de Auditorias — requiere VPN CGR"),
        ("DIARI", "Directorio de Informes de Auditoria — requiere VPN CGR"),
    ]

    for nombre, desc in servicios_cgr:
        servicios.append({
            "servicio": nombre,
            "estado": "pendiente",
            "latencia_ms": None,
            "ultimo_chequeo": ahora,
            "mensaje": desc,
        })

    logger.info("Verificacion de estado de integraciones: %d servicios", len(servicios))
    return servicios


# ── Endpoints SECOP ──────────────────────────────────────────────────────────


@enrutador.get(
    "/secop/contratos",
    response_model=list[ContratoSECOP],
    summary="Buscar contratos en SECOP",
    description="Consulta contratos publicos en SECOP II por entidad, contratista o proceso.",
)
async def buscar_contratos_secop(
    entidad: Optional[str] = Query(default=None, description="Nombre de la entidad compradora"),
    contratista: Optional[str] = Query(default=None, description="Nombre o NIT del contratista"),
    numero_proceso: Optional[str] = Query(default=None, description="Numero del proceso contractual"),
    valor_minimo: Optional[float] = Query(default=None, ge=0, description="Valor minimo del contrato"),
    valor_maximo: Optional[float] = Query(default=None, ge=0, description="Valor maximo del contrato"),
    limite: int = Query(default=20, ge=1, le=100),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> list[dict[str, Any]]:
    """Busca contratos en SECOP II con multiples filtros."""
    if not any([entidad, contratista, numero_proceso]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe especificar al menos un criterio: entidad, contratista o numero_proceso.",
        )

    from app.integraciones.secop import ClienteSECOP

    try:
        async with ClienteSECOP() as cliente:
            resultados = await cliente.buscar_contratos(
                entidad=entidad,
                contratista=contratista,
                numero_proceso=numero_proceso,
                valor_minimo=valor_minimo,
                valor_maximo=valor_maximo,
                limite=limite,
            )
            logger.info(
                "SECOP contratos: %d resultados (entidad=%s, contratista=%s, usuario=%d)",
                len(resultados), entidad, contratista, usuario_id,
            )
            return resultados
    except Exception as exc:
        logger.exception("Error en endpoint SECOP contratos.")
        raise HTTPException(status_code=502, detail=f"Error al consultar SECOP: {exc}")


@enrutador.get(
    "/secop/contratista/{nit_o_nombre}",
    summary="Buscar contratista en SECOP",
    description="Busca todos los contratos de un contratista por NIT o nombre.",
)
async def buscar_contratista_secop(
    nit_o_nombre: str,
    limite: int = Query(default=50, ge=1, le=200),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Busca contratos de un contratista por NIT o nombre."""
    from app.integraciones.secop import ClienteSECOP

    try:
        async with ClienteSECOP() as cliente:
            resultado = await cliente.buscar_contratista(nit_o_nombre=nit_o_nombre, limite=limite)
            logger.info("SECOP contratista: '%s' — %d contratos", nit_o_nombre, resultado.get("total_contratos", 0))
            return resultado
    except Exception as exc:
        logger.exception("Error en endpoint SECOP contratista.")
        raise HTTPException(status_code=502, detail=f"Error al consultar contratista: {exc}")


@enrutador.get(
    "/secop/detalle/{numero_proceso}",
    summary="Detalle de contrato SECOP",
    description="Obtiene el detalle completo de un contrato por numero de proceso.",
)
async def detalle_contrato_secop(
    numero_proceso: str,
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Obtiene detalle de un contrato por numero de proceso."""
    from app.integraciones.secop import ClienteSECOP

    try:
        async with ClienteSECOP() as cliente:
            resultado = await cliente.obtener_detalle_contrato(numero_proceso=numero_proceso)
            return resultado
    except Exception as exc:
        logger.exception("Error en endpoint SECOP detalle.")
        raise HTTPException(status_code=502, detail=f"Error al obtener detalle: {exc}")


@enrutador.get(
    "/secop/precios",
    summary="Analisis de precios de mercado SECOP",
    description="Analiza precios de mercado para un tipo de objeto contractual.",
)
async def analizar_precios_secop(
    objeto: str = Query(..., description="Descripcion del objeto contractual"),
    region: Optional[str] = Query(default=None, description="Departamento o region"),
    anno: Optional[int] = Query(default=None, description="Ano de contratos a considerar"),
    limite: int = Query(default=100, ge=10, le=500),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Analiza precios de mercado para un tipo de objeto contractual."""
    from app.integraciones.secop import ClienteSECOP

    try:
        async with ClienteSECOP() as cliente:
            resultado = await cliente.analizar_precios_mercado(
                objeto_contractual=objeto,
                region=region,
                anno=anno,
                limite=limite,
            )
            return resultado
    except Exception as exc:
        logger.exception("Error en endpoint SECOP precios.")
        raise HTTPException(status_code=502, detail=f"Error al analizar precios: {exc}")


# ── Endpoints DANE ───────────────────────────────────────────────────────────


@enrutador.get(
    "/dane/indicadores",
    summary="Consultar indicadores DANE",
    description="Obtiene indicadores estadisticos del DANE por codigo o categoria.",
)
async def obtener_indicadores_dane(
    codigo: Optional[str] = Query(default=None, description="Codigo del indicador DANE"),
    periodo: Optional[str] = Query(default=None, description="Periodo de consulta (e.g., '2025')"),
    departamento: Optional[str] = Query(default=None, description="Codigo DIVIPOLA del departamento"),
    limite: int = Query(default=20, ge=1, le=100),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Consulta indicadores estadisticos del DANE."""
    from app.integraciones.dane import ClienteDANE

    if not codigo:
        # Retornar catalogo de indicadores disponibles
        cliente = ClienteDANE()
        catalogo = cliente.obtener_indicadores_disponibles()
        await cliente.cerrar()
        return {"indicadores_disponibles": catalogo}

    try:
        async with ClienteDANE() as cliente:
            registros = await cliente.obtener_indicador(
                codigo_indicador=codigo,
                periodo=periodo,
                departamento=departamento,
                limite=limite,
            )
            return {
                "indicador": codigo,
                "total_registros": len(registros),
                "registros": registros,
            }
    except Exception as exc:
        logger.exception("Error en endpoint DANE indicadores.")
        raise HTTPException(status_code=502, detail=f"Error al consultar DANE: {exc}")


@enrutador.get(
    "/dane/ipc",
    summary="Obtener IPC",
    description="Obtiene el Indice de Precios al Consumidor.",
)
async def obtener_ipc_dane(
    periodo: Optional[str] = Query(default=None, description="Ano o periodo"),
    departamento: Optional[str] = Query(default=None),
    limite: int = Query(default=12, ge=1, le=100),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Obtiene datos del IPC."""
    from app.integraciones.dane import ClienteDANE

    try:
        async with ClienteDANE() as cliente:
            return await cliente.obtener_ipc(periodo=periodo, departamento=departamento, limite=limite)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error al consultar IPC: {exc}")


@enrutador.get(
    "/dane/pib",
    summary="Obtener PIB sectorial",
    description="Obtiene el PIB desglosado por sector economico.",
)
async def obtener_pib_dane(
    sector: Optional[str] = Query(default=None, description="Sector economico"),
    periodo: Optional[str] = Query(default=None, description="Ano o trimestre"),
    limite: int = Query(default=20, ge=1, le=100),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Obtiene datos del PIB sectorial."""
    from app.integraciones.dane import ClienteDANE

    try:
        async with ClienteDANE() as cliente:
            return await cliente.obtener_pib_sectorial(sector=sector, periodo=periodo, limite=limite)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error al consultar PIB: {exc}")


@enrutador.get(
    "/dane/tic",
    summary="Obtener estadisticas TIC",
    description="Obtiene indicadores de Tecnologias de Informacion y Comunicaciones.",
)
async def obtener_tic_dane(
    indicador: Optional[str] = Query(default=None, description="Indicador TIC especifico"),
    periodo: Optional[str] = Query(default=None),
    departamento: Optional[str] = Query(default=None),
    limite: int = Query(default=20, ge=1, le=100),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Obtiene estadisticas TIC del DANE."""
    from app.integraciones.dane import ClienteDANE

    try:
        async with ClienteDANE() as cliente:
            return await cliente.obtener_estadisticas_tic(
                indicador=indicador, periodo=periodo, departamento=departamento, limite=limite,
            )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error al consultar TIC: {exc}")


# ── Endpoints Congreso ───────────────────────────────────────────────────────


@enrutador.get(
    "/congreso/proyectos",
    summary="Consultar proyectos de ley",
    description="Busca proyectos de ley y actos legislativos.",
)
async def obtener_proyectos_congreso(
    termino_busqueda: Optional[str] = Query(default=None, description="Termino de busqueda"),
    legislatura: Optional[str] = Query(default=None, description="Legislatura (e.g., '2025-2026')"),
    estado: Optional[str] = Query(default=None, description="Estado del tramite"),
    comision: Optional[str] = Query(default=None, description="Comision asignada"),
    limite: int = Query(default=20, ge=1, le=100),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> list[dict[str, Any]]:
    """Busca proyectos de ley en el Congreso."""
    from app.integraciones.congreso import ClienteCongreso

    try:
        async with ClienteCongreso() as cliente:
            return await cliente.buscar_proyectos(
                termino_busqueda=termino_busqueda,
                legislatura=legislatura,
                estado=estado,
                comision=comision,
                limite=limite,
            )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error al consultar Congreso: {exc}")


@enrutador.get(
    "/congreso/norma",
    summary="Buscar norma especifica",
    description="Busca una norma por tipo, numero y ano.",
)
async def buscar_norma_congreso(
    tipo: str = Query(..., description="Tipo de norma: ley, decreto, acto_legislativo, resolucion"),
    numero: Optional[int] = Query(default=None, description="Numero de la norma"),
    anio: Optional[int] = Query(default=None, description="Ano de la norma"),
    termino: Optional[str] = Query(default=None, description="Termino de busqueda en titulo"),
    limite: int = Query(default=10, ge=1, le=50),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> list[dict[str, Any]]:
    """Busca una norma especifica por tipo, numero y ano."""
    from app.integraciones.congreso import ClienteCongreso

    try:
        async with ClienteCongreso() as cliente:
            return await cliente.buscar_norma(
                tipo=tipo, numero=numero, anio=anio, termino=termino, limite=limite,
            )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error al buscar norma: {exc}")


@enrutador.get(
    "/congreso/vigencia",
    summary="Verificar vigencia de norma",
    description="Verifica si una norma sigue vigente.",
)
async def verificar_vigencia_norma(
    tipo: str = Query(..., description="Tipo: ley, decreto, acto_legislativo"),
    numero: Optional[int] = Query(default=None, description="Numero de la norma"),
    anio: Optional[int] = Query(default=None, description="Ano de la norma"),
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Verifica la vigencia de una norma."""
    from app.integraciones.congreso import ClienteCongreso

    try:
        async with ClienteCongreso() as cliente:
            return await cliente.verificar_vigencia(tipo=tipo, numero=numero, anio=anio)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error al verificar vigencia: {exc}")


# ── Consulta generica por nombre de conector ─────────────────────────────────


@enrutador.post(
    "/{nombre}/consultar",
    response_model=ConsultaGenericaResponse,
    summary="Consulta generica a un conector",
    description="Permite enviar una consulta personalizada a cualquier conector.",
)
async def consultar_conector(
    nombre: str,
    request: ConsultaGenericaRequest,
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Consulta generica a un conector por nombre."""
    import time

    nombre_lower = nombre.lower()
    inicio = time.monotonic()

    conectores_disponibles = {
        "secop": ("app.integraciones.secop", "ClienteSECOP", "buscar_contratos"),
        "dane": ("app.integraciones.dane", "ClienteDANE", "obtener_indicador"),
        "congreso": ("app.integraciones.congreso", "ClienteCongreso", "buscar_proyectos"),
        "sireci": ("app.integraciones.sireci", "ClienteSIRECI", "consultar_rendicion"),
        "sigeci": ("app.integraciones.sigeci", "ClienteSIGECI", "obtener_auditoria"),
        "apa": ("app.integraciones.apa", "ClienteAPA", "obtener_plan_vigilancia"),
        "diari": ("app.integraciones.diari", "ClienteDIARI", "buscar_informes"),
    }

    if nombre_lower not in conectores_disponibles:
        raise HTTPException(
            status_code=404,
            detail=f"Conector '{nombre}' no encontrado. Disponibles: {list(conectores_disponibles.keys())}",
        )

    modulo_path, clase_name, metodo_default = conectores_disponibles[nombre_lower]

    try:
        import importlib
        modulo = importlib.import_module(modulo_path)
        clase = getattr(modulo, clase_name)
        cliente = clase()

        metodo_nombre = request.parametros.pop("metodo", metodo_default)
        metodo = getattr(cliente, metodo_nombre, None)

        if not metodo:
            await cliente.cerrar()
            raise HTTPException(
                status_code=400,
                detail=f"Metodo '{metodo_nombre}' no disponible en el conector '{nombre}'.",
            )

        resultado = await metodo(**request.parametros)
        await cliente.cerrar()
        duracion = (time.monotonic() - inicio) * 1000

        return {
            "servicio": nombre,
            "exito": True,
            "datos": resultado,
            "duracion_ms": round(duracion, 1),
        }

    except HTTPException:
        raise
    except Exception as exc:
        duracion = (time.monotonic() - inicio) * 1000
        logger.exception("Error en consulta generica a '%s'.", nombre)
        return {
            "servicio": nombre,
            "exito": False,
            "mensaje": str(exc),
            "duracion_ms": round(duracion, 1),
        }


# ── Configuracion de APIs (administrable) ──────────────────────────────────


class ConfiguracionAPIRequest(BaseModel):
    """Request para guardar configuracion de APIs."""
    apis: list[dict[str, Any]] = Field(..., description="Lista de configuraciones de API")


class ConfiguracionAPIResponse(BaseModel):
    """Response de configuracion guardada."""
    exito: bool
    mensaje: str
    apis_configuradas: int


# Almacenamiento en memoria (en produccion se persistiria en BD)
_config_apis: dict[str, dict[str, Any]] = {}


@enrutador.post(
    "/configurar",
    response_model=ConfiguracionAPIResponse,
    summary="Configurar APIs externas",
    description="Permite al admin configurar API keys, URLs base y estado de conectores.",
)
async def configurar_apis(
    request: ConfiguracionAPIRequest,
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Guarda la configuracion de APIs proporcionada por el admin.

    En produccion, esto se persistiria en base de datos y se usaria
    para inicializar los clientes de integracion.
    """
    global _config_apis

    for api_config in request.apis:
        nombre = api_config.get("nombre", "")
        if nombre:
            _config_apis[nombre] = {
                "url_base": api_config.get("url_base", ""),
                "clave": api_config.get("clave", ""),
                "activo": api_config.get("activo", False),
                "tipo": api_config.get("tipo", "publica"),
            }

    logger.info(
        "Configuracion de APIs actualizada por usuario_id=%d: %d APIs configuradas",
        usuario_id, len(request.apis),
    )

    return {
        "exito": True,
        "mensaje": f"Configuracion guardada para {len(request.apis)} APIs.",
        "apis_configuradas": len(request.apis),
    }


@enrutador.get(
    "/configuracion",
    summary="Obtener configuracion actual de APIs",
    description="Retorna la configuracion actual de los conectores.",
)
async def obtener_configuracion_apis(
    usuario_id: int = Depends(_obtener_usuario_actual_id),
) -> dict[str, Any]:
    """Retorna la configuracion actual de APIs."""
    return {
        "apis": _config_apis,
        "total": len(_config_apis),
    }
