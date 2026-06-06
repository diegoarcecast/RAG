import argparse

from app.embeddings.ollama_client import generate_embedding
from app.embeddings.search_repository import search_similar_chunks
from app.rag_trace_repository import (
    insert_rag_query,
    insert_retrieval_log,
    get_query_retrieval_trace,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Busca chunks similares y registra trazabilidad en rag_queries y retrieval_logs."
    )

    parser.add_argument(
        "query",
        help="Consulta en lenguaje natural.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Cantidad máxima de chunks similares a recuperar.",
    )

    parser.add_argument(
        "--channel",
        type=str,
        default="terminal",
        help="Canal desde donde se realiza la consulta.",
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


def distance_to_similarity(distance: float) -> float:
    """
    Convierte distancia vectorial en similitud aproximada.

    Con distancia coseno de pgvector, mientras menor sea la distancia,
    mayor es la similitud. Esta conversión deja un valor más interpretable.
    """
    similarity = 1.0 - float(distance)

    if similarity < 0:
        return 0.0

    if similarity > 1:
        return 1.0

    return similarity


def main() -> None:
    args = parse_arguments()

    if args.limit <= 0:
        raise ValueError("--limit debe ser mayor que 0.")

    query_embedding = generate_embedding(args.query)
    results = search_similar_chunks(
        query_embedding,
        limit=args.limit,
        document_id=args.document_id,
        source_type=args.source_type,
    )

    rag_query = insert_rag_query(
        question=args.query,
        answer=None,
        channel=args.channel,
        model_name="nomic-embed-text",
    )

    for rank_position, result in enumerate(results, start=1):
        similarity_score = distance_to_similarity(result["distance"])

        insert_retrieval_log(
            query_id=rag_query.id,
            chunk_id=int(result["chunk_id"]),
            similarity_score=similarity_score,
            rank_position=rank_position,
        )

    trace = get_query_retrieval_trace(rag_query.id)

    print("Consulta registrada con trazabilidad")
    print("=" * 80)
    print("query_id:", rag_query.id)
    print("consulta:", rag_query.question)
    print("resultados:", len(trace))

    for item in trace:
        print()
        print(f"Resultado {item['rank_position']}")
        print("-" * 80)
        print("similarity_score:", item["similarity_score"])
        print("document_id:", item["document_id"])
        print("document_title:", item["document_title"])
        print("source_type:", item["source_type"])
        print("chunk_id:", item["chunk_id"])
        print("chunk_index:", item["chunk_index"])
        print()
        print(item["chunk_text"][:1200])


if __name__ == "__main__":
    main()
