import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from services.analytics.analytics_service import get_consultations, get_messages, toggle_disponibilite

logger = logging.getLogger(__name__)

consultation_router = APIRouter(prefix="/api", tags=["Consultations"])


@consultation_router.get("/consultations")
async def list_consultations(
    limit: int = Query(default=20),
    start_key: Optional[str] = Query(default=None),
    statut: Optional[str] = Query(default=None),
    date: Optional[str] = Query(default=None),
    medecin_id: Optional[str] = Query(default=None),
    patient_id: Optional[str] = Query(default=None),
):
    try:
        return get_consultations(limit, start_key, statut, date, medecin_id, patient_id)
    except Exception as e:
        logger.exception("Error listing consultations")
        raise HTTPException(500, str(e))


@consultation_router.get("/consultation/{consultation_id}/messages")
async def consultation_messages(consultation_id: str):
    try:
        return get_messages(consultation_id)
    except Exception as e:
        logger.exception("Error getting messages")
        raise HTTPException(500, str(e))


@consultation_router.put("/medecin/{medecin_id}/disponibilite")
async def update_disponibilite(medecin_id: str, payload: dict):
    disponible = payload.get("disponible", True)
    try:
        return toggle_disponibilite(medecin_id, disponible)
    except Exception as e:
        logger.exception("Error toggling disponibilite")
        raise HTTPException(500, str(e))
