from fastapi import APIRouter

from app.api.v1.routes import (
    auth,
    cart,
    chat,
    docs,
    gowa,
    gowa_webhook,
    insights,
    orders,
    promotions,
    rag,
    store,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(cart.router, tags=["Cart"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(docs.router, tags=["GoWA Documentation"])
api_router.include_router(gowa_webhook.router, tags=["GoWA Webhook"])
api_router.include_router(gowa.router, tags=["GoWA"])
api_router.include_router(insights.router, tags=["Insights"])
api_router.include_router(orders.router, tags=["Orders"])
api_router.include_router(promotions.router, tags=["Promotions"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG"])
api_router.include_router(store.router, tags=["Stores"])
