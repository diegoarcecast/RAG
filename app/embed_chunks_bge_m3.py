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
    """
    Genera embedding usando bge-m3 mediante Ollama.
    Usa urllib para evitar agregar dependencias externas.
    """
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
    """
    Convierte una lista Python en literal aceptado por pgvector.
    Ejemplo: [0.1, 0.2, -0.3]
    """
    return "[" + ",".join(str(value) for value in embedding) + "]"


def fetch_pending_chunks(limit: int) -> list[dict[str, Any]]:
    """
    Obtiene chunks que todavía no tienen embedding bge-m3.
    """
    sql = """
        SELECT
            dc.id,
            dc.chunk_text
        FROM document_chunks dc
        LEFT JOIN chunk_embeddings_bge_m3 eb
            ON eb.chunk_id = dc.id
            AND eb.model_name = %s
        WHERE eb.id IS NULL
        ORDER BY dc.id ASC
        LIMIT %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (MODEL_NAME, limit))
            rows = cur.fetchall()

    return [
        {
            "chunk_id": int(row[0]),
            "chunk_text": str(row[1]),
        }
        for row in rows
    ]


def insert_embedding(chunk_id: int, embedding: list[float]) -> None:
    """
    Inserta o actualiza el embedding bge-m3 de un chunk.
    """
    sql = """
        INSERT INTO chunk_embeddings_bge_m3 (
            chunk_id,
            model_name,
            dimensions,
            embedding
        )
        VALUES (%s, %s, %s, %s::vector)
        ON CONFLICT (chunk_id, model_name)
        DO UPDATE SET
            dimensions = EXCLUDED.dimensions,
            embedding = EXCLUDED.embedding,
            created_at = NOW();
    """

    embedding_literal = vector_to_pgvector_literal(embedding)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    chunk_id,
                    MODEL_NAME,
                    EMBEDDING_DIMENSIONS,
                    embedding_literal,
                ),
            )
            conn.commit()


def count_pending_chunks() -> int:
    """
    Cuenta chunks pendientes de embedding bge-m3.
    """
    sql = """
        SELECT COUNT(*)
        FROM document_chunks dc
        LEFT JOIN chunk_embeddings_bge_m3 eb
            ON eb.chunk_id = dc.id
            AND eb.model_name = %s
        WHERE eb.id IS NULL;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (MODEL_NAME,))
            row = cur.fetchone()

    return int(row[0])


def count_completed_embeddings() -> int:
    """
    Cuenta embeddings bge-m3 generados.
    """
    sql = """
        SELECT COUNT(*)
        FROM chunk_embeddings_bge_m3
        WHERE model_name = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (MODEL_NAME,))
            row = cur.fetchone()

    return int(row[0])


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera embeddings multilingües bge-m3 para chunks pendientes."
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Cantidad máxima de chunks a procesar en esta ejecución.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    if args.limit <= 0:
        raise ValueError("--limit debe ser mayor que 0.")

    pending_before = count_pending_chunks()
    completed_before = count_completed_embeddings()

    print("Modelo:", MODEL_NAME)
    print("Dimensiones:", EMBEDDING_DIMENSIONS)
    print("Embeddings existentes antes:", completed_before)
    print("Chunks pendientes antes:", pending_before)
    print("=" * 80)

    chunks = fetch_pending_chunks(limit=args.limit)

    if not chunks:
        print("No hay chunks pendientes para bge-m3.")
        return

    for index, chunk in enumerate(chunks, start=1):
        chunk_id = chunk["chunk_id"]
        chunk_text = chunk["chunk_text"]

        print(f"[{index}/{len(chunks)}] Generando embedding para chunk_id={chunk_id}")

        embedding = generate_bge_m3_embedding(chunk_text)
        insert_embedding(chunk_id=chunk_id, embedding=embedding)

        print(f"OK chunk_id={chunk_id}")

    pending_after = count_pending_chunks()
    completed_after = count_completed_embeddings()

    print("=" * 80)
    print("Embeddings existentes después:", completed_after)
    print("Chunks pendientes después:", pending_after)


if __name__ == "__main__":
    main()
