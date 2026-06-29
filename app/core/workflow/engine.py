import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from core.workflow.types import StepType, StepStatus, WorkflowStep, StepResult
from core.workflow.handlers import LLMHandler, FunctionHandler, ConditionHandler, HttpHandler
from core.workflow.handlers.llm_action_handler import LLMActionHandler
from core.workflow.validators import Validators

logger = logging.getLogger(__name__)

NON_INTERACTIVE_STEPS = {StepType.CONDITION, StepType.FUNCTION}


class WorkflowEngine:
    def __init__(self, db: Any, llm_provider: Any):
        self.db = db
        self.llm_handler = LLMHandler(llm_provider)
        self.fn_handler = FunctionHandler()
        self.condition_handler = ConditionHandler()
        self.http_handler = HttpHandler()
        self.validators = Validators()
        self.llm_action_handler = LLMActionHandler(llm_provider, self.validators)

    def register_check(self, name: str, fn: Callable) -> None:
        self.fn_handler.register(name, fn)

    async def run(self, workflow_id: str, input_data: dict) -> dict:
        steps = await self.db.get_steps_by_workflow(workflow_id)
        if not steps:
            raise ValueError(f"Workflow '{workflow_id}' introuvable ou sans etapes")

        step_index = {s.id: s for s in steps}
        execution_id = str(uuid.uuid4())
        await self.db.create_execution(execution_id, workflow_id, input_data)
        context = dict(input_data)
        steps_log = []
        current_step = sorted(steps, key=lambda s: s.step_order)[0]

        while current_step is not None:
            result = await self._execute_step(current_step, context)
            if result.output is not None:
                context[f"step_{current_step.name}_output"] = result.output
            steps_log.append({
                "step_id": current_step.id,
                "step_name": current_step.name,
                "status": result.status.value,
                "output": result.output,
                "error": result.error,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            await self.db.save_step_execution(execution_id, result)
            if current_step.is_terminal:
                break
            next_id = (
                current_step.on_success_step_id
                if result.status == StepStatus.SUCCESS
                else current_step.on_failure_step_id
            )
            if next_id and next_id not in step_index:
                break
            current_step = step_index.get(next_id) if next_id else None

        final_status = "completed" if all(e["status"] == StepStatus.SUCCESS.value for e in steps_log) else "failed"
        await self.db.update_execution(execution_id, final_status, context)
        return {
            "execution_id": execution_id,
            "status": final_status,
            "context": context,
            "steps_log": steps_log,
        }

    async def _execute_step(self, step: WorkflowStep, context: dict) -> StepResult:
        try:
            if step.step_type == StepType.LLM:
                return await self.llm_handler.run(step, context)
            elif step.step_type == StepType.FUNCTION:
                return await self.fn_handler.run(step, context)
            elif step.step_type == StepType.CONDITION:
                return await self.condition_handler.run(step, context)
            elif step.step_type == StepType.HTTP:
                return await self.http_handler.run(step, context)
            elif step.step_type == StepType.LLM_ACTION:
                return await self.llm_action_handler.run(step, context)
            else:
                return StepResult(step.id, StepStatus.FAILURE, error=f"StepType '{step.step_type}' non supporte")
        except Exception as exc:
            logger.error(f"Error executing step {step.id}: {exc}")
            return StepResult(step.id, StepStatus.FAILURE, error=str(exc))

    async def get_step(self, workflow_id: str, step_id: str) -> WorkflowStep:
        steps = await self.db.get_steps_by_workflow(workflow_id)
        step_map = {s.id: s for s in steps}
        step = step_map.get(step_id)
        if not step:
            raise ValueError(f"Step '{step_id}' introuvable dans '{workflow_id}'")
        return step

    async def run_single_step(self, workflow_id: str, step_id: str, context: dict) -> dict:
        steps = await self.db.get_steps_by_workflow(workflow_id)
        step_map = {s.id: s for s in steps}
        step = step_map.get(step_id)
        if not step:
            raise ValueError(f"Step '{step_id}' introuvable dans le workflow '{workflow_id}'")

        result = await self._execute_step(step, context)

        next_step_id = (
            step.on_success_step_id
            if result.status == StepStatus.SUCCESS
            else step.on_failure_step_id
        )

        output = result.output or {}
        return {
            "status": result.status.value,
            "collected_key": output.get("collected_key"),
            "collected_value": output.get("collected_value"),
            "next_step_id": next_step_id if result.status == StepStatus.SUCCESS else None,
            "whatsapp_reply": output.get("whatsapp_reply", ""),
        }
