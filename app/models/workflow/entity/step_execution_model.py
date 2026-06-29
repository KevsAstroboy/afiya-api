from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class StepExecution:
    workflow_execution_id: int
    step_id: int
    status: str
    id: Optional[int] = None
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    llm_response: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
