import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from services.analytics.analytics_service import (
    get_patient_with_history,
    get_patient_history,
    get_consultation_detail,
)

logger = logging.getLogger(__name__)

patient_router = APIRouter(prefix="/api/patient", tags=["Patient"])


@patient_router.get("/{patient_id}")
async def patient_detail(patient_id: str):
    result = get_patient_with_history(patient_id)
    if not result:
        raise HTTPException(404, "Patient not found")
    return result


@patient_router.get("/{patient_id}/historique")
async def patient_historique(
    patient_id: str,
    limit: int = Query(default=20),
    start_key: Optional[str] = Query(default=None),
):
    result = get_patient_history(patient_id, limit, start_key)
    return result


@patient_router.get("/{patient_id}/consultation/{consultation_id}")
async def patient_consultation_detail(patient_id: str, consultation_id: str):
    result = get_consultation_detail(consultation_id)
    if not result:
        raise HTTPException(404, "Consultation not found")
    return result
