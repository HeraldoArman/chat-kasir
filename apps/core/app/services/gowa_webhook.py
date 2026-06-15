"""GoWA webhook verification and message routing."""

import hashlib
import hmac
import json

import structlog
from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.executor import AgentExecutor
from app.core.config import get_config
from app.db.session import async_session_factory
from app.models.commerce import Store
from app.models.user import User
from app.schemas.gowa import GowaWebhookPayload
from app.services.gowa import GowaClient, GowaClientError


def _extract_phone(jid_or_phone: str) -> str:
    value = jid_or_phone.strip().split("@")[0].replace("-", "").replace(" ", "")
    if value.startswith("+"):
        value = value[1:]
    return value

log = structlog.get_logger()


class WebhookVerificationError(Exception):
    pass


class GowaWebhookHandler:
    def __init__(self, agent: "AgentExecutor | None" = None) -> None:
        self.agent = agent
        self.config = get_config()
        self.gowa_client = GowaClient()

    async def handle_request(self, request: Request) -> dict[str, object]:
        """Verify, parse, and process a GoWA webhook request."""
        body = await request.body()
        signature = request.headers.get("x-hub-signature-256", "")
        self._verify_signature(body, signature)

        log.info(
            "gowa_webhook_received",
            content_type=request.headers.get("content-type"),
            content_length=len(body),
        )

        try:
            raw = json.loads(body)
            log.info("gowa_webhook_raw_payload", raw=raw)
            payload = GowaWebhookPayload(**raw)
        except (json.JSONDecodeError, ValueError) as e:
            log.warning("gowa_invalid_payload", error=str(e))
            raise WebhookVerificationError("Invalid JSON payload") from e

        log.info(
            "gowa_webhook_config",
            device_id_config=self.config.gowa.device_id,
            base_url=self.config.gowa.base_url,
            phone_config=self.config.gowa.phone,
            has_secret=bool(self.config.gowa.webhook_secret),
        )

        if payload.event != "message":
            log.info("gowa_non_message_event_skipped", event=payload.event)
            return {"status": "ignored", "event": payload.event}

        message_body = payload.payload.body
        if not message_body:
            log.info(
                "gowa_empty_message_body",
                chat_id=payload.payload.chat_id,
                from_=payload.payload.from_,
            )
            await self._send_reply(
                chat_id=payload.payload.chat_id,
                text="Maaf, saat ini saya hanya bisa membalas pesan teks. 🙏",
            )
            return {"status": "no_text"}

        context = await self._build_context(payload)
        if context.store is None:
            log.warning(
                "gowa_store_not_found",
                device_id=payload.device_id,
                chat_id=payload.payload.chat_id,
                customer_phone=context.customer_phone,
            )
            await self._send_reply(
                chat_id=payload.payload.chat_id,
                text="Maaf, toko ini belum terdaftar di sistem kami.",
            )
            return {"status": "store_not_found"}

        try:
            if self.agent is None:
                raise RuntimeError("Agent executor not configured")
            reply = await self.agent.run(
                message=message_body,
                store=context.store,
                customer_phone=context.customer_phone,
                customer_name=payload.payload.from_name or None,
                is_merchant=context.is_merchant,
            )
        except Exception as e:
            log.error("agent_execution_failed", error=str(e))
            reply = "Maaf, terjadi kesalahan saat memproses pesan Anda. Silakan coba lagi."

        await self._send_reply(chat_id=payload.payload.chat_id, text=reply)
        return {"status": "processed"}

    def _verify_signature(self, body: bytes, signature: str) -> None:
        secret = self.config.gowa.webhook_secret
        if not secret:
            log.warning("gowa_webhook_secret_not_set")
            return

        if not signature.startswith("sha256="):
            raise WebhookVerificationError("Invalid signature format")

        expected = hmac.new(
            secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()
        received = signature[7:]
        if not hmac.compare_digest(expected, received):
            raise WebhookVerificationError("Signature mismatch")

    async def _build_context(self, payload: GowaWebhookPayload) -> "_MessageContext":
        from_value = payload.payload.from_ or payload.payload.chat_id
        customer_phone = _extract_phone(from_value)
        store_phone = _extract_phone(payload.device_id)

        log.info(
            "gowa_webhook_context_start",
            raw_device_id=payload.device_id,
            store_phone=store_phone,
            customer_phone=customer_phone,
            from_raw=from_value,
        )

        async with async_session_factory() as db:
            store = await self._get_store_by_whatsapp(db, store_phone)

            is_merchant = False
            if store is not None:
                log.info(
                    "gowa_store_found",
                    store_slug=store.slug,
                    store_id=str(store.id),
                    store_whatsapp=store.whatsapp_number,
                )
                result = await db.execute(
                    select(User).where(User.id == store.owner_id)
                )
                owner = result.scalar_one_or_none()
                if owner:
                    log.info(
                        "gowa_owner_found",
                        owner_id=str(owner.id),
                        owner_whatsapp=owner.whatsapp_number,
                        customer_phone=customer_phone,
                        match=_extract_phone(owner.whatsapp_number) == customer_phone if owner.whatsapp_number else False,
                    )
                    if owner.whatsapp_number:
                        is_merchant = customer_phone == _extract_phone(
                            owner.whatsapp_number
                        )
                else:
                    log.warning("gowa_owner_not_found", store_id=str(store.id))
            else:
                log.warning(
                    "gowa_store_not_found_debug",
                    looked_up_phone=store_phone,
                    db_stores=[
                        {"slug": s.slug, "whatsapp": s.whatsapp_number}
                        for s in (await db.execute(select(Store))).scalars().all()
                    ],
                )

            return _MessageContext(
                store=store,
                customer_phone=customer_phone,
                is_merchant=is_merchant,
            )

    async def _get_store_by_whatsapp(
        self, db: AsyncSession, phone: str
    ) -> Store | None:
        """Find a store whose whatsapp_number matches (after normalisation)."""
        log.info("gowa_lookup_store_start", phone=phone)
        result = await db.execute(select(Store))
        stores = result.scalars().all()
        log.info("gowa_lookup_store_total", count=len(stores), phone=phone)
        for store in stores:
            if store.whatsapp_number and _extract_phone(store.whatsapp_number) == phone:
                log.info(
                    "gowa_lookup_store_match",
                    store_slug=store.slug,
                    store_whatsapp=store.whatsapp_number,
                    looked_up_phone=phone,
                )
                return store

        log.warning(
            "gowa_lookup_store_no_match",
            looked_up_phone=phone,
            total_stores=len(stores),
            store_numbers=[
                s.whatsapp_number
                for s in stores
                if s.whatsapp_number
            ],
        )
        return None

    async def _send_reply(self, chat_id: str, text: str) -> None:
        try:
            await self.gowa_client.send_text_message(phone=chat_id, message=text)
        except GowaClientError:
            log.warning("gowa_reply_failed", chat_id=chat_id)


class _MessageContext:
    def __init__(self, store: Store | None, customer_phone: str, is_merchant: bool) -> None:
        self.store = store
        self.customer_phone = customer_phone
        self.is_merchant = is_merchant
