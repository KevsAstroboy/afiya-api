import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from core.workflow.dynamodb_workflow_db import DynamoDBWorkflowDB
from services.whatsapp.whatsapp_service import WhatsAppService
from core.workflow.session_manager import SessionManager
from core.workflow.redis_session import RedisSessionStore
from core.workflow.engine import WorkflowEngine
from core.workflow.providers.factory import LLMProviderFactory
from core.workflow.postgresql_workflow_db import PostgreSQLWorkflowDB
from core.workflow.checks import BusinessChecks

logger = logging.getLogger(__name__)

whatsapp_router = APIRouter(prefix="/api/webhook/whatsapp", tags=["Webhook - WhatsApp"])


@whatsapp_router.get("")
async def verify_webhook(
    hub_mode: str = "",
    hub_verify_token: str = "",
    hub_challenge: str = "",
):
    wa = WhatsAppService()
    result = wa.verify_webhook(hub_mode, hub_verify_token, hub_challenge)
    if result is not None:
        return int(result) if result.isdigit() else result
    raise HTTPException(status_code=403, detail="Verification failed")


@whatsapp_router.post("")
async def receive_message(
    request: Request,
):
    wa = WhatsAppService()
    body = await request.json()
    wa_id, message_text, wamid, profile_name = wa.parse_message(body)

    if not wa_id or not message_text:
        return {"status": "ignored"}

    logger.info(f"WhatsApp message from {wa_id} ({profile_name}): {message_text}")

    db = DynamoDBWorkflowDB()
    provider = LLMProviderFactory.create()
    engine = WorkflowEngine(db, provider)

    store = RedisSessionStore()
    mgr = SessionManager(store, engine, db)

    reply = await mgr.handle_message(wa_id, message_text, profile_name)
    await wa.send_text_message(wa_id, reply)

    return {"status": "replied"}
