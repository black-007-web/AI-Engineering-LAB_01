
from pathlib import Path

import pymupdf


def extract_pdf(content: bytes) -> list[dict]:

    pages = []

    with pymupdf.open(
        stream=content,
        filetype="pdf"
    ) as document:

        if document.is_encrypted:
            raise ValueError(
                "Password-protected PDFs are not supported."
            )

        if document.page_count == 0:
            raise ValueError("PDF contains no pages.")

        for page_index, page in enumerate(document):

            text = page.get_text("text").strip()

            if text:
                pages.append({
                    "page_number": page_index + 1,
                    "text": text,
                })

    return pages


def extract_txt(content: bytes) -> list[dict]:

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "TXT file must be UTF-8 encoded."
        ) from exc

    text = text.strip()

    if not text:
        raise ValueError("TXT file contains no text.")

    return [{
        "page_number": None,
        "text": text,
    }]


def extract_document(
    filename: str,
    content: bytes,
) -> list[dict]:

    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        return extract_pdf(content)

    if extension == ".txt":
        return extract_txt(content)

    raise ValueError("Unsupported document format.")
