"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: test_chunking.py
Propósito: Pruebas unitarias del módulo de fragmentación (chunking) de documentos para el motor RAG
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

import pytest


# ---------------------------------------------------------------------------
# Funciones de chunking a probar
# ---------------------------------------------------------------------------

def fragmentar_por_tamano(
    texto: str,
    tamano: int = 1024,
    solapamiento: int = 128,
) -> list[str]:
    """Divide un texto en fragmentos de tamaño fijo con solapamiento.

    Parámetros:
        texto: Texto a fragmentar.
        tamano: Tamaño máximo de cada fragmento en caracteres.
        solapamiento: Cantidad de caracteres que se solapan entre fragmentos consecutivos.

    Retorna:
        Lista de fragmentos de texto.
    """
    if not texto or not texto.strip():
        return []

    if tamano <= 0:
        raise ValueError("El tamaño del fragmento debe ser mayor a cero.")

    if solapamiento < 0:
        raise ValueError("El solapamiento no puede ser negativo.")

    if solapamiento >= tamano:
        raise ValueError("El solapamiento debe ser menor que el tamaño del fragmento.")

    if len(texto) <= tamano:
        return [texto]

    fragmentos: list[str] = []
    inicio = 0
    while inicio < len(texto):
        fin = inicio + tamano
        fragmento = texto[inicio:fin]
        fragmentos.append(fragmento)
        inicio += tamano - solapamiento

    return fragmentos


def fragmentar_por_parrafos(
    texto: str,
    tamano_max: int = 1024,
    solapamiento: int = 128,
) -> list[str]:
    """Divide un texto en fragmentos respetando límites de párrafo.

    Intenta no cortar un párrafo a la mitad. Si un párrafo excede
    el tamaño máximo, se fragmenta por tamaño fijo.

    Parámetros:
        texto: Texto a fragmentar.
        tamano_max: Tamaño máximo de cada fragmento en caracteres.
        solapamiento: Caracteres de contexto previo para agregar al inicio del siguiente fragmento.

    Retorna:
        Lista de fragmentos de texto.
    """
    if not texto or not texto.strip():
        return []

    if tamano_max <= 0:
        raise ValueError("El tamaño máximo debe ser mayor a cero.")

    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]

    if not parrafos:
        return []

    fragmentos: list[str] = []
    fragmento_actual: list[str] = []
    tamano_actual = 0

    for parrafo in parrafos:
        tamano_parrafo = len(parrafo)

        # Si el párrafo solo excede el tamaño, fragmentar por tamaño
        if tamano_parrafo > tamano_max:
            # Guardar lo acumulado hasta ahora
            if fragmento_actual:
                fragmentos.append("\n\n".join(fragmento_actual))
                fragmento_actual = []
                tamano_actual = 0

            # Fragmentar el párrafo largo
            sub_fragmentos = fragmentar_por_tamano(parrafo, tamano_max, solapamiento)
            fragmentos.extend(sub_fragmentos)
            continue

        # Si agregar el párrafo excede el límite, guardar y empezar nuevo fragmento
        tamano_con_separador = tamano_actual + tamano_parrafo + (2 if fragmento_actual else 0)
        if tamano_con_separador > tamano_max:
            fragmentos.append("\n\n".join(fragmento_actual))
            # Iniciar nuevo fragmento con solapamiento
            if solapamiento > 0 and fragmento_actual:
                ultimo = fragmento_actual[-1]
                contexto = ultimo[-solapamiento:] if len(ultimo) > solapamiento else ultimo
                fragmento_actual = [contexto, parrafo]
                tamano_actual = len(contexto) + 2 + tamano_parrafo
            else:
                fragmento_actual = [parrafo]
                tamano_actual = tamano_parrafo
        else:
            fragmento_actual.append(parrafo)
            tamano_actual = tamano_con_separador

    # Guardar el último fragmento
    if fragmento_actual:
        fragmentos.append("\n\n".join(fragmento_actual))

    return fragmentos


def contar_tokens_aproximado(texto: str) -> int:
    """Estimación aproximada de tokens (1 token ~ 4 caracteres en español)."""
    return max(1, len(texto) // 4)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def texto_corto():
    """Texto que cabe en un solo fragmento."""
    return "Este es un texto corto de prueba para CecilIA v2."


@pytest.fixture
def texto_largo():
    """Texto largo que requiere múltiples fragmentos."""
    parrafo = (
        "La Contraloría General de la República ejerce el control fiscal "
        "sobre la administración y los particulares o entidades que manejen "
        "fondos o bienes de la Nación, de conformidad con lo establecido en "
        "el artículo 267 de la Constitución Política de Colombia. "
    )
    return parrafo * 50  # ~10000 caracteres


@pytest.fixture
def texto_con_parrafos():
    """Texto con múltiples párrafos separados por doble salto de línea."""
    return (
        "Artículo 267. El control fiscal es una función pública que ejercerá "
        "la Contraloría General de la República, la cual vigila la gestión "
        "fiscal de la administración y de los particulares o entidades que "
        "manejen fondos o bienes de la Nación.\n\n"
        "Artículo 268. El Contralor General de la República tendrá las "
        "siguientes atribuciones: Prescribir los métodos y la forma de "
        "rendir cuentas los responsables del manejo de fondos o bienes de "
        "la Nación.\n\n"
        "Artículo 269. En las entidades públicas, las autoridades "
        "correspondientes están obligadas a diseñar y aplicar, según la "
        "naturaleza de sus funciones, métodos y procedimientos de control "
        "interno.\n\n"
        "Artículo 270. La ley organizará las formas y los sistemas de "
        "participación ciudadana que permitan vigilar la gestión pública "
        "que se cumpla en los diversos niveles administrativos."
    )


@pytest.fixture
def texto_vacio():
    return ""


@pytest.fixture
def texto_solo_espacios():
    return "   \n\n   \t   "


# ---------------------------------------------------------------------------
# Tests de fragmentación por tamaño
# ---------------------------------------------------------------------------
class TestFragmentarPorTamano:
    """Pruebas de la fragmentación por tamaño fijo con solapamiento."""

    def test_texto_corto_genera_un_fragmento(self, texto_corto):
        """Un texto menor al tamaño máximo debe generar un solo fragmento."""
        fragmentos = fragmentar_por_tamano(texto_corto, tamano=1024)
        assert len(fragmentos) == 1
        assert fragmentos[0] == texto_corto

    def test_texto_largo_genera_multiples_fragmentos(self, texto_largo):
        """Un texto largo debe generar múltiples fragmentos."""
        fragmentos = fragmentar_por_tamano(texto_largo, tamano=500, solapamiento=50)
        assert len(fragmentos) > 1

    def test_cada_fragmento_no_excede_tamano(self, texto_largo):
        """Ningún fragmento debe exceder el tamaño máximo."""
        tamano = 500
        fragmentos = fragmentar_por_tamano(texto_largo, tamano=tamano, solapamiento=50)
        for f in fragmentos:
            assert len(f) <= tamano

    def test_solapamiento_entre_fragmentos(self, texto_largo):
        """Fragmentos consecutivos deben compartir caracteres (solapamiento)."""
        solapamiento = 100
        fragmentos = fragmentar_por_tamano(texto_largo, tamano=500, solapamiento=solapamiento)

        for i in range(len(fragmentos) - 1):
            # El final del fragmento actual debe coincidir con el inicio del siguiente
            final_actual = fragmentos[i][-solapamiento:]
            inicio_siguiente = fragmentos[i + 1][:solapamiento]
            assert final_actual == inicio_siguiente

    def test_texto_vacio_retorna_lista_vacia(self, texto_vacio):
        """Un texto vacío debe retornar lista vacía."""
        fragmentos = fragmentar_por_tamano(texto_vacio, tamano=1024)
        assert fragmentos == []

    def test_texto_solo_espacios_retorna_lista_vacia(self, texto_solo_espacios):
        """Un texto con solo espacios debe retornar lista vacía."""
        fragmentos = fragmentar_por_tamano(texto_solo_espacios, tamano=1024)
        assert fragmentos == []

    def test_todo_el_texto_esta_cubierto(self, texto_largo):
        """La concatenación de fragmentos (sin solapamiento) debe cubrir todo el texto."""
        tamano = 500
        solapamiento = 0
        fragmentos = fragmentar_por_tamano(texto_largo, tamano=tamano, solapamiento=solapamiento)

        reconstruido = "".join(fragmentos)
        assert reconstruido == texto_largo


# ---------------------------------------------------------------------------
# Tests de validación de parámetros
# ---------------------------------------------------------------------------
class TestValidacionParametros:
    """Pruebas de validación de parámetros de entrada."""

    def test_tamano_cero_lanza_error(self):
        """Tamaño 0 debe lanzar ValueError."""
        with pytest.raises(ValueError, match="mayor a cero"):
            fragmentar_por_tamano("texto", tamano=0)

    def test_tamano_negativo_lanza_error(self):
        """Tamaño negativo debe lanzar ValueError."""
        with pytest.raises(ValueError, match="mayor a cero"):
            fragmentar_por_tamano("texto", tamano=-100)

    def test_solapamiento_negativo_lanza_error(self):
        """Solapamiento negativo debe lanzar ValueError."""
        with pytest.raises(ValueError, match="negativo"):
            fragmentar_por_tamano("texto", tamano=100, solapamiento=-1)

    def test_solapamiento_mayor_que_tamano_lanza_error(self):
        """Solapamiento >= tamaño debe lanzar ValueError."""
        with pytest.raises(ValueError, match="menor que"):
            fragmentar_por_tamano("texto", tamano=100, solapamiento=100)

    def test_solapamiento_igual_a_tamano_lanza_error(self):
        """Solapamiento igual al tamaño debe lanzar ValueError."""
        with pytest.raises(ValueError, match="menor que"):
            fragmentar_por_tamano("texto", tamano=50, solapamiento=50)


# ---------------------------------------------------------------------------
# Tests de fragmentación por párrafos
# ---------------------------------------------------------------------------
class TestFragmentarPorParrafos:
    """Pruebas de la fragmentación respetando límites de párrafo."""

    def test_parrafos_cortos_se_agrupan(self, texto_con_parrafos):
        """Párrafos cortos deben agruparse hasta el límite del tamaño máximo."""
        fragmentos = fragmentar_por_parrafos(texto_con_parrafos, tamano_max=2000)
        # Todos los párrafos caben en menos fragmentos que el total de párrafos
        total_parrafos = len([p for p in texto_con_parrafos.split("\n\n") if p.strip()])
        assert len(fragmentos) <= total_parrafos

    def test_fragmentos_no_exceden_tamano_maximo(self, texto_con_parrafos):
        """Cada fragmento no debe exceder el tamaño máximo (salvo párrafos individuales largos)."""
        tamano = 300
        fragmentos = fragmentar_por_parrafos(texto_con_parrafos, tamano_max=tamano)
        for f in fragmentos:
            assert len(f) <= tamano

    def test_texto_vacio_retorna_lista_vacia(self, texto_vacio):
        """Un texto vacío debe retornar lista vacía."""
        assert fragmentar_por_parrafos(texto_vacio) == []

    def test_un_solo_parrafo_corto(self):
        """Un solo párrafo corto debe generar un fragmento."""
        texto = "Este es un párrafo único y corto."
        fragmentos = fragmentar_por_parrafos(texto, tamano_max=1024)
        assert len(fragmentos) == 1
        assert fragmentos[0] == texto

    def test_parrafos_preservan_contenido(self, texto_con_parrafos):
        """Todos los párrafos originales deben estar presentes en los fragmentos."""
        fragmentos = fragmentar_por_parrafos(texto_con_parrafos, tamano_max=2000)
        concatenado = " ".join(fragmentos)

        for parrafo in texto_con_parrafos.split("\n\n"):
            parrafo_limpio = parrafo.strip()
            if parrafo_limpio:
                assert parrafo_limpio in concatenado


# ---------------------------------------------------------------------------
# Tests de estimación de tokens
# ---------------------------------------------------------------------------
class TestContarTokens:
    """Pruebas de la estimación aproximada de tokens."""

    def test_texto_vacio_retorna_uno(self):
        """Un texto vacío debe retornar al menos 1 token."""
        assert contar_tokens_aproximado("") >= 1

    def test_texto_corto(self):
        """Un texto de 20 caracteres debe estimar ~5 tokens."""
        tokens = contar_tokens_aproximado("12345678901234567890")
        assert tokens == 5

    def test_texto_largo_proporcional(self):
        """La estimación debe ser proporcional al tamaño del texto."""
        tokens_corto = contar_tokens_aproximado("a" * 100)
        tokens_largo = contar_tokens_aproximado("a" * 1000)
        assert tokens_largo == tokens_corto * 10

    def test_retorna_entero(self):
        """El resultado siempre debe ser un entero positivo."""
        tokens = contar_tokens_aproximado("texto de prueba")
        assert isinstance(tokens, int)
        assert tokens > 0


# ---------------------------------------------------------------------------
# Tests de configuraciones de producción
# ---------------------------------------------------------------------------
class TestConfiguracionProduccion:
    """Pruebas con la configuración por defecto de producción."""

    def test_configuracion_default(self, texto_largo):
        """Los valores por defecto deben funcionar correctamente."""
        fragmentos = fragmentar_por_tamano(texto_largo)  # 1024, 128
        assert len(fragmentos) > 1
        for f in fragmentos:
            assert len(f) <= 1024

    def test_fragmentos_default_tienen_solapamiento(self, texto_largo):
        """Con la configuración por defecto (128 overlap), debe existir solapamiento."""
        fragmentos = fragmentar_por_tamano(texto_largo)
        for i in range(len(fragmentos) - 1):
            final = fragmentos[i][-128:]
            inicio = fragmentos[i + 1][:128]
            assert final == inicio
