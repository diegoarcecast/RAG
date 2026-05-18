import argparse
import json
from pathlib import Path

from app.ingestion.pipeline import ingest_document_to_memory


def parse_arguments() -> argparse.Namespace:
    """
    Define y procesa los argumentos recibidos desde terminal.
    """

    parser = argparse.ArgumentParser(
        description="Ejecuta el pipeline de ingestión documental en memoria."
    )

    parser.add_argument(
        "file_path",
        help="Ruta del archivo que se desea procesar.",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1200,
        help="Tamaño máximo aproximado de cada chunk en caracteres. Valor por defecto: 1200.",
    )

    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Cantidad de caracteres repetidos entre chunks. Valor por defecto: 200.",
    )

    parser.add_argument(
        "--min-chunk-size",
        type=int,
        default=120,
        help="Tamaño mínimo permitido para chunks finales. Valor por defecto: 120.",
    )

    parser.add_argument(
        "--show-text",
        action="store_true",
        help="Muestra el texto completo extraído.",
    )

    parser.add_argument(
        "--show-chunks",
        action="store_true",
        help="Muestra el contenido de cada chunk generado.",
    )

    parser.add_argument(
        "--json-output",
        type=str,
        default=None,
        help="Ruta opcional para guardar el resultado completo en formato JSON.",
    )

    return parser.parse_args()


def main() -> None:
    """
    Punto de entrada del script.
    """

    args = parse_arguments()

    result = ingest_document_to_memory(
        file_path=args.file_path,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        min_chunk_size=args.min_chunk_size,
        verbose=True,
    )

    print()
    print("Resumen final")
    print("=" * 60)
    print("Éxito:", result.get("success"))

    if not result.get("success"):
        print("Etapa fallida:", result.get("failed_stage"))
        print("Tipo de error:", result.get("error_type"))
        print("Mensaje:", result.get("error_message"))
        print()
        print("Instrucciones:")
        for instruction in result.get("instructions", []):
            print("-", instruction)
        return

    document = result["document"]

    print("Archivo:", document["file_name"])
    print("Tipo documental:", document["document_type"])
    print("MIME:", document["mime_type"])
    print("Método de extracción:", document["extraction_method"])
    print("Caracteres extraídos:", document["character_count"])
    print("Chunks generados:", document["chunk_count"])

    if args.show_text:
        print()
        print("Texto extraído")
        print("=" * 60)
        print(result["text"])

    if args.show_chunks:
        print()
        print("Chunks")
        print("=" * 60)

        for chunk in result["chunks"]:
            print()
            print("-" * 60)
            print("Chunk:", chunk["chunk_index"])
            print("Rango:", chunk["start_character"], "-", chunk["end_character"])
            print("Tamaño:", chunk["metadata"]["chunk_size"])
            print("Contenido:")
            print(chunk["content"])

    if args.json_output:
        output_path = Path(args.json_output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as output_file:
            json.dump(result, output_file, ensure_ascii=False, indent=2)

        print()
        print("Resultado JSON guardado en:", output_path)


if __name__ == "__main__":
    main()
