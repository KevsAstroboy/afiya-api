from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class WorkflowCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class WorkflowUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class WorkflowResponseSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkflowStepCreateSchema(BaseModel):
    workflow_id: int
    name: str
    step_order: int
    step_type: str
    description: Optional[str] = None
    llm_prompt: Optional[str] = None
    llm_model: Optional[str] = None
    llm_max_tokens: Optional[int] = None
    on_success_step_id: Optional[int] = None
    on_failure_step_id: Optional[int] = None
    is_terminal: bool = False
    config: Optional[dict] = {}


class WorkflowStepUpdateSchema(BaseModel):
    name: Optional[str] = None
    step_order: Optional[int] = None
    step_type: Optional[str] = None
    description: Optional[str] = None
    llm_prompt: Optional[str] = None
    llm_model: Optional[str] = None
    llm_max_tokens: Optional[int] = None
    on_success_step_id: Optional[int] = None
    on_failure_step_id: Optional[int] = None
    is_terminal: Optional[bool] = None
    config: Optional[dict] = None


class WorkflowStepResponseSchema(BaseModel):
    id: int
    workflow_id: int
    name: str
    step_order: int
    step_type: str
    description: Optional[str] = None
    llm_prompt: Optional[str] = None
    llm_model: Optional[str] = None
    llm_max_tokens: Optional[int] = None
    on_success_step_id: Optional[int] = None
    on_failure_step_id: Optional[int] = None
    is_terminal: bool
    config: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkflowExecutionResponseSchema(BaseModel):
    id: int
    workflow_id: int
    status: str
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StepExecutionResponseSchema(BaseModel):
    id: int
    workflow_execution_id: int
    step_id: int
    status: str
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    llm_response: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkflowExecuteRequestSchema(BaseModel):
    workflow_id: int
    input_data: dict = {}


class WorkflowExecuteResponseSchema(BaseModel):
    execution_id: str
    status: str
    context: Optional[dict] = None
    steps_log: Optional[list] = None
