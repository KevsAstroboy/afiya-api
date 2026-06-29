import json
import logging
from typing import Optional, Tuple

import httpx
from core.config import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://graph.facebook.com/v21.0"


class WhatsAppService:
    def __init__(self):
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.verify_token = settings.WHATSAPP_VERIFY_TOKEN

    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        if mode == "subscribe" and token == self.verify_token:
            return challenge
        return None

    def parse_message(self, body: dict) -> Tuple[Optional[str], Optional[str], Optional[str], str]:
        try:
            entry = body.get("entry", [{}])[0]
            change = entry.get("changes", [{}])[0]
            value = change.get("value", {})
            messages = value.get("messages", [])
            contacts = value.get("contacts", [])

            wa_id = None
            message_text = None
            wamid = None
            profile_name = ""

            if messages:
                msg = messages[0]
                wa_id = msg.get("from")
                wamid = msg.get("id")
                if msg.get("type") == "text":
                    message_text = msg.get("text", {}).get("body")

            if contacts:
                profile_name = contacts[0].get("profile", {}).get("name", "")

            return wa_id, message_text, wamid, profile_name
        except (KeyError, IndexError, TypeError) as e:
            logger.warning(f"Failed to parse WhatsApp message: {e}")
            return None, None, None, ""

    async def send_text_message(self, to: str, body: str) -> dict:
        url = f"{BASE_URL}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": body},
        }
        print(payload)
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    @staticmethod
    def _format_wa_phone(to: str) -> str:
        if to.startswith("225") and len(to) == 11 and to[3:].isdigit():
            return f"22507{to[3:]}"
        return to
