"""GoWA device info routes."""

from fastapi import APIRouter

from app.core.config import get_config


def _extract_phone(jid_or_phone: str) -> str:
    value = jid_or_phone.strip().split("@")[0].replace("-", "").replace(" ", "")
    if value.startswith("+"):
        value = value[1:]
    return value


router = APIRouter(prefix="/gowa", tags=["GoWA"])


@router.get("/phone")
async def get_gowa_phone() -> dict[str, str | None]:
    """Return the GoWA-connected phone number extracted from GOWA_DEVICE_ID."""
    config = get_config()
    device_id = config.gowa.device_id
    if not device_id:
        return {"phone": None}
    return {"phone": _extract_phone(device_id)}
