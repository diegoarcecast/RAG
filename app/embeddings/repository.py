from app.db import get_connection


def get_chunks_without_embeddings(limit: int = 10) -> list[dict]:
    """
    Obtiene chunks que todavía no tienen embedding.
    """

    if limit <= 0:
        raise ValueError("limit debe ser mayor que 0.")

    query = """
        SELECT
            id,
            document_id,
            chunk_index,
            chunk_text
        FROM document_chunks
        WHERE embedding IS NULL
        ORDER BY id
        LIMIT %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "document_id": row[1],
            "chunk_index": row[2],
            "chunk_text": row[3],
        }
        for row in rows
    ]


def update_chunk_embedding(chunk_id: int, embedding: list[float]) -> None:
    """
    Actualiza el embedding de un chunk.
    """

    if chunk_id <= 0:
        raise ValueError("chunk_id debe ser mayor que 0.")

    if not embedding:
        raise ValueError("embedding no puede estar vacío.")

    embedding_as_text = "[" + ",".join(str(value) for value in embedding) + "]"

    query = """
        UPDATE document_chunks
        SET embedding = %s::vector
        WHERE id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (embedding_as_text, chunk_id))
        conn.commit()


def count_chunks_without_embeddings() -> int:
    """
    Cuenta chunks pendientes de embedding.
    """

    query = """
        SELECT COUNT(*)
        FROM document_chunks
        WHERE embedding IS NULL;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            count = cur.fetchone()[0]

    return count


def count_chunks_with_embeddings() -> int:
    """
    Cuenta chunks que ya tienen embedding.
    """

    query = """
        SELECT COUNT(*)
        FROM document_chunks
        WHERE embedding IS NOT NULL;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            count = cur.fetchone()[0]

    return count
