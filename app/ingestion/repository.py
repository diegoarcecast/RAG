import json
from typing import Any

from app.db import get_connection


def insert_document(document: dict[str, Any]) -> int:
    """
    Inserta un registro en la tabla documents y retorna el ID generado.
    """
    title = document.get("file_name") or "Documento sin título"
    source_type = document.get("document_type") or "unknown"
    file_path = document.get("file_path")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO documents (
                    title,
                    source_type,
                    file_path
                )
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (
                    title,
                    source_type,
                    file_path,
                ),
            )

            document_id = cur.fetchone()[0]
            conn.commit()
            return document_id


def insert_document_chunks(document_id: int, chunks: list[dict[str, Any]]) -> int:
    """
    Inserta los chunks asociados a un documento.
    Retorna la cantidad de chunks insertados.
    """
    if not chunks:
        return 0

    rows = []

    for chunk in chunks:
        metadata = chunk.get("metadata") or {}

        rows.append(
            (
                document_id,
                chunk.get("chunk_index"),
                chunk.get("content"),
                metadata.get("page_number"),
                metadata.get("section_title"),
                json.dumps(metadata, ensure_ascii=False),
            )
        )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO document_chunks (
                    document_id,
                    chunk_index,
                    chunk_text,
                    page_number,
                    section_title,
                    metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s::jsonb);
                """,
                rows,
            )

            conn.commit()
            return len(rows)


def save_ingestion_result(ingestion_result: dict[str, Any]) -> dict[str, Any]:
    """
    Guarda en PostgreSQL el resultado generado por el pipeline de ingesta.
    """
    if not ingestion_result.get("success"):
        raise ValueError("No se puede guardar una ingesta fallida.")

    document = ingestion_result.get("document") or {}
    chunks = ingestion_result.get("chunks") or []

    document_id = insert_document(document)
    inserted_chunks = insert_document_chunks(document_id, chunks)

    return {
        "document_id": document_id,
        "inserted_chunks": inserted_chunks,
    }


def delete_document_by_file_path(file_path: str) -> int:
    """
    Elimina documentos por file_path.
    Por ON DELETE CASCADE, también elimina sus chunks asociados.
    Retorna la cantidad de documentos eliminados.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM documents
                WHERE file_path = %s;
                """,
                (file_path,),
            )

            deleted_count = cur.rowcount
            conn.commit()
            return deleted_count
