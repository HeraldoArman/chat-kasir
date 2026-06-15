"""Pydantic schemas for GoWA WhatsApp integration."""

from pydantic import BaseModel, Field


class GowaMessagePayload(BaseModel):
    id: str | None = None
    chat_id: str = Field(..., description="Chat JID, e.g. 6289...@s.whatsapp.net")
    from_: str | None = Field(None, alias="from")
    from_name: str | None = None
    timestamp: str | None = None
    is_from_me: bool = False
    body: str | None = None


class GowaWebhookPayload(BaseModel):
    event: str
    device_id: str
    timestamp: str | None = None
    payload: GowaMessagePayload


class GowaSendMessageRequest(BaseModel):
    phone: str = Field(..., description="Recipient JID or phone number with country code")
    message: str = Field(..., min_length=1)


class GowaSendMessageResponse(BaseModel):
    code: str | None = None
    message: str | None = None
    results: dict[str, object] | None = None
