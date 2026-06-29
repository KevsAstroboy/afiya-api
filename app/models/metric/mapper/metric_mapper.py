from typing import Optional, List
from models.metric.entity.metric_entity import MetricEntity
from models.metric.entity.metric_model import Metric


class MetricMapper:
    """Mapper for Metric entity"""

    @classmethod
    def to_domain(cls, entity: Optional[MetricEntity]) -> Optional[Metric]:
        if entity is None:
            return None
        return Metric(
            id=entity.id,
            consultation_id=entity.consultation_id,
            type_metric=entity.type_metric,
            valeur=entity.valeur,
            unite=entity.unite,
            date_mesure=entity.date_mesure,
            is_deleted=entity.is_deleted,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
            created_by=entity.created_by,
            updated_by=entity.updated_by,
            deleted_by=entity.deleted_by,
            deletion_reason=entity.deletion_reason,
        )

    @staticmethod
    def to_entity(domain: Metric) -> MetricEntity:
        return MetricEntity(
            id=domain.id,
            consultation_id=domain.consultation_id,
            type_metric=domain.type_metric,
            valeur=domain.valeur,
            unite=domain.unite,
            date_mesure=domain.date_mesure,
            is_deleted=domain.is_deleted,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            deleted_at=domain.deleted_at,
            created_by=domain.created_by,
            updated_by=domain.updated_by,
            deleted_by=domain.deleted_by,
            deletion_reason=domain.deletion_reason,
        )

    @classmethod
    def to_domain_list(cls, entities: List[MetricEntity]) -> List[Metric]:
        return [cls.to_domain(e) for e in entities] if entities else []
