
from pathlib import Path

import pymupdf
from docx import Document as DocxDocument


class DocumentParsingError(Exception):
    pass


class UnsupportedFileTypeError(DocumentParsingError):
    pass


class EmptyDocumentError(DocumentParsingError):
    pass


def extract_text_from_pdf(file_path: Path) -> str:
    text_parts: list[str] = []

    try:
        with pymupdf.open(file_path) as pdf:
            for page in pdf:
                page_text = page.get_text("text")

                if page_text.strip():
                    text_parts.append(page_text)

    except Exception as exc:
        raise DocumentParsingError(
            f"Failed to parse PDF file: {file_path.name}"
        ) from exc

    text = "\n\n".join(text_parts).strip()

    if not text:
        raise EmptyDocumentError(
            "No extractable text was found in the PDF."
        )

    return text


def extract_text_from_docx(file_path: Path) -> str:
    try:
        document = DocxDocument(file_path)

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

    except Exception as exc:
        raise DocumentParsingError(
            f"Failed to parse DOCX file: {file_path.name}"
        ) from exc

    text = "\n\n".join(paragraphs).strip()

    if not text:
        raise EmptyDocumentError(
            "No extractable text was found in the DOCX file."
        )

    return text


def extract_text(file_path: str | Path) -> str:
    path = Path(file_path)

    if not path.exists():
        raise DocumentParsingError(
            f"File does not exist: {path}"
        )

    extension = path.suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(path)

    if extension == ".docx":
        return extract_text_from_docx(path)

    raise UnsupportedFileTypeError(
        f"Unsupported file type: {extension}"
    )