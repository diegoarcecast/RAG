from dataclasses import dataclass


@dataclass
class TextChunk:
    chunk_index: int
    content: str
    start_character: int
    end_character: int
    metadata: dict


def split_text_into_chunks(
    text: str,
    chunk_size: int = 1200,
    chunk_overlap: int = 200,
    min_chunk_size: int = 80,
    base_metadata: dict | None = None,
) -> list[TextChunk]:
    """
    Divide un texto en chunks con solapamiento.

    chunk_size define el tamaño máximo aproximado del fragmento.
    chunk_overlap define cuántos caracteres se repiten entre chunks.
    min_chunk_size evita guardar fragmentos finales demasiado pequeños.
    base_metadata permite heredar metadata del documento original.
    """

    if text is None:
        text = ""

    text = text.strip()

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size debe ser mayor que 0.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap no puede ser negativo.")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap debe ser menor que chunk_size.")

    if min_chunk_size < 0:
        raise ValueError("min_chunk_size no puede ser negativo.")

    base_metadata = base_metadata or {}

    chunks: list[TextChunk] = []
    start = 0
    chunk_index = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)

        if end < text_length:
            paragraph_break = text.rfind("\n\n", start, end)
            sentence_break = text.rfind(". ", start, end)

            if paragraph_break > start + int(chunk_size * 0.5):
                end = paragraph_break
            elif sentence_break > start + int(chunk_size * 0.5):
                end = sentence_break + 1

        content = text[start:end].strip()

        is_last_chunk = end >= text_length
        is_too_small = len(content) < min_chunk_size

        if content and not (chunks and is_last_chunk and is_too_small):
            metadata = {
                **base_metadata,
                "chunk_index": chunk_index,
                "start_character": start,
                "end_character": end,
                "chunk_size": len(content),
            }

            chunks.append(
                TextChunk(
                    chunk_index=chunk_index,
                    content=content,
                    start_character=start,
                    end_character=end,
                    metadata=metadata,
                )
            )

            chunk_index += 1

        next_start = end - chunk_overlap

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


def chunks_to_dicts(chunks: list[TextChunk]) -> list[dict]:
    """
    Convierte chunks a diccionarios simples para inserción o serialización.
    """

    return [
        {
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "start_character": chunk.start_character,
            "end_character": chunk.end_character,
            "metadata": chunk.metadata,
        }
        for chunk in chunks
    ]
