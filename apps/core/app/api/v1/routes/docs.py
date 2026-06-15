from fastapi import APIRouter
from fastapi.responses import FileResponse, PlainTextResponse

router = APIRouter(prefix="/docs/gowa", tags=["GoWA Documentation"])


@router.get("/openapi.yaml")
async def get_openapi_spec():
    return FileResponse("app/docs/gowa/openapi.yaml", media_type="application/x-yaml")


@router.get("/webhook")
async def get_webhook_docs():
    with open("app/docs/gowa/webhook-payload.md") as f:
        content = f.read()
    return PlainTextResponse(content, media_type="text/markdown")
