
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.services.rag_service import answer_question


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG"])


class RAGRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    document_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=10)


@router.post("/ask")
async def ask_rag(
    request: RAGRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        result = await answer_question(
            question=request.question,
            access_token=current_user["access_token"],
            top_k=request.top_k,
            document_id=request.document_id,
        )

        return {
            "answer": result["answer"],
            "citations": result.get("citations", []),
            "retrieved_count": result["retrieved_count"],
            "provider": result.get("provider"),
            "model": result.get("model"),
            "usage": result.get("usage"),
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("RAG answer generation failed")

        raise HTTPException(
            status_code=500,
            detail="RAG answer generation failed.",
        )
