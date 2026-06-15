from fastapi import APIRouter

from app.api.v1.routes import auth, chat, docs, orders, rag, store

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(docs.router, tags=["GoWA Documentation"])
api_router.include_router(orders.router, tags=["Orders"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG"])
api_router.include_router(store.router, tags=["Stores"])
