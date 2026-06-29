import json
import asyncio

import boto3
from core.config import settings
from core.workflow.providers.base import LLMProvider


class BedrockAnthropicProvider(LLMProvider):
    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
        )

    async def generate(self, prompt: str, model: str, max_tokens: int) -> str:
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        })

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.invoke_model(
                modelId=model,
                accept="application/json",
                contentType="application/json",
                body=body,
            )
        )

        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"]
