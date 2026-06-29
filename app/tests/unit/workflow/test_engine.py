import pytest
from unittest.mock import AsyncMock, MagicMock
from core.workflow.types import WorkflowStep, StepType, StepStatus, StepResult


class TestStepTypes:
    def test_step_type_enum_values(self):
        assert StepType.LLM == "llm"
        assert StepType.FUNCTION == "function"
        assert StepType.CONDITION == "condition"
        assert StepType.HTTP == "http"

    def test_step_status_values(self):
        assert StepStatus.SUCCESS == "success"
        assert StepStatus.FAILURE == "failure"

    def test_workflow_step_defaults(self):
        step = WorkflowStep(id="1", name="test", step_order=1, step_type=StepType.LLM)
        assert step.is_terminal is False
        assert step.config == {}
        assert step.llm_max_tokens == 1000

    def test_step_result_success(self):
        result = StepResult(step_id="1", status=StepStatus.SUCCESS, output="hello")
        assert result.status == StepStatus.SUCCESS
        assert result.output == "hello"
        assert result.error is None
