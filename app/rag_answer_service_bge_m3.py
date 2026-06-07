from __future__ import annotations

from dataclasses import dataclass

from app.retrieval_service_bge_m3 import retrieve_chunks_bge_m3, RetrievedChunk
from app.generation.ollama_generation_client import generate_text
from app.rag_trace_repository import update_rag_query_answer
from app.rag_answer_service import (
    build_context,
    build_prompt,
    clean_evidence_preview,
    classify_evidence_relevance,
)


EMBEDDING_MODEL_NAME = "bge-m3"


@dataclass
class RagAnswerResult:
    query_id: int | None
    question: str
    answer: str
    model_name: str
    chunks: list[RetrievedChunk]


def build_evaluation_block_bge_m3(
    query_id: int | None,
    question: str,
    chunks: list[RetrievedChunk],
    generation_model: str,
    limit: int,
    document_id: int | None,
    source_type: str | None,
) -> str:
    document_filter = str(document_id) if document_id is not None else "sin filtro"
    source_filter = str(source_type) if source_type is not None else "sin filtro"

    lines = [
        "",
        "---",
        "",
        "Ficha para evaluación",
        "",
        f"query_id: {query_id}",
        f"pregunta: {question}",
        f"modelo_generacion: {generation_model}",
        f"modelo_embeddings: {EMBEDDING_MODEL_NAME}",
        f"limite_recuperacion: {limit}",
        f"filtro_document_id: {document_filter}",
        f"filtro_source_type: {source_filter}",
        f"cantidad_chunks_recuperados: {len(chunks)}",
        "",
        "Evidencia recuperada:",
    ]

    for chunk in chunks:
        evidence_preview = clean_evidence_preview(chunk.chunk_text)
        relevance_hint = classify_evidence_relevance(
            rank_position=chunk.rank_position,
            similarity_score=chunk.similarity_score,
        )

        lines.extend(
            [
                "",
                f"{chunk.rank_position}) rank_position: {chunk.rank_position}",
                f"document_title: {chunk.document_title}",
                f"document_id: {chunk.document_id}",
                f"source_type: {chunk.source_type}",
                f"chunk_id: {chunk.chunk_id}",
                f"chunk_index: {chunk.chunk_index}",
                f"similarity_score: {chunk.similarity_score:.4f}",
                f"distance: {chunk.distance:.4f}",
                f"clasificacion_preliminar: {relevance_hint}",
                f"evidencia: {evidence_preview}",
            ]
        )

    return "\n".join(lines)


def generate_rag_answer_bge_m3(
    question: str,
    limit: int = 3,
    document_id: int | None = None,
    source_type: str | None = None,
    channel: str = "terminal",
    generation_model: str = "gemma4:e4b",
) -> RagAnswerResult:
    """
    Ejecuta flujo RAG completo usando recuperación multilingüe BGE-M3.

    1. Recupera chunks con bge-m3.
    2. Registra trazabilidad.
    3. Genera respuesta con Ollama.
    4. Agrega ficha de evaluación.
    5. Guarda la respuesta completa en rag_queries.answer.
    """
    retrieval_result = retrieve_chunks_bge_m3(
        query=question,
        limit=limit,
        document_id=document_id,
        source_type=source_type,
        trace=True,
        channel=channel,
        model_name=EMBEDDING_MODEL_NAME,
    )

    context = build_context(retrieval_result.chunks)
    prompt = build_prompt(question, context)

    generated_answer = generate_text(
        prompt=prompt,
        model_name=generation_model,
        temperature=0.2,
    )

    evaluation_block = build_evaluation_block_bge_m3(
        query_id=retrieval_result.query_id,
        question=question,
        chunks=retrieval_result.chunks,
        generation_model=generation_model,
        limit=limit,
        document_id=document_id,
        source_type=source_type,
    )

    final_answer = generated_answer.strip() + "\n" + evaluation_block

    if retrieval_result.query_id is not None:
        update_rag_query_answer(
            query_id=retrieval_result.query_id,
            answer=final_answer,
        )

    return RagAnswerResult(
        query_id=retrieval_result.query_id,
        question=question,
        answer=final_answer,
        model_name=generation_model,
        chunks=retrieval_result.chunks,
    )
