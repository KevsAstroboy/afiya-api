from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text, func
from core.database import Base


class WorkflowStepEntity(Base):
    __tablename__ = "workflow_step"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    workflow_id = Column(BigInteger, ForeignKey("public.workflow.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    step_order = Column(Integer, nullable=False)
    step_type = Column(String(50), nullable=False)
    llm_prompt = Column(Text, nullable=True)
    llm_model = Column(String(100), nullable=True)
    llm_max_tokens = Column(Integer, nullable=True)
    on_success_step_id = Column(BigInteger, ForeignKey("public.workflow_step.id"), nullable=True)
    on_failure_step_id = Column(BigInteger, ForeignKey("public.workflow_step.id"), nullable=True)
    is_terminal = Column(Boolean, nullable=False, default=False)
    config = Column(JSON, nullable=False, default={})

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    deleted_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    deletion_reason = Column(Text, nullable=True)

    def __repr__(self):
        return f"<WorkflowStepEntity(id={self.id}, name={self.name})>"
