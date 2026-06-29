import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.avis_consultation.entity.avis_consultation_model import AvisConsultation
from services.avis_consultation.avis_consultation_service import AvisConsultationService
from models.avis_consultation.avis_consultation_schemas import AvisConsultationCreateSchema, AvisConsultationUpdateSchema, AvisConsultationResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

avis_consultation_router = APIRouter(prefix="/api/avis-consultation", tags=["AvisConsultation"])


@avis_consultation_router.post("/", response_model=AvisConsultationResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_avis_consultation(
    payload: AvisConsultationCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new AvisConsultation"""
    try:
        service = AvisConsultationService(backend)
        domain = AvisConsultation(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@avis_consultation_router.get("/", response_model=List[AvisConsultationResponseSchema])
async def get_all_avis_consultations(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all AvisConsultation records"""
    try:
        service = AvisConsultationService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@avis_consultation_router.get("/{record_id}", response_model=AvisConsultationResponseSchema)
async def get_avis_consultation_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get AvisConsultation by ID"""
    try:
        service = AvisConsultationService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@avis_consultation_router.put("/{record_id}", response_model=AvisConsultationResponseSchema)
async def update_avis_consultation(
    record_id: int,
    payload: AvisConsultationUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update AvisConsultation"""
    try:
        service = AvisConsultationService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@avis_consultation_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_avis_consultation(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete AvisConsultation"""
    try:
        service = AvisConsultationService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
