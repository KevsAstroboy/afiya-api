import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.statut_paiement.entity.statut_paiement_model import StatutPaiement
from services.statut_paiement.statut_paiement_service import StatutPaiementService
from models.statut_paiement.statut_paiement_schemas import StatutPaiementCreateSchema, StatutPaiementUpdateSchema, StatutPaiementResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

statut_paiement_router = APIRouter(prefix="/api/statut-paiement", tags=["StatutPaiement"])


@statut_paiement_router.post("/", response_model=StatutPaiementResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_statut_paiement(
    payload: StatutPaiementCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new StatutPaiement"""
    try:
        service = StatutPaiementService(backend)
        domain = StatutPaiement(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@statut_paiement_router.get("/", response_model=List[StatutPaiementResponseSchema])
async def get_all_statut_paiements(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all StatutPaiement records"""
    try:
        service = StatutPaiementService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@statut_paiement_router.get("/{record_id}", response_model=StatutPaiementResponseSchema)
async def get_statut_paiement_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get StatutPaiement by ID"""
    try:
        service = StatutPaiementService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@statut_paiement_router.put("/{record_id}", response_model=StatutPaiementResponseSchema)
async def update_statut_paiement(
    record_id: int,
    payload: StatutPaiementUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update StatutPaiement"""
    try:
        service = StatutPaiementService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@statut_paiement_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_statut_paiement(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete StatutPaiement"""
    try:
        service = StatutPaiementService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
