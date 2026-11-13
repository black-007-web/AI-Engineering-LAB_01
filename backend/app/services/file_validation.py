
from pathlib import Path


MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {".pdf", ".txt"}

ALLOWED_MIME_TYPES = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
}


def validate_document(
    filename: str,
    mime_type: str,
    content: bytes,
) -> str:

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only PDF and TXT files are supported.")

    if mime_type != ALLOWED_MIME_TYPES[extension]:
        raise ValueError("File MIME type does not match its extension.")

    if not content:
        raise ValueError("Empty files are not allowed.")

    if len(content) > MAX_FILE_SIZE:
        raise ValueError("Maximum file size is 10 MB.")

    if extension == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise ValueError("Invalid PDF file signature.")

    if extension == ".txt":
        try:
            content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError(
                "TXT files must use UTF-8 encoding."
            ) from exc

    return extension
