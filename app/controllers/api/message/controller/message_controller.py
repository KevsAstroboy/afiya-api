import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.message.entity.message_model import Message
from services.message.message_service import MessageService
from models.message.message_schemas import MessageCreateSchema, MessageUpdateSchema, MessageResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

message_router = APIRouter(prefix="/api/message", tags=["Message"])


@message_router.post("/", response_model=MessageResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_message(
    payload: MessageCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new Message"""
    try:
        service = MessageService(backend)
        domain = Message(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@message_router.get("/", response_model=List[MessageResponseSchema])
async def get_all_messages(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all Message records"""
    try:
        service = MessageService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@message_router.get("/{record_id}", response_model=MessageResponseSchema)
async def get_message_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get Message by ID"""
    try:
        service = MessageService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@message_router.put("/{record_id}", response_model=MessageResponseSchema)
async def update_message(
    record_id: int,
    payload: MessageUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update Message"""
    try:
        service = MessageService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@message_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete Message"""
    try:
        service = MessageService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
