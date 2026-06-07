from __future__ import annotations

import argparse
import json
import urllib.request
from typing import Any

from app.db import get_connection


MODEL_NAME = "bge-m3"
EMBEDDING_DIMENSIONS = 1024
OLLAMA_EMBEDDINGS_URL = "http://localhost:11434/api/embeddings"


def generate_bge_m3_embedding(text: str) -> list[float]:
    payload = {
        "model": MODEL_NAME,
        "prompt": text,
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_EMBEDDINGS_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        result: dict[str, Any] = json.loads(response.read().decode("utf-8"))

    embedding = result.get("embedding")

    if not isinstance(embedding, list):
        raise RuntimeError("Ollama no devolvió un embedding válido.")

    if len(embedding) != EMBEDDING_DIMENSIONS:
        raise RuntimeError(
            f"Dimensión inesperada para {MODEL_NAME}: "
            f"{len(embedding)}. Se esperaba {EMBEDDING_DIMENSIONS}."
        )

    return [float(value) for value in embedding]


def vector_to_pgvector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(str(value) for value in embedding) + "]"


def search_similar_chunks_bge_m3(
    query_embedding: list[float],
    limit: int = 5,
    document_id: int | None = None,
    source_type: str | None = None,
) -> list[dict[str, Any]]:
    sql = """
        SELECT
            eb.embedding <=> %s::vector AS distance,
            d.id AS document_id,
            d.title,
            d.source_type,
            dc.id AS chunk_id,
            dc.chunk_index,
            dc.chunk_text
        FROM chunk_embeddings_bge_m3 eb
        INNER JOIN document_chunks dc
            ON dc.id = eb.chunk_id
        INNER JOIN documents d
            ON d.id = dc.document_id
        WHERE eb.model_name = %s
          AND (%s::bigint IS NULL OR d.id = %s::bigint)
          AND (%s::text IS NULL OR d.source_type = %s::text)
        ORDER BY eb.embedding <=> %s::vector
        LIMIT %s;
    """

    embedding_literal = vector_to_pgvector_literal(query_embedding)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    embedding_literal,
                    MODEL_NAME,
                    document_id,
                    document_id,
                    source_type,
                    source_type,
                    embedding_literal,
                    limit,
                ),
            )
            rows = cur.fetchall()

    return [
        {
            "distance": float(row[0]),
            "document_id": int(row[1]),
            "title": str(row[2]),
            "source_type": str(row[3]),
            "chunk_id": int(row[4]),
            "chunk_index": int(row[5]),
            "chunk_text": str(row[6]),
        }
        for row in rows
    ]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Busca chunks similares usando embeddings experimentales bge-m3."
    )

    parser.add_argument(
        "query",
        help="Consulta en lenguaje natural.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Cantidad máxima de chunks similares a mostrar.",
    )

    parser.add_argument(
        "--document-id",
        type=int,
        default=None,
        help="Filtra la búsqueda por document_id.",
    )

    parser.add_argument(
        "--source-type",
        type=str,
        default=None,
        help="Filtra la búsqueda por tipo documental, por ejemplo: pdf, html, xlsx.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    if args.limit <= 0:
        raise ValueError("--limit debe ser mayor que 0.")

    query_embedding = generate_bge_m3_embedding(args.query)

    results = search_similar_chunks_bge_m3(
        query_embedding=query_embedding,
        limit=args.limit,
        document_id=args.document_id,
        source_type=args.source_type,
    )

    print("Modelo:", MODEL_NAME)
    print("Consulta:", args.query)
    print("Resultados:", len(results))
    print("=" * 80)

    for index, result in enumerate(results, start=1):
        similarity = 1.0 - result["distance"]

        print()
        print(f"Resultado {index}")
        print("-" * 80)
        print("distance:", result["distance"])
        print("similarity_score:", similarity)
        print("document_id:", result["document_id"])
        print("title:", result["title"])
        print("source_type:", result["source_type"])
        print("chunk_id:", result["chunk_id"])
        print("chunk_index:", result["chunk_index"])
        print()
        print(result["chunk_text"][:1200])


if __name__ == "__main__":
    main()
