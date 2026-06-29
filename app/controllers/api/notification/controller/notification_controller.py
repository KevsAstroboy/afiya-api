import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.notification.entity.notification_model import Notification
from services.notification.notification_service import NotificationService
from models.notification.notification_schemas import NotificationCreateSchema, NotificationUpdateSchema, NotificationResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

notification_router = APIRouter(prefix="/api/notification", tags=["Notification"])


@notification_router.post("/", response_model=NotificationResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_notification(
    payload: NotificationCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new Notification"""
    try:
        service = NotificationService(backend)
        domain = Notification(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@notification_router.get("/", response_model=List[NotificationResponseSchema])
async def get_all_notifications(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all Notification records"""
    try:
        service = NotificationService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@notification_router.get("/{record_id}", response_model=NotificationResponseSchema)
async def get_notification_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get Notification by ID"""
    try:
        service = NotificationService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@notification_router.put("/{record_id}", response_model=NotificationResponseSchema)
async def update_notification(
    record_id: int,
    payload: NotificationUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update Notification"""
    try:
        service = NotificationService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@notification_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete Notification"""
    try:
        service = NotificationService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
