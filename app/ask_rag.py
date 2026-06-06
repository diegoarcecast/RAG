from __future__ import annotations

import argparse

from app.rag_answer_service import generate_rag_answer


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta una pregunta contra el sistema RAG y muestra la respuesta con ficha de evaluación."
    )

    parser.add_argument(
        "question",
        help="Pregunta o consulta que se enviará al sistema RAG.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Cantidad máxima de chunks a recuperar. Valor por defecto: 3.",
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

    parser.add_argument(
        "--channel",
        type=str,
        default="terminal",
        help="Canal desde donde se realiza la consulta. Valor por defecto: terminal.",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="gemma4:e4b",
        help="Modelo generativo a utilizar. Valor por defecto: gemma4:e4b.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    if args.limit <= 0:
        raise ValueError("--limit debe ser mayor que 0.")

    result = generate_rag_answer(
        question=args.question,
        limit=args.limit,
        document_id=args.document_id,
        source_type=args.source_type,
        channel=args.channel,
        generation_model=args.model,
    )

    print(result.answer)


if __name__ == "__main__":
    main()
