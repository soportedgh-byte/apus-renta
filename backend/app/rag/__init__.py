"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloría General de la República de Colombia

Archivo: __init__.py
Propósito: Paquete RAG (Retrieval-Augmented Generation)
Sprint: 0
Autor: Equipo Técnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from backend.app.rag.ingesta import ingestar_documento
from backend.app.rag.chunking import dividir_en_fragmentos
from backend.app.rag.embeddings import generar_embeddings
from backend.app.rag.retriever import buscar_similares
from backend.app.rag.reranker import reordenar_resultados

__all__: list[str] = [
    "ingestar_documento",
    "dividir_en_fragmentos",
    "generar_embeddings",
    "buscar_similares",
    "reordenar_resultados",
]
