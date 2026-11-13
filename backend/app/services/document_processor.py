
import httpx

from app.core.config import settings
from app.llm.embedding_registry import get_embedding_provider
from app.services.document_extraction import extract_document
from app.services.chunking import chunk_document


BUCKET = "knowledge-documents"
EMBEDDING_DIMENSIONS = 768


def get_headers(access_token: str) -> dict:
    return {
        "apikey": settings.SUPABASE_PUBLISHABLE_KEY,
        "Authorization": f"Bearer {access_token}",
    }


async def process_document(
    access_token: str,
    document_id: str,
    owner_id: str,
    storage_path: str,
    filename: str,
) -> int:
    headers = get_headers(access_token)

    async with httpx.AsyncClient(timeout=120.0) as client:

        # 1. Download the uploaded file from private Supabase Storage.
        storage_url = (
            f"{settings.SUPABASE_URL}/storage/v1/object/"
            f"{BUCKET}/{storage_path}"
        )

        response = await client.get(storage_url, headers=headers)
        response.raise_for_status()

        file_content = response.content

        # 2. Extract text from the document.
        pages = extract_document(filename, file_content)

        if not pages:
            raise ValueError("No extractable text found in this document.")

        # 3. Split extracted text into chunks.
        chunks = chunk_document(pages)

        if not chunks:
            raise ValueError("Document did not produce any text chunks.")

        # 4. Generate embeddings using Ollama.
        embedding_provider = get_embedding_provider("ollama")

        texts = [chunk["content"] for chunk in chunks]
        embeddings = await embedding_provider.embed(texts)

        if len(embeddings) != len(chunks):
            raise RuntimeError("Embedding count does not match chunk count.")

        # 5. Validate embedding dimensions.
        for embedding in embeddings:
            if len(embedding) != EMBEDDING_DIMENSIONS:
                raise RuntimeError("Unexpected embedding dimensions.")

        # 6. Remove existing chunks if this document is being reprocessed.
        delete_url = (
            f"{settings.SUPABASE_URL}/rest/v1/document_chunks"
        )

        delete_response = await client.delete(
            delete_url,
            headers=headers,
            params={"document_id": f"eq.{document_id}"},
        )
        delete_response.raise_for_status()

        # 7. Prepare chunk records for Supabase.
        records = []

        for chunk, embedding in zip(chunks, embeddings):
            records.append({
                "document_id": document_id,
                "owner_id": owner_id,
                "chunk_index": chunk["chunk_index"],
                "content": chunk["content"],
                "embedding": embedding,
                "metadata": chunk["metadata"],
            })

        # 8. Insert all chunks into the database.
        insert_response = await client.post(
            delete_url,
            headers={
                **headers,
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            json=records,
        )
        insert_response.raise_for_status()

        # 9. Mark the document as ready.
        update_response = await client.patch(
            f"{settings.SUPABASE_URL}/rest/v1/documents",
            headers={
                **headers,
                "Content-Type": "application/json",
            },
            params={"id": f"eq.{document_id}"},
            json={
                "status": "ready",
                "chunk_count": len(chunks),
                "error_message": None,
            },
        )
        update_response.raise_for_status()

    return len(chunks)
