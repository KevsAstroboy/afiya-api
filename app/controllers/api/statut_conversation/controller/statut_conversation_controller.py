import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.statut_conversation.entity.statut_conversation_model import StatutConversation
from services.statut_conversation.statut_conversation_service import StatutConversationService
from models.statut_conversation.statut_conversation_schemas import StatutConversationCreateSchema, StatutConversationUpdateSchema, StatutConversationResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

statut_conversation_router = APIRouter(prefix="/api/statut-conversation", tags=["StatutConversation"])


@statut_conversation_router.post("/", response_model=StatutConversationResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_statut_conversation(
    payload: StatutConversationCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new StatutConversation"""
    try:
        service = StatutConversationService(backend)
        domain = StatutConversation(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@statut_conversation_router.get("/", response_model=List[StatutConversationResponseSchema])
async def get_all_statut_conversations(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all StatutConversation records"""
    try:
        service = StatutConversationService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@statut_conversation_router.get("/{record_id}", response_model=StatutConversationResponseSchema)
async def get_statut_conversation_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get StatutConversation by ID"""
    try:
        service = StatutConversationService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@statut_conversation_router.put("/{record_id}", response_model=StatutConversationResponseSchema)
async def update_statut_conversation(
    record_id: int,
    payload: StatutConversationUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update StatutConversation"""
    try:
        service = StatutConversationService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@statut_conversation_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_statut_conversation(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete StatutConversation"""
    try:
        service = StatutConversationService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
