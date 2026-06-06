from __future__ import annotations

import json
import urllib.request
import urllib.error


OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
DEFAULT_GENERATION_MODEL = "gemma4:e4b"


def generate_text(
    prompt: str,
    model_name: str = DEFAULT_GENERATION_MODEL,
    temperature: float = 0.2,
) -> str:
    """
    Genera texto usando un modelo local de Ollama.

    Usa /api/generate con stream=False para recibir una respuesta completa.
    """
    if not prompt or not prompt.strip():
        raise ValueError("prompt no puede estar vacío.")

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }

    request = urllib.request.Request(
        OLLAMA_GENERATE_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.URLError as error:
        raise RuntimeError(f"No se pudo conectar con Ollama: {error}") from error

    data = json.loads(response_body)

    generated_response = data.get("response")

    if not generated_response:
        raise RuntimeError("Ollama no devolvió contenido en el campo 'response'.")

    return generated_response.strip()
