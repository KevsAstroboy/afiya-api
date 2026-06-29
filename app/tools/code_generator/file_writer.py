"""
file_writer.py
--------------
Rendu des templates et écriture des fichiers générés dans le projet.

Usage:
    from app.tools.code_generator.file_writer import FileWriter
    writer = FileWriter(project_root="/path/to/app")
    writer.write_all("sexe", metadata)
"""

import os
import logging
from typing import Dict, Any, List
from pathlib import Path

from tools.code_generator.db_inspector import ColumnInfo, AUDIT_FIELDS

logger = logging.getLogger(__name__)

# Imports SQLAlchemy qui seront toujours présents
BASE_SA_IMPORTS = {"Column", "BigInteger", "DateTime", "func"}
AUDIT_SA_IMPORTS = {"Boolean", "Text"}


class FileWriter:
    """
    Génère et écrit tous les fichiers CRUD pour une table donnée.
    Suit strictement l'architecture du projet :

        app/
        ├── models/{table}/
        │   ├── entity/{table}_entity.py   (SQLAlchemy)
        │   ├── entity/{table}_model.py    (dataclass)
        │   ├── mapper/{table}_mapper.py
        │   ├── repository/{table}_repository.py
        │   └── {table}_schemas.py         (Pydantic)
        ├── services/{table}/
        │   └── {table}_service.py
        └── controllers/api/{table}/controller/
            └── {table}_controller.py
    """

    def __init__(self, project_root: str):
        self.root = Path(project_root)
        self.tpl_dir = Path(__file__).parent / "templates"

    # ------------------------------------------------------------------ #
    #  Point d'entrée principal                                           #
    # ------------------------------------------------------------------ #

    def write_all(self, table_name: str, metadata: Dict[str, Any]) -> List[str]:
        """
        Génère tous les fichiers pour une table.
        Retourne la liste des fichiers créés.
        """
        created = []
        cn         = metadata["class_name"]
        columns    = metadata["columns"]
        has_audit  = metadata["has_audit"]
        url_slug   = metadata["url_slug"]

        created += self._write_entity(table_name, cn, columns, has_audit)
        created += self._write_model(table_name, cn, columns, has_audit)
        created += self._write_mapper(table_name, cn, columns, has_audit)
        created += self._write_repository(table_name, cn, has_audit)
        created += self._write_schemas(table_name, cn, columns)
        created += self._write_service(table_name, cn, has_audit)
        created += self._write_controller(table_name, cn, url_slug)

        return created

    # ------------------------------------------------------------------ #
    #  Entity                                                              #
    # ------------------------------------------------------------------ #

    def _write_entity(self, table, cn, columns: List[ColumnInfo], has_audit: bool):
        # Calcul des imports SQLAlchemy nécessaires
        sa_types = set(BASE_SA_IMPORTS)
        if has_audit:
            sa_types |= AUDIT_SA_IMPORTS

        has_fk = any(c.fk_table for c in columns)
        if has_fk:
            sa_types.add("ForeignKey")

        for col in columns:
            base = col.sa_type.split("(")[0]
            sa_types.add(base)

        sa_imports = ", ".join(sorted(sa_types))

        col_lines = "\n".join(col.to_sa_column() for col in columns)

        if has_audit:
            audit_block = """
    # Audit fields
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    deleted_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    deletion_reason = Column(Text, nullable=True)"""
        else:
            audit_block = ""

        content = f"""from sqlalchemy import {sa_imports}
from sqlalchemy.dialects.postgresql import JSON
from app.core.database import Base


class {cn}Entity(Base):
    __tablename__ = "{table}"
    __table_args__ = {{"schema": "public"}}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
{col_lines}
{audit_block}

    def __repr__(self):
        return f"<{cn}Entity(id={{self.id}})>"
"""
        return self._write_file(
            self.root / "models" / table / "entity" / f"{table}_entity.py",
            content,
            init=f"from .{table}_entity import {cn}Entity\n",
            init_path=self.root / "models" / table / "entity" / "__init__.py"
        )

    # ------------------------------------------------------------------ #
    #  Domain Model                                                        #
    # ------------------------------------------------------------------ #

    def _write_model(self, table, cn, columns: List[ColumnInfo], has_audit: bool):
        required = [c for c in columns if not c.is_nullable]
        optional = [c for c in columns if c.is_nullable]

        req_lines = "\n".join(f"    {c.name}: {c.py_type}" for c in required)
        opt_lines = "\n".join(f"    {c.name}: Optional[{c.py_type}] = None" for c in optional)

        has_datetime = any(c.py_type in ("datetime", "date") for c in columns)
        dt_import = "from datetime import datetime\n" if (has_datetime or has_audit) else ""

        audit_fields = """    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None
    is_deleted: bool = field(default=False)
    deletion_reason: Optional[str] = None""" if has_audit else ""

        content = f"""from dataclasses import dataclass, field
from typing import Optional
{dt_import}

@dataclass
class {cn}:
{req_lines if req_lines else "    pass  # no required fields"}
    id: Optional[int] = None
{opt_lines}
{audit_fields}
"""
        return self._write_file(
            self.root / "models" / table / "entity" / f"{table}_model.py",
            content
        )

    # ------------------------------------------------------------------ #
    #  Mapper                                                              #
    # ------------------------------------------------------------------ #

    def _write_mapper(self, table, cn, columns: List[ColumnInfo], has_audit: bool):
        all_cols = [c.name for c in columns]

        domain_fields = "\n".join(f"            {n}=entity.{n}," for n in all_cols)
        entity_fields = "\n".join(f"            {n}=domain.{n}," for n in all_cols)

        audit_to_domain = """            is_deleted=entity.is_deleted,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
            created_by=entity.created_by,
            updated_by=entity.updated_by,
            deleted_by=entity.deleted_by,
            deletion_reason=entity.deletion_reason,""" if has_audit else ""

        audit_to_entity = """            is_deleted=domain.is_deleted,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            deleted_at=domain.deleted_at,
            created_by=domain.created_by,
            updated_by=domain.updated_by,
            deleted_by=domain.deleted_by,
            deletion_reason=domain.deletion_reason,""" if has_audit else ""

        content = f"""from typing import Optional, List
from app.models.{table}.entity.{table}_entity import {cn}Entity
from app.models.{table}.entity.{table}_model import {cn}


class {cn}Mapper:
    \"\"\"Mapper for {cn} entity\"\"\"

    @classmethod
    def to_domain(cls, entity: Optional[{cn}Entity]) -> Optional[{cn}]:
        if entity is None:
            return None
        return {cn}(
            id=entity.id,
{domain_fields}
{audit_to_domain}
        )

    @staticmethod
    def to_entity(domain: {cn}) -> {cn}Entity:
        return {cn}Entity(
            id=domain.id,
{entity_fields}
{audit_to_entity}
        )

    @classmethod
    def to_domain_list(cls, entities: List[{cn}Entity]) -> List[{cn}]:
        return [cls.to_domain(e) for e in entities] if entities else []
"""
        return self._write_file(
            self.root / "models" / table / "mapper" / f"{table}_mapper.py",
            content,
            init=f"from .{table}_mapper import {cn}Mapper\n",
            init_path=self.root / "models" / table / "mapper" / "__init__.py"
        )

    # ------------------------------------------------------------------ #
    #  Repository                                                          #
    # ------------------------------------------------------------------ #

    def _write_repository(self, table, cn, has_audit: bool):
        soft_delete = f"""            # Soft delete
            entity.is_deleted = True
            entity.deleted_at = datetime.now()
            entity.deleted_by = deleted_by""" if has_audit else """            # Hard delete
            await self.session.delete(entity)"""

        is_deleted_filter = f",\n                {cn}Entity.is_deleted == False" if has_audit else ""
        get_all_filter = f".where({cn}Entity.is_deleted == False)" if has_audit else ""

        content = f"""import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.{table}.entity.{table}_entity import {cn}Entity
from app.models.{table}.entity.{table}_model import {cn}
from app.models.{table}.mapper.{table}_mapper import {cn}Mapper
from app.core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class {cn}Repository:
    \"\"\"Repository for {cn} CRUD operations\"\"\"

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, domain: {cn}) -> {cn}:
        try:
            entity = {cn}Mapper.to_entity(domain)
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            return {cn}Mapper.to_domain(entity)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating {cn}: {{e}}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[{cn}]:
        try:
            stmt = select({cn}Entity).where(
                {cn}Entity.id == record_id{is_deleted_filter}
            )
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(
                    f"{cn} with id {{record_id}} not found",
                    ErrorType.NOT_FOUND
                )
            return {cn}Mapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Error fetching {cn} {{record_id}}: {{e}}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[{cn}]:
        try:
            stmt = select({cn}Entity){get_all_filter}.offset(skip).limit(limit)
            result = await self.session.execute(stmt)
            return {cn}Mapper.to_domain_list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error fetching {cn} list: {{e}}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def update(self, record_id: int, updates: dict) -> {cn}:
        try:
            await self.get_by_id(record_id)
            stmt = select({cn}Entity).where({cn}Entity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"{cn} {{record_id}} not found", ErrorType.NOT_FOUND)
            updates["updated_at"] = datetime.now()
            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            await self.session.commit()
            await self.session.refresh(entity)
            return {cn}Mapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating {cn} {{record_id}}: {{e}}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        try:
            stmt = select({cn}Entity).where({cn}Entity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"{cn} {{record_id}} not found", ErrorType.NOT_FOUND)
{soft_delete}
            await self.session.commit()
            return True
        except BusinessException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting {cn} {{record_id}}: {{e}}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)
"""
        return self._write_file(
            self.root / "models" / table / "repository" / f"{table}_repository.py",
            content,
            init=f"from .{table}_repository import {cn}Repository\n",
            init_path=self.root / "models" / table / "repository" / "__init__.py"
        )

    # ------------------------------------------------------------------ #
    #  Schemas Pydantic                                                    #
    # ------------------------------------------------------------------ #

    def _write_schemas(self, table, cn, columns: List[ColumnInfo]):
        required = [c for c in columns if not c.is_nullable]
        optional = [c for c in columns if c.is_nullable]

        create_required = "\n".join(f"    {c.name}: {c.py_type}" for c in required)
        create_optional = "\n".join(
            f"    {c.name}: Optional[{c.py_type}] = None" for c in optional
        )
        create_fields = "\n".join(filter(None, [create_required, create_optional])) or "    pass"

        update_fields = "\n".join(
            f"    {c.name}: Optional[{c.py_type}] = None"
            for c in required + optional
        ) or "    pass"

        response_required = "\n".join(f"    {c.name}: {c.py_type}" for c in required)
        response_optional = "\n".join(
            f"    {c.name}: Optional[{c.py_type}] = None" for c in optional
        )
        response_fields = "\n".join(filter(None, [response_required, response_optional]))

        content = f"""from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class {cn}CreateSchema(BaseModel):
{create_fields}

    class Config:
        from_attributes = True


class {cn}UpdateSchema(BaseModel):
{update_fields}

    class Config:
        from_attributes = True


class {cn}ResponseSchema(BaseModel):
    id: int
{response_fields}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
"""
        files = self._write_file(
            self.root / "models" / table / f"{table}_schemas.py",
            content
        )
        # __init__.py du model package
        init_path = self.root / "models" / table / "__init__.py"
        if not init_path.exists():
            init_path.write_text("")
        return files

    # ------------------------------------------------------------------ #
    #  Service                                                             #
    # ------------------------------------------------------------------ #

    def _write_service(self, table, cn, has_audit: bool):
        deleted_by_arg = ", deleted_by: Optional[int] = None" if has_audit else ""
        deleted_by_pass = ", deleted_by=deleted_by" if has_audit else ""

        content = f"""import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.{table}.entity.{table}_model import {cn}
from app.models.{table}.repository.{table}_repository import {cn}Repository
from app.core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class {cn}Service:
    \"\"\"Service layer for {cn} business logic\"\"\"

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = {cn}Repository(session)

    async def create(self, domain: {cn}) -> {cn}:
        \"\"\"Create a new {cn}\"\"\"
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating {cn}: {{e}}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[{cn}]:
        \"\"\"Get {cn} by ID\"\"\"
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[{cn}]:
        \"\"\"Get all {cn} records\"\"\"
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> {cn}:
        \"\"\"Update {cn}\"\"\"
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int{deleted_by_arg}) -> bool:
        \"\"\"Delete {cn}\"\"\"
        return await self.repository.delete(record_id{deleted_by_pass})
"""
        return self._write_file(
            self.root / "services" / table / f"{table}_service.py",
            content,
            init=f"from .{table}_service import {cn}Service\n",
            init_path=self.root / "services" / table / "__init__.py"
        )

    # ------------------------------------------------------------------ #
    #  Controller                                                          #
    # ------------------------------------------------------------------ #

    def _write_controller(self, table, cn, url_slug: str):
        content = f"""import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.models.{table}.entity.{table}_model import {cn}
from app.services.{table}.{table}_service import {cn}Service
from app.models.{table}.{table}_schemas import {cn}CreateSchema, {cn}UpdateSchema, {cn}ResponseSchema
from app.core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)

{table}_router = APIRouter(prefix="/api/{url_slug}", tags=["{cn}"])


@{table}_router.post("/", response_model={cn}ResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_{table}(
    payload: {cn}CreateSchema,
    session: AsyncSession = Depends(get_async_session)
):
    \"\"\"Create a new {cn}\"\"\"
    try:
        service = {cn}Service(session)
        domain = {cn}(**payload.model_dump())
        return await service.create(domain)
    except BusinessException as e:
        raise HTTPException(
            status_code=400 if e.error_type != ErrorType.ALREADY_EXISTS else 409,
            detail=e.to_dict()
        )


@{table}_router.get("/", response_model=List[{cn}ResponseSchema])
async def get_all_{table}s(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_async_session)
):
    \"\"\"Get all {cn} records\"\"\"
    try:
        service = {cn}Service(session)
        return await service.get_all(skip=skip, limit=limit)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@{table}_router.get("/{{record_id}}", response_model={cn}ResponseSchema)
async def get_{table}_by_id(
    record_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    \"\"\"Get {cn} by ID\"\"\"
    try:
        service = {cn}Service(session)
        return await service.get_by_id(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@{table}_router.put("/{{record_id}}", response_model={cn}ResponseSchema)
async def update_{table}(
    record_id: int,
    payload: {cn}UpdateSchema,
    session: AsyncSession = Depends(get_async_session)
):
    \"\"\"Update {cn}\"\"\"
    try:
        service = {cn}Service(session)
        updates = {{k: v for k, v in payload.model_dump().items() if v is not None}}
        return await service.update(record_id, updates)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())


@{table}_router.delete("/{{record_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{table}(
    record_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    \"\"\"Delete {cn}\"\"\"
    try:
        service = {cn}Service(session)
        await service.delete(record_id)
    except BusinessException as e:
        status_code = 404 if e.error_type == ErrorType.NOT_FOUND else 400
        raise HTTPException(status_code=status_code, detail=e.to_dict())
"""
        ctrl_dir = self.root / "controllers" / "api" / table / "controller"
        return self._write_file(
            ctrl_dir / f"{table}_controller.py",
            content,
            init=f"from .{table}_controller import {table}_router\n",
            init_path=ctrl_dir / "__init__.py"
        )

    # ------------------------------------------------------------------ #
    #  Utilitaire d'écriture                                               #
    # ------------------------------------------------------------------ #

    def _write_file(
        self,
        path: Path,
        content: str,
        init: str = None,
        init_path: Path = None
    ) -> List[str]:
        """Crée les dossiers et écrit le fichier. Retourne les chemins créés."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        created = [str(path)]

        if init and init_path:
            init_path.write_text(init, encoding="utf-8")
            created.append(str(init_path))

        return created
