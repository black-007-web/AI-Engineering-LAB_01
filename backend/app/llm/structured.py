
import json

from pydantic import BaseModel

from app.llm.registry import get_provider


async def generate_structured(
    prompt: str,
    output_schema: type[BaseModel],
    provider_name: str = "ollama"
) -> BaseModel:

    provider = get_provider(provider_name)

    schema_json = json.dumps(
        output_schema.model_json_schema()
    )

    result = await provider.generate(
        prompt=(
            f"{prompt}\n\n"
            "Return only valid JSON matching this schema:\n"
            f"{schema_json}"
        )
    )

    raw = result["answer"]

    try:
        return output_schema.model_validate_json(raw)

    except Exception as exc:
        raise RuntimeError(
            "Model returned invalid structured output."
        ) from exc
