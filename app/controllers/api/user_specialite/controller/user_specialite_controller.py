import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.user_specialite.entity.user_specialite_model import UserSpecialite
from services.user_specialite.user_specialite_service import UserSpecialiteService
from models.user_specialite.user_specialite_schemas import UserSpecialiteCreateSchema, UserSpecialiteUpdateSchema, UserSpecialiteResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

user_specialite_router = APIRouter(prefix="/api/user-specialite", tags=["UserSpecialite"])


@user_specialite_router.post("/", response_model=UserSpecialiteResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_user_specialite(
    payload: UserSpecialiteCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new UserSpecialite"""
    try:
        service = UserSpecialiteService(backend)
        domain = UserSpecialite(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@user_specialite_router.get("/", response_model=List[UserSpecialiteResponseSchema])
async def get_all_user_specialites(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all UserSpecialite records"""
    try:
        service = UserSpecialiteService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@user_specialite_router.get("/{record_id}", response_model=UserSpecialiteResponseSchema)
async def get_user_specialite_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get UserSpecialite by ID"""
    try:
        service = UserSpecialiteService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@user_specialite_router.put("/{record_id}", response_model=UserSpecialiteResponseSchema)
async def update_user_specialite(
    record_id: int,
    payload: UserSpecialiteUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update UserSpecialite"""
    try:
        service = UserSpecialiteService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@user_specialite_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_specialite(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete UserSpecialite"""
    try:
        service = UserSpecialiteService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
