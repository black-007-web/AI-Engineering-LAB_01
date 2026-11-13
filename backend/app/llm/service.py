from app.core.config import settings
from app.llm.registry import get_provider
from app.llm.telemetry import tracked_generate


async def generate_answer(
    prompt: str,
    provider_name: str | None = None,
    system_prompt: str | None = None
) -> dict:
    primary = provider_name or settings.LLM_DEFAULT_PROVIDER
    fallback = settings.LLM_FALLBACK_PROVIDER

    try:
        provider = get_provider(primary)

        result = await tracked_generate(
            provider=provider,
            prompt=prompt,
            system_prompt=system_prompt
        )

        result["fallback_used"] = False
        return result

    except (RuntimeError, ValueError) as primary_error:
        if not fallback or fallback == primary:
            raise primary_error

        provider = get_provider(fallback)

        result = await tracked_generate(
            provider=provider,
            prompt=prompt,
            system_prompt=system_prompt
        )

        result["fallback_used"] = True
        result["fallback_reason"] = type(primary_error).__name__
        return result