import json
import logging
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key

from core.config import settings
from core.repository.interface import RepositoryInterface

logger = logging.getLogger(__name__)
T = object


class DynamoDBRepository(RepositoryInterface[T]):
    """Generic DynamoDB repository using single-table design with PK/SK pattern."""

    def __init__(self, table_name: str, entity_type: str, domain_class: type, mapper: Any):
        self.entity_type = entity_type
        self.domain_class = domain_class
        self.mapper = mapper
        resource = boto3.resource(
            "dynamodb",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
        )
        self.table = resource.Table(table_name)

    def _make_pk(self, record_id: str = None) -> str:
        rid = record_id or str(uuid.uuid4())
        return f"{self.entity_type.upper()}#{rid}"

    def _make_sk(self, suffix: str = "METADATA") -> str:
        return f"{suffix}#{uuid.uuid4()}"

    def _domain_to_item(self, domain: Any, record_id: str = None) -> dict:
        rid = record_id or str(uuid.uuid4())
        item = {
            "PK": self._make_pk(rid),
            "SK": self._make_sk(),
            "EntityType": self.entity_type,
            "EntityId": rid,
        }
        if hasattr(domain, "__dataclass_fields__"):
            for field_name in domain.__dataclass_fields__:
                value = getattr(domain, field_name, None)
                if value is not None and field_name not in ("id",):
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    elif isinstance(value, (dict, list)):
                        value = json.dumps(value)
                    item[field_name] = value
        elif isinstance(domain, dict):
            item.update({k: v for k, v in domain.items() if k not in ("id",)})
        return item

    def _item_to_domain(self, item: dict) -> Optional[Any]:
        if not item:
            return None
        attrs = {"id": item.get("EntityId")}
        for key, value in item.items():
            if key not in ("PK", "SK", "EntityType", "EntityId"):
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        pass
                attrs[key] = value
        try:
            return self.domain_class(**attrs)
        except TypeError:
            return item

    async def create(self, domain: T) -> T:
        item = self._domain_to_item(domain)
        self.table.put_item(Item=item)
        return self._item_to_domain(item)

    async def get_by_id(self, record_id: Any) -> Optional[T]:
        pk = self._make_pk(str(record_id))
        result = self.table.query(
            KeyConditionExpression=Key("PK").eq(pk) & Key("SK").begins_with("METADATA"),
            Limit=1,
        )
        items = result.get("Items", [])
        return self._item_to_domain(items[0]) if items else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        result = self.table.query(
            IndexName="EntityTypeIndex",
            KeyConditionExpression=Key("EntityType").eq(self.entity_type),
            Limit=limit,
        )
        items = result.get("Items", [])
        return [self._item_to_domain(i) for i in items[skip:skip + limit] if i]

    async def update(self, record_id: Any, updates: Dict[str, Any]) -> T:
        pk = self._make_pk(str(record_id))
        result = self.table.query(
            KeyConditionExpression=Key("PK").eq(pk) & Key("SK").begins_with("METADATA"),
            Limit=1,
        )
        items = result.get("Items", [])
        if not items:
            raise ValueError(f"{self.entity_type} with id {record_id} not found")
        item = items[0]
        update_expr = "SET " + ", ".join(f"#{k} = :{k}" for k in updates)
        expr_attr_names = {f"#{k}": k for k in updates}
        expr_attr_values = {f":{k}": v for k, v in updates.items()}
        expr_attr_values[":updated_at"] = datetime.now(timezone.utc).isoformat()
        update_expr += ", #updated_at = :updated_at"
        expr_attr_names["#updated_at"] = "updated_at"
        self.table.update_item(
            Key={"PK": item["PK"], "SK": item["SK"]},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values,
        )
        item.update(updates)
        return self._item_to_domain(item)

    async def delete(self, record_id: Any, deleted_by: Optional[Any] = None) -> bool:
        pk = self._make_pk(str(record_id))
        result = self.table.query(
            KeyConditionExpression=Key("PK").eq(pk) & Key("SK").begins_with("METADATA"),
            Limit=1,
        )
        items = result.get("Items", [])
        if not items:
            raise ValueError(f"{self.entity_type} with id {record_id} not found")
        self.table.delete_item(Key={"PK": items[0]["PK"], "SK": items[0]["SK"]})
        return True

    async def find_one(self, filters: Dict[str, Any]) -> Optional[T]:
        results = await self.find_by(filters, 0, 1)
        return results[0] if results else None

    async def find_by(self, filters: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[T]:
        filter_expression = None
        for key, value in filters.items():
            condition = Key(key).eq(value)
            if filter_expression is None:
                filter_expression = condition
        if not filter_expression:
            result = self.table.scan(Limit=limit)
        else:
            result = self.table.scan(
                FilterExpression=filter_expression,
                Limit=limit,
            )
        items = result.get("Items", [])
        return [self._item_to_domain(i) for i in items[skip:skip + limit] if i]
