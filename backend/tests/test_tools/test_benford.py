"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: test_benford.py
Propósito: Pruebas unitarias del análisis de la Ley de Benford para detección de anomalías en registros financieros
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

import math
from dataclasses import dataclass, field

import pytest


# ---------------------------------------------------------------------------
# Distribución esperada de Benford (primer dígito)
# ---------------------------------------------------------------------------
BENFORD_ESPERADO: dict[int, float] = {
    1: 0.30103,
    2: 0.17609,
    3: 0.12494,
    4: 0.09691,
    5: 0.07918,
    6: 0.06695,
    7: 0.05799,
    8: 0.05115,
    9: 0.04576,
}


@dataclass
class ResultadoBenford:
    """Resultado del análisis de Benford sobre un conjunto de datos."""

    total_registros: int
    registros_validos: int
    distribucion_observada: dict[int, float]
    distribucion_esperada: dict[int, float]
    desviaciones: dict[int, float]
    estadistico_chi2: float
    valor_p: float | None
    digitos_anomalos: list[int]
    conclusion: str


# ---------------------------------------------------------------------------
# Funciones de análisis de Benford
# ---------------------------------------------------------------------------

def primer_digito(numero: float) -> int | None:
    """Obtiene el primer dígito significativo de un número.

    Retorna None si el número es cero o no es válido.
    """
    if numero == 0:
        return None

    numero_abs = abs(numero)
    while numero_abs < 1:
        numero_abs *= 10
    while numero_abs >= 10:
        numero_abs /= 10

    return int(numero_abs)


def calcular_distribucion(datos: list[float]) -> tuple[dict[int, float], int]:
    """Calcula la distribución del primer dígito de una lista de datos.

    Retorna la distribución como proporción y el total de registros válidos.
    """
    conteo: dict[int, int] = {d: 0 for d in range(1, 10)}
    validos = 0

    for valor in datos:
        digito = primer_digito(valor)
        if digito is not None and digito in conteo:
            conteo[digito] += 1
            validos += 1

    if validos == 0:
        return {d: 0.0 for d in range(1, 10)}, 0

    distribucion = {d: conteo[d] / validos for d in range(1, 10)}
    return distribucion, validos


def calcular_chi_cuadrado(
    observada: dict[int, float],
    esperada: dict[int, float],
    n: int,
) -> float:
    """Calcula el estadístico chi-cuadrado entre distribuciones observada y esperada."""
    chi2 = 0.0
    for digito in range(1, 10):
        obs = observada.get(digito, 0.0) * n
        esp = esperada.get(digito, 0.0) * n
        if esp > 0:
            chi2 += ((obs - esp) ** 2) / esp
    return chi2


def analizar_benford(
    datos: list[float],
    umbral_desviacion: float = 0.03,
) -> ResultadoBenford:
    """Ejecuta el análisis de Benford sobre un conjunto de datos financieros.

    Parámetros:
        datos: Lista de valores numéricos (montos, pagos, etc.).
        umbral_desviacion: Desviación máxima aceptable por dígito.

    Retorna:
        ResultadoBenford con el análisis completo.
    """
    if not datos:
        raise ValueError("La lista de datos no puede estar vacía.")

    distribucion_obs, validos = calcular_distribucion(datos)

    if validos < 50:
        raise ValueError(
            f"Se requieren al menos 50 registros válidos para el análisis. "
            f"Se encontraron {validos}."
        )

    desviaciones = {
        d: abs(distribucion_obs[d] - BENFORD_ESPERADO[d])
        for d in range(1, 10)
    }

    chi2 = calcular_chi_cuadrado(distribucion_obs, BENFORD_ESPERADO, validos)

    # Identificar dígitos con desviación significativa
    digitos_anomalos = [
        d for d, desv in desviaciones.items() if desv > umbral_desviacion
    ]

    # Valor crítico chi-cuadrado para 8 grados de libertad y alfa=0.05: 15.507
    VALOR_CRITICO_005 = 15.507
    cumple_benford = chi2 <= VALOR_CRITICO_005

    if cumple_benford and not digitos_anomalos:
        conclusion = (
            "La distribución de los datos es consistente con la Ley de Benford. "
            "No se detectan anomalías significativas."
        )
    elif not digitos_anomalos:
        conclusion = (
            "La distribución general es aceptable, aunque el estadístico chi-cuadrado "
            "sugiere revisar los datos con mayor detalle."
        )
    else:
        digitos_str = ", ".join(str(d) for d in digitos_anomalos)
        conclusion = (
            f"Se detectan desviaciones significativas en los dígitos: {digitos_str}. "
            f"Se recomienda revisión detallada de los registros."
        )

    return ResultadoBenford(
        total_registros=len(datos),
        registros_validos=validos,
        distribucion_observada=distribucion_obs,
        distribucion_esperada=BENFORD_ESPERADO.copy(),
        desviaciones=desviaciones,
        estadistico_chi2=round(chi2, 4),
        valor_p=None,  # Requiere scipy para calcular
        digitos_anomalos=digitos_anomalos,
        conclusion=conclusion,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def datos_benford_natural():
    """Genera datos que siguen la distribución de Benford."""
    import random

    random.seed(42)
    datos = []
    for digito in range(1, 10):
        cantidad = int(BENFORD_ESPERADO[digito] * 1000)
        for _ in range(cantidad):
            # Generar número cuyo primer dígito es el esperado
            factor = random.uniform(1.0, 9.99)
            exponente = random.randint(2, 8)
            valor = digito * (10 ** exponente) + factor * (10 ** (exponente - 1))
            datos.append(valor)
    random.shuffle(datos)
    return datos


@pytest.fixture
def datos_anomalos():
    """Genera datos que NO siguen la distribución de Benford (muchos 5 y 9)."""
    import random

    random.seed(123)
    datos = []
    # Sobrerrepresentar dígitos 5 y 9
    for _ in range(300):
        datos.append(random.uniform(5_000_000, 5_999_999))
    for _ in range(200):
        datos.append(random.uniform(9_000_000, 9_999_999))
    for _ in range(500):
        datos.append(random.uniform(1_000_000, 9_999_999))
    random.shuffle(datos)
    return datos


@pytest.fixture
def datos_pocos():
    """Genera muy pocos datos (insuficientes para Benford)."""
    return [100.0, 200.0, 300.0, 500.0, 1000.0]


# ---------------------------------------------------------------------------
# Tests del primer dígito
# ---------------------------------------------------------------------------
class TestPrimerDigito:
    """Pruebas de la función de extracción del primer dígito."""

    @pytest.mark.parametrize(
        "numero, esperado",
        [
            (1234, 1),
            (5678, 5),
            (999, 9),
            (0.00456, 4),
            (0.123, 1),
            (7.89, 7),
            (100_000_000, 1),
            (-456, 4),
            (-0.0089, 8),
        ],
    )
    def test_primer_digito_correcto(self, numero, esperado):
        """El primer dígito debe extraerse correctamente de diversos formatos."""
        assert primer_digito(numero) == esperado

    def test_cero_retorna_none(self):
        """El número cero no tiene primer dígito significativo."""
        assert primer_digito(0) is None

    def test_numeros_negativos_usan_valor_absoluto(self):
        """Los números negativos deben usar su valor absoluto."""
        assert primer_digito(-321) == 3
        assert primer_digito(-0.067) == 6


# ---------------------------------------------------------------------------
# Tests de la distribución de Benford
# ---------------------------------------------------------------------------
class TestDistribucionBenford:
    """Pruebas de la distribución esperada de Benford."""

    def test_distribucion_esperada_suma_uno(self):
        """Las probabilidades esperadas de Benford deben sumar 1."""
        total = sum(BENFORD_ESPERADO.values())
        assert abs(total - 1.0) < 1e-5

    def test_distribucion_esperada_nueve_digitos(self):
        """Deben existir exactamente 9 entradas (dígitos 1-9)."""
        assert len(BENFORD_ESPERADO) == 9
        assert set(BENFORD_ESPERADO.keys()) == set(range(1, 10))

    def test_digito_1_es_el_mas_frecuente(self):
        """El dígito 1 debe tener la mayor probabilidad (~30.1%)."""
        assert BENFORD_ESPERADO[1] == max(BENFORD_ESPERADO.values())
        assert abs(BENFORD_ESPERADO[1] - 0.30103) < 1e-5

    def test_digito_9_es_el_menos_frecuente(self):
        """El dígito 9 debe tener la menor probabilidad (~4.6%)."""
        assert BENFORD_ESPERADO[9] == min(BENFORD_ESPERADO.values())

    def test_formula_log10(self):
        """Cada probabilidad debe seguir P(d) = log10(1 + 1/d)."""
        for d in range(1, 10):
            esperado = math.log10(1 + 1 / d)
            assert abs(BENFORD_ESPERADO[d] - esperado) < 1e-5


# ---------------------------------------------------------------------------
# Tests del análisis completo
# ---------------------------------------------------------------------------
class TestAnalisisBenford:
    """Pruebas del análisis completo de Benford."""

    def test_datos_naturales_cumplen_benford(self, datos_benford_natural):
        """Datos que siguen Benford deben pasar el análisis sin anomalías graves."""
        resultado = analizar_benford(datos_benford_natural)

        assert resultado.registros_validos > 50
        # El estadístico chi-cuadrado debe ser relativamente bajo
        assert resultado.estadistico_chi2 < 30.0  # Umbral generoso

    def test_datos_anomalos_detectan_desviaciones(self, datos_anomalos):
        """Datos manipulados deben generar dígitos anómalos."""
        resultado = analizar_benford(datos_anomalos)

        assert len(resultado.digitos_anomalos) > 0
        # Los dígitos 5 y/o 9 deberían aparecer como anómalos
        assert any(d in resultado.digitos_anomalos for d in [5, 9])

    def test_pocos_datos_lanza_error(self, datos_pocos):
        """Menos de 50 registros válidos deben lanzar ValueError."""
        with pytest.raises(ValueError, match="al menos 50"):
            analizar_benford(datos_pocos)

    def test_datos_vacios_lanza_error(self):
        """Una lista vacía debe lanzar ValueError."""
        with pytest.raises(ValueError, match="vacía"):
            analizar_benford([])

    def test_resultado_contiene_todos_los_campos(self, datos_benford_natural):
        """El resultado debe contener todos los campos esperados."""
        resultado = analizar_benford(datos_benford_natural)

        assert resultado.total_registros > 0
        assert resultado.registros_validos > 0
        assert len(resultado.distribucion_observada) == 9
        assert len(resultado.distribucion_esperada) == 9
        assert len(resultado.desviaciones) == 9
        assert isinstance(resultado.estadistico_chi2, float)
        assert isinstance(resultado.digitos_anomalos, list)
        assert isinstance(resultado.conclusion, str)
        assert len(resultado.conclusion) > 0

    def test_distribucion_observada_suma_uno(self, datos_benford_natural):
        """La distribución observada debe sumar aproximadamente 1."""
        resultado = analizar_benford(datos_benford_natural)
        total = sum(resultado.distribucion_observada.values())
        assert abs(total - 1.0) < 1e-5


# ---------------------------------------------------------------------------
# Tests del cálculo chi-cuadrado
# ---------------------------------------------------------------------------
class TestChiCuadrado:
    """Pruebas del cálculo del estadístico chi-cuadrado."""

    def test_distribuciones_identicas_dan_chi2_cero(self):
        """Distribuciones idénticas deben producir chi-cuadrado = 0."""
        chi2 = calcular_chi_cuadrado(BENFORD_ESPERADO, BENFORD_ESPERADO, 1000)
        assert abs(chi2) < 1e-10

    def test_chi2_siempre_positivo(self, datos_benford_natural):
        """El estadístico chi-cuadrado siempre debe ser >= 0."""
        resultado = analizar_benford(datos_benford_natural)
        assert resultado.estadistico_chi2 >= 0

    def test_distribucion_uniforme_alto_chi2(self):
        """Una distribución uniforme (no Benford) debe tener chi-cuadrado alto."""
        distribucion_uniforme = {d: 1.0 / 9 for d in range(1, 10)}
        chi2 = calcular_chi_cuadrado(distribucion_uniforme, BENFORD_ESPERADO, 1000)
        # La diferencia con Benford es significativa
        assert chi2 > 15.507  # Valor crítico para alfa=0.05, gl=8


# ---------------------------------------------------------------------------
# Tests del umbral de desviación
# ---------------------------------------------------------------------------
class TestUmbralDesviacion:
    """Pruebas de configuración del umbral de desviación."""

    def test_umbral_estricto_detecta_mas_anomalias(self, datos_benford_natural):
        """Un umbral más estricto debe detectar más (o igual) dígitos anómalos."""
        resultado_normal = analizar_benford(datos_benford_natural, umbral_desviacion=0.03)
        resultado_estricto = analizar_benford(datos_benford_natural, umbral_desviacion=0.01)

        assert len(resultado_estricto.digitos_anomalos) >= len(resultado_normal.digitos_anomalos)

    def test_umbral_laxo_detecta_menos_anomalias(self, datos_anomalos):
        """Un umbral más laxo debe detectar menos (o igual) dígitos anómalos."""
        resultado_normal = analizar_benford(datos_anomalos, umbral_desviacion=0.03)
        resultado_laxo = analizar_benford(datos_anomalos, umbral_desviacion=0.10)

        assert len(resultado_laxo.digitos_anomalos) <= len(resultado_normal.digitos_anomalos)
