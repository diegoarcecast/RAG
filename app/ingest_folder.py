import argparse
from pathlib import Path

from app.ingestion.detector import ensure_supported_file
from app.ingestion.pipeline import ingest_document_to_memory
from app.ingestion.repository import save_ingestion_result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta ingesta documental por carpeta."
    )

    parser.add_argument(
        "folder_path",
        help="Ruta de la carpeta que contiene documentos a procesar.",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1200,
        help="Tamaño máximo aproximado de cada chunk en caracteres.",
    )

    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Cantidad de caracteres repetidos entre chunks.",
    )

    parser.add_argument(
        "--min-chunk-size",
        type=int,
        default=120,
        help="Tamaño mínimo permitido para chunks finales.",
    )

    parser.add_argument(
        "--save-db",
        action="store_true",
        help="Guarda cada documento y sus chunks en PostgreSQL.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    folder = Path(args.folder_path).expanduser().resolve()

    if not folder.exists():
        raise FileNotFoundError(f"No existe la carpeta: {folder}")

    if not folder.is_dir():
        raise NotADirectoryError(f"La ruta no es una carpeta: {folder}")

    files = sorted(
    [
        path
        for path in folder.iterdir()
        if path.is_file() and not path.name.startswith(".")
    ]
)
    print("Carpeta:", folder)
    print("Archivos encontrados:", len(files))
    print("=" * 60)

    processed = 0
    failed = 0
    saved_count = 0

    for file_path in files:
        print()
        print("-" * 60)
        print("Procesando:", file_path.name)

        try:
            ensure_supported_file(file_path)

            result = ingest_document_to_memory(
                file_path=str(file_path),
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap,
                min_chunk_size=args.min_chunk_size,
                verbose=False,
            )

            if not result.get("success"):
                failed += 1
                print("Estado: ERROR")
                print("Etapa:", result.get("failed_stage"))
                print("Mensaje:", result.get("error_message"))
                continue

            processed += 1

            document = result["document"]

            print("Estado: OK")
            print("Tipo:", document["document_type"])
            print("Caracteres:", document["character_count"])
            print("Chunks:", document["chunk_count"])

            if args.save_db:
                saved = save_ingestion_result(result)
                saved_count += 1
                print("Guardado en BD: sí")
                print("document_id:", saved["document_id"])
                print("chunks_insertados:", saved["inserted_chunks"])

        except Exception as error:
            failed += 1
            print("Estado: ERROR")
            print("Tipo de error:", type(error).__name__)
            print("Mensaje:", str(error))

    print()
    print("=" * 60)
    print("Resumen de ingesta por carpeta")
    print("Procesados correctamente:", processed)
    print("Fallidos:", failed)
    print("Guardados en BD:", saved_count)


if __name__ == "__main__":
    main()
