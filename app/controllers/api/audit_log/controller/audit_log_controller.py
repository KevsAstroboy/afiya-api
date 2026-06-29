import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.audit_log.entity.audit_log_model import AuditLog
from services.audit_log.audit_log_service import AuditLogService
from models.audit_log.audit_log_schemas import AuditLogCreateSchema, AuditLogUpdateSchema, AuditLogResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

audit_log_router = APIRouter(prefix="/api/audit-log", tags=["AuditLog"])


@audit_log_router.post("/", response_model=AuditLogResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_audit_log(
    payload: AuditLogCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new AuditLog"""
    try:
        service = AuditLogService(backend)
        domain = AuditLog(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@audit_log_router.get("/", response_model=List[AuditLogResponseSchema])
async def get_all_audit_logs(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all AuditLog records"""
    try:
        service = AuditLogService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@audit_log_router.get("/{record_id}", response_model=AuditLogResponseSchema)
async def get_audit_log_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get AuditLog by ID"""
    try:
        service = AuditLogService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@audit_log_router.put("/{record_id}", response_model=AuditLogResponseSchema)
async def update_audit_log(
    record_id: int,
    payload: AuditLogUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update AuditLog"""
    try:
        service = AuditLogService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@audit_log_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audit_log(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete AuditLog"""
    try:
        service = AuditLogService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
