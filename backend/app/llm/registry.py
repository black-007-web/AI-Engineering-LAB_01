from app.llm.ollama_provider import OllamaProvider


def get_provider(provider_name: str):

    if provider_name == "ollama":
        return OllamaProvider()

    raise ValueError(
        f"Unsupported LLM provider: {provider_name}"
    )


from app.llm.ollama_provider import OllamaProvider
from app.llm.gemini_provider import GeminiProvider


def get_provider(provider_name: str):

    if provider_name == "ollama":
        return OllamaProvider()

    if provider_name == "gemini":
        return GeminiProvider()

    raise ValueError(
        f"Unsupported LLM provider: {provider_name}"
    )
