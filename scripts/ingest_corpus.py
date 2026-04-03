"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: ingest_corpus.py
Propósito: Ingestión del corpus documental — escaneo, extracción de texto, generación de embeddings y almacenamiento en pgvector
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

import os
import sys
import time
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("ingest_corpus")

DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
EMBEDDING_MODEL: str = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
CHUNK_SIZE: int = int(os.environ.get("CHUNK_SIZE", "1024"))
CHUNK_OVERLAP: int = int(os.environ.get("CHUNK_OVERLAP", "128"))
CORPUS_DIR: Path = Path(os.environ.get("CORPUS_DIR", "corpus"))

EXTENSIONES_SOPORTADAS: set[str] = {".pdf", ".docx", ".xlsx"}

# ---------------------------------------------------------------------------
# Colecciones del corpus
# ---------------------------------------------------------------------------
COLECCIONES = [
    "normativo",
    "institucional",
    "academico",
    "tecnico_tic",
    "estadistico",
    "jurisprudencial",
    "auditoria",
]


# ---------------------------------------------------------------------------
# Estructuras de datos
# ---------------------------------------------------------------------------
@dataclass
class Fragmento:
    """Representa un fragmento (chunk) de texto extraído de un documento."""

    coleccion: str
    archivo: str
    contenido: str
    pagina: int | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class EstadisticasIngestion:
    """Acumula estadísticas del proceso de ingestión."""

    archivos_procesados: int = 0
    archivos_omitidos: int = 0
    fragmentos_generados: int = 0
    embeddings_almacenados: int = 0
    errores: int = 0
    tiempo_inicio: float = field(default_factory=time.time)

    def resumen(self) -> str:
        duracion = time.time() - self.tiempo_inicio
        return (
            "\n" + "=" * 60 + "\n"
            "RESUMEN DE INGESTIÓN DEL CORPUS\n"
            f"  Archivos procesados  : {self.archivos_procesados}\n"
            f"  Archivos omitidos    : {self.archivos_omitidos}\n"
            f"  Fragmentos generados : {self.fragmentos_generados}\n"
            f"  Embeddings almacenados: {self.embeddings_almacenados}\n"
            f"  Errores              : {self.errores}\n"
            f"  Duración             : {duracion:.1f} s\n"
            + "=" * 60
        )


# ---------------------------------------------------------------------------
# Extracción de texto según formato
# ---------------------------------------------------------------------------

def extraer_texto_pdf(ruta: Path) -> list[tuple[int, str]]:
    """Extrae texto página a página de un PDF.

    Retorna lista de tuplas (número_página, texto).
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.error("PyMuPDF (fitz) no está instalado. Ejecute: pip install pymupdf")
        return []

    paginas: list[tuple[int, str]] = []
    with fitz.open(str(ruta)) as doc:
        for i, pagina in enumerate(doc, start=1):
            texto = pagina.get_text("text")
            if texto.strip():
                paginas.append((i, texto))
    return paginas


def extraer_texto_docx(ruta: Path) -> list[tuple[None, str]]:
    """Extrae texto completo de un archivo DOCX."""
    try:
        from docx import Document
    except ImportError:
        logger.error("python-docx no está instalado. Ejecute: pip install python-docx")
        return []

    doc = Document(str(ruta))
    texto = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return [(None, texto)] if texto else []


def extraer_texto_xlsx(ruta: Path) -> list[tuple[None, str]]:
    """Extrae contenido textual de un archivo XLSX (todas las hojas)."""
    try:
        import openpyxl
    except ImportError:
        logger.error("openpyxl no está instalado. Ejecute: pip install openpyxl")
        return []

    wb = openpyxl.load_workbook(str(ruta), read_only=True, data_only=True)
    textos: list[str] = []
    for hoja in wb.sheetnames:
        ws = wb[hoja]
        filas = []
        for fila in ws.iter_rows(values_only=True):
            celdas = [str(c) for c in fila if c is not None]
            if celdas:
                filas.append(" | ".join(celdas))
        if filas:
            textos.append(f"[Hoja: {hoja}]\n" + "\n".join(filas))
    wb.close()
    contenido = "\n\n".join(textos)
    return [(None, contenido)] if contenido else []


EXTRACTORES = {
    ".pdf": extraer_texto_pdf,
    ".docx": extraer_texto_docx,
    ".xlsx": extraer_texto_xlsx,
}


# ---------------------------------------------------------------------------
# Fragmentación (chunking)
# ---------------------------------------------------------------------------

def fragmentar_texto(
    texto: str,
    tamano: int = CHUNK_SIZE,
    solapamiento: int = CHUNK_OVERLAP,
) -> list[str]:
    """Divide un texto largo en fragmentos con solapamiento."""
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


# ---------------------------------------------------------------------------
# Generación de embeddings
# ---------------------------------------------------------------------------

def generar_embeddings(textos: list[str]) -> list[list[float]]:
    """Genera embeddings utilizando la API de OpenAI (o compatible).

    En producción se utiliza un modelo de embeddings configurado vía
    variables de entorno.  Para ejecución local sin API, retorna vectores
    vacíos y registra una advertencia.
    """
    if not OPENAI_API_KEY:
        logger.warning(
            "OPENAI_API_KEY no configurada. Se omiten embeddings reales."
        )
        return [[0.0] * 1536 for _ in textos]

    try:
        import openai

        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        respuesta = client.embeddings.create(
            input=textos,
            model=EMBEDDING_MODEL,
        )
        return [item.embedding for item in respuesta.data]
    except Exception as exc:
        logger.error("Error al generar embeddings: %s", exc)
        return [[0.0] * 1536 for _ in textos]


# ---------------------------------------------------------------------------
# Almacenamiento en pgvector
# ---------------------------------------------------------------------------

def almacenar_fragmentos(
    session,
    fragmentos: list[Fragmento],
    embeddings: list[list[float]],
) -> int:
    """Inserta fragmentos con sus embeddings en la tabla *corpus_chunks*."""
    insertados = 0
    for frag, emb in zip(fragmentos, embeddings):
        try:
            session.execute(
                text("""
                    INSERT INTO corpus_chunks
                        (coleccion, archivo, pagina, contenido, embedding, metadata)
                    VALUES
                        (:col, :arch, :pag, :cont, :emb, :meta)
                """),
                {
                    "col": frag.coleccion,
                    "arch": frag.archivo,
                    "pag": frag.pagina,
                    "cont": frag.contenido,
                    "emb": str(emb),
                    "meta": str(frag.metadata),
                },
            )
            insertados += 1
        except Exception as exc:
            logger.error("Error al insertar fragmento de %s: %s", frag.archivo, exc)
    return insertados


# ---------------------------------------------------------------------------
# Escaneo del corpus
# ---------------------------------------------------------------------------

def escanear_corpus(base: Path) -> Iterator[tuple[str, Path]]:
    """Recorre los directorios de colecciones y genera tuplas (colección, ruta)."""
    for coleccion in COLECCIONES:
        directorio = base / coleccion
        if not directorio.is_dir():
            logger.info("Directorio no encontrado, se omite: %s", directorio)
            continue
        for archivo in sorted(directorio.rglob("*")):
            if archivo.is_file() and archivo.suffix.lower() in EXTENSIONES_SOPORTADAS:
                yield coleccion, archivo


# ---------------------------------------------------------------------------
# Proceso principal
# ---------------------------------------------------------------------------

def ingestar() -> None:
    """Ejecuta el flujo completo de ingestión del corpus."""
    if not DATABASE_URL:
        logger.error("DATABASE_URL no configurada.")
        sys.exit(1)

    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    stats = EstadisticasIngestion()

    logger.info("Iniciando ingestión del corpus desde: %s", CORPUS_DIR.resolve())

    for coleccion, ruta in escanear_corpus(CORPUS_DIR):
        logger.info("Procesando [%s] %s …", coleccion, ruta.name)
        extractor = EXTRACTORES.get(ruta.suffix.lower())

        if extractor is None:
            stats.archivos_omitidos += 1
            continue

        try:
            paginas = extractor(ruta)
        except Exception as exc:
            logger.error("Error al extraer texto de %s: %s", ruta, exc)
            stats.errores += 1
            continue

        if not paginas:
            stats.archivos_omitidos += 1
            continue

        fragmentos_doc: list[Fragmento] = []
        for pagina_num, texto in paginas:
            trozos = fragmentar_texto(texto)
            for trozo in trozos:
                fragmentos_doc.append(
                    Fragmento(
                        coleccion=coleccion,
                        archivo=ruta.name,
                        contenido=trozo,
                        pagina=pagina_num,
                        metadata={"ruta_original": str(ruta)},
                    )
                )

        if not fragmentos_doc:
            stats.archivos_omitidos += 1
            continue

        # Generar embeddings por lotes de 64
        BATCH = 64
        total_insertados = 0
        for i in range(0, len(fragmentos_doc), BATCH):
            lote = fragmentos_doc[i : i + BATCH]
            textos_lote = [f.contenido for f in lote]
            embs = generar_embeddings(textos_lote)
            insertados = almacenar_fragmentos(session, lote, embs)
            total_insertados += insertados

        session.commit()
        stats.archivos_procesados += 1
        stats.fragmentos_generados += len(fragmentos_doc)
        stats.embeddings_almacenados += total_insertados
        logger.info(
            "  → %d fragmentos, %d embeddings almacenados",
            len(fragmentos_doc),
            total_insertados,
        )

    session.close()
    logger.info(stats.resumen())


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    ingestar()
