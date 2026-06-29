import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.medecin_disponibilite.entity.medecin_disponibilite_model import MedecinDisponibilite
from services.medecin_disponibilite.medecin_disponibilite_service import MedecinDisponibiliteService
from models.medecin_disponibilite.medecin_disponibilite_schemas import MedecinDisponibiliteCreateSchema, MedecinDisponibiliteUpdateSchema, MedecinDisponibiliteResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

medecin_disponibilite_router = APIRouter(prefix="/api/medecin-disponibilite", tags=["MedecinDisponibilite"])


@medecin_disponibilite_router.post("/", response_model=MedecinDisponibiliteResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_medecin_disponibilite(
    payload: MedecinDisponibiliteCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new MedecinDisponibilite"""
    try:
        service = MedecinDisponibiliteService(backend)
        domain = MedecinDisponibilite(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@medecin_disponibilite_router.get("/", response_model=List[MedecinDisponibiliteResponseSchema])
async def get_all_medecin_disponibilites(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all MedecinDisponibilite records"""
    try:
        service = MedecinDisponibiliteService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@medecin_disponibilite_router.get("/{record_id}", response_model=MedecinDisponibiliteResponseSchema)
async def get_medecin_disponibilite_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get MedecinDisponibilite by ID"""
    try:
        service = MedecinDisponibiliteService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@medecin_disponibilite_router.put("/{record_id}", response_model=MedecinDisponibiliteResponseSchema)
async def update_medecin_disponibilite(
    record_id: int,
    payload: MedecinDisponibiliteUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update MedecinDisponibilite"""
    try:
        service = MedecinDisponibiliteService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@medecin_disponibilite_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medecin_disponibilite(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete MedecinDisponibilite"""
    try:
        service = MedecinDisponibiliteService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
