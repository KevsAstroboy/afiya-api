import logging
import operator
from typing import Any, Callable, Optional

from core.workflow.types import StepType, StepStatus, WorkflowStep, StepResult

logger = logging.getLogger(__name__)


class LLMHandler:
    def __init__(self, provider: Any):
        self.provider = provider

    async def run(self, step: WorkflowStep, context: dict) -> StepResult:
        if not step.llm_prompt:
            return StepResult(step.id, StepStatus.FAILURE, error="Prompt manquant")
        try:
            prompt = step.llm_prompt.format_map(context)
        except KeyError as e:
            return StepResult(step.id, StepStatus.FAILURE, error=f"Variable manquante dans le prompt : {e}")
        try:
            text = await self.provider.generate(prompt, step.llm_model, step.llm_max_tokens)
            text = text.strip()
            try:
                text = float(text)
            except ValueError:
                pass
            return StepResult(step.id, StepStatus.SUCCESS, output=text)
        except Exception as exc:
            return StepResult(step.id, StepStatus.FAILURE, error=str(exc))


class FunctionHandler:
    def __init__(self):
        self._registry: dict[str, Callable] = {}

    def register(self, name: str, fn: Callable) -> None:
        self._registry[name] = fn

    async def run(self, step: WorkflowStep, context: dict) -> StepResult:
        fn_name = step.config.get("function_name")
        fn = self._registry.get(fn_name)
        if not fn:
            return StepResult(step.id, StepStatus.FAILURE, error=f"Fonction '{fn_name}' non enregistree")
        kwargs = {k: v for k, v in step.config.items() if k != "function_name"}
        try:
            result = fn(context, **kwargs)
            from core.workflow.types import CheckResult
            if isinstance(result, CheckResult):
                status = StepStatus.SUCCESS if result.passed else StepStatus.FAILURE
                return StepResult(step.id, status, output={"reason": result.reason, "data": result.data})
            return StepResult(step.id, StepStatus.SUCCESS, output=result)
        except Exception as exc:
            return StepResult(step.id, StepStatus.FAILURE, error=str(exc))


class ConditionHandler:
    OPERATORS = {
        "==": operator.eq,
        "!=": operator.ne,
        ">": operator.gt,
        ">=": operator.ge,
        "<": operator.lt,
        "<=": operator.le,
        "in": lambda a, b: a in b,
        "not_in": lambda a, b: a not in b,
    }

    async def run(self, step: WorkflowStep, context: dict) -> StepResult:
        config = step.config
        left_key = config.get("left")
        op_symbol = config.get("operator")
        if left_key not in context:
            return StepResult(step.id, StepStatus.FAILURE, error=f"Cle '{left_key}' absente du contexte")
        left_val = context[left_key]
        right_val = context[config["right"]] if config.get("right_is_key") else config.get("right")
        op_fn = self.OPERATORS.get(op_symbol)
        if not op_fn:
            return StepResult(step.id, StepStatus.FAILURE, error=f"Operateur '{op_symbol}' non supporte")
        try:
            result = op_fn(left_val, right_val)
        except TypeError as exc:
            return StepResult(step.id, StepStatus.FAILURE, error=f"Erreur de type : {exc}")
        status = StepStatus.SUCCESS if result else StepStatus.FAILURE
        return StepResult(step.id, status, output={"condition_result": result})


class HttpHandler:
    def __init__(self):
        import httpx
        self._client = None

    async def _get_client(self):
        if self._client is None:
            import httpx
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def run(self, step: WorkflowStep, context: dict) -> StepResult:
        config = step.config
        url_template = config.get("url", "")
        method = config.get("method", "POST")
        body_template = config.get("body_template", "")
        headers_template = config.get("headers", {})
        success_status = config.get("success_status", 200)
        auth_type = config.get("auth_type")

        try:
            url = url_template.format_map(context)
            body = body_template.format_map(context) if body_template else None
            headers = {k: v.format_map(context) for k, v in headers_template.items()} if headers_template else {}
        except KeyError as e:
            return StepResult(step.id, StepStatus.FAILURE, error=f"Variable manquante dans le template HTTP : {e}")

        import httpx
        client = await self._get_client()

        auth = None
        if auth_type == "basic":
            username = config.get("auth_username", "").format_map(context)
            password = config.get("auth_password", "").format_map(context)
            auth = httpx.BasicAuth(username, password)

        try:
            response = await client.request(
                method=method,
                url=url,
                content=body,
                headers=headers,
                auth=auth,
            )
            if response.status_code == success_status:
                return StepResult(step.id, StepStatus.SUCCESS, output=response.text)
            return StepResult(
                step.id, StepStatus.FAILURE,
                error=f"HTTP {response.status_code}: {response.text[:500]}"
            )
        except Exception as exc:
            return StepResult(step.id, StepStatus.FAILURE, error=str(exc))
