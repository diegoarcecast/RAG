from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.embeddings.ollama_client import generate_embedding
from app.embeddings.search_repository import search_similar_chunks
from app.rag_trace_repository import (
    insert_rag_query,
    insert_retrieval_log,
    get_query_retrieval_trace,
)


@dataclass
class RetrievedChunk:
    rank_position: int
    chunk_id: int
    document_id: int
    document_title: str
    source_type: str
    chunk_index: int
    chunk_text: str
    distance: float
    similarity_score: float


@dataclass
class RetrievalResult:
    query: str
    query_id: int | None
    channel: str | None
    model_name: str
    limit: int
    document_id: int | None
    source_type: str | None
    chunks: list[RetrievedChunk]


def distance_to_similarity(distance: float) -> float:
    """
    Convierte distancia vectorial en similitud aproximada.

    En pgvector, cuando se usa el operador <=> con distancia coseno,
    una distancia menor indica mayor cercanía semántica.
    """
    similarity = 1.0 - float(distance)

    if similarity < 0:
        return 0.0

    if similarity > 1:
        return 1.0

    return similarity


def retrieve_chunks(
    query: str,
    limit: int = 5,
    document_id: int | None = None,
    source_type: str | None = None,
    trace: bool = False,
    channel: str | None = "terminal",
    model_name: str = "nomic-embed-text",
) -> RetrievalResult:
    """
    Ejecuta recuperación semántica sobre document_chunks.

    Si trace=True:
    - registra la consulta en rag_queries
    - registra los chunks recuperados en retrieval_logs

    Si trace=False:
    - solo recupera chunks, sin insertar trazabilidad.
    """
    if not query or not query.strip():
        raise ValueError("query no puede estar vacío.")

    if limit <= 0:
        raise ValueError("limit debe ser mayor que 0.")

    query = query.strip()

    query_embedding = generate_embedding(query)

    raw_results = search_similar_chunks(
        query_embedding=query_embedding,
        limit=limit,
        document_id=document_id,
        source_type=source_type,
    )

    query_id: int | None = None

    if trace:
        rag_query = insert_rag_query(
            question=query,
            answer=None,
            channel=channel,
            model_name=model_name,
        )
        query_id = rag_query.id

    retrieved_chunks: list[RetrievedChunk] = []

    for rank_position, result in enumerate(raw_results, start=1):
        distance = float(result["distance"])
        similarity_score = distance_to_similarity(distance)

        retrieved_chunk = RetrievedChunk(
            rank_position=rank_position,
            chunk_id=int(result["chunk_id"]),
            document_id=int(result["document_id"]),
            document_title=str(result["title"]),
            source_type=str(result["source_type"]),
            chunk_index=int(result["chunk_index"]),
            chunk_text=str(result["chunk_text"]),
            distance=distance,
            similarity_score=similarity_score,
        )

        retrieved_chunks.append(retrieved_chunk)

        if trace and query_id is not None:
            insert_retrieval_log(
                query_id=query_id,
                chunk_id=retrieved_chunk.chunk_id,
                similarity_score=retrieved_chunk.similarity_score,
                rank_position=retrieved_chunk.rank_position,
            )

    return RetrievalResult(
        query=query,
        query_id=query_id,
        channel=channel,
        model_name=model_name,
        limit=limit,
        document_id=document_id,
        source_type=source_type,
        chunks=retrieved_chunks,
    )


def retrieval_result_to_dict(result: RetrievalResult) -> dict[str, Any]:
    """
    Convierte el resultado de recuperación a diccionario simple.
    Útil para JSON, pruebas, API o integración posterior.
    """
    return {
        "query": result.query,
        "query_id": result.query_id,
        "channel": result.channel,
        "model_name": result.model_name,
        "limit": result.limit,
        "document_id": result.document_id,
        "source_type": result.source_type,
        "chunks": [
            {
                "rank_position": chunk.rank_position,
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "document_title": chunk.document_title,
                "source_type": chunk.source_type,
                "chunk_index": chunk.chunk_index,
                "chunk_text": chunk.chunk_text,
                "distance": chunk.distance,
                "similarity_score": chunk.similarity_score,
            }
            for chunk in result.chunks
        ],
    }


def get_trace(query_id: int) -> list[dict]:
    """
    Devuelve la trazabilidad registrada para una consulta específica.
    """
    if query_id <= 0:
        raise ValueError("query_id debe ser mayor que 0.")

    return get_query_retrieval_trace(query_id)
