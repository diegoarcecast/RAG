from __future__ import annotations

from dataclasses import dataclass

from app.db import get_connection


@dataclass
class RagQueryRecord:
    id: int
    question: str
    answer: str | None
    channel: str | None
    model_name: str | None


def insert_rag_query(
    question: str,
    answer: str | None = None,
    channel: str | None = "terminal",
    model_name: str | None = "nomic-embed-text",
) -> RagQueryRecord:
    """
    Registra una consulta RAG en la tabla rag_queries.

    Por ahora answer queda en NULL porque todavía estamos en fase de recuperación,
    no en fase de generación de respuesta.
    """
    sql = """
        INSERT INTO rag_queries (
            question,
            answer,
            channel,
            model_name
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id, question, answer, channel, model_name;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    question,
                    answer,
                    channel,
                    model_name,
                ),
            )
            row = cur.fetchone()
            conn.commit()

    if row is None:
        raise RuntimeError("No se pudo registrar la consulta en rag_queries.")

    return RagQueryRecord(
        id=row[0],
        question=row[1],
        answer=row[2],
        channel=row[3],
        model_name=row[4],
    )


def insert_retrieval_log(
    query_id: int,
    chunk_id: int,
    similarity_score: float,
    rank_position: int,
) -> int:
    """
    Registra un chunk recuperado para una consulta específica.
    """
    sql = """
        INSERT INTO retrieval_logs (
            query_id,
            chunk_id,
            similarity_score,
            rank_position
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    query_id,
                    chunk_id,
                    similarity_score,
                    rank_position,
                ),
            )
            row = cur.fetchone()
            conn.commit()

    if row is None:
        raise RuntimeError("No se pudo registrar el resultado en retrieval_logs.")

    return int(row[0])


def get_query_retrieval_trace(query_id: int) -> list[dict]:
    """
    Recupera la trazabilidad documental asociada a una consulta.
    """
    sql = """
        SELECT
            rq.id AS query_id,
            rq.question,
            rq.answer,
            rq.channel,
            rq.model_name,
            rl.rank_position,
            rl.similarity_score,
            d.id AS document_id,
            d.title AS document_title,
            d.source_type,
            dc.id AS chunk_id,
            dc.chunk_index,
            dc.chunk_text
        FROM rag_queries rq
        INNER JOIN retrieval_logs rl
            ON rl.query_id = rq.id
        INNER JOIN document_chunks dc
            ON dc.id = rl.chunk_id
        INNER JOIN documents d
            ON d.id = dc.document_id
        WHERE rq.id = %s
        ORDER BY rl.rank_position ASC;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (query_id,))
            rows = cur.fetchall()

    return [
        {
            "query_id": row[0],
            "question": row[1],
            "answer": row[2],
            "channel": row[3],
            "model_name": row[4],
            "rank_position": row[5],
            "similarity_score": float(row[6]) if row[6] is not None else None,
            "document_id": row[7],
            "document_title": row[8],
            "source_type": row[9],
            "chunk_id": row[10],
            "chunk_index": row[11],
            "chunk_text": row[12],
        }
        for row in rows
    ]


def update_rag_query_answer(query_id: int, answer: str) -> None:
    """
    Actualiza la respuesta generada para una consulta RAG existente.
    """
    if query_id <= 0:
        raise ValueError("query_id debe ser mayor que 0.")

    if answer is None:
        raise ValueError("answer no puede ser None.")

    sql = """
        UPDATE rag_queries
        SET answer = %s
        WHERE id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (answer, query_id))
            conn.commit()

            if cur.rowcount == 0:
                raise RuntimeError(f"No existe rag_query con id={query_id}.")
