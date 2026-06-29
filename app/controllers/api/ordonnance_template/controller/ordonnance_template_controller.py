import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.ordonnance_template.entity.ordonnance_template_model import OrdonnanceTemplate
from services.ordonnance_template.ordonnance_template_service import OrdonnanceTemplateService
from models.ordonnance_template.ordonnance_template_schemas import OrdonnanceTemplateCreateSchema, OrdonnanceTemplateUpdateSchema, OrdonnanceTemplateResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

ordonnance_template_router = APIRouter(prefix="/api/ordonnance-template", tags=["OrdonnanceTemplate"])


@ordonnance_template_router.post("/", response_model=OrdonnanceTemplateResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_ordonnance_template(
    payload: OrdonnanceTemplateCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new OrdonnanceTemplate"""
    try:
        service = OrdonnanceTemplateService(backend)
        domain = OrdonnanceTemplate(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@ordonnance_template_router.get("/", response_model=List[OrdonnanceTemplateResponseSchema])
async def get_all_ordonnance_templates(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all OrdonnanceTemplate records"""
    try:
        service = OrdonnanceTemplateService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@ordonnance_template_router.get("/{record_id}", response_model=OrdonnanceTemplateResponseSchema)
async def get_ordonnance_template_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get OrdonnanceTemplate by ID"""
    try:
        service = OrdonnanceTemplateService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@ordonnance_template_router.put("/{record_id}", response_model=OrdonnanceTemplateResponseSchema)
async def update_ordonnance_template(
    record_id: int,
    payload: OrdonnanceTemplateUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update OrdonnanceTemplate"""
    try:
        service = OrdonnanceTemplateService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@ordonnance_template_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ordonnance_template(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete OrdonnanceTemplate"""
    try:
        service = OrdonnanceTemplateService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
