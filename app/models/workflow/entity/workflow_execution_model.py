from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class WorkflowExecution:
    workflow_id: int
    id: Optional[int] = None
    status: str = "running"
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
