from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, JSON, String, Text, func
from core.database import Base


class WorkflowExecutionEntity(Base):
    __tablename__ = "workflow_execution"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    workflow_id = Column(BigInteger, ForeignKey("public.workflow.id"), nullable=False)
    status = Column(String(50), nullable=False, default="running")
    input_data = Column(JSON, nullable=False, default={})
    output_data = Column(JSON, nullable=True)
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<WorkflowExecutionEntity(id={self.id}, status={self.status})>"
