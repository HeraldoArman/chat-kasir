from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_config
from app.core.env_validator import validate_env
from app.core.exceptions import AppException
from app.core.logging import init_logging
from app.middleware.logging import LoggingMiddleware

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_logging()
    validate_env()
    log.info("application_started")
    yield
    log.info("application_stopping")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Core API",
        description="AI Chat Core API Server",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)

    app.include_router(api_router, prefix="/api/v1")

    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException) -> dict[str, int | str]:
        return exc.to_response()

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    config = get_config()
    uvicorn.run(
        "app.main:app",
        host=config.server.host,
        port=config.server.port,
        reload=config.server.reload,
        workers=config.server.workers,
    )
