"""Migración inicial — crea todas las tablas del sistema CecilIA v2

CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia
Sprint: 0

Revision ID: 001_migracion_inicial
Revises: None
Create Date: 2026-04-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Identificadores de revisión utilizados por Alembic
revision: str = "001_migracion_inicial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crea todas las tablas del esquema de CecilIA v2.

    Tablas creadas:
    - usuarios: Funcionarios de la CGR con roles y direcciones.
    - conversaciones: Sesiones de chat entre usuario y CecilIA.
    - mensajes: Mensajes individuales dentro de una conversación.
    - documentos: Documentos cargados para el pipeline RAG.
    - auditorias: Procesos de auditoría gestionados.
    - proyectos_auditoria: Sesiones de trabajo dentro de auditorías.
    - hallazgos: Hallazgos con los cinco elementos fiscales.
    - alertas: Alertas y notificaciones del sistema.
    - formatos_generados: Formatos CGR (1-30) generados.
    - logs_trazabilidad: Registro completo de trazabilidad de operaciones.
    """

    # ── Tipos enumerados ─────────────────────────────────────────────────

    tipo_rol_usuario = postgresql.ENUM(
        "auditor_des", "auditor_dvf",
        "profesional_des", "profesional_dvf",
        "director_des", "director_dvf",
        "admin_tic", "observatorio",
        name="rol_usuario_enum",
        create_type=True,
    )
    tipo_rol_usuario.create(op.get_bind(), checkfirst=True)

    tipo_direccion_usuario = postgresql.ENUM(
        "DES", "DVF",
        name="direccion_usuario_enum",
        create_type=True,
    )
    tipo_direccion_usuario.create(op.get_bind(), checkfirst=True)

    # ── Tabla: usuarios ──────────────────────────────────────────────────

    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "usuario", sa.String(100), nullable=False, unique=True,
            comment="Nombre de usuario unico para inicio de sesion",
        ),
        sa.Column(
            "nombre_completo", sa.String(255), nullable=False,
            comment="Nombre completo del funcionario",
        ),
        sa.Column(
            "email", sa.String(255), nullable=False, unique=True,
            comment="Correo electronico institucional",
        ),
        sa.Column(
            "rol", tipo_rol_usuario, nullable=False,
            comment="Rol del usuario en el sistema",
        ),
        sa.Column(
            "direccion", tipo_direccion_usuario, nullable=True,
            comment="Direccion misional (DES/DVF) — nulo para admin_tic",
        ),
        sa.Column(
            "password_hash", sa.String(255), nullable=False,
            comment="Hash bcrypt de la contrasena",
        ),
        sa.Column(
            "activo", sa.Boolean(), nullable=False, server_default=sa.text("true"),
            comment="Indica si el usuario esta activo en el sistema",
        ),
        sa.Column(
            "ultimo_acceso", sa.DateTime(timezone=True), nullable=True,
            comment="Fecha y hora del ultimo inicio de sesion",
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usuarios_usuario", "usuarios", ["usuario"])
    op.create_index("ix_usuarios_email", "usuarios", ["email"])

    # ── Tabla: conversaciones ────────────────────────────────────────────

    op.create_table(
        "conversaciones",
        sa.Column("id", sa.String(36), nullable=False, comment="UUID de la conversacion"),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("titulo", sa.String(500), nullable=False, server_default="Nueva conversación"),
        sa.Column("modelo_utilizado", sa.String(100), nullable=True, comment="Modelo LLM usado"),
        sa.Column("fase", sa.String(50), nullable=True, comment="Fase de auditoria en contexto"),
        sa.Column("proyecto_auditoria_id", sa.String(36), nullable=True),
        sa.Column("total_mensajes", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversaciones_usuario_id", "conversaciones", ["usuario_id"])

    # ── Tabla: mensajes ──────────────────────────────────────────────────

    op.create_table(
        "mensajes",
        sa.Column("id", sa.String(36), nullable=False, comment="UUID del mensaje"),
        sa.Column(
            "conversacion_id", sa.String(36),
            sa.ForeignKey("conversaciones.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("rol", sa.String(20), nullable=False, comment="user | assistant | system"),
        sa.Column("contenido", sa.Text(), nullable=False, comment="Texto del mensaje"),
        sa.Column(
            "fuentes", postgresql.JSONB(), nullable=True,
            comment="Fuentes citadas en la respuesta (JSON)",
        ),
        sa.Column(
            "metadata_modelo", postgresql.JSONB(), nullable=True,
            comment="Metadatos del modelo (tokens, latencia, etc.)",
        ),
        sa.Column("feedback_puntuacion", sa.SmallInteger(), nullable=True, comment="-1, 0, 1"),
        sa.Column("feedback_comentario", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mensajes_conversacion_id", "mensajes", ["conversacion_id"])
    op.create_index("ix_mensajes_created_at", "mensajes", ["created_at"])

    # ── Tabla: documentos ────────────────────────────────────────────────

    op.create_table(
        "documentos",
        sa.Column("id", sa.String(36), nullable=False, comment="UUID del documento"),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("nombre_archivo", sa.String(500), nullable=False),
        sa.Column("tipo_mime", sa.String(100), nullable=False),
        sa.Column("tamano_bytes", sa.BigInteger(), nullable=False),
        sa.Column("coleccion", sa.String(50), nullable=False, server_default="general"),
        sa.Column(
            "estado", sa.String(20), nullable=False, server_default="subido",
            comment="subido | procesando | indexado | error",
        ),
        sa.Column("ruta_almacenamiento", sa.String(1000), nullable=True),
        sa.Column("hash_contenido", sa.String(64), nullable=True, comment="SHA-256 del archivo"),
        sa.Column("total_fragmentos", sa.Integer(), nullable=True, comment="Fragmentos generados para RAG"),
        sa.Column("etiquetas", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("metadata_extra", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documentos_coleccion", "documentos", ["coleccion"])
    op.create_index("ix_documentos_estado", "documentos", ["estado"])
    op.create_index("ix_documentos_usuario_id", "documentos", ["usuario_id"])

    # ── Tabla: auditorias ────────────────────────────────────────────────

    op.create_table(
        "auditorias",
        sa.Column("id", sa.String(36), nullable=False, comment="UUID de la auditoria"),
        sa.Column("nombre", sa.String(500), nullable=False),
        sa.Column("entidad_auditada", sa.String(500), nullable=False),
        sa.Column(
            "tipo_auditoria", sa.String(50), nullable=False,
            comment="financiera | cumplimiento | desempeno | especial | integral",
        ),
        sa.Column("vigencia", sa.String(20), nullable=False),
        sa.Column("direccion", sa.String(10), nullable=False, comment="DES | DVF"),
        sa.Column(
            "fase_actual", sa.String(50), nullable=False, server_default="preplaneacion",
            comment="preplaneacion | planeacion | ejecucion | informe | seguimiento",
        ),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("fecha_inicio_planeada", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fecha_fin_planeada", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fecha_inicio_real", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fecha_fin_real", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "usuario_creador_id", sa.Integer(),
            sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column("metadata_extra", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_auditorias_direccion", "auditorias", ["direccion"])
    op.create_index("ix_auditorias_fase_actual", "auditorias", ["fase_actual"])
    op.create_index("ix_auditorias_entidad_auditada", "auditorias", ["entidad_auditada"])

    # ── Tabla: proyectos_auditoria ───────────────────────────────────────

    op.create_table(
        "proyectos_auditoria",
        sa.Column("id", sa.String(36), nullable=False, comment="UUID del proyecto"),
        sa.Column(
            "auditoria_id", sa.String(36),
            sa.ForeignKey("auditorias.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "usuario_id", sa.Integer(),
            sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column("nombre_sesion", sa.String(300), nullable=False),
        sa.Column("fase", sa.String(50), nullable=False),
        sa.Column("objetivo", sa.Text(), nullable=True),
        sa.Column(
            "estado", sa.String(20), nullable=False, server_default="activo",
            comment="activo | finalizado | archivado",
        ),
        sa.Column("contexto", postgresql.JSONB(), nullable=True, comment="Contexto acumulado de la sesión"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_proyectos_auditoria_auditoria_id", "proyectos_auditoria", ["auditoria_id"])

    # ── Tabla: hallazgos ─────────────────────────────────────────────────

    op.create_table(
        "hallazgos",
        sa.Column("id", sa.String(36), nullable=False, comment="UUID del hallazgo"),
        sa.Column(
            "auditoria_id", sa.String(36),
            sa.ForeignKey("auditorias.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "usuario_id", sa.Integer(),
            sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column("titulo", sa.String(500), nullable=False),
        sa.Column(
            "tipo", sa.String(50), nullable=False,
            comment="administrativo | fiscal | disciplinario | penal | fiscal_y_disciplinario",
        ),
        sa.Column(
            "estado", sa.String(30), nullable=False, server_default="borrador",
            comment="borrador | en_revision | aprobado | notificado | con_respuesta | confirmado | trasladado | archivado",
        ),
        sa.Column("cuantia", sa.Numeric(precision=20, scale=2), nullable=True, comment="Cuantia en pesos COP"),
        # Cinco elementos del hallazgo fiscal
        sa.Column("condicion", sa.Text(), nullable=False, comment="Lo que se encontro"),
        sa.Column("criterio", sa.Text(), nullable=False, comment="Norma o parametro incumplido"),
        sa.Column("causa", sa.Text(), nullable=False, comment="Razon de la diferencia"),
        sa.Column("efecto", sa.Text(), nullable=False, comment="Consecuencia o impacto"),
        sa.Column("recomendacion", sa.Text(), nullable=False, comment="Accion correctiva sugerida"),
        sa.Column("evidencias", postgresql.ARRAY(sa.String()), nullable=True, comment="IDs de documentos de evidencia"),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.Column("metadata_extra", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_hallazgos_auditoria_id", "hallazgos", ["auditoria_id"])
    op.create_index("ix_hallazgos_tipo", "hallazgos", ["tipo"])
    op.create_index("ix_hallazgos_estado", "hallazgos", ["estado"])

    # ── Tabla: alertas ───────────────────────────────────────────────────

    op.create_table(
        "alertas",
        sa.Column("id", sa.String(36), nullable=False, comment="UUID de la alerta"),
        sa.Column(
            "usuario_destino_id", sa.Integer(),
            sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "tipo", sa.String(50), nullable=False,
            comment="info | advertencia | error | accion_requerida",
        ),
        sa.Column("titulo", sa.String(300), nullable=False),
        sa.Column("mensaje", sa.Text(), nullable=False),
        sa.Column("leida", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("url_accion", sa.String(500), nullable=True, comment="URL para accion asociada"),
        sa.Column(
            "modulo_origen", sa.String(50), nullable=True,
            comment="Modulo que genero la alerta (chat, hallazgos, formatos, etc.)",
        ),
        sa.Column("metadata_extra", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alertas_usuario_destino_id", "alertas", ["usuario_destino_id"])
    op.create_index("ix_alertas_leida", "alertas", ["leida"])

    # ── Tabla: formatos_generados ────────────────────────────────────────

    op.create_table(
        "formatos_generados",
        sa.Column("id", sa.String(36), nullable=False, comment="UUID del formato"),
        sa.Column("numero_formato", sa.SmallInteger(), nullable=False, comment="Numero del formato CGR (1-30)"),
        sa.Column("nombre_formato", sa.String(300), nullable=False),
        sa.Column(
            "auditoria_id", sa.String(36),
            sa.ForeignKey("auditorias.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column(
            "usuario_id", sa.Integer(),
            sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column(
            "estado", sa.String(20), nullable=False, server_default="generando",
            comment="generando | completado | error",
        ),
        sa.Column("generado_con_ia", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("ruta_archivo", sa.String(1000), nullable=True),
        sa.Column("parametros", postgresql.JSONB(), nullable=True, comment="Parametros usados para generacion"),
        sa.Column("contenido_generado", sa.Text(), nullable=True, comment="Contenido generado por IA"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_formatos_generados_auditoria_id", "formatos_generados", ["auditoria_id"])
    op.create_index("ix_formatos_generados_numero_formato", "formatos_generados", ["numero_formato"])

    # ── Tabla: logs_trazabilidad ─────────────────────────────────────────

    op.create_table(
        "logs_trazabilidad",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "usuario_id", sa.Integer(),
            sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column("accion", sa.String(100), nullable=False, comment="Tipo de accion realizada"),
        sa.Column(
            "modulo", sa.String(50), nullable=False,
            comment="Modulo del sistema (chat, rag, hallazgos, formatos, admin, etc.)",
        ),
        sa.Column("detalle", sa.Text(), nullable=True, comment="Descripcion detallada de la operacion"),
        sa.Column("modelo_utilizado", sa.String(100), nullable=True, comment="Modelo LLM utilizado"),
        sa.Column("fuentes_consultadas", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("tokens_entrada", sa.Integer(), nullable=True),
        sa.Column("tokens_salida", sa.Integer(), nullable=True),
        sa.Column("duracion_ms", sa.Float(), nullable=True, comment="Duracion en milisegundos"),
        sa.Column("ip_origen", sa.String(45), nullable=True, comment="Direccion IP del cliente"),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("codigo_respuesta", sa.SmallInteger(), nullable=True, comment="Codigo HTTP de respuesta"),
        sa.Column("metadata_extra", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_logs_trazabilidad_usuario_id", "logs_trazabilidad", ["usuario_id"])
    op.create_index("ix_logs_trazabilidad_accion", "logs_trazabilidad", ["accion"])
    op.create_index("ix_logs_trazabilidad_modulo", "logs_trazabilidad", ["modulo"])
    op.create_index("ix_logs_trazabilidad_created_at", "logs_trazabilidad", ["created_at"])

    # ── Extensión pgvector para embeddings ───────────────────────────────

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ── Tabla: fragmentos_vectoriales ────────────────────────────────────
    # Tabla para almacenar los embeddings de fragmentos de documentos (pgvector)

    op.create_table(
        "fragmentos_vectoriales",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column(
            "documento_id", sa.String(36),
            sa.ForeignKey("documentos.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("contenido", sa.Text(), nullable=False, comment="Texto del fragmento"),
        sa.Column("coleccion", sa.String(50), nullable=False),
        sa.Column("pagina", sa.Integer(), nullable=True),
        sa.Column("posicion_fragmento", sa.Integer(), nullable=True, comment="Orden del fragmento en el documento"),
        sa.Column("metadata_extra", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Columna de embedding vectorial (3072 dimensiones para text-embedding-3-large)
    op.execute(
        "ALTER TABLE fragmentos_vectoriales ADD COLUMN embedding vector(3072)"
    )

    op.create_index("ix_fragmentos_vectoriales_documento_id", "fragmentos_vectoriales", ["documento_id"])
    op.create_index("ix_fragmentos_vectoriales_coleccion", "fragmentos_vectoriales", ["coleccion"])

    # Índice HNSW para búsqueda de similitud coseno eficiente
    op.execute(
        "CREATE INDEX ix_fragmentos_vectoriales_embedding_hnsw "
        "ON fragmentos_vectoriales "
        "USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )


def downgrade() -> None:
    """Revierte la migración eliminando todas las tablas e índices."""

    # Eliminar tablas en orden inverso de dependencias
    op.drop_table("fragmentos_vectoriales")
    op.drop_table("logs_trazabilidad")
    op.drop_table("formatos_generados")
    op.drop_table("alertas")
    op.drop_table("hallazgos")
    op.drop_table("proyectos_auditoria")
    op.drop_table("auditorias")
    op.drop_table("documentos")
    op.drop_table("mensajes")
    op.drop_table("conversaciones")
    op.drop_table("usuarios")

    # Eliminar tipos enumerados
    op.execute("DROP TYPE IF EXISTS direccion_usuario_enum")
    op.execute("DROP TYPE IF EXISTS rol_usuario_enum")

    # No eliminamos la extensión pgvector ya que puede ser usada por otros esquemas
