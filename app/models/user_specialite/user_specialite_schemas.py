from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserSpecialiteCreateSchema(BaseModel):
    user_id: int
    specialite_id: int

    class Config:
        from_attributes = True


class UserSpecialiteUpdateSchema(BaseModel):
    user_id: Optional[int] = None
    specialite_id: Optional[int] = None

    class Config:
        from_attributes = True


class UserSpecialiteResponseSchema(BaseModel):
    id: int
    user_id: int
    specialite_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
