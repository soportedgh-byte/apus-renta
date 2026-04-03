"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: seed_users.py
Propósito: Poblar la base de datos con 12 usuarios de prueba para el entorno de desarrollo
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

import os
import sys
import logging
from datetime import datetime, timezone

import bcrypt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# ---------------------------------------------------------------------------
# Configuración de logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("seed_users")

# ---------------------------------------------------------------------------
# Conexión a base de datos
# ---------------------------------------------------------------------------
DATABASE_URL: str = os.environ.get("DATABASE_URL", "")

if not DATABASE_URL:
    logger.error(
        "La variable de entorno DATABASE_URL no está configurada. "
        "Ejemplo: postgresql+psycopg2://usuario:clave@localhost:5432/cecilia"
    )
    sys.exit(1)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

# ---------------------------------------------------------------------------
# Catálogo de usuarios de prueba
# ---------------------------------------------------------------------------
USUARIOS = [
    {
        "usuario": "admin.cecilia",
        "nombre": "Administrador CecilIA",
        "rol": "ADMIN",
        "dir": None,
        "pwd": "CecilIA_Admin_2026!",
    },
    {
        "usuario": "juan.cobo",
        "nombre": "Dr. Juan Carlos Cobo Gómez",
        "rol": "DIRECTOR_DES",
        "dir": "DES",
        "pwd": "DES_Director_2026!",
    },
    {
        "usuario": "auditor.des.01",
        "nombre": "Auditor DES Pruebas 01",
        "rol": "AUDITOR_DES",
        "dir": "DES",
        "pwd": "Auditor_DES_2026!",
    },
    {
        "usuario": "auditor.des.02",
        "nombre": "Auditor DES Pruebas 02",
        "rol": "AUDITOR_DES",
        "dir": "DES",
        "pwd": "Auditor_DES_2026!",
    },
    {
        "usuario": "esteban.deleon",
        "nombre": "Ing. Esteban De León",
        "rol": "AUDITOR_DES",
        "dir": "DES",
        "pwd": "Auditor_DES_2026!",
    },
    {
        "usuario": "jose.ramirez",
        "nombre": "Dr. José Fernando Ramírez Muñoz",
        "rol": "DIRECTOR_DVF",
        "dir": "DVF",
        "pwd": "DVF_Director_2026!",
    },
    {
        "usuario": "auditor.dvf.01",
        "nombre": "Auditor DVF Pruebas 01",
        "rol": "AUDITOR_DVF",
        "dir": "DVF",
        "pwd": "Auditor_DVF_2026!",
    },
    {
        "usuario": "auditor.dvf.02",
        "nombre": "Auditor DVF Pruebas 02",
        "rol": "AUDITOR_DVF",
        "dir": "DVF",
        "pwd": "Auditor_DVF_2026!",
    },
    {
        "usuario": "jose.rey",
        "nombre": "Ing. José A. Rey",
        "rol": "AUDITOR_DVF",
        "dir": "DVF",
        "pwd": "Auditor_DVF_2026!",
    },
    {
        "usuario": "gustavo.castillo",
        "nombre": "Ing. Gustavo Adolfo Castillo Romero",
        "rol": "LIDER_TECNICO",
        "dir": None,
        "pwd": "Lider_Tech_2026!",
    },
    {
        "usuario": "karen.suevis",
        "nombre": "Abog. Karen Tatiana Suevis Gómez",
        "rol": "COORDINADOR",
        "dir": None,
        "pwd": "Coord_Legal_2026!",
    },
    {
        "usuario": "observador.cgr",
        "nombre": "Observador CGR",
        "rol": "OBSERVADOR",
        "dir": None,
        "pwd": "Observador_2026!",
    },
]


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def hash_password(plain: str) -> str:
    """Genera un hash bcrypt a partir de una contraseña en texto plano."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def user_exists(session, username: str) -> bool:
    """Verifica si un usuario ya existe en la tabla *usuarios*."""
    result = session.execute(
        text("SELECT 1 FROM usuarios WHERE usuario = :u LIMIT 1"),
        {"u": username},
    )
    return result.fetchone() is not None


INSERT_SQL = text("""
    INSERT INTO usuarios (usuario, nombre_completo, rol, direccion, password_hash, activo, creado_en)
    VALUES (:usuario, :nombre, :rol, :dir, :pwd_hash, TRUE, :now)
""")


def seed() -> None:
    """Inserta los usuarios de prueba en la base de datos."""
    session = SessionLocal()
    creados: list[str] = []
    omitidos: list[str] = []

    try:
        for u in USUARIOS:
            if user_exists(session, u["usuario"]):
                omitidos.append(u["usuario"])
                logger.info("⏭  Usuario ya existe, se omite: %s", u["usuario"])
                continue

            pwd_hash = hash_password(u["pwd"])
            session.execute(
                INSERT_SQL,
                {
                    "usuario": u["usuario"],
                    "nombre": u["nombre"],
                    "rol": u["rol"],
                    "dir": u["dir"],
                    "pwd_hash": pwd_hash,
                    "now": datetime.now(timezone.utc),
                },
            )
            creados.append(u["usuario"])
            logger.info("✅  Usuario creado: %s (%s)", u["usuario"], u["rol"])

        session.commit()
    except IntegrityError as exc:
        session.rollback()
        logger.error("Error de integridad al insertar usuarios: %s", exc)
        raise
    except Exception as exc:
        session.rollback()
        logger.error("Error inesperado: %s", exc)
        raise
    finally:
        session.close()

    # ---- Resumen ----
    logger.info("=" * 60)
    logger.info("RESUMEN DE CARGA DE USUARIOS")
    logger.info("  Creados : %d", len(creados))
    logger.info("  Omitidos: %d (ya existían)", len(omitidos))
    logger.info("  Total   : %d", len(USUARIOS))
    logger.info("=" * 60)


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("Iniciando carga de usuarios de prueba …")
    seed()
    logger.info("Proceso finalizado.")
