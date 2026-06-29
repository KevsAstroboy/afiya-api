import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.models.{table_name}.entity.{table_name}_model import {ClassName}
from app.services.{table_name}.{table_name}_service import {ClassName}Service
from app.models.{table_name}.{table_name}_schemas import {ClassName}CreateSchema, {ClassName}UpdateSchema, {ClassName}ResponseSchema
from app.core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

{table_name}_router = APIRouter(prefix="/api/{url_slug}", tags=["{ClassName}"])


@{table_name}_router.post("/", response_model={ClassName}ResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_{table_name}(
    payload: {ClassName}CreateSchema,
    session: AsyncSession = Depends(get_async_session)
):
    """Create a new {ClassName}"""
    try:
        service = {ClassName}Service(session)
        domain = {ClassName}(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@{table_name}_router.get("/", response_model=List[{ClassName}ResponseSchema])
async def get_all_{table_name}s(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_async_session)
):
    """Get all {ClassName} records"""
    try:
        service = {ClassName}Service(session)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@{table_name}_router.get("/{record_id}", response_model={ClassName}ResponseSchema)
async def get_{table_name}_by_id(
    record_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Get {ClassName} by ID"""
    try:
        service = {ClassName}Service(session)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@{table_name}_router.put("/{record_id}", response_model={ClassName}ResponseSchema)
async def update_{table_name}(
    record_id: int,
    payload: {ClassName}UpdateSchema,
    session: AsyncSession = Depends(get_async_session)
):
    """Update {ClassName}"""
    try:
        service = {ClassName}Service(session)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@{table_name}_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{table_name}(
    record_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Delete {ClassName}"""
    try:
        service = {ClassName}Service(session)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
