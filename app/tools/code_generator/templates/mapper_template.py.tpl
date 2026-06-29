from typing import Optional, List
from app.models.{table_name}.entity.{table_name}_entity import {ClassName}Entity
from app.models.{table_name}.entity.{table_name}_model import {ClassName}


class {ClassName}Mapper:
    """Mapper for {ClassName} entity"""

    @classmethod
    def to_domain(cls, entity: Optional[{ClassName}Entity]) -> Optional[{ClassName}]:
        if entity is None:
            return None
        return {ClassName}(
            id=entity.id,
{to_domain_fields}
        )

    @staticmethod
    def to_entity(domain: {ClassName}) -> {ClassName}Entity:
        return {ClassName}Entity(
            id=domain.id,
{to_entity_fields}
        )

    @classmethod
    def to_domain_list(cls, entities: List[{ClassName}Entity]) -> List[{ClassName}]:
        return [cls.to_domain(e) for e in entities] if entities else []
