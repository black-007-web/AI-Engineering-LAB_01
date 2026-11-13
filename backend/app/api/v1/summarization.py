
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.services.summarization_service import summarize_document


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/summarization",
    tags=["Summarization"],
)


class SummarizeRequest(BaseModel):
    document_id: str = Field(min_length=1)


@router.post("/document")
async def summarize(
    request: SummarizeRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        result = await summarize_document(
            document_id=request.document_id,
            access_token=current_user["access_token"],
        )

        return result

    except ValueError as exc:
        message = str(exc)

        if message == "Document not found or access denied.":
            raise HTTPException(
                status_code=404,
                detail=message,
            ) from exc

        if message == "Document is not ready for summarization.":
            raise HTTPException(
                status_code=409,
                detail=message,
            ) from exc

        if message in (
            "Document contains no indexed content.",
            "No document content fits the summarization context.",
        ):
            raise HTTPException(
                status_code=422,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=400,
            detail=message,
        ) from exc

    except Exception:
        logger.exception("Document summarization failed")

        raise HTTPException(
            status_code=500,
            detail="Document summarization failed.",
        )
