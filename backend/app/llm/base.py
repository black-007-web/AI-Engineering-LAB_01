from typing import Protocol


class LLMProvider(Protocol):

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None
    ) -> dict:
        ...