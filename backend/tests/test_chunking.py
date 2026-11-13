
from app.services.chunking import split_text, chunk_document


def test_split_text_returns_chunks():
    text = "word " * 500

    chunks = split_text(
        text,
        chunk_size=100,
        overlap=20,
    )

    assert len(chunks) > 1


def test_empty_text():
    assert split_text("") == []


def test_chunk_document_preserves_page():
    pages = [
        {
            "page_number": 3,
            "text": "This is a sample document."
        }
    ]

    chunks = chunk_document(pages)

    assert chunks[0]["metadata"]["page_number"] == 3


def test_invalid_overlap():
    try:
        split_text("sample", chunk_size=100, overlap=100)
    except ValueError:
        return

    assert False, "Expected ValueError"
