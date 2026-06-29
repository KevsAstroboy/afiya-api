from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class WorkflowStep:
    workflow_id: int
    name: str
    step_order: int
    step_type: str
    id: Optional[int] = None
    description: Optional[str] = None
    llm_prompt: Optional[str] = None
    llm_model: Optional[str] = None
    llm_max_tokens: Optional[int] = None
    on_success_step_id: Optional[int] = None
    on_failure_step_id: Optional[int] = None
    is_terminal: bool = False
    config: dict = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None
    is_deleted: bool = field(default=False)
    deletion_reason: Optional[str] = None
