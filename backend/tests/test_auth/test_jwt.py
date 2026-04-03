"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: test_jwt.py
Propósito: Pruebas unitarias del módulo de autenticación JWT — generación, validación y expiración de tokens
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

import time
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Constantes de prueba
# ---------------------------------------------------------------------------
SECRET_KEY = "clave-secreta-de-prueba-cecilia-v2-no-usar-en-produccion"
ALGORITHM = "HS256"
EXPIRATION_MINUTES = 480  # 8 horas


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def jwt_settings():
    """Configuración JWT para pruebas."""
    return {
        "secret_key": SECRET_KEY,
        "algorithm": ALGORITHM,
        "expiration_minutes": EXPIRATION_MINUTES,
    }


@pytest.fixture
def sample_user_payload():
    """Payload de usuario estándar para pruebas."""
    return {
        "sub": "auditor.des.01",
        "nombre": "Auditor DES Pruebas 01",
        "rol": "AUDITOR_DES",
        "dir": "DES",
    }


@pytest.fixture
def admin_payload():
    """Payload de administrador para pruebas."""
    return {
        "sub": "admin.cecilia",
        "nombre": "Administrador CecilIA",
        "rol": "ADMIN",
        "dir": None,
    }


# ---------------------------------------------------------------------------
# Tests de generación de tokens
# ---------------------------------------------------------------------------
class TestGenerarToken:
    """Pruebas para la función de generación de tokens JWT."""

    def test_genera_token_valido(self, jwt_settings, sample_user_payload):
        """Un token generado debe ser una cadena no vacía con tres segmentos."""
        import jwt

        token = jwt.encode(
            {
                **sample_user_payload,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=jwt_settings["expiration_minutes"]),
                "iat": datetime.now(timezone.utc),
            },
            jwt_settings["secret_key"],
            algorithm=jwt_settings["algorithm"],
        )

        assert isinstance(token, str)
        assert len(token) > 0
        # JWT tiene tres segmentos separados por punto
        assert len(token.split(".")) == 3

    def test_token_contiene_claims_esperados(self, jwt_settings, sample_user_payload):
        """El token decodificado debe contener todos los claims del payload."""
        import jwt

        now = datetime.now(timezone.utc)
        token = jwt.encode(
            {
                **sample_user_payload,
                "exp": now + timedelta(minutes=jwt_settings["expiration_minutes"]),
                "iat": now,
            },
            jwt_settings["secret_key"],
            algorithm=jwt_settings["algorithm"],
        )

        decoded = jwt.decode(
            token,
            jwt_settings["secret_key"],
            algorithms=[jwt_settings["algorithm"]],
        )

        assert decoded["sub"] == "auditor.des.01"
        assert decoded["rol"] == "AUDITOR_DES"
        assert decoded["dir"] == "DES"
        assert "exp" in decoded
        assert "iat" in decoded

    def test_token_admin_sin_direccion(self, jwt_settings, admin_payload):
        """Un token de administrador puede tener dirección nula."""
        import jwt

        token = jwt.encode(
            {
                **admin_payload,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=jwt_settings["expiration_minutes"]),
                "iat": datetime.now(timezone.utc),
            },
            jwt_settings["secret_key"],
            algorithm=jwt_settings["algorithm"],
        )

        decoded = jwt.decode(
            token,
            jwt_settings["secret_key"],
            algorithms=[jwt_settings["algorithm"]],
        )

        assert decoded["sub"] == "admin.cecilia"
        assert decoded["rol"] == "ADMIN"
        assert decoded["dir"] is None


# ---------------------------------------------------------------------------
# Tests de validación de tokens
# ---------------------------------------------------------------------------
class TestValidarToken:
    """Pruebas para la validación de tokens JWT."""

    def test_token_valido_se_decodifica(self, jwt_settings, sample_user_payload):
        """Un token válido debe decodificarse sin errores."""
        import jwt

        token = jwt.encode(
            {
                **sample_user_payload,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
                "iat": datetime.now(timezone.utc),
            },
            jwt_settings["secret_key"],
            algorithm=jwt_settings["algorithm"],
        )

        decoded = jwt.decode(
            token,
            jwt_settings["secret_key"],
            algorithms=[jwt_settings["algorithm"]],
        )

        assert decoded["sub"] == sample_user_payload["sub"]

    def test_token_con_clave_incorrecta_falla(self, jwt_settings, sample_user_payload):
        """Un token firmado con una clave diferente debe ser rechazado."""
        import jwt

        token = jwt.encode(
            {
                **sample_user_payload,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
                "iat": datetime.now(timezone.utc),
            },
            "clave-incorrecta",
            algorithm=jwt_settings["algorithm"],
        )

        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(
                token,
                jwt_settings["secret_key"],
                algorithms=[jwt_settings["algorithm"]],
            )

    def test_token_manipulado_falla(self, jwt_settings, sample_user_payload):
        """Un token cuyo contenido ha sido alterado debe ser rechazado."""
        import jwt

        token = jwt.encode(
            {
                **sample_user_payload,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
                "iat": datetime.now(timezone.utc),
            },
            jwt_settings["secret_key"],
            algorithm=jwt_settings["algorithm"],
        )

        # Alterar un carácter del payload (segundo segmento)
        partes = token.split(".")
        payload_alterado = partes[1][:-1] + ("A" if partes[1][-1] != "A" else "B")
        token_alterado = f"{partes[0]}.{payload_alterado}.{partes[2]}"

        with pytest.raises(jwt.exceptions.DecodeError):
            jwt.decode(
                token_alterado,
                jwt_settings["secret_key"],
                algorithms=[jwt_settings["algorithm"]],
            )

    def test_algoritmo_none_rechazado(self, jwt_settings, sample_user_payload):
        """No debe aceptarse un token con algoritmo 'none'."""
        import jwt

        token = jwt.encode(
            {
                **sample_user_payload,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            },
            jwt_settings["secret_key"],
            algorithm=jwt_settings["algorithm"],
        )

        with pytest.raises(jwt.InvalidAlgorithmError):
            jwt.decode(
                token,
                jwt_settings["secret_key"],
                algorithms=["none"],
            )


# ---------------------------------------------------------------------------
# Tests de expiración
# ---------------------------------------------------------------------------
class TestExpiracionToken:
    """Pruebas para el manejo de expiración de tokens."""

    def test_token_expirado_es_rechazado(self, jwt_settings, sample_user_payload):
        """Un token con fecha de expiración pasada debe ser rechazado."""
        import jwt

        token = jwt.encode(
            {
                **sample_user_payload,
                "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
                "iat": datetime.now(timezone.utc) - timedelta(minutes=30),
            },
            jwt_settings["secret_key"],
            algorithm=jwt_settings["algorithm"],
        )

        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(
                token,
                jwt_settings["secret_key"],
                algorithms=[jwt_settings["algorithm"]],
            )

    def test_token_recien_creado_es_valido(self, jwt_settings, sample_user_payload):
        """Un token recién creado debe ser válido."""
        import jwt

        token = jwt.encode(
            {
                **sample_user_payload,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=jwt_settings["expiration_minutes"]),
                "iat": datetime.now(timezone.utc),
            },
            jwt_settings["secret_key"],
            algorithm=jwt_settings["algorithm"],
        )

        decoded = jwt.decode(
            token,
            jwt_settings["secret_key"],
            algorithms=[jwt_settings["algorithm"]],
        )

        assert decoded["sub"] == sample_user_payload["sub"]

    def test_token_sin_expiracion_es_rechazado(self, jwt_settings, sample_user_payload):
        """Un token sin claim 'exp' debe ser rechazado cuando se requiere."""
        import jwt

        token = jwt.encode(
            {
                **sample_user_payload,
                "iat": datetime.now(timezone.utc),
            },
            jwt_settings["secret_key"],
            algorithm=jwt_settings["algorithm"],
        )

        with pytest.raises(jwt.MissingRequiredClaimError):
            jwt.decode(
                token,
                jwt_settings["secret_key"],
                algorithms=[jwt_settings["algorithm"]],
                options={"require": ["exp"]},
            )
