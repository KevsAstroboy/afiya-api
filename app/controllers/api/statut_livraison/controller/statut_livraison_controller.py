import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.statut_livraison.entity.statut_livraison_model import StatutLivraison
from services.statut_livraison.statut_livraison_service import StatutLivraisonService
from models.statut_livraison.statut_livraison_schemas import StatutLivraisonCreateSchema, StatutLivraisonUpdateSchema, StatutLivraisonResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

statut_livraison_router = APIRouter(prefix="/api/statut-livraison", tags=["StatutLivraison"])


@statut_livraison_router.post("/", response_model=StatutLivraisonResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_statut_livraison(
    payload: StatutLivraisonCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new StatutLivraison"""
    try:
        service = StatutLivraisonService(backend)
        domain = StatutLivraison(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@statut_livraison_router.get("/", response_model=List[StatutLivraisonResponseSchema])
async def get_all_statut_livraisons(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all StatutLivraison records"""
    try:
        service = StatutLivraisonService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@statut_livraison_router.get("/{record_id}", response_model=StatutLivraisonResponseSchema)
async def get_statut_livraison_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get StatutLivraison by ID"""
    try:
        service = StatutLivraisonService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@statut_livraison_router.put("/{record_id}", response_model=StatutLivraisonResponseSchema)
async def update_statut_livraison(
    record_id: int,
    payload: StatutLivraisonUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update StatutLivraison"""
    try:
        service = StatutLivraisonService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@statut_livraison_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_statut_livraison(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete StatutLivraison"""
    try:
        service = StatutLivraisonService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
