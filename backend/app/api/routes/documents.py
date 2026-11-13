
import logging
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from app.auth.dependencies import get_current_user
from app.database.supabase import (
    create_document_record,
    update_document_record,
    delete_document_record,
)
from app.services.file_validation import (
    validate_document,
    MAX_FILE_SIZE,
)
from app.services.document_upload import (
    upload_to_storage,
    delete_from_storage,
)
from app.services.document_processor import process_document


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"],
)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    token = current_user["access_token"]

    # Read only up to the allowed size + 1 byte.
    content = await file.read(MAX_FILE_SIZE + 1)

    try:
        extension = validate_document(
            filename=file.filename or "",
            mime_type=file.content_type or "",
            content=content,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    document_id = str(uuid.uuid4())

    storage_path = f"{user_id}/{document_id}{extension}"

    original_filename = Path(
        file.filename or "document"
    ).name

    metadata = {
        "id": document_id,
        "owner_id": user_id,
        "title": original_filename,
        "original_filename": original_filename,
        "storage_path": storage_path,
        "mime_type": file.content_type,
        "file_size_bytes": len(content),
        "status": "uploaded",
    }

    record_created = False
    storage_uploaded = False

    # STEP 1: Create document record and upload file.
    try:
        await create_document_record(
            token,
            metadata,
        )
        record_created = True

        await upload_to_storage(
            token,
            storage_path,
            content,
            file.content_type or "application/octet-stream",
        )
        storage_uploaded = True

        await update_document_record(
            token,
            document_id,
            {"status": "processing"},
        )

    except Exception as exc:
        logger.exception(
            "Document upload stage failed. Document ID: %s",
            document_id,
        )

        # Clean up only when the upload stage fails.
        if storage_uploaded:
            try:
                await delete_from_storage(
                    token,
                    storage_path,
                )
            except Exception:
                logger.exception("Storage cleanup failed.")

        if record_created:
            try:
                await delete_document_record(
                    token,
                    document_id,
                )
            except Exception:
                logger.exception("Document record cleanup failed.")

        raise HTTPException(
            status_code=502,
            detail="Document upload failed. Please try again.",
        ) from exc

    # STEP 2: Extract, chunk, embed and store document content.
    try:
        chunk_count = await process_document(
            access_token=token,
            document_id=document_id,
            owner_id=user_id,
            storage_path=storage_path,
            filename=original_filename,
        )

        return {
            "document_id": document_id,
            "filename": original_filename,
            "status": "ready",
            "chunk_count": chunk_count,
            "message": "Document uploaded and processed successfully.",
        }

    except Exception as exc:
        logger.exception(
            "Document processing failed. Document ID: %s",
            document_id,
        )

        # Keep the uploaded file and record for diagnosis or retry.
        try:
            await update_document_record(
                token,
                document_id,
                {
                    "status": "failed",
                    "error_message": "Document processing failed.",
                },
            )
        except Exception:
            logger.exception(
                "Failed to update document status. Document ID: %s",
                document_id,
            )

        raise HTTPException(
            status_code=500,
            detail={
                "document_id": document_id,
                "status": "failed",
                "message": "Document uploaded, but processing failed.",
            },
        ) from exc
