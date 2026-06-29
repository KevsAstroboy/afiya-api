import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.dossier_medical.entity.dossier_medical_model import DossierMedical
from services.dossier_medical.dossier_medical_service import DossierMedicalService
from models.dossier_medical.dossier_medical_schemas import DossierMedicalCreateSchema, DossierMedicalUpdateSchema, DossierMedicalResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

dossier_medical_router = APIRouter(prefix="/api/dossier-medical", tags=["DossierMedical"])


@dossier_medical_router.post("/", response_model=DossierMedicalResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_dossier_medical(
    payload: DossierMedicalCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new DossierMedical"""
    try:
        service = DossierMedicalService(backend)
        domain = DossierMedical(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@dossier_medical_router.get("/", response_model=List[DossierMedicalResponseSchema])
async def get_all_dossier_medicals(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all DossierMedical records"""
    try:
        service = DossierMedicalService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@dossier_medical_router.get("/{record_id}", response_model=DossierMedicalResponseSchema)
async def get_dossier_medical_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get DossierMedical by ID"""
    try:
        service = DossierMedicalService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@dossier_medical_router.put("/{record_id}", response_model=DossierMedicalResponseSchema)
async def update_dossier_medical(
    record_id: int,
    payload: DossierMedicalUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update DossierMedical"""
    try:
        service = DossierMedicalService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@dossier_medical_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dossier_medical(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete DossierMedical"""
    try:
        service = DossierMedicalService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
