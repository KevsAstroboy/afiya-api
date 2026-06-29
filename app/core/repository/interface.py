from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any

T = TypeVar('T')


class RepositoryInterface(ABC, Generic[T]):
    """Generic repository interface for all entities. Parameterized by domain model type T."""

    @abstractmethod
    async def create(self, domain: T) -> T:
        ...

    @abstractmethod
    async def get_by_id(self, record_id: Any) -> Optional[T]:
        ...

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        ...

    @abstractmethod
    async def update(self, record_id: Any, updates: Dict[str, Any]) -> T:
        ...

    @abstractmethod
    async def delete(self, record_id: Any, deleted_by: Optional[Any] = None) -> bool:
        ...

    @abstractmethod
    async def find_one(self, filters: Dict[str, Any]) -> Optional[T]:
        ...

    @abstractmethod
    async def find_by(self, filters: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[T]:
        ...
