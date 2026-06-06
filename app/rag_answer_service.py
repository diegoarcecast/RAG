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
                    f"source_type: {chunk.source_type}",
                    f"chunk_id: {chunk.chunk_id}",
                    f"chunk_index: {chunk.chunk_index}",
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
No agregues fuentes inventadas.
Responde en el mismo idioma de la pregunta.
Al final de tu respuesta puedes mencionar brevemente que la evidencia proviene de los documentos recuperados, pero no generes una tabla de evaluación. Esa tabla será generada automáticamente por el sistema.

PREGUNTA:
{question}

CONTEXTO:
{context}

RESPUESTA:
""".strip()


def clean_evidence_preview(text: str, max_length: int = 280) -> str:
    """
    Limpia el fragmento recuperado para que sea legible en la ficha de evaluación.
    """
    preview = " ".join(text.replace("\n", " ").split())

    if len(preview) > max_length:
        preview = preview[:max_length].rstrip() + "..."

    return preview


def classify_evidence_relevance(rank_position: int, similarity_score: float) -> str:
    """
    Clasificación simple para orientar la revisión manual.
    No reemplaza la evaluación humana.
    """
    if rank_position == 1 and similarity_score >= 0.70:
        return "evidencia directa probable"

    if similarity_score >= 0.60:
        return "evidencia relacionada"

    return "evidencia secundaria o débil"


def build_evaluation_block(
    query_id: int | None,
    question: str,
    chunks: list[RetrievedChunk],
    generation_model: str,
    limit: int,
    document_id: int | None,
    source_type: str | None,
) -> str:
    """
    Construye una ficha textual para evaluación manual en Excel.

    Esta sección no depende del modelo generativo. Se genera desde los datos reales
    de recuperación y trazabilidad.
    """
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
        "modelo_embeddings: nomic-embed-text",
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
    4. Agrega ficha de evaluación.
    5. Guarda la respuesta completa en rag_queries.answer.
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

    generated_answer = generate_text(
        prompt=prompt,
        model_name=generation_model,
        temperature=0.2,
    )

    evaluation_block = build_evaluation_block(
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
