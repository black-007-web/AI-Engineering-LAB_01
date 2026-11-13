
import logging
import time
import uuid

logger = logging.getLogger("ai_engineering.llm")


async def tracked_generate(
    provider,
    prompt: str,
    system_prompt: str | None = None
) -> dict:

    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    try:
        result = await provider.generate(
            prompt=prompt,
            system_prompt=system_prompt
        )

        result["request_id"] = request_id
        result["latency_ms"] = round(
            (time.perf_counter() - start) * 1000,
            2
        )

        logger.info(
            "llm_request_completed",
            extra={
                "request_id": request_id,
                "provider": result.get("provider"),
                "model": result.get("model"),
                "latency_ms": result.get("latency_ms"),
                "input_tokens": result.get("input_tokens"),
                "output_tokens": result.get("output_tokens"),
            }
        )

        return result

    except Exception as exc:

        logger.exception(
            "llm_request_failed",
            extra={
                "request_id": request_id,
                "error_type": type(exc).__name__,
                "latency_ms": round(
                    (time.perf_counter() - start) * 1000,
                    2
                )
            }
        )

        raise
