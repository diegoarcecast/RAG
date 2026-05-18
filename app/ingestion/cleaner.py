import re
import unicodedata


def normalize_unicode(text: str) -> str:
    """
    Normaliza caracteres Unicode para reducir inconsistencias.
    """
    if text is None:
        return ""

    return unicodedata.normalize("NFKC", text)


def remove_control_characters(text: str) -> str:
    """
    Elimina caracteres de control invisibles, excepto saltos de línea y tabulaciones.
    """
    return "".join(
        character
        for character in text
        if character == "\n" or character == "\t" or not unicodedata.category(character).startswith("C")
    )


def normalize_whitespace(text: str) -> str:
    """
    Normaliza espacios, tabulaciones y saltos de línea excesivos.
    """
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_text(text: str) -> str:
    """
    Aplica limpieza básica al texto extraído antes de dividirlo en chunks.
    """
    text = normalize_unicode(text)
    text = remove_control_characters(text)
    text = normalize_whitespace(text)

    return text


def has_sufficient_text(text: str, min_characters: int = 300) -> bool:
    """
    Determina si el texto extraído directamente es suficiente.
    Se usa para decidir si debe aplicarse OCR como respaldo.
    """
    cleaned_text = clean_text(text)
    useful_characters = re.sub(r"\s+", "", cleaned_text)

    return len(useful_characters) >= min_characters
