import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from core.workflow.db_interface import WorkflowDBInterface
from core.workflow.types import WorkflowStep, StepType, StepResult
from models.workflow.repository.workflow_step_repository import WorkflowStepRepository
from models.workflow.repository.workflow_execution_repository import WorkflowExecutionRepository
from models.workflow.repository.step_execution_repository import StepExecutionRepository
from core.repository.backends.postgresql import SqlAlchemyRepository

logger = logging.getLogger(__name__)

_BUSINESS_REPOSITORIES: Dict[str, type] = {}


def register_business_repository(table: str, entity_class: type, domain_class: type, mapper: Any):
    _BUSINESS_REPOSITORIES[table] = (entity_class, domain_class, mapper)


class PostgreSQLWorkflowDB(WorkflowDBInterface):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.step_repo = WorkflowStepRepository(session)
        self.exec_repo = WorkflowExecutionRepository(session)
        self.step_exec_repo = StepExecutionRepository(session)
        self._repo_cache: Dict[str, SqlAlchemyRepository] = {}

    async def get_steps_by_workflow(self, workflow_id: str) -> List[WorkflowStep]:
        steps = await self.step_repo.get_by_workflow_id(int(workflow_id))
        return [
            WorkflowStep(
                id=str(s.id),
                name=s.name,
                step_order=s.step_order,
                step_type=StepType(s.step_type),
                llm_prompt=s.llm_prompt,
                llm_model=s.llm_model or "claude-sonnet-4-20250514",
                llm_max_tokens=s.llm_max_tokens or 1000,
                on_success_step_id=str(s.on_success_step_id) if s.on_success_step_id else None,
                on_failure_step_id=str(s.on_failure_step_id) if s.on_failure_step_id else None,
                is_terminal=s.is_terminal,
                llm_prompt_success=s.llm_prompt_success or "",
                llm_prompt_error=s.llm_prompt_error or "",
                config=s.config or {},
            )
            for s in steps
        ]

    async def create_execution(self, execution_id: str, workflow_id: str, input_data: dict) -> None:
        await self.exec_repo.create_execution(execution_id, int(workflow_id), input_data)

    async def save_step_execution(self, execution_id: str, result: StepResult) -> None:
        await self.step_exec_repo.save_step_execution(execution_id, result)

    async def update_execution(self, execution_id: str, status: str, output_data: Optional[dict] = None) -> None:
        await self.exec_repo.update_execution(execution_id, status, output_data)

    async def find_one(self, table: str, filters: Dict[str, Any]) -> Optional[Any]:
        import importlib
        if table not in _BUSINESS_REPOSITORIES:
            module_name = f"models.{table}.entity.{table}_entity"
            model_name = f"models.{table}.entity.{table}_model"
            mapper_name = f"models.{table}.mapper.{table}_mapper"
            try:
                entity_mod = importlib.import_module(module_name)
                model_mod = importlib.import_module(model_name)
                mapper_mod = importlib.import_module(mapper_name)
            except ImportError:
                logger.warning(f"Could not import entity/model/mapper for table '{table}'")
                return None
            entity_class = getattr(entity_mod, [n for n in dir(entity_mod) if n.endswith('Entity')][0])
            domain_class = getattr(model_mod, [n for n in dir(model_mod) if not n.startswith('_')][0])
            mapper = getattr(mapper_mod, [n for n in dir(mapper_mod) if n.endswith('Mapper')][0])
            _BUSINESS_REPOSITORIES[table] = (entity_class, domain_class, mapper)

        entity_class, domain_class, mapper = _BUSINESS_REPOSITORIES[table]
        repo = SqlAlchemyRepository(self.session, entity_class, domain_class, mapper)
        return await repo.find_one(filters)

    async def insert(self, table: str, data: Dict[str, Any]) -> str:
        import importlib, uuid
        if table not in _BUSINESS_REPOSITORIES:
            module_name = f"models.{table}.entity.{table}_entity"
            model_name = f"models.{table}.entity.{table}_model"
            mapper_name = f"models.{table}.mapper.{table}_mapper"
            try:
                entity_mod = importlib.import_module(module_name)
                model_mod = importlib.import_module(model_name)
                mapper_mod = importlib.import_module(mapper_name)
            except ImportError:
                logger.warning(f"Could not import entity/model/mapper for table '{table}'")
                return ""
            entity_class = getattr(entity_mod, [n for n in dir(entity_mod) if n.endswith('Entity')][0])
            domain_class = getattr(model_mod, [n for n in dir(model_mod) if not n.startswith('_')][0])
            mapper = getattr(mapper_mod, [n for n in dir(mapper_mod) if n.endswith('Mapper')][0])
            _BUSINESS_REPOSITORIES[table] = (entity_class, domain_class, mapper)

        entity_class, domain_class, mapper = _BUSINESS_REPOSITORIES[table]
        domain = domain_class(**data)
        repo = SqlAlchemyRepository(self.session, entity_class, domain_class, mapper)
        created = await repo.create(domain)
        return str(getattr(created, 'id', ''))
