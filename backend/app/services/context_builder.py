
def estimate_tokens(text: str) -> int:
    """
    Lightweight token approximation.
    This is not a provider's exact tokenizer.
    """
    return max(1, len(text) // 4)


def build_context(
    chunks: list[dict],
    max_context_tokens: int = 1800,
) -> tuple[str, list[dict]]:

    selected = []
    context_parts = []
    used_tokens = 0

    for chunk in chunks:
        content = chunk["content"]

        source_label = chunk.get("source_label", "S?")

        page = chunk.get("metadata", {}).get("page_number")

        source_description = (
            f"{source_label} | Page {page}"
            if page
            else source_label
        )

        formatted = (
            f"[{source_description}]\n"
            f"{content}"
        )

        tokens = estimate_tokens(formatted)

        if used_tokens + tokens > max_context_tokens:
            continue

        context_parts.append(formatted)
        selected.append(chunk)

        used_tokens += tokens

    context = "\n\n---\n\n".join(context_parts)

    return context, selected
