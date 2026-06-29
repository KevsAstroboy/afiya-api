import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.specialite.entity.specialite_model import Specialite
from services.specialite.specialite_service import SpecialiteService
from models.specialite.specialite_schemas import SpecialiteCreateSchema, SpecialiteUpdateSchema, SpecialiteResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

specialite_router = APIRouter(prefix="/api/specialite", tags=["Specialite"])


@specialite_router.post("/", response_model=SpecialiteResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_specialite(
    payload: SpecialiteCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new Specialite"""
    try:
        service = SpecialiteService(backend)
        domain = Specialite(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@specialite_router.get("/", response_model=List[SpecialiteResponseSchema])
async def get_all_specialites(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all Specialite records"""
    try:
        service = SpecialiteService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@specialite_router.get("/{record_id}", response_model=SpecialiteResponseSchema)
async def get_specialite_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get Specialite by ID"""
    try:
        service = SpecialiteService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@specialite_router.put("/{record_id}", response_model=SpecialiteResponseSchema)
async def update_specialite(
    record_id: int,
    payload: SpecialiteUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update Specialite"""
    try:
        service = SpecialiteService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@specialite_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_specialite(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete Specialite"""
    try:
        service = SpecialiteService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
