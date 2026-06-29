import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session, PostgreSQLBackend
from core.workflow.engine import WorkflowEngine
from core.workflow.providers.factory import LLMProviderFactory
from core.workflow.postgresql_workflow_db import PostgreSQLWorkflowDB
from core.workflow.checks import BusinessChecks
from models.workflow.workflow_schemas import WorkflowExecuteRequestSchema, WorkflowExecuteResponseSchema

logger = logging.getLogger(__name__)

workflow_router = APIRouter(prefix="/api/workflow", tags=["Workflow"])


@workflow_router.post("/execute", response_model=WorkflowExecuteResponseSchema)
async def execute_workflow(
    payload: WorkflowExecuteRequestSchema,
    session: AsyncSession = Depends(get_async_session),
):
    db = PostgreSQLWorkflowDB(session)
    checks = BusinessChecks(db)
    provider = LLMProviderFactory.create()
    engine = WorkflowEngine(db, provider)
    engine.register_check("check_record_exists", checks.check_record_exists)
    engine.register_check("check_fields_complete", checks.check_fields_complete)
    engine.register_check("check_payment_status", checks.check_payment_status)
    try:
        result = await engine.run(str(payload.workflow_id), payload.input_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Workflow execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
