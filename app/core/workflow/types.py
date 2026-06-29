from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class StepType(str, Enum):
    LLM = "llm"
    FUNCTION = "function"
    CONDITION = "condition"
    HTTP = "http"
    LLM_ACTION = "llm_action"


class StepStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"


@dataclass
class WorkflowStep:
    id: str
    name: str
    step_order: int
    step_type: StepType
    llm_prompt: Optional[str] = None
    llm_prompt_success: str = ""
    llm_prompt_error: str = ""
    llm_model: str = "claude-sonnet-4-20250514"
    llm_max_tokens: int = 1000
    on_success_step_id: Optional[str] = None
    on_failure_step_id: Optional[str] = None
    is_terminal: bool = False
    config: dict = field(default_factory=dict)


@dataclass
class StepResult:
    step_id: str
    status: StepStatus
    output: Any = None
    error: Optional[str] = None


@dataclass
class CheckResult:
    passed: bool
    reason: str
    data: Optional[dict] = None


@dataclass
class ValidationResult:
    valid: bool
    value: Any = None
    reason: Optional[str] = None
