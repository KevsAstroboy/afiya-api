import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.workflow.entity.workflow_step_entity import WorkflowStepEntity
from models.workflow.entity.workflow_step_model import WorkflowStep
from models.workflow.mapper.workflow_step_mapper import WorkflowStepMapper
from core.repository.backends.postgresql import SqlAlchemyRepository

logger = logging.getLogger(__name__)


class WorkflowStepRepository(SqlAlchemyRepository[WorkflowStep]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, WorkflowStepEntity, WorkflowStep, WorkflowStepMapper)

    async def get_by_workflow_id(self, workflow_id: int) -> List[WorkflowStep]:
        stmt = select(WorkflowStepEntity).where(
            WorkflowStepEntity.workflow_id == workflow_id,
            WorkflowStepEntity.is_deleted == False,
        ).order_by(WorkflowStepEntity.step_order.asc())
        result = await self.session.execute(stmt)
        return WorkflowStepMapper.to_domain_list(result.scalars().all())
