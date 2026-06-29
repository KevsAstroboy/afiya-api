import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.paiement.entity.paiement_model import Paiement
from services.paiement.paiement_service import PaiementService
from models.paiement.paiement_schemas import PaiementCreateSchema, PaiementUpdateSchema, PaiementResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

paiement_router = APIRouter(prefix="/api/paiement", tags=["Paiement"])


@paiement_router.post("/", response_model=PaiementResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_paiement(
    payload: PaiementCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new Paiement"""
    try:
        service = PaiementService(backend)
        domain = Paiement(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@paiement_router.get("/", response_model=List[PaiementResponseSchema])
async def get_all_paiements(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all Paiement records"""
    try:
        service = PaiementService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@paiement_router.get("/{record_id}", response_model=PaiementResponseSchema)
async def get_paiement_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get Paiement by ID"""
    try:
        service = PaiementService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@paiement_router.put("/{record_id}", response_model=PaiementResponseSchema)
async def update_paiement(
    record_id: int,
    payload: PaiementUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update Paiement"""
    try:
        service = PaiementService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@paiement_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paiement(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete Paiement"""
    try:
        service = PaiementService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
