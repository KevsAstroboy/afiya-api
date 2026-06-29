import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.images_consultation.entity.images_consultation_model import ImagesConsultation
from services.images_consultation.images_consultation_service import ImagesConsultationService
from models.images_consultation.images_consultation_schemas import ImagesConsultationCreateSchema, ImagesConsultationUpdateSchema, ImagesConsultationResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

images_consultation_router = APIRouter(prefix="/api/images-consultation", tags=["ImagesConsultation"])


@images_consultation_router.post("/", response_model=ImagesConsultationResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_images_consultation(
    payload: ImagesConsultationCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new ImagesConsultation"""
    try:
        service = ImagesConsultationService(backend)
        domain = ImagesConsultation(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@images_consultation_router.get("/", response_model=List[ImagesConsultationResponseSchema])
async def get_all_images_consultations(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all ImagesConsultation records"""
    try:
        service = ImagesConsultationService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@images_consultation_router.get("/{record_id}", response_model=ImagesConsultationResponseSchema)
async def get_images_consultation_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get ImagesConsultation by ID"""
    try:
        service = ImagesConsultationService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@images_consultation_router.put("/{record_id}", response_model=ImagesConsultationResponseSchema)
async def update_images_consultation(
    record_id: int,
    payload: ImagesConsultationUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update ImagesConsultation"""
    try:
        service = ImagesConsultationService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@images_consultation_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_images_consultation(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete ImagesConsultation"""
    try:
        service = ImagesConsultationService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
