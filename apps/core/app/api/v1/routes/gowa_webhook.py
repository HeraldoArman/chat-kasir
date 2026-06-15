from fastapi import APIRouter, HTTPException, Request, status

from app.agent.executor import AgentExecutor
from app.services.gowa_webhook import GowaWebhookHandler, WebhookVerificationError

router = APIRouter(tags=["GoWA Webhook"])


@router.post("/webhook/gowa")
async def gowa_webhook(request: Request) -> dict[str, str]:
    handler = GowaWebhookHandler(agent=AgentExecutor())
    try:
        result = await handler.handle_request(request)
        return {"status": str(result.get("status", "ok"))}
    except WebhookVerificationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {e}",
        ) from e
