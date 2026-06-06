from __future__ import annotations

from dataclasses import dataclass

from app.rag_answer_service import generate_rag_answer


@dataclass
class OpenClawRagResponse:
    query_id: int | None
    channel: str
    answer: str


def answer_from_openclaw(
    question: str,
    limit: int = 3,
    document_id: int | None = None,
    source_type: str | None = None,
    channel: str = "discord-openclaw",
    model: str = "gemma4:e4b",
) -> OpenClawRagResponse:
    """
    Adaptador para que OpenClaw o Discord consulten el sistema RAG.

    Esta función no implementa Discord directamente.
    Su responsabilidad es recibir una pregunta desde una capa externa,
    ejecutar el flujo RAG formal y devolver la respuesta lista para enviar
    al canal conversacional.
    """
    if not question or not question.strip():
        raise ValueError("La pregunta no puede estar vacía.")

    if limit <= 0:
        raise ValueError("limit debe ser mayor que 0.")

    result = generate_rag_answer(
        question=question.strip(),
        limit=limit,
        document_id=document_id,
        source_type=source_type,
        channel=channel,
        generation_model=model,
    )

    return OpenClawRagResponse(
        query_id=result.query_id,
        channel=channel,
        answer=result.answer,
    )
