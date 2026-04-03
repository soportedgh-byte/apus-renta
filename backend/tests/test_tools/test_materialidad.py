"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: test_materialidad.py
Propósito: Pruebas unitarias del cálculo de materialidad según NIA 320 — materialidad global y de ejecución
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

import pytest


# ---------------------------------------------------------------------------
# Modelo del cálculo de materialidad
# ---------------------------------------------------------------------------
class BaseMaterialidad(str, Enum):
    """Bases de cálculo de materialidad según NIA 320."""

    PRESUPUESTO_INVERSION = "presupuesto_inversion"
    INGRESOS_TOTALES = "ingresos_totales"
    ACTIVOS_TOTALES = "activos_totales"
    GASTOS_TOTALES = "gastos_totales"


# Porcentajes de referencia por base de cálculo (rango inferior y superior)
PORCENTAJES_MATERIALIDAD: dict[BaseMaterialidad, tuple[float, float]] = {
    BaseMaterialidad.PRESUPUESTO_INVERSION: (0.005, 0.02),   # 0.5% a 2%
    BaseMaterialidad.INGRESOS_TOTALES: (0.005, 0.02),        # 0.5% a 2%
    BaseMaterialidad.ACTIVOS_TOTALES: (0.005, 0.01),          # 0.5% a 1%
    BaseMaterialidad.GASTOS_TOTALES: (0.005, 0.02),           # 0.5% a 2%
}

# Factor de materialidad de ejecución (60% a 85% de la materialidad global)
FACTOR_EJECUCION_MIN = 0.60
FACTOR_EJECUCION_MAX = 0.85
FACTOR_EJECUCION_DEFAULT = 0.75


@dataclass
class ResultadoMaterialidad:
    """Resultado del cálculo de materialidad."""

    base_calculo: str
    monto_base: float
    porcentaje_aplicado: float
    materialidad_global: float
    materialidad_ejecucion: float
    factor_ejecucion: float
    nivel_confianza: float


def calcular_materialidad(
    monto_base: float,
    base: BaseMaterialidad = BaseMaterialidad.PRESUPUESTO_INVERSION,
    nivel_confianza: float = 0.95,
    factor_ejecucion: float = FACTOR_EJECUCION_DEFAULT,
) -> ResultadoMaterialidad:
    """Calcula la materialidad global y de ejecución.

    Parámetros:
        monto_base: Monto total de la base de cálculo (en pesos colombianos).
        base: Tipo de base de cálculo.
        nivel_confianza: Nivel de confianza (0.0 a 1.0). Mayor confianza = menor materialidad.
        factor_ejecucion: Factor para derivar materialidad de ejecución (0.60 a 0.85).

    Retorna:
        ResultadoMaterialidad con los valores calculados.

    Excepciones:
        ValueError: Si los parámetros están fuera de rango.
    """
    # Validaciones
    if monto_base <= 0:
        raise ValueError("El monto base debe ser mayor a cero.")

    if not (0.0 < nivel_confianza <= 1.0):
        raise ValueError("El nivel de confianza debe estar entre 0 y 1 (exclusivo e inclusivo).")

    if not (FACTOR_EJECUCION_MIN <= factor_ejecucion <= FACTOR_EJECUCION_MAX):
        raise ValueError(
            f"El factor de ejecución debe estar entre {FACTOR_EJECUCION_MIN} y {FACTOR_EJECUCION_MAX}."
        )

    # Determinar porcentaje basado en nivel de confianza
    pct_min, pct_max = PORCENTAJES_MATERIALIDAD[base]
    # Mayor confianza → menor porcentaje (más conservador)
    porcentaje = pct_max - (nivel_confianza * (pct_max - pct_min))

    materialidad_global = monto_base * porcentaje
    materialidad_ejecucion = materialidad_global * factor_ejecucion

    return ResultadoMaterialidad(
        base_calculo=base.value,
        monto_base=monto_base,
        porcentaje_aplicado=porcentaje,
        materialidad_global=round(materialidad_global, 2),
        materialidad_ejecucion=round(materialidad_ejecucion, 2),
        factor_ejecucion=factor_ejecucion,
        nivel_confianza=nivel_confianza,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def presupuesto_grande():
    """Presupuesto de inversión de $450.000 millones."""
    return 450_000_000_000_000.0  # 450 billones de pesos


@pytest.fixture
def presupuesto_mediano():
    """Presupuesto de inversión de $50.000 millones."""
    return 50_000_000_000_000.0


@pytest.fixture
def presupuesto_pequeno():
    """Presupuesto de $1.000 millones."""
    return 1_000_000_000_000.0


# ---------------------------------------------------------------------------
# Tests de cálculos correctos
# ---------------------------------------------------------------------------
class TestCalculoMaterialidad:
    """Pruebas del cálculo de materialidad global."""

    def test_materialidad_presupuesto_inversion(self, presupuesto_grande):
        """El cálculo con presupuesto de inversión debe retornar valores positivos."""
        resultado = calcular_materialidad(
            presupuesto_grande,
            base=BaseMaterialidad.PRESUPUESTO_INVERSION,
        )

        assert resultado.materialidad_global > 0
        assert resultado.materialidad_ejecucion > 0
        assert resultado.base_calculo == "presupuesto_inversion"

    def test_materialidad_global_mayor_que_ejecucion(self, presupuesto_grande):
        """La materialidad global siempre debe ser mayor que la de ejecución."""
        resultado = calcular_materialidad(presupuesto_grande)

        assert resultado.materialidad_global > resultado.materialidad_ejecucion

    def test_materialidad_ejecucion_es_factor_de_global(self, presupuesto_mediano):
        """La materialidad de ejecución debe ser exactamente el factor aplicado sobre la global."""
        factor = 0.75
        resultado = calcular_materialidad(
            presupuesto_mediano,
            factor_ejecucion=factor,
        )

        esperado = round(resultado.materialidad_global * factor, 2)
        assert resultado.materialidad_ejecucion == esperado

    def test_mayor_confianza_menor_materialidad(self, presupuesto_grande):
        """A mayor nivel de confianza, menor debe ser la materialidad."""
        resultado_alta = calcular_materialidad(
            presupuesto_grande, nivel_confianza=0.99,
        )
        resultado_baja = calcular_materialidad(
            presupuesto_grande, nivel_confianza=0.80,
        )

        assert resultado_alta.materialidad_global < resultado_baja.materialidad_global

    def test_porcentaje_dentro_de_rango(self, presupuesto_mediano):
        """El porcentaje aplicado debe estar dentro del rango definido para la base."""
        resultado = calcular_materialidad(
            presupuesto_mediano,
            base=BaseMaterialidad.PRESUPUESTO_INVERSION,
        )

        pct_min, pct_max = PORCENTAJES_MATERIALIDAD[BaseMaterialidad.PRESUPUESTO_INVERSION]
        assert pct_min <= resultado.porcentaje_aplicado <= pct_max

    def test_diferentes_bases_producen_diferentes_resultados(self, presupuesto_mediano):
        """Diferentes bases de cálculo pueden producir materialidades distintas."""
        resultado_inversion = calcular_materialidad(
            presupuesto_mediano, base=BaseMaterialidad.PRESUPUESTO_INVERSION,
        )
        resultado_activos = calcular_materialidad(
            presupuesto_mediano, base=BaseMaterialidad.ACTIVOS_TOTALES,
        )

        # Los rangos de porcentaje son diferentes, por lo que los resultados difieren
        assert resultado_inversion.porcentaje_aplicado != resultado_activos.porcentaje_aplicado


# ---------------------------------------------------------------------------
# Tests de factores de ejecución
# ---------------------------------------------------------------------------
class TestFactorEjecucion:
    """Pruebas del factor de materialidad de ejecución."""

    @pytest.mark.parametrize("factor", [0.60, 0.65, 0.70, 0.75, 0.80, 0.85])
    def test_factores_validos(self, presupuesto_pequeno, factor):
        """Todos los factores dentro del rango válido deben funcionar."""
        resultado = calcular_materialidad(
            presupuesto_pequeno, factor_ejecucion=factor,
        )

        assert resultado.factor_ejecucion == factor
        esperado = round(resultado.materialidad_global * factor, 2)
        assert resultado.materialidad_ejecucion == esperado

    def test_factor_default_es_075(self, presupuesto_pequeno):
        """El factor por defecto debe ser 0.75."""
        resultado = calcular_materialidad(presupuesto_pequeno)
        assert resultado.factor_ejecucion == 0.75


# ---------------------------------------------------------------------------
# Tests de validación de entradas
# ---------------------------------------------------------------------------
class TestValidacionEntradas:
    """Pruebas de validación de parámetros de entrada."""

    def test_monto_cero_lanza_error(self):
        """Un monto base de cero debe lanzar ValueError."""
        with pytest.raises(ValueError, match="mayor a cero"):
            calcular_materialidad(0)

    def test_monto_negativo_lanza_error(self):
        """Un monto base negativo debe lanzar ValueError."""
        with pytest.raises(ValueError, match="mayor a cero"):
            calcular_materialidad(-1_000_000)

    def test_nivel_confianza_cero_lanza_error(self):
        """Nivel de confianza 0 debe lanzar ValueError."""
        with pytest.raises(ValueError, match="nivel de confianza"):
            calcular_materialidad(1_000_000, nivel_confianza=0.0)

    def test_nivel_confianza_mayor_a_uno_lanza_error(self):
        """Nivel de confianza > 1 debe lanzar ValueError."""
        with pytest.raises(ValueError, match="nivel de confianza"):
            calcular_materialidad(1_000_000, nivel_confianza=1.5)

    def test_factor_ejecucion_menor_al_minimo_lanza_error(self):
        """Factor de ejecución por debajo del mínimo debe lanzar ValueError."""
        with pytest.raises(ValueError, match="factor de ejecución"):
            calcular_materialidad(1_000_000, factor_ejecucion=0.50)

    def test_factor_ejecucion_mayor_al_maximo_lanza_error(self):
        """Factor de ejecución por encima del máximo debe lanzar ValueError."""
        with pytest.raises(ValueError, match="factor de ejecución"):
            calcular_materialidad(1_000_000, factor_ejecucion=0.95)


# ---------------------------------------------------------------------------
# Tests de estructura del resultado
# ---------------------------------------------------------------------------
class TestEstructuraResultado:
    """Pruebas de la estructura del objeto de resultado."""

    def test_resultado_contiene_todos_los_campos(self, presupuesto_pequeno):
        """El resultado debe contener todos los campos esperados."""
        resultado = calcular_materialidad(presupuesto_pequeno)

        assert hasattr(resultado, "base_calculo")
        assert hasattr(resultado, "monto_base")
        assert hasattr(resultado, "porcentaje_aplicado")
        assert hasattr(resultado, "materialidad_global")
        assert hasattr(resultado, "materialidad_ejecucion")
        assert hasattr(resultado, "factor_ejecucion")
        assert hasattr(resultado, "nivel_confianza")

    def test_resultado_tipos_correctos(self, presupuesto_pequeno):
        """Los tipos de los campos del resultado deben ser correctos."""
        resultado = calcular_materialidad(presupuesto_pequeno)

        assert isinstance(resultado.base_calculo, str)
        assert isinstance(resultado.monto_base, float)
        assert isinstance(resultado.porcentaje_aplicado, float)
        assert isinstance(resultado.materialidad_global, float)
        assert isinstance(resultado.materialidad_ejecucion, float)
        assert isinstance(resultado.factor_ejecucion, float)
        assert isinstance(resultado.nivel_confianza, float)
