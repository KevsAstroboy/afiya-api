import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.document.entity.document_model import Document
from services.document.document_service import DocumentService
from models.document.document_schemas import DocumentCreateSchema, DocumentUpdateSchema, DocumentResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

document_router = APIRouter(prefix="/api/document", tags=["Document"])


@document_router.post("/", response_model=DocumentResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_document(
    payload: DocumentCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new Document"""
    try:
        service = DocumentService(backend)
        domain = Document(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@document_router.get("/", response_model=List[DocumentResponseSchema])
async def get_all_documents(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all Document records"""
    try:
        service = DocumentService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@document_router.get("/{record_id}", response_model=DocumentResponseSchema)
async def get_document_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get Document by ID"""
    try:
        service = DocumentService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@document_router.put("/{record_id}", response_model=DocumentResponseSchema)
async def update_document(
    record_id: int,
    payload: DocumentUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update Document"""
    try:
        service = DocumentService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@document_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete Document"""
    try:
        service = DocumentService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
