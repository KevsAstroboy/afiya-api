from typing import Optional, List
from models.audit_log.entity.audit_log_entity import AuditLogEntity
from models.audit_log.entity.audit_log_model import AuditLog


class AuditLogMapper:
    """Mapper for AuditLog entity"""

    @classmethod
    def to_domain(cls, entity: Optional[AuditLogEntity]) -> Optional[AuditLog]:
        if entity is None:
            return None
        return AuditLog(
            id=entity.id,
            table_name=entity.table_name,
            record_id=entity.record_id,
            action=entity.action,
            user_id=entity.user_id,
            old_values=entity.old_values,
            new_values=entity.new_values,
            ip_address=entity.ip_address,
            user_agent=entity.user_agent,

        )

    @staticmethod
    def to_entity(domain: AuditLog) -> AuditLogEntity:
        return AuditLogEntity(
            id=domain.id,
            table_name=domain.table_name,
            record_id=domain.record_id,
            action=domain.action,
            user_id=domain.user_id,
            old_values=domain.old_values,
            new_values=domain.new_values,
            ip_address=domain.ip_address,
            user_agent=domain.user_agent,

        )

    @classmethod
    def to_domain_list(cls, entities: List[AuditLogEntity]) -> List[AuditLog]:
        return [cls.to_domain(e) for e in entities] if entities else []
