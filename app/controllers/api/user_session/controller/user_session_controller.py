import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.user_session.entity.user_session_model import UserSession
from services.user_session.user_session_service import UserSessionService
from models.user_session.user_session_schemas import UserSessionCreateSchema, UserSessionUpdateSchema, UserSessionResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

user_session_router = APIRouter(prefix="/api/user-session", tags=["UserSession"])


@user_session_router.post("/", response_model=UserSessionResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_user_session(
    payload: UserSessionCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new UserSession"""
    try:
        service = UserSessionService(backend)
        domain = UserSession(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@user_session_router.get("/", response_model=List[UserSessionResponseSchema])
async def get_all_user_sessions(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all UserSession records"""
    try:
        service = UserSessionService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@user_session_router.get("/{record_id}", response_model=UserSessionResponseSchema)
async def get_user_session_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get UserSession by ID"""
    try:
        service = UserSessionService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@user_session_router.put("/{record_id}", response_model=UserSessionResponseSchema)
async def update_user_session(
    record_id: int,
    payload: UserSessionUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update UserSession"""
    try:
        service = UserSessionService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@user_session_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_session(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete UserSession"""
    try:
        service = UserSessionService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
