from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from core.workflow.types import WorkflowStep, StepResult


class WorkflowDBInterface(ABC):
    @abstractmethod
    async def get_steps_by_workflow(self, workflow_id: str) -> List[WorkflowStep]:
        ...

    @abstractmethod
    async def create_execution(self, execution_id: str, workflow_id: str, input_data: dict) -> None:
        ...

    @abstractmethod
    async def save_step_execution(self, execution_id: str, result: StepResult) -> None:
        ...

    @abstractmethod
    async def update_execution(self, execution_id: str, status: str, output_data: Optional[dict] = None) -> None:
        ...

    @abstractmethod
    async def find_one(self, table: str, filters: Dict[str, Any]) -> Optional[Any]:
        ...

    @abstractmethod
    async def insert(self, table: str, data: Dict[str, Any]) -> str:
        ...
