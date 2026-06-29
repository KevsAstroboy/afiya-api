import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.workflow.entity.workflow_entity import WorkflowEntity
from models.workflow.entity.workflow_model import Workflow
from models.workflow.mapper.workflow_mapper import WorkflowMapper
from core.repository.backends.postgresql import SqlAlchemyRepository

logger = logging.getLogger(__name__)


class WorkflowRepository(SqlAlchemyRepository[Workflow]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, WorkflowEntity, Workflow, WorkflowMapper)
