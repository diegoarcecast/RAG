from __future__ import annotations

from dataclasses import dataclass

from app.retrieval_service import retrieve_chunks, RetrievedChunk
from app.generation.ollama_generation_client import generate_text
from app.rag_trace_repository import update_rag_query_answer


@dataclass
class RagAnswerResult:
    query_id: int | None
    question: str
    answer: str
    model_name: str
    chunks: list[RetrievedChunk]


def build_context(chunks: list[RetrievedChunk]) -> str:
    """
    Construye el contexto documental que se enviará al modelo generativo.
    """
    context_parts = []

    for chunk in chunks:
        context_parts.append(
            "\n".join(
                [
                    f"[Fuente {chunk.rank_position}]",
                    f"document_id: {chunk.document_id}",
                    f"document_title: {chunk.document_title}",
                    f"chunk_id: {chunk.chunk_id}",
                    f"similarity_score: {chunk.similarity_score:.4f}",
                    "contenido:",
                    chunk.chunk_text,
                ]
            )
        )

    return "\n\n".join(context_parts)


def build_prompt(question: str, context: str) -> str:
    """
    Construye el prompt RAG con reglas estrictas de respuesta basada en evidencia.
    """
    return f"""
Eres un asistente técnico para un sistema RAG académico.

Debes responder usando únicamente la evidencia documental incluida en el CONTEXTO.
No inventes información.
Si el contexto no contiene evidencia suficiente, responde: "No hay evidencia suficiente en los documentos recuperados."
Incluye una sección final llamada "Fuentes utilizadas" indicando document_title y chunk_id.
Responde en el mismo idioma de la pregunta.

PREGUNTA:
{question}

CONTEXTO:
{context}

RESPUESTA:
""".strip()


def generate_rag_answer(
    question: str,
    limit: int = 3,
    document_id: int | None = None,
    source_type: str | None = None,
    channel: str = "terminal",
    generation_model: str = "gemma4:e4b",
) -> RagAnswerResult:
    """
    Ejecuta flujo RAG completo:

    1. Recupera chunks relevantes.
    2. Registra trazabilidad.
    3. Genera respuesta con Ollama.
    4. Guarda la respuesta en rag_queries.answer.
    """
    retrieval_result = retrieve_chunks(
        query=question,
        limit=limit,
        document_id=document_id,
        source_type=source_type,
        trace=True,
        channel=channel,
        model_name=generation_model,
    )

    context = build_context(retrieval_result.chunks)
    prompt = build_prompt(question, context)

    answer = generate_text(
        prompt=prompt,
        model_name=generation_model,
        temperature=0.2,
    )

    if retrieval_result.query_id is not None:
        update_rag_query_answer(
            query_id=retrieval_result.query_id,
            answer=answer,
        )

    return RagAnswerResult(
        query_id=retrieval_result.query_id,
        question=question,
        answer=answer,
        model_name=generation_model,
        chunks=retrieval_result.chunks,
    )
