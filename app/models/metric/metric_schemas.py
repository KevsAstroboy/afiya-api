from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MetricCreateSchema(BaseModel):
    consultation_id: int
    type_metric: str
    valeur: float
    unite: str
    date_mesure: datetime

    class Config:
        from_attributes = True


class MetricUpdateSchema(BaseModel):
    consultation_id: Optional[int] = None
    type_metric: Optional[str] = None
    valeur: Optional[float] = None
    unite: Optional[str] = None
    date_mesure: Optional[datetime] = None

    class Config:
        from_attributes = True


class MetricResponseSchema(BaseModel):
    id: int
    consultation_id: int
    type_metric: str
    valeur: float
    unite: str
    date_mesure: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
