"""
Tests para el endpoint POST /api/formatos/generar.
Sprint: 4
"""

import io
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from docx import Document

from app.formatos.registro import obtener_generador, CATALOGO_FORMATOS, FORMATOS_IMPLEMENTADOS


class TestRegistroFormatos:
    """Tests para el registro y catalogo de formatos."""

    def test_catalogo_tiene_30_formatos(self):
        """El catalogo debe contener exactamente 30 formatos."""
        assert len(CATALOGO_FORMATOS) == 30

    def test_formatos_implementados(self):
        """Verifica los 11 formatos implementados."""
        esperados = {1, 3, 5, 7, 12, 14, 17, 18, 20, 22, 25}
        assert FORMATOS_IMPLEMENTADOS == esperados

    def test_obtener_generador_implementado(self):
        """Obtiene generadores para formatos implementados."""
        for num in FORMATOS_IMPLEMENTADOS:
            gen = obtener_generador(num)
            assert gen is not None
            assert gen.numero_formato == num

    def test_obtener_generador_no_implementado(self):
        """Obtiene generador generico para formatos no implementados."""
        gen = obtener_generador(2)  # No implementado
        assert gen is not None
        assert gen.numero_formato == 2

    def test_obtener_generador_invalido(self):
        """Lanza ValueError para formato fuera de rango."""
        with pytest.raises(ValueError):
            obtener_generador(31)
        with pytest.raises(ValueError):
            obtener_generador(0)

    def test_generar_todos_los_implementados(self):
        """Genera DOCX para cada formato implementado sin errores."""
        for num in FORMATOS_IMPLEMENTADOS:
            gen = obtener_generador(num, datos={"nombre_entidad": "Test", "vigencia": "2025"})
            resultado = gen.generar_bytes()
            assert isinstance(resultado, bytes)
            assert len(resultado) > 0
            # Verificar que es DOCX valido
            doc = Document(io.BytesIO(resultado))
            assert len(doc.paragraphs) > 0

    def test_generar_formato_generico(self):
        """Genera formato generico (no implementado) sin errores."""
        gen = obtener_generador(2, datos={"nombre_entidad": "Test"})
        resultado = gen.generar_bytes()
        assert isinstance(resultado, bytes)
        assert len(resultado) > 0

    def test_cada_formato_tiene_fase(self):
        """Cada formato del catalogo debe tener una fase asignada."""
        fases_validas = {"pre-planeacion", "planeacion", "ejecucion"}
        for num, info in CATALOGO_FORMATOS.items():
            assert "fase" in info, f"Formato {num} sin fase"
            assert info["fase"] in fases_validas, f"Formato {num} con fase invalida"

    def test_cada_formato_tiene_nombre(self):
        """Cada formato del catalogo debe tener nombre."""
        for num, info in CATALOGO_FORMATOS.items():
            assert "nombre" in info, f"Formato {num} sin nombre"
            assert len(info["nombre"]) > 0, f"Formato {num} con nombre vacio"
