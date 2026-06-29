from sqlalchemy import {sa_imports}
from sqlalchemy.dialects.postgresql import JSON
from app.core.database import Base


class {ClassName}Entity(Base):
    __tablename__ = "{table_name}"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
{columns}

    def __repr__(self):
        return f"<{ClassName}Entity(id={self.id})>"
