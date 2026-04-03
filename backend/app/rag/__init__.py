"""
CecilIA v2 — Sistema de IA para Control Fiscal
Contraloria General de la Republica de Colombia

Archivo: __init__.py
Proposito: Paquete RAG (Retrieval-Augmented Generation)
Sprint: 1
Autor: Equipo Tecnico CecilIA — CD-TIC-CGR
Fecha: Abril 2026
"""

from app.rag.ingesta import ingestar_documento
from app.rag.chunking import dividir_en_fragmentos, detectar_modo_por_coleccion
from app.rag.embeddings import generar_embeddings, generar_embedding_consulta, obtener_dimension
from app.rag.retriever import buscar_similares, ResultadoBusqueda
from app.rag.reranker import reordenar_resultados

__all__: list[str] = [
    "ingestar_documento",
    "dividir_en_fragmentos",
    "detectar_modo_por_coleccion",
    "generar_embeddings",
    "generar_embedding_consulta",
    "obtener_dimension",
    "buscar_similares",
    "ResultadoBusqueda",
    "reordenar_resultados",
]
