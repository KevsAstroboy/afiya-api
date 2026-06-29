import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.statut_consultation.entity.statut_consultation_model import StatutConsultation
from services.statut_consultation.statut_consultation_service import StatutConsultationService
from models.statut_consultation.statut_consultation_schemas import StatutConsultationCreateSchema, StatutConsultationUpdateSchema, StatutConsultationResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

statut_consultation_router = APIRouter(prefix="/api/statut-consultation", tags=["StatutConsultation"])


@statut_consultation_router.post("/", response_model=StatutConsultationResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_statut_consultation(
    payload: StatutConsultationCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new StatutConsultation"""
    try:
        service = StatutConsultationService(backend)
        domain = StatutConsultation(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@statut_consultation_router.get("/", response_model=List[StatutConsultationResponseSchema])
async def get_all_statut_consultations(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all StatutConsultation records"""
    try:
        service = StatutConsultationService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@statut_consultation_router.get("/{record_id}", response_model=StatutConsultationResponseSchema)
async def get_statut_consultation_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get StatutConsultation by ID"""
    try:
        service = StatutConsultationService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@statut_consultation_router.put("/{record_id}", response_model=StatutConsultationResponseSchema)
async def update_statut_consultation(
    record_id: int,
    payload: StatutConsultationUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update StatutConsultation"""
    try:
        service = StatutConsultationService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@statut_consultation_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_statut_consultation(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete StatutConsultation"""
    try:
        service = StatutConsultationService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
