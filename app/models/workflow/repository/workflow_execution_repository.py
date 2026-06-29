import logging
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from models.workflow.entity.workflow_execution_entity import WorkflowExecutionEntity
from models.workflow.entity.workflow_execution_model import WorkflowExecution
from models.workflow.mapper.workflow_execution_mapper import WorkflowExecutionMapper
from core.repository.backends.postgresql import SqlAlchemyRepository

logger = logging.getLogger(__name__)


class WorkflowExecutionRepository(SqlAlchemyRepository[WorkflowExecution]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, WorkflowExecutionEntity, WorkflowExecution, WorkflowExecutionMapper)

    async def create_execution(self, execution_id: str, workflow_id: int, input_data: dict) -> WorkflowExecution:
        entity = WorkflowExecutionEntity(
            id=int(execution_id.replace("-", ""), 16) % (2**63),
            workflow_id=workflow_id,
            status="running",
            input_data=input_data,
            started_at=datetime.now(timezone.utc),
        )
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return WorkflowExecutionMapper.to_domain(entity)

    async def update_execution(self, execution_id: str, status: str, output_data: Optional[dict] = None):
        entity_id = int(execution_id.replace("-", ""), 16) % (2**63)
        stmt = select(WorkflowExecutionEntity).where(WorkflowExecutionEntity.id == entity_id)
        result = await self.session.execute(stmt)
        entity = result.scalar_one_or_none()
        if entity:
            entity.status = status
            entity.output_data = output_data
            entity.finished_at = datetime.now(timezone.utc)
            await self.session.commit()
