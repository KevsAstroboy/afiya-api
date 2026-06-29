import logging
from typing import Any

from core.workflow.types import StepStatus, StepResult, WorkflowStep
from core.workflow.validators import Validators

logger = logging.getLogger(__name__)

LLM_SYSTEM_PROMPT = (
    "Tu es un assistant WhatsApp bienveillant qui collecte des informations medicales. "
    "Tes messages sont courts, clairs et chaleureux. "
    "Tu n'utilises pas de markdown sauf le gras (*mot*) supporte par WhatsApp. "
    "Tu ne poses qu'une seule question a la fois."
)


class LLMActionHandler:
    def __init__(self, llm_provider: Any, validators: Validators):
        self.provider = llm_provider
        self.validators = validators

    async def run(self, step: WorkflowStep, context: dict) -> StepResult:
        config = step.config
        raw = context.get("user_message", "").strip()
        validator_name = config.get("validator")
        target = config.get("context_target")

        validation = self._validate(validator_name, raw, config)

        if validation.valid:
            if target:
                context[target] = validation.value
            reply = await self._format_success(step, context, validation.value)
            return StepResult(
                step_id=step.id,
                status=StepStatus.SUCCESS,
                output={
                    "collected_key": target,
                    "collected_value": validation.value,
                    "whatsapp_reply": reply,
                },
            )
        else:
            reply = await self._format_error(step, validation.reason or "", raw)
            return StepResult(
                step_id=step.id,
                status=StepStatus.FAILURE,
                output={
                    "collected_key": None,
                    "collected_value": None,
                    "whatsapp_reply": reply,
                },
            )

    def _validate(self, validator_name: str | None, raw: str, config: dict):
        from core.workflow.types import ValidationResult
        if not validator_name:
            return ValidationResult(valid=True, value=raw)
        validator_fn = self.validators.get(validator_name)
        if not validator_fn:
            logger.error("[VALIDATOR] '%s' non enregistre", validator_name)
            return ValidationResult(valid=False, reason=f"Validator '{validator_name}' introuvable.")
        kwargs = {k: v for k, v in config.items() if k not in ("validator", "context_target")}
        try:
            return validator_fn(raw, **kwargs)
        except Exception as exc:
            logger.exception("[VALIDATOR] Erreur sur '%s'", validator_name)
            return ValidationResult(valid=False, reason=str(exc))

    async def _format_success(self, step: WorkflowStep, context: dict, value: Any) -> str:
        prompt = step.llm_prompt_success.format_map({**context, "collected_value": value})
        return await self._call_llm(step, prompt)

    async def _format_error(self, step: WorkflowStep, reason: str, raw: str) -> str:
        prompt = step.llm_prompt_error.format_map({"error_reason": reason, "user_input": raw})
        return await self._call_llm(step, prompt)

    async def _call_llm(self, step: WorkflowStep, prompt: str) -> str:
        try:
            text = await self.provider.generate(prompt, step.llm_model, step.llm_max_tokens)
            return text.strip()
        except Exception as exc:
            logger.exception("[LLM] Erreur formatage message")
            return "Une erreur est survenue. Veuillez reessayer."
