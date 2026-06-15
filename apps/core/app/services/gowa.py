"""GoWA outbound message client."""

import httpx
import structlog

from app.core.config import get_config

log = structlog.get_logger()


class GowaClientError(Exception):
    pass


class GowaClient:
    def __init__(
        self,
        base_url: str | None = None,
        device_id: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        config = get_config()
        self.base_url = (base_url or config.gowa.base_url).rstrip("/")
        self.device_id = device_id or config.gowa.device_id
        self.timeout = timeout

    async def send_text_message(self, phone: str, message: str) -> dict[str, object]:
        """Send a text message via GoWA REST API."""
        if not self.device_id:
            raise GowaClientError("GOWA_DEVICE_ID not configured")

        phone_clean = self._normalize_phone(phone)
        url = f"{self.base_url}/send/message"
        headers = {
            "Content-Type": "application/json",
            "X-Device-Id": self.device_id,
        }
        payload = {"phone": phone_clean, "message": message}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data: dict[str, object] = response.json()
                log.info(
                    "gowa_message_sent",
                    phone=phone_clean,
                    code=data.get("code"),
                )
                return data
        except httpx.HTTPStatusError as e:
            log.error(
                "gowa_send_failed",
                status_code=e.response.status_code,
                body=e.response.text,
                phone=phone_clean,
            )
            raise GowaClientError(
                f"GoWA send failed ({e.response.status_code}): {e.response.text}"
            ) from e
        except httpx.RequestError as e:
            log.error("gowa_request_error", error=str(e), phone=phone_clean)
            raise GowaClientError(f"GoWA request error: {e}") from e

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """Normalize a WhatsApp JID or phone number to GoWA send format."""
        cleaned = phone.strip().replace(" ", "").replace("-", "")
        if "@" in cleaned:
            cleaned = cleaned.split("@")[0]
        return cleaned
