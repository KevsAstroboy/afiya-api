from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from core.config import settings
import logging
import importlib
import pkgutil
import sys

# Configuration complète du logging pour SQLAlchemy
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine.base.Engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)


class DatabaseManager:
    """
    Centralized database connection and session management
    """
    _engine = None
    _async_session = None

    @classmethod
    def get_engine(cls):
        try:
            """
            Create or return existing async engine
            """
            if not cls._engine:
                # Configure connection pooling and logging based on environment
                connect_args = {"server_settings": {"application_name": "telemedecine-api"}}

                engine_kwargs = {
                    "echo": False,  # Désactiver le logging SQL
                    "echo_pool": False,  # Désactiver le logging du pool de connexions
                    "future": True,
                    "pool_pre_ping": True,  # Connection health check
                    "pool_size": 10,  # Connection pool size
                    "max_overflow": 20,  # Additional connections if pool is full
                }

                cls._engine = create_async_engine(
                    str(settings.DATABASE_URL),
                    **engine_kwargs,
                    connect_args=connect_args
                )
            return cls._engine
        except Exception as e:
            logging.error(f"Database connection error: {e}")
            raise

    @classmethod
    async def create_all_tables(cls):
        """
        Dynamically discover and create all SQLAlchemy models
        """
        try:
            # Explicitly import all model modules
            cls._import_all_models()

            async with cls.get_engine().begin() as conn:
                # Create tables for all discovered models
                await conn.run_sync(Base.metadata.create_all)

            logging.info("All database tables created successfully")
        except Exception as e:
            logging.error(f"Error creating database tables: {e}")
            raise

    @classmethod
    def _import_all_models(cls):
        import os
        import importlib

        models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
        models_dir = os.path.abspath(models_dir)

        # Tables de référence à importer EN PREMIER (sans FK)
        priority_models = [
            'models.sexe.entity.sexe_entity',
            'models.statut.entity.statut_entity',
            'models.specialite.entity.specialite_entity',
            'models.statut_consultation.entity.statut_consultation_entity',
            'models.statut_paiement.entity.statut_paiement_entity',
            'models.statut_conversation.entity.statut_conversation_entity',
            'models.statut_livraison.entity.statut_livraison_entity',
            'models.emetteur.entity.emetteur_entity',
            'models.operateur.entity.operateur_entity',
            'models.workflow.entity.workflow_entity',
            'models.workflow.entity.workflow_step_entity',
            'models.workflow.entity.workflow_execution_entity',
            'models.workflow.entity.step_execution_entity',
        ]

        # Importer les prioritaires d'abord
        for module_name in priority_models:
            try:
                importlib.import_module(module_name)
                logging.info(f"Imported priority model: {module_name}")
            except Exception as e:
                logging.warning(f"Could not import priority model {module_name}: {e}")

        # Ensuite importer tout le reste dynamiquement
        for root, dirs, files in os.walk(models_dir):
            for file in files:
                if file.endswith('_entity.py') and not file.startswith('__'):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, os.path.dirname(models_dir))
                    module_name = relative_path.replace(os.sep, '.').replace('.py', '')

                    # Skiper ceux déjà importés
                    if module_name in priority_models:
                        continue

                    try:
                        importlib.import_module(module_name)
                        logging.info(f"Imported model: {module_name}")
                    except Exception as e:
                        logging.warning(f"Could not import model {module_name}: {e}")

    @classmethod
    def get_session_factory(cls):
        """
        Create async session factory
        """
        if not cls._async_session:
            cls._async_session = async_sessionmaker(
                cls.get_engine(),
                expire_on_commit=False,
                class_=AsyncSession
            )
        return cls._async_session

    @classmethod
    async def get_session(cls) -> AsyncGenerator[AsyncSession, None]:
        """
        Dependency function to get async database session

        :yield: AsyncSession for database operations
        """
        async with cls.get_session_factory()() as session:
            try:
                yield session
            finally:
                await session.close()


# Base class for declarative models
class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy declarative models
    Provides common configurations
    """
    __abstract__ = True

    # Optional: Add common methods or configurations


# Convenience function for FastAPI dependency injection
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Wrapper for DatabaseManager session retrieval
    """
    async for session in DatabaseManager.get_session():
        yield session


# Repository backend abstraction

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type


class DatabaseBackend(ABC):
    """Abstract backend for database operations. Implementations provide repository instances."""

    @abstractmethod
    def get_repository(self, entity_class: Type, domain_class: Type, mapper: Any) -> Any:
        ...

    @abstractmethod
    async def find_one(self, entity_class: Type, domain_class: Type, mapper: Any, filters: Dict[str, Any]) -> Optional[Any]:
        ...


class PostgreSQLBackend(DatabaseBackend):
    """PostgreSQL backend using SQLAlchemy async sessions."""

    def __init__(self, session: AsyncSession):
        from core.repository.backends.postgresql import SqlAlchemyRepository as PgRepo
        self.session = session
        self._repo_class = PgRepo

    def get_repository(self, entity_class: Type, domain_class: Type, mapper: Any) -> Any:
        return self._repo_class(self.session, entity_class, domain_class, mapper)

    async def find_one(self, entity_class: Type, domain_class: Type, mapper: Any, filters: Dict[str, Any]) -> Optional[Any]:
        repo = self.get_repository(entity_class, domain_class, mapper)
        return await repo.find_one(filters)


async def get_db_backend() -> AsyncGenerator[DatabaseBackend, None]:
    """FastAPI dependency: yield the appropriate DatabaseBackend based on DB_BACKEND config."""
    if settings.DB_BACKEND == "dynamodb":
        yield DynamoDBBackend()
    else:
        async for session in DatabaseManager.get_session():
            yield PostgreSQLBackend(session)


class DynamoDBBackend(DatabaseBackend):
    """DynamoDB backend using boto3 single-table design."""

    def __init__(self):
        self._repo_cache: Dict[str, Any] = {}

    def get_repository(self, entity_class: Type, domain_class: Type, mapper: Any) -> Any:
        from core.repository.backends.dynamodb import DynamoDBRepository
        entity_type = getattr(entity_class, "__tablename__", entity_class.__name__)
        cache_key = f"{entity_type}"
        if cache_key not in self._repo_cache:
            self._repo_cache[cache_key] = DynamoDBRepository(
                "afiya-data", entity_type, domain_class, mapper
            )
        return self._repo_cache[cache_key]

    async def find_one(self, entity_class: Type, domain_class: Type, mapper: Any, filters: Dict[str, Any]) -> Optional[Any]:
        repo = self.get_repository(entity_class, domain_class, mapper)
        return await repo.find_one(filters)
