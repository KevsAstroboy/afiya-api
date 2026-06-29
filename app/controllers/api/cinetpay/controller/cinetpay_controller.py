import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from services.cinetpay.cinetpay_service import CinetPayService
from core.workflow.engine import WorkflowEngine
from core.workflow.providers.factory import LLMProviderFactory
from core.workflow.postgresql_workflow_db import PostgreSQLWorkflowDB
from core.workflow.checks import BusinessChecks
from models.paiement.entity.paiement_model import Paiement
from models.paiement.mapper.paiement_mapper import PaiementMapper
from models.paiement.entity.paiement_entity import PaiementEntity
from sqlalchemy import select
from core.repository.backends.postgresql import SqlAlchemyRepository

logger = logging.getLogger(__name__)

cinetpay_router = APIRouter(prefix="/api/webhook/cinetpay", tags=["Webhook - CinetPay"])


@cinetpay_router.post("")
async def cinetpay_webhook(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    cinetpay = CinetPayService()
    body = await request.body()
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    received_signature = request.headers.get("X-CinetPay-Signature", payload.get("signature", ""))
    if not cinetpay.validate_ipn_signature(payload, received_signature):
        raise HTTPException(status_code=403, detail="Invalid CinetPay signature")

    transaction_id = payload.get("cpm_trans_id", payload.get("transaction_id", ""))
    status = payload.get("cpm_result", payload.get("status", ""))
    logger.info(f"CinetPay IPN received: tx={transaction_id}, status={status}")

    repo = SqlAlchemyRepository(session, PaiementEntity, Paiement, PaiementMapper)
    existing = await repo.find_one({"transaction_id": transaction_id})
    if not existing:
        raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")

    if status.upper() == "00":
        await repo.update(existing.id, {
            "verify_payload": json.dumps(payload),
            "date_validation": datetime.now(timezone.utc),
        })

        db = PostgreSQLWorkflowDB(session)
        provider = LLMProviderFactory.create()
        engine = WorkflowEngine(db, provider)
        checks = BusinessChecks(db)
        engine.register_check("check_record_exists", checks.check_record_exists)
        engine.register_check("check_fields_complete", checks.check_fields_complete)
        engine.register_check("check_payment_status", checks.check_payment_status)

        try:
            await engine.run(
                "1",
                {
                    "input_transaction_id": transaction_id,
                    "input_consultation_id": existing.consultation_id,
                },
            )
        except ValueError:
            logger.warning(f"No post-payment workflow configured for transaction {transaction_id}")

    return {"status": "processed"}
