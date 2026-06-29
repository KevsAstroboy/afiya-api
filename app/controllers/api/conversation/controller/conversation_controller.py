import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.conversation.entity.conversation_model import Conversation
from services.conversation.conversation_service import ConversationService
from models.conversation.conversation_schemas import ConversationCreateSchema, ConversationUpdateSchema, ConversationResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

conversation_router = APIRouter(prefix="/api/conversation", tags=["Conversation"])


@conversation_router.post("/", response_model=ConversationResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new Conversation"""
    try:
        service = ConversationService(backend)
        domain = Conversation(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@conversation_router.get("/", response_model=List[ConversationResponseSchema])
async def get_all_conversations(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all Conversation records"""
    try:
        service = ConversationService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@conversation_router.get("/{record_id}", response_model=ConversationResponseSchema)
async def get_conversation_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get Conversation by ID"""
    try:
        service = ConversationService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@conversation_router.put("/{record_id}", response_model=ConversationResponseSchema)
async def update_conversation(
    record_id: int,
    payload: ConversationUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update Conversation"""
    try:
        service = ConversationService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@conversation_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete Conversation"""
    try:
        service = ConversationService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
