from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AuditLog:
    table_name: str
    record_id: int
    action: str
    id: Optional[int] = None
    user_id: Optional[int] = None
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

