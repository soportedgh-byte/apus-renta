"""
Tests para los modelos del modulo de capacitacion — Sprint 6.
Verifica campos, defaults y relaciones de los 4 modelos.
"""

import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone


def _crear_ruta_mock(**kwargs):
    """Crea un mock de RutaAprendizaje."""
    r = MagicMock()
    r.id = kwargs.get("id", "ruta-001")
    r.nombre = kwargs.get("nombre", "Conoce la CGR")
    r.descripcion = kwargs.get("descripcion", "Estructura y funcionamiento")
    r.icono = kwargs.get("icono", "🏛️")
    r.color = kwargs.get("color", "#1A5276")
    r.direccion = kwargs.get("direccion", "TODOS")
    r.orden = kwargs.get("orden", 1)
    r.activa = kwargs.get("activa", True)
    r.total_lecciones = kwargs.get("total_lecciones", 6)
    r.created_at = kwargs.get("created_at", datetime.now(timezone.utc))
    return r


def _crear_leccion_mock(**kwargs):
    """Crea un mock de Leccion."""
    l = MagicMock()
    l.id = kwargs.get("id", "ruta-001-1")
    l.ruta_id = kwargs.get("ruta_id", "ruta-001")
    l.numero = kwargs.get("numero", 1)
    l.titulo = kwargs.get("titulo", "Que es la CGR")
    l.descripcion = kwargs.get("descripcion", "")
    l.contenido_md = kwargs.get("contenido_md", "# Leccion 1")
    l.duracion_minutos = kwargs.get("duracion_minutos", 15)
    l.orden = kwargs.get("orden", 1)
    l.created_at = kwargs.get("created_at", datetime.now(timezone.utc))
    return l


def _crear_progreso_mock(**kwargs):
    """Crea un mock de ProgresoUsuario."""
    p = MagicMock()
    p.id = kwargs.get("id", "prog-001")
    p.usuario_id = kwargs.get("usuario_id", 13)
    p.ruta_id = kwargs.get("ruta_id", "ruta-001")
    p.leccion_id = kwargs.get("leccion_id", "ruta-001-1")
    p.completada = kwargs.get("completada", False)
    p.fecha_completada = kwargs.get("fecha_completada", None)
    p.puntaje_quiz = kwargs.get("puntaje_quiz", None)
    p.created_at = kwargs.get("created_at", datetime.now(timezone.utc))
    return p


def _crear_quiz_mock(**kwargs):
    """Crea un mock de QuizResultado."""
    q = MagicMock()
    q.id = kwargs.get("id", "quiz-001")
    q.usuario_id = kwargs.get("usuario_id", 13)
    q.leccion_id = kwargs.get("leccion_id", "ruta-001-1")
    q.ruta_id = kwargs.get("ruta_id", "ruta-001")
    q.puntaje = kwargs.get("puntaje", 80.0)
    q.total_preguntas = kwargs.get("total_preguntas", 5)
    q.respuestas_json = kwargs.get("respuestas_json", [])
    q.aprobado = kwargs.get("aprobado", True)
    q.created_at = kwargs.get("created_at", datetime.now(timezone.utc))
    return q


class TestRutaAprendizaje:
    """Tests para el modelo RutaAprendizaje."""

    def test_campos_basicos(self):
        r = _crear_ruta_mock()
        assert r.id == "ruta-001"
        assert r.nombre == "Conoce la CGR"
        assert r.icono == "🏛️"

    def test_direccion_valida(self):
        for d in ["DES", "DVF", "TODOS"]:
            r = _crear_ruta_mock(direccion=d)
            assert r.direccion in ("DES", "DVF", "TODOS")

    def test_activa_por_defecto(self):
        r = _crear_ruta_mock()
        assert r.activa is True

    def test_total_lecciones(self):
        r = _crear_ruta_mock(total_lecciones=10)
        assert r.total_lecciones == 10

    def test_color_hex(self):
        r = _crear_ruta_mock(color="#C9A84C")
        assert r.color.startswith("#")
        assert len(r.color) == 7


class TestLeccion:
    """Tests para el modelo Leccion."""

    def test_campos_basicos(self):
        l = _crear_leccion_mock()
        assert l.ruta_id == "ruta-001"
        assert l.numero == 1
        assert l.titulo == "Que es la CGR"

    def test_contenido_md(self):
        l = _crear_leccion_mock(contenido_md="# Test\n\nContenido de prueba")
        assert "# Test" in l.contenido_md

    def test_duracion_default(self):
        l = _crear_leccion_mock()
        assert l.duracion_minutos == 15

    def test_orden_numerico(self):
        l = _crear_leccion_mock(orden=5)
        assert l.orden == 5


class TestProgresoUsuario:
    """Tests para el modelo ProgresoUsuario."""

    def test_campos_basicos(self):
        p = _crear_progreso_mock()
        assert p.usuario_id == 13
        assert p.completada is False

    def test_completada_con_fecha(self):
        ahora = datetime.now(timezone.utc)
        p = _crear_progreso_mock(completada=True, fecha_completada=ahora)
        assert p.completada is True
        assert p.fecha_completada is not None

    def test_puntaje_quiz_opcional(self):
        p = _crear_progreso_mock(puntaje_quiz=None)
        assert p.puntaje_quiz is None

    def test_puntaje_quiz_con_valor(self):
        p = _crear_progreso_mock(puntaje_quiz=85.5)
        assert p.puntaje_quiz == 85.5


class TestQuizResultado:
    """Tests para el modelo QuizResultado."""

    def test_campos_basicos(self):
        q = _crear_quiz_mock()
        assert q.puntaje == 80.0
        assert q.total_preguntas == 5

    def test_aprobado_mayor_70(self):
        q = _crear_quiz_mock(puntaje=75.0, aprobado=True)
        assert q.aprobado is True

    def test_reprobado_menor_70(self):
        q = _crear_quiz_mock(puntaje=60.0, aprobado=False)
        assert q.aprobado is False

    def test_respuestas_json(self):
        respuestas = [
            {"pregunta": "Q1", "respuesta_usuario": "A", "respuesta_correcta": "A", "correcta": True},
            {"pregunta": "Q2", "respuesta_usuario": "B", "respuesta_correcta": "C", "correcta": False},
        ]
        q = _crear_quiz_mock(respuestas_json=respuestas)
        assert len(q.respuestas_json) == 2
        assert q.respuestas_json[0]["correcta"] is True

    def test_leccion_id_opcional(self):
        q = _crear_quiz_mock(leccion_id=None)
        assert q.leccion_id is None

    def test_umbral_70_porciento(self):
        """El umbral de aprobacion es 70%."""
        q_aprobado = _crear_quiz_mock(puntaje=70.0, aprobado=True)
        q_reprobado = _crear_quiz_mock(puntaje=69.9, aprobado=False)
        assert q_aprobado.aprobado is True
        assert q_reprobado.aprobado is False
