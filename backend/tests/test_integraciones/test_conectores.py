"""
Tests para los conectores SECOP, DANE y Congreso.
Valida inicializacion, metodos disponibles y normalizacion de datos.
"""

import pytest


def _cargar_modulo(nombre_archivo):
    """Carga un modulo de integraciones directamente para evitar import chain."""
    import importlib.util
    import os
    import sys

    # Asegurar que httpx esta disponible o mockeado
    if "httpx" not in sys.modules:
        import types
        mock_httpx = types.ModuleType("httpx")
        mock_httpx.AsyncClient = type("AsyncClient", (), {"__init__": lambda self, **kw: None})
        mock_httpx.Timeout = lambda x: None
        mock_httpx.ConnectTimeout = Exception
        mock_httpx.ReadTimeout = Exception
        mock_httpx.ConnectError = Exception
        mock_httpx.Response = type("Response", (), {})
        sys.modules["httpx"] = mock_httpx

    # Cargar base primero
    base_path = os.path.join(os.path.dirname(__file__), "..", "..", "app", "integraciones", "base.py")
    spec_base = importlib.util.spec_from_file_location("app.integraciones.base", base_path)
    mod_base = importlib.util.module_from_spec(spec_base)
    sys.modules["app.integraciones.base"] = mod_base
    spec_base.loader.exec_module(mod_base)

    # Cargar el modulo solicitado
    mod_path = os.path.join(os.path.dirname(__file__), "..", "..", "app", "integraciones", nombre_archivo)
    spec = importlib.util.spec_from_file_location(f"app.integraciones.{nombre_archivo[:-3]}", mod_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestClienteSECOP:
    """Tests del cliente SECOP."""

    def test_nombre_servicio(self):
        mod = _cargar_modulo("secop.py")
        assert mod.ClienteSECOP.nombre_servicio == "SECOP II"

    def test_url_base(self):
        mod = _cargar_modulo("secop.py")
        assert mod.ClienteSECOP.url_base == "https://www.datos.gov.co"

    def test_normalizar_contrato(self):
        mod = _cargar_modulo("secop.py")
        cliente = mod.ClienteSECOP.__new__(mod.ClienteSECOP)
        # No inicializamos __init__ para evitar httpx

        contrato_raw = {
            "id_del_portafolio": "ABC123",
            "referencia_del_contrato": "REF-001",
            "nombre_entidad": "Ministerio TIC",
            "proveedor_adjudicado": "Empresa XYZ",
            "nit_del_proveedor_adjudicado": "900123456",
            "descripcion_del_proceso": "Servicio de internet",
            "valor_del_contrato": "1500000000",
            "fecha_de_firma": "2025-06-15",
            "estado_contrato": "Celebrado",
            "tipo_de_contrato": "Prestacion de servicios",
            "modalidad_de_contratacion": "Licitacion publica",
            "departamento": "Bogota D.C.",
            "ciudad": "Bogota",
        }

        resultado = cliente._normalizar_contrato(contrato_raw)

        assert resultado["id_contrato"] == "ABC123"
        assert resultado["entidad_compradora"] == "Ministerio TIC"
        assert resultado["contratista"] == "Empresa XYZ"
        assert resultado["nit_contratista"] == "900123456"
        assert resultado["valor_total"] == 1500000000.0
        assert resultado["estado"] == "Celebrado"
        assert resultado["departamento"] == "Bogota D.C."

    def test_tiene_metodos_nuevos(self):
        mod = _cargar_modulo("secop.py")
        assert hasattr(mod.ClienteSECOP, "buscar_contratista")
        assert hasattr(mod.ClienteSECOP, "obtener_detalle_contrato")
        assert hasattr(mod.ClienteSECOP, "analizar_precios_mercado")

    def test_urls_datasets(self):
        mod = _cargar_modulo("secop.py")
        assert "jbjy-vk9h" in mod.SECOP_II_CONTRATOS_URL
        assert "p6dx-8zbt" in mod.SECOP_II_PROCESOS_URL


class TestClienteDANE:
    """Tests del cliente DANE."""

    def test_nombre_servicio(self):
        mod = _cargar_modulo("dane.py")
        assert mod.ClienteDANE.nombre_servicio == "DANE"

    def test_indicadores_disponibles(self):
        mod = _cargar_modulo("dane.py")
        indicadores = mod.INDICADORES_DANE
        assert "ipc" in indicadores
        assert "pib" in indicadores
        assert "desempleo" in indicadores
        assert "pobreza" in indicadores
        assert "poblacion" in indicadores
        assert "tic" in indicadores  # Nuevo en Sprint 7

    def test_sectores_pib_disponibles(self):
        mod = _cargar_modulo("dane.py")
        sectores = mod.SECTORES_PIB
        assert "agricultura" in sectores
        assert "construccion" in sectores
        assert "informacion" in sectores
        assert "administracion_publica" in sectores

    def test_tiene_metodos_nuevos(self):
        mod = _cargar_modulo("dane.py")
        assert hasattr(mod.ClienteDANE, "obtener_ipc")
        assert hasattr(mod.ClienteDANE, "obtener_pib_sectorial")
        assert hasattr(mod.ClienteDANE, "obtener_estadisticas_tic")

    def test_normalizar_indicador(self):
        mod = _cargar_modulo("dane.py")
        cliente = mod.ClienteDANE.__new__(mod.ClienteDANE)

        registro_raw = {
            "valor": "3.5",
            "unidad_medida": "porcentaje",
            "anno": "2025",
            "fecha_publicacion": "2025-07-15",
        }

        resultado = cliente._normalizar_indicador("ipc", registro_raw)
        assert resultado["codigo"] == "ipc"
        assert resultado["nombre"] == "Indice de Precios al Consumidor"
        assert resultado["valor"] == 3.5
        assert resultado["periodo"] == "2025"


class TestClienteCongreso:
    """Tests del cliente Congreso."""

    def test_nombre_servicio(self):
        mod = _cargar_modulo("congreso.py")
        assert mod.ClienteCongreso.nombre_servicio == "Congreso"

    def test_tipos_norma(self):
        mod = _cargar_modulo("congreso.py")
        assert "ley" in mod.TIPOS_NORMA
        assert "decreto" in mod.TIPOS_NORMA
        assert mod.TIPOS_NORMA["ley"] == "Ley"

    def test_tiene_metodos_nuevos(self):
        mod = _cargar_modulo("congreso.py")
        assert hasattr(mod.ClienteCongreso, "buscar_norma")
        assert hasattr(mod.ClienteCongreso, "verificar_vigencia")
        assert hasattr(mod.ClienteCongreso, "buscar_proyectos_ley")

    def test_normalizar_proyecto(self):
        mod = _cargar_modulo("congreso.py")
        cliente = mod.ClienteCongreso.__new__(mod.ClienteCongreso)

        proyecto_raw = {
            "numero_proyecto": "042",
            "titulo_proyecto": "Por la cual se regula el control fiscal",
            "autores": "Autor A, Autor B, Autor C",
            "estado": "Sancionado",
            "comision": "Primera",
            "fecha_radicacion": "1993-01-15",
            "legislatura": "1992-1993",
            "tipo_proyecto": "Ley",
            "url_proceso": "https://congreso.gov.co/ley42",
        }

        resultado = cliente._normalizar_proyecto(proyecto_raw)
        assert resultado["numero"] == "042"
        assert "control fiscal" in resultado["titulo"]
        assert len(resultado["autores"]) == 3
        assert resultado["estado"] == "Sancionado"
        assert resultado["tipo"] == "Ley"


class TestStubs:
    """Tests de los stubs CGR (SIRECI, SIGECI, APA, DIARI)."""

    def test_sireci_retorna_pendiente(self):
        mod = _cargar_modulo("sireci.py")
        assert hasattr(mod.ClienteSIRECI, "consultar_rendicion")
        assert hasattr(mod.ClienteSIRECI, "obtener_estados_financieros")

    def test_sigeci_retorna_pendiente(self):
        mod = _cargar_modulo("sigeci.py")
        assert hasattr(mod.ClienteSIGECI, "obtener_auditoria")
        assert hasattr(mod.ClienteSIGECI, "consultar_plan_mejoramiento")

    def test_apa_retorna_pendiente(self):
        mod = _cargar_modulo("apa.py")
        assert hasattr(mod.ClienteAPA, "obtener_plan_vigilancia")
        assert hasattr(mod.ClienteAPA, "obtener_universo_auditable")

    def test_diari_retorna_pendiente(self):
        mod = _cargar_modulo("diari.py")
        assert hasattr(mod.ClienteDIARI, "buscar_informes")
        assert hasattr(mod.ClienteDIARI, "obtener_informe")
