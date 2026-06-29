import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.operateur.entity.operateur_model import Operateur
from services.operateur.operateur_service import OperateurService
from models.operateur.operateur_schemas import OperateurCreateSchema, OperateurUpdateSchema, OperateurResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

operateur_router = APIRouter(prefix="/api/operateur", tags=["Operateur"])


@operateur_router.post("/", response_model=OperateurResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_operateur(
    payload: OperateurCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new Operateur"""
    try:
        service = OperateurService(backend)
        domain = Operateur(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@operateur_router.get("/", response_model=List[OperateurResponseSchema])
async def get_all_operateurs(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all Operateur records"""
    try:
        service = OperateurService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@operateur_router.get("/{record_id}", response_model=OperateurResponseSchema)
async def get_operateur_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get Operateur by ID"""
    try:
        service = OperateurService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@operateur_router.put("/{record_id}", response_model=OperateurResponseSchema)
async def update_operateur(
    record_id: int,
    payload: OperateurUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update Operateur"""
    try:
        service = OperateurService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@operateur_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_operateur(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete Operateur"""
    try:
        service = OperateurService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
