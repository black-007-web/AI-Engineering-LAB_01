from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.core.config import settings
from app.llm.service import generate_answer
from app.schemas.llm import ChatRequest, ChatResponse

router = APIRouter(
    prefix="/api/v1/llm",
    tags=["LLM"]
)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):

    try:
        result = await generate_answer(
            prompt=request.prompt,
            provider_name=settings.LLM_DEFAULT_PROVIDER,
            system_prompt=(
                "You are a helpful AI assistant. "
                "Answer clearly and accurately. "
                "If you do not know something, say so."
            )
        )

        return result

    except (RuntimeError, ValueError) as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc)
        )