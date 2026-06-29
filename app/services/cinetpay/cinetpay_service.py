import hashlib
import hmac
import json
import logging
from typing import Optional
from datetime import datetime, timezone

import httpx
from core.config import settings

logger = logging.getLogger(__name__)


class CinetPayService:
    def __init__(self):
        self.site_id = settings.CINETPAY_SITE_ID
        self.api_key = settings.CINETPAY_API_KEY
        self.secret_key = settings.CINETPAY_SECRET_KEY
        self.init_endpoint = settings.CINETPAY_INIT_ENDPOINT
        self.check_endpoint = settings.CINETPAY_CHECK_ENDPOINT

    async def initiate_payment(
        self,
        transaction_id: str,
        amount: int,
        currency: str = "XOF",
        customer_name: str = "",
        customer_surname: str = "",
        description: str = "",
        return_url: str = "",
        notify_url: str = "",
    ) -> dict:
        payload = {
            "apikey": self.api_key,
            "site_id": self.site_id,
            "transaction_id": transaction_id,
            "amount": amount,
            "currency": currency,
            "customer_name": customer_name,
            "customer_surname": customer_surname,
            "description": description,
            "return_url": return_url,
            "notify_url": notify_url,
            "channels": "ALL",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.init_endpoint, json=payload)
            data = response.json()
            if data.get("code") != "201":
                logger.error(f"CinetPay init failed: {data}")
                raise Exception(f"CinetPay payment initialization failed: {data.get('message', 'Unknown error')}")
            return data

    async def verify_payment(self, transaction_id: str) -> dict:
        payload = {
            "apikey": self.api_key,
            "site_id": self.site_id,
            "transaction_id": transaction_id,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.check_endpoint, json=payload)
            return response.json()

    def validate_ipn_signature(self, payload: dict, received_signature: str) -> bool:
        sorted_keys = sorted(payload.keys())
        signature_data = "".join(f"{k}={payload[k]}" for k in sorted_keys)
        computed = hmac.new(
            self.secret_key.encode("utf-8"),
            signature_data.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest().upper()
        return hmac.compare_digest(computed, received_signature.upper())
