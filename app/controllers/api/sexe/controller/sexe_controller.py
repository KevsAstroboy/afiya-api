import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.sexe.entity.sexe_model import Sexe
from services.sexe.sexe_service import SexeService
from models.sexe.sexe_schemas import SexeCreateSchema, SexeUpdateSchema, SexeResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

sexe_router = APIRouter(prefix="/api/sexe", tags=["Sexe"])


@sexe_router.post("/", response_model=SexeResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_sexe(
    payload: SexeCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new Sexe"""
    try:
        service = SexeService(backend)
        domain = Sexe(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@sexe_router.get("/", response_model=List[SexeResponseSchema])
async def get_all_sexes(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all Sexe records"""
    try:
        service = SexeService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@sexe_router.get("/{record_id}", response_model=SexeResponseSchema)
async def get_sexe_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get Sexe by ID"""
    try:
        service = SexeService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@sexe_router.put("/{record_id}", response_model=SexeResponseSchema)
async def update_sexe(
    record_id: int,
    payload: SexeUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update Sexe"""
    try:
        service = SexeService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@sexe_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sexe(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete Sexe"""
    try:
        service = SexeService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
