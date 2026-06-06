from app.db import get_connection


def search_similar_chunks(
    query_embedding: list[float],
    limit: int = 5,
    document_id: int | None = None,
    source_type: str | None = None,
) -> list[dict]:
    if not query_embedding:
        raise ValueError("query_embedding no puede estar vacío.")

    if limit <= 0:
        raise ValueError("limit debe ser mayor que 0.")

    embedding_as_text = "[" + ",".join(str(value) for value in query_embedding) + "]"

    filters = ["c.embedding IS NOT NULL"]
    params: list = [embedding_as_text]

    if document_id is not None:
        filters.append("c.document_id = %s")
        params.append(document_id)

    if source_type is not None:
        filters.append("d.source_type = %s")
        params.append(source_type)

    where_clause = " AND ".join(filters)

    query = f"""
        SELECT
            c.id AS chunk_id,
            c.document_id,
            d.title,
            d.source_type,
            c.chunk_index,
            c.chunk_text,
            c.embedding <=> %s::vector AS distance
        FROM document_chunks c
        INNER JOIN documents d ON d.id = c.document_id
        WHERE {where_clause}
        ORDER BY c.embedding <=> %s::vector
        LIMIT %s;
    """

    params.append(embedding_as_text)
    params.append(limit)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

    return [
        {
            "chunk_id": row[0],
            "document_id": row[1],
            "title": row[2],
            "source_type": row[3],
            "chunk_index": row[4],
            "chunk_text": row[5],
            "distance": float(row[6]),
        }
        for row in rows
    ]
