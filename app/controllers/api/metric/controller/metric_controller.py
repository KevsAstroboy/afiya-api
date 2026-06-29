import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.metric.entity.metric_model import Metric
from services.metric.metric_service import MetricService
from models.metric.metric_schemas import MetricCreateSchema, MetricUpdateSchema, MetricResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

metric_router = APIRouter(prefix="/api/metric", tags=["Metric"])


@metric_router.post("/", response_model=MetricResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_metric(
    payload: MetricCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new Metric"""
    try:
        service = MetricService(backend)
        domain = Metric(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@metric_router.get("/", response_model=List[MetricResponseSchema])
async def get_all_metrics(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all Metric records"""
    try:
        service = MetricService(backend)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@metric_router.get("/{record_id}", response_model=MetricResponseSchema)
async def get_metric_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get Metric by ID"""
    try:
        service = MetricService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@metric_router.put("/{record_id}", response_model=MetricResponseSchema)
async def update_metric(
    record_id: int,
    payload: MetricUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update Metric"""
    try:
        service = MetricService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@metric_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_metric(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete Metric"""
    try:
        service = MetricService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
