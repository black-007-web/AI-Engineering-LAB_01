
import re


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[str]:

    if chunk_size <= overlap:
        raise ValueError(
            "chunk_size must be greater than overlap."
        )

    text = clean_text(text)

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):

        end = min(start + chunk_size, len(text))

        # Prefer splitting at a word boundary
        if end < len(text):
            boundary = text.rfind(" ", start, end)

            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(end - overlap, start + 1)

    return chunks


def chunk_document(
    pages: list[dict],
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[dict]:

    results = []
    chunk_index = 0

    for page in pages:

        page_text = clean_text(page["text"])

        page_chunks = split_text(
            page_text,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk in page_chunks:

            results.append({
                "chunk_index": chunk_index,
                "content": chunk,
                "metadata": {
                    "page_number": page["page_number"],
                },
            })

            chunk_index += 1

    return results
