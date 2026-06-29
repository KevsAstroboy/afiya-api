import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import boto3
from boto3.dynamodb.conditions import Key

from core.config import settings
from core.workflow.db_interface import WorkflowDBInterface
from core.workflow.types import WorkflowStep, StepType, StepResult

logger = logging.getLogger(__name__)

TABLE_NAME = "afiya-data"


def _get_table():
    resource = boto3.resource(
        "dynamodb",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
    )
    return resource.Table(TABLE_NAME)


class DynamoDBWorkflowDB(WorkflowDBInterface):
    def __init__(self):
        self.table = _get_table()

    @staticmethod
    def _parse_config(config_value):
        import json
        if isinstance(config_value, str):
            try:
                return json.loads(config_value)
            except (json.JSONDecodeError, TypeError):
                return {}
        return config_value or {}

    async def get_steps_by_workflow(self, workflow_id: str) -> List[WorkflowStep]:
        pk = f"WORKFLOW#{workflow_id}"
        result = self.table.query(
            KeyConditionExpression=Key("PK").eq(pk) & Key("SK").begins_with("STEP#"),
        )
        items = sorted(result.get("Items", []), key=lambda i: int(i.get("step_order", 0)))
        return [
            WorkflowStep(
                id=item.get("EntityId", ""),
                name=item.get("name", ""),
                step_order=int(item.get("step_order", 0)),
                step_type=StepType(item.get("step_type", "function")),
                llm_prompt=item.get("llm_prompt"),
                llm_model=item.get("llm_model", "claude-sonnet-4-20250514"),
                llm_max_tokens=int(item.get("llm_max_tokens", 1000)),
                on_success_step_id=item.get("on_success_step_id"),
                on_failure_step_id=item.get("on_failure_step_id"),
                is_terminal=item.get("is_terminal", False),
                llm_prompt_success=item.get("llm_prompt_success", ""),
                llm_prompt_error=item.get("llm_prompt_error", ""),
                config=self._parse_config(item.get("config", {})),
            )
            for item in items
        ]

    async def create_execution(self, execution_id: str, workflow_id: str, input_data: dict) -> None:
        pk = f"EXECUTION#{execution_id}"
        gsipk = f"WORKFLOW#{workflow_id}"
        item = {
            "PK": pk,
            "SK": f"METADATA#{execution_id}",
            "EntityType": "workflow_execution",
            "EntityId": execution_id,
            "workflow_id": workflow_id,
            "status": "running",
            "input_data": input_data,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "GSI1PK": gsipk,
            "GSI1SK": f"STARTED#{datetime.now(timezone.utc).isoformat()}",
        }
        self.table.put_item(Item=item)

    async def save_step_execution(self, execution_id: str, result: StepResult) -> None:
        pk = f"EXECUTION#{execution_id}"
        step_exec_id = str(uuid.uuid4())
        gsipk = pk
        item = {
            "PK": pk,
            "SK": f"STEP_EXEC#{result.step_id}#{step_exec_id[:8]}",
            "EntityType": "step_execution",
            "EntityId": step_exec_id,
            "step_id": result.step_id,
            "status": result.status.value,
            "output_data": {"output": result.output} if result.output is not None else None,
            "error_message": result.error,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "GSI1PK": gsipk,
            "GSI1SK": f"STEP#{datetime.now(timezone.utc).isoformat()}",
        }
        self.table.put_item(Item=item)

    async def update_execution(self, execution_id: str, status: str, output_data: Optional[dict] = None) -> None:
        pk = f"EXECUTION#{execution_id}"
        result = self.table.query(
            KeyConditionExpression=Key("PK").eq(pk) & Key("SK").begins_with("METADATA"),
            Limit=1,
        )
        items = result.get("Items", [])
        if items:
            item = items[0]
            self.table.update_item(
                Key={"PK": item["PK"], "SK": item["SK"]},
                UpdateExpression="SET #status = :status, output_data = :output, finished_at = :finished_at",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":status": status,
                    ":output": output_data,
                    ":finished_at": datetime.now(timezone.utc).isoformat(),
                },
            )

    async def find_one(self, table: str, filters: Dict[str, Any]) -> Optional[Any]:
        filter_expression = None
        for key, value in filters.items():
            condition = Key(key).eq(value)
            filter_expression = condition if filter_expression is None else filter_expression & condition
        result = self.table.scan(
            FilterExpression=filter_expression,
            Limit=1,
        )
        items = result.get("Items", [])
        return items[0] if items else None

    async def insert(self, table: str, data: Dict[str, Any]) -> str:
        import json
        record_id = data.get("id") or str(uuid.uuid4())
        pk = f"{table.upper()}#{record_id}"
        sk = f"METADATA#{record_id}"
        item = {
            "PK": pk,
            "SK": sk,
            "EntityType": table,
            "EntityId": record_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        for k, v in data.items():
            if v is not None and k not in ("id",):
                if isinstance(v, datetime):
                    v = v.isoformat()
                elif isinstance(v, (dict, list)):
                    v = json.dumps(v)
                item[k] = v
        self.table.put_item(Item=item)
        return record_id
