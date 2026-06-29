import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_db_backend, DatabaseBackend
from models.user.entity.user_model import User
from services.user.user_service import UserService
from models.user.user_schemas import UserCreateSchema, UserUpdateSchema, UserResponseSchema
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

user_router = APIRouter(prefix="/api/user", tags=["User"])


@user_router.post("/", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Create a new User"""
    try:
        service = UserService(backend)
        domain = User(**payload.model_dump())
        created_user = await service.create(domain)
        return UserResponseSchema.to_response(created_user)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@user_router.get("/", response_model=List[UserResponseSchema])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get all User records"""
    try:
        service = UserService(backend)
        users = await service.get_all(skip=skip, limit=limit)
        return [UserResponseSchema.to_response(user) for user in users]
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@user_router.get("/{record_id}", response_model=UserResponseSchema)
async def get_user_by_id(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Get User by ID"""
    try:
        service = UserService(backend)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@user_router.put("/{record_id}", response_model=UserResponseSchema)
async def update_user(
    record_id: int,
    payload: UserUpdateSchema,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Update User"""
    try:
        service = UserService(backend)
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@user_router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    record_id: int,
    backend: DatabaseBackend = Depends(get_db_backend)
):
    """Delete User"""
    try:
        service = UserService(backend)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
