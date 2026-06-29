import logging
from fastapi import APIRouter, HTTPException, Query

from services.analytics.analytics_service import get_analytics

logger = logging.getLogger(__name__)

analytics_router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@analytics_router.get("")
async def analytics(
    date_debut: str = Query(default="", description="YYYY-MM-DD, default=today"),
    date_fin: str = Query(default="", description="YYYY-MM-DD, default=today"),
    period: str = Query(default="day", description="day|week|month|year"),
):
    if not date_debut:
        from datetime import datetime, timezone
        date_debut = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not date_fin:
        from datetime import datetime, timezone
        date_fin = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if period not in ("day", "week", "month", "year"):
        raise HTTPException(400, "Period must be day, week, month, or year")

    try:
        return get_analytics(date_debut, date_fin, period)
    except Exception as e:
        logger.exception("Analytics error")
        raise HTTPException(500, str(e))
