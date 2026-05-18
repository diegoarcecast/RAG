from pathlib import Path
import csv
import fitz
import pandas as pd
import pytesseract
from bs4 import BeautifulSoup
from docx import Document
from pdf2image import convert_from_path

from app.ingestion.cleaner import clean_text, has_sufficient_text


OCR_LANGUAGES = "spa+eng"
MIN_DIRECT_TEXT_CHARACTERS = 300


def extract_text_from_pdf_direct(file_path: str | Path) -> dict:
    """
    Extrae texto directo desde un PDF usando PyMuPDF.
    """
    path = Path(file_path)
    pages = []

    with fitz.open(path) as document:
        for page_index, page in enumerate(document):
            page_text = page.get_text("text")

            if page_text:
                pages.append(
                    {
                        "page_number": page_index + 1,
                        "text": page_text,
                    }
                )

    full_text = "\n\n".join(page["text"] for page in pages)
    full_text = clean_text(full_text)

    return {
        "text": full_text,
        "pages": pages,
        "extraction_method": "direct",
    }


def extract_text_from_pdf_ocr(file_path: str | Path, dpi: int = 300) -> dict:
    """
    Extrae texto desde un PDF usando OCR.
    Convierte cada página a imagen y luego aplica Tesseract.
    """
    path = Path(file_path)
    images = convert_from_path(str(path), dpi=dpi)

    pages = []

    for page_index, image in enumerate(images):
        page_text = pytesseract.image_to_string(image, lang=OCR_LANGUAGES)

        pages.append(
            {
                "page_number": page_index + 1,
                "text": page_text,
            }
        )

    full_text = "\n\n".join(page["text"] for page in pages)
    full_text = clean_text(full_text)

    return {
        "text": full_text,
        "pages": pages,
        "extraction_method": "ocr",
    }


def extract_text_from_pdf(file_path: str | Path) -> dict:
    """
    Intenta extracción directa desde PDF.
    Si el texto es insuficiente, aplica OCR.
    """
    direct_result = extract_text_from_pdf_direct(file_path)

    if has_sufficient_text(
        direct_result["text"],
        min_characters=MIN_DIRECT_TEXT_CHARACTERS,
    ):
        return direct_result

    return extract_text_from_pdf_ocr(file_path)


def extract_text_from_docx(file_path: str | Path) -> dict:
    """
    Extrae texto desde un archivo DOCX.
    """
    path = Path(file_path)
    document = Document(path)

    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text and paragraph.text.strip()
    ]

    text = "\n\n".join(paragraphs)
    text = clean_text(text)

    return {
        "text": text,
        "pages": [],
        "extraction_method": "direct",
    }


def extract_text_from_plain_text(file_path: str | Path) -> dict:
    """
    Extrae texto desde TXT o Markdown.
    """
    path = Path(file_path)

    text = path.read_text(encoding="utf-8", errors="replace")
    text = clean_text(text)

    return {
        "text": text,
        "pages": [],
        "extraction_method": "direct",
    }


def extract_text_from_html(file_path: str | Path) -> dict:
    """
    Extrae texto visible desde HTML.
    """
    path = Path(file_path)

    html = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    text = clean_text(text)

    return {
        "text": text,
        "pages": [],
        "extraction_method": "direct",
    }


def extract_text_from_csv(file_path: str | Path) -> dict:
    """
    Convierte un CSV a texto estructurado por filas.
    """
    path = Path(file_path)
    rows_as_text = []

    with path.open("r", encoding="utf-8", errors="replace", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames:
            for row_index, row in enumerate(reader, start=1):
                row_text = f"Fila {row_index}: " + " | ".join(
                    f"{column}: {value}"
                    for column, value in row.items()
                )
                rows_as_text.append(row_text)
        else:
            csv_file.seek(0)
            raw_reader = csv.reader(csv_file)
            for row_index, row in enumerate(raw_reader, start=1):
                rows_as_text.append(f"Fila {row_index}: " + " | ".join(row))

    text = "\n".join(rows_as_text)
    text = clean_text(text)

    return {
        "text": text,
        "pages": [],
        "extraction_method": "direct",
    }


def extract_text_from_xlsx(file_path: str | Path) -> dict:
    """
    Convierte un XLSX a texto estructurado por hojas y filas.
    """
    path = Path(file_path)
    workbook = pd.read_excel(path, sheet_name=None, dtype=str)

    sections = []

    for sheet_name, dataframe in workbook.items():
        sections.append(f"Hoja: {sheet_name}")

        dataframe = dataframe.fillna("")

        for row_index, row in dataframe.iterrows():
            values = [
                f"{column}: {row[column]}"
                for column in dataframe.columns
                if str(row[column]).strip()
            ]

            if values:
                sections.append(f"Fila {row_index + 1}: " + " | ".join(values))

    text = "\n".join(sections)
    text = clean_text(text)

    return {
        "text": text,
        "pages": [],
        "extraction_method": "direct",
    }


def extract_text(file_path: str | Path, document_type: str) -> dict:
    """
    Extrae texto según el tipo documental detectado.
    """
    extractors = {
        "pdf": extract_text_from_pdf,
        "docx": extract_text_from_docx,
        "txt": extract_text_from_plain_text,
        "markdown": extract_text_from_plain_text,
        "html": extract_text_from_html,
        "csv": extract_text_from_csv,
        "xlsx": extract_text_from_xlsx,
    }

    extractor = extractors.get(document_type)

    if extractor is None:
        raise ValueError(f"No existe extractor para el tipo documental: {document_type}")

    return extractor(file_path)
