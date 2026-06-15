"""GoWA device info routes."""

from fastapi import APIRouter

from app.core.config import get_config

router = APIRouter(prefix="/gowa", tags=["GoWA"])


@router.get("/phone")
async def get_gowa_phone() -> dict[str, str | None]:
    """Return the GoWA-connected phone number from GOWA_PHONE config."""
    config = get_config()
    phone = config.gowa.phone
    if not phone:
        return {"phone": None}
    return {"phone": phone}
