import argparse

from app.embeddings.ollama_client import generate_embedding
from app.embeddings.search_repository import search_similar_chunks


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Busca chunks similares usando embeddings y pgvector."
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

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    query_embedding = generate_embedding(args.query)
    results = search_similar_chunks(query_embedding, limit=args.limit)

    print("Consulta:", args.query)
    print("Resultados:", len(results))
    print("=" * 80)

    for index, result in enumerate(results, start=1):
        print()
        print(f"Resultado {index}")
        print("-" * 80)
        print("distance:", result["distance"])
        print("document_id:", result["document_id"])
        print("title:", result["title"])
        print("source_type:", result["source_type"])
        print("chunk_id:", result["chunk_id"])
        print("chunk_index:", result["chunk_index"])
        print()
        print(result["chunk_text"][:1200])


if __name__ == "__main__":
    main()
