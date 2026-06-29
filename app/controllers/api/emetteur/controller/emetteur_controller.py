import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.emetteur.entity.emetteur_model import Emetteur
from services.emetteur.emetteur_service import EmetteurService
from models.emetteur.emetteur_schemas import EmetteurCreateSchema, EmetteurUpdateSchema, EmetteurResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

emetteur_router = APIRouter(prefix="/api/emetteur", tags=["Emetteur"])


@emetteur_router.post("/", response_model=EmetteurResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_emetteur(
    payload: EmetteurCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new Emetteur"""
    try:
        service = EmetteurService(backend)
        domain = Emetteur(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@emetteur_router.get("/", response_model=List[EmetteurResponseSchema])
async def get_all_emetteurs(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all Emetteur records"""
    try:
        service = EmetteurService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@emetteur_router.get("/{record_id}", response_model=EmetteurResponseSchema)
async def get_emetteur_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get Emetteur by ID"""
    try:
        service = EmetteurService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@emetteur_router.put("/{record_id}", response_model=EmetteurResponseSchema)
async def update_emetteur(
    record_id: int,
    payload: EmetteurUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update Emetteur"""
    try:
        service = EmetteurService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@emetteur_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_emetteur(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete Emetteur"""
    try:
        service = EmetteurService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
