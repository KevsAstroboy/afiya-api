from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class {ClassName}CreateSchema(BaseModel):
{create_fields}

    class Config:
        from_attributes = True


class {ClassName}UpdateSchema(BaseModel):
{update_fields}

    class Config:
        from_attributes = True


class {ClassName}ResponseSchema(BaseModel):
    id: int
{response_fields}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
