import argparse
import time

from app.embeddings.ollama_client import generate_embedding
from app.embeddings.repository import (
    count_chunks_without_embeddings,
    count_chunks_with_embeddings,
    get_chunks_without_embeddings,
    update_chunk_embedding,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera embeddings para chunks pendientes usando Ollama."
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Cantidad máxima de chunks a procesar en esta ejecución.",
    )

    parser.add_argument(
        "--sleep",
        type=float,
        default=0.0,
        help="Pausa opcional en segundos entre chunks.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    if args.limit <= 0:
        raise ValueError("--limit debe ser mayor que 0.")

    pending_before = count_chunks_without_embeddings()
    processed_before = count_chunks_with_embeddings()

    print("Estado inicial")
    print("=" * 60)
    print("Chunks sin embedding:", pending_before)
    print("Chunks con embedding:", processed_before)
    print("Límite de esta ejecución:", args.limit)

    chunks = get_chunks_without_embeddings(limit=args.limit)

    if not chunks:
        print()
        print("No hay chunks pendientes de embedding.")
        return

    generated = 0
    failed = 0

    print()
    print("Generando embeddings")
    print("=" * 60)

    for chunk in chunks:
        chunk_id = chunk["id"]
        text = chunk["chunk_text"]

        try:
            print(f"Procesando chunk_id={chunk_id} document_id={chunk['document_id']} chunk_index={chunk['chunk_index']}")

            embedding = generate_embedding(text)
            update_chunk_embedding(chunk_id, embedding)

            generated += 1
            print("Estado: OK")

            if args.sleep > 0:
                time.sleep(args.sleep)

        except Exception as error:
            failed += 1
            print("Estado: ERROR")
            print("Tipo:", type(error).__name__)
            print("Mensaje:", str(error))

    pending_after = count_chunks_without_embeddings()
    processed_after = count_chunks_with_embeddings()

    print()
    print("Resumen")
    print("=" * 60)
    print("Embeddings generados:", generated)
    print("Fallidos:", failed)
    print("Chunks sin embedding antes:", pending_before)
    print("Chunks sin embedding después:", pending_after)
    print("Chunks con embedding antes:", processed_before)
    print("Chunks con embedding después:", processed_after)


if __name__ == "__main__":
    main()
