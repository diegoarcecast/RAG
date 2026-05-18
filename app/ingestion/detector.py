from pathlib import Path
import mimetypes
import magic


SUPPORTED_EXTENSIONS = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".txt": "txt",
    ".md": "markdown",
    ".markdown": "markdown",
    ".html": "html",
    ".htm": "html",
    ".csv": "csv",
    ".xlsx": "xlsx",
}


def detect_file_type(file_path: str | Path) -> dict:
    """
    Detecta el tipo de archivo usando extensión, mimetype estándar
    y libmagic como respaldo.

    Retorna un diccionario con:
    - path
    - file_name
    - extension
    - document_type
    - mime_type
    - is_supported
    """

    path = Path(file_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")

    if not path.is_file():
        raise ValueError(f"La ruta no corresponde a un archivo: {path}")

    extension = path.suffix.lower()
    document_type = SUPPORTED_EXTENSIONS.get(extension)

    mime_type, _ = mimetypes.guess_type(str(path))

    if mime_type is None:
        try:
            mime_type = magic.from_file(str(path), mime=True)
        except Exception:
            mime_type = "application/octet-stream"

    return {
        "path": str(path),
        "file_name": path.name,
        "extension": extension,
        "document_type": document_type,
        "mime_type": mime_type,
        "is_supported": document_type is not None,
    }


def ensure_supported_file(file_path: str | Path) -> dict:
    """
    Valida que el archivo exista y que su extensión esté soportada.
    """

    file_info = detect_file_type(file_path)

    if not file_info["is_supported"]:
        raise ValueError(
            f"Tipo de archivo no soportado: {file_info['extension']} "
            f"({file_info['mime_type']})"
        )

    return file_info
