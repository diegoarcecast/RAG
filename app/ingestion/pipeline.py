from pathlib import Path
from datetime import datetime, timezone
import traceback

from app.ingestion.detector import ensure_supported_file
from app.ingestion.extractors import extract_text
from app.ingestion.chunker import split_text_into_chunks, chunks_to_dicts


DEFAULT_CHUNK_SIZE = 1200
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_MIN_CHUNK_SIZE = 120


def build_pipeline_error(stage: str, error: Exception) -> dict:
    """
    Construye una respuesta estructurada cuando falla alguna etapa del pipeline.
    Esto permite documentar claramente en qué punto falló la ingesta.
    """

    return {
        "success": False,
        "failed_stage": stage,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "instructions": [
            "Verifique que el archivo exista y que la ruta sea correcta.",
            "Verifique que la extensión del archivo esté soportada por el pipeline.",
            "Si el error ocurre en extracción PDF/OCR, confirme que poppler-utils y tesseract estén instalados.",
            "Si el error ocurre en DOCX/XLSX, confirme que el archivo no esté corrupto o protegido.",
            "Revise el traceback técnico si necesita depurar el fallo exacto.",
        ],
        "traceback": traceback.format_exc(),
    }


def ingest_document_to_memory(
    file_path: str | Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    min_chunk_size: int = DEFAULT_MIN_CHUNK_SIZE,
    verbose: bool = True,
) -> dict:
    """
    Ejecuta el pipeline de ingestión documental en memoria.

    Etapas:
    1. Detectar y validar tipo de archivo.
    2. Extraer texto según el tipo documental.
    3. Registrar método de extracción: direct u ocr.
    4. Preparar metadata base del documento.
    5. Dividir texto en chunks.
    6. Retornar resultado estructurado.

    Esta función todavía NO inserta en base de datos.
    """

    started_at = datetime.now(timezone.utc).isoformat()

    try:
        if verbose:
            print("[1/5] Detectando tipo de archivo...")

        file_info = ensure_supported_file(file_path)

        if verbose:
            print(f"      Archivo: {file_info['file_name']}")
            print(f"      Tipo documental: {file_info['document_type']}")
            print(f"      MIME: {file_info['mime_type']}")

    except Exception as error:
        return build_pipeline_error("file_detection", error)

    try:
        if verbose:
            print("[2/5] Extrayendo texto del documento...")

        extraction_result = extract_text(
            file_info["path"],
            file_info["document_type"],
        )

        extracted_text = extraction_result["text"]
        extraction_method = extraction_result["extraction_method"]

        if verbose:
            print(f"      Método de extracción: {extraction_method}")
            print(f"      Caracteres extraídos: {len(extracted_text)}")

    except Exception as error:
        return build_pipeline_error("text_extraction", error)

    try:
        if verbose:
            print("[3/5] Construyendo metadata base...")

        document_metadata = {
            "source_path": file_info["path"],
            "source_file": file_info["file_name"],
            "extension": file_info["extension"],
            "document_type": file_info["document_type"],
            "mime_type": file_info["mime_type"],
            "extraction_method": extraction_method,
            "ingested_at": started_at,
        }

        if verbose:
            print("      Metadata base creada.")

    except Exception as error:
        return build_pipeline_error("metadata_building", error)

    try:
        if verbose:
            print("[4/5] Dividiendo texto en chunks...")

        chunks = split_text_into_chunks(
            extracted_text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            min_chunk_size=min_chunk_size,
            base_metadata=document_metadata,
        )

        chunk_dicts = chunks_to_dicts(chunks)

        if verbose:
            print(f"      Chunks generados: {len(chunk_dicts)}")
            print(f"      chunk_size: {chunk_size}")
            print(f"      chunk_overlap: {chunk_overlap}")
            print(f"      min_chunk_size: {min_chunk_size}")

    except Exception as error:
        return build_pipeline_error("chunking", error)

    try:
        if verbose:
            print("[5/5] Construyendo resultado final...")

        completed_at = datetime.now(timezone.utc).isoformat()

        result = {
            "success": True,
            "started_at": started_at,
            "completed_at": completed_at,
            "document": {
                "file_path": file_info["path"],
                "file_name": file_info["file_name"],
                "extension": file_info["extension"],
                "document_type": file_info["document_type"],
                "mime_type": file_info["mime_type"],
                "extraction_method": extraction_method,
                "character_count": len(extracted_text),
                "chunk_count": len(chunk_dicts),
                "metadata": document_metadata,
            },
            "text": extracted_text,
            "pages": extraction_result.get("pages", []),
            "chunks": chunk_dicts,
            "next_steps": [
                "Validar visualmente que los chunks contienen texto útil.",
                "Insertar documents y document_chunks en PostgreSQL.",
                "Generar embeddings después de confirmar que la ingesta textual es correcta.",
            ],
        }

        if verbose:
            print("      Pipeline finalizado correctamente.")

        return result

    except Exception as error:
        return build_pipeline_error("result_building", error)
