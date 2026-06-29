import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.statut.entity.statut_model import Statut
from services.statut.statut_service import StatutService
from models.statut.statut_schemas import StatutCreateSchema, StatutUpdateSchema, StatutResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

statut_router = APIRouter(prefix="/api/statut", tags=["Statut"])


@statut_router.post("/", response_model=StatutResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_statut(
    payload: StatutCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new Statut"""
    try:
        service = StatutService(backend)
        domain = Statut(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@statut_router.get("/", response_model=List[StatutResponseSchema])
async def get_all_statuts(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all Statut records"""
    try:
        service = StatutService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@statut_router.get("/{record_id}", response_model=StatutResponseSchema)
async def get_statut_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get Statut by ID"""
    try:
        service = StatutService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@statut_router.put("/{record_id}", response_model=StatutResponseSchema)
async def update_statut(
    record_id: int,
    payload: StatutUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update Statut"""
    try:
        service = StatutService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@statut_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_statut(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete Statut"""
    try:
        service = StatutService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
