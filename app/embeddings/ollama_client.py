import json
import urllib.request
from typing import Any


DEFAULT_OLLAMA_URL = "http://localhost:11434/api/embeddings"
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
EXPECTED_EMBEDDING_DIMENSIONS = 768


def generate_embedding(
    text: str,
    model: str = DEFAULT_EMBEDDING_MODEL,
    url: str = DEFAULT_OLLAMA_URL,
) -> list[float]:
    """
    Genera un embedding usando Ollama local.
    """

    if text is None:
        text = ""

    text = text.strip()

    if not text:
        raise ValueError("No se puede generar embedding para texto vacío.")

    payload: dict[str, Any] = {
        "model": model,
        "prompt": text,
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode("utf-8"))

    embedding = data.get("embedding")

    if not embedding:
        raise ValueError("Ollama no devolvió un embedding válido.")

    if len(embedding) != EXPECTED_EMBEDDING_DIMENSIONS:
        raise ValueError(
            f"Dimensión inválida del embedding. "
            f"Esperado: {EXPECTED_EMBEDDING_DIMENSIONS}, recibido: {len(embedding)}"
        )

    return embedding
