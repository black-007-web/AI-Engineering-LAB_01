import re
from typing import Any


CITATION_PATTERN = re.compile(r"\[S(\d+)\]")


def validate_citations(
    answer: str,
    chunks: list[dict[str, Any]],
) -> tuple[str, list[dict[str, Any]]]:

    # Only chunks included in the final context are valid sources.
    source_map = {
        chunk["source_label"]: chunk
        for chunk in chunks
        if chunk.get("source_label")
    }

    valid_labels = {
        label[1:]
        for label in source_map
    }

    # Remove citations that refer to unavailable sources.
    def replace_invalid(match: re.Match) -> str:
        number = match.group(1)

        if number not in valid_labels:
            return ""

        return match.group(0)

    answer = CITATION_PATTERN.sub(replace_invalid, answer)

    # Extract unique, valid citations from the final answer.
    cited_numbers = sorted(
        {
            match.group(1)
            for match in CITATION_PATTERN.finditer(answer)
        },
        key=int,
    )

    citations = []

    for number in cited_numbers:
        chunk = source_map.get(f"S{number}")

        if not chunk:
            continue

        metadata = chunk.get("metadata") or {}

        citations.append({
            "source_label": f"S{number}",
            "chunk_id": chunk.get("chunk_id") or chunk.get("id"),
            "document_id": chunk.get("document_id"),
            "document_title": (
                chunk.get("document_title")
                or metadata.get("document_title")
            ),
            "page": (
                metadata.get("page_number")
                or metadata.get("page")
            ),
            "similarity": chunk.get("similarity"),
        })

    return answer, citations
