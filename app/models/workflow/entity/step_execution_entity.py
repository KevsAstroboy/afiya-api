from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, JSON, String, Text, func
from core.database import Base


class StepExecutionEntity(Base):
    __tablename__ = "step_execution"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    workflow_execution_id = Column(BigInteger, ForeignKey("public.workflow_execution.id"), nullable=False)
    step_id = Column(BigInteger, ForeignKey("public.workflow_step.id"), nullable=False)
    status = Column(String(50), nullable=False)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    llm_response = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<StepExecutionEntity(id={self.id}, status={self.status})>"
