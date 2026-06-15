import os
from collections.abc import AsyncGenerator
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

RAW_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@host/dbname",
)


def _normalize_asyncpg_url(url: str) -> tuple[str, dict[str, object]]:
    """Return a SQLAlchemy asyncpg URL and connect kwargs.

    asyncpg does not accept sslmode/channel_binding as query-string args; it
    expects them as explicit connect() arguments or as `ssl`.
    """
    if not url.startswith(("postgresql://", "postgresql+")):
        return url, {}

    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    connect_args: dict[str, object] = {}

    if "sslmode" in query_params:
        sslmode = query_params.pop("sslmode")[-1]
        if sslmode == "require":
            connect_args["ssl"] = True
        elif sslmode == "disable":
            connect_args["ssl"] = False
        elif sslmode in {"prefer", "allow", "verify-ca", "verify-full"}:
            connect_args["ssl"] = True

    if "channel_binding" in query_params:
        query_params.pop("channel_binding")

    new_query = urlencode(query_params, doseq=True)
    normalized_url = urlunparse(parsed_url._replace(query=new_query))
    sa_url = make_url(normalized_url)
    if sa_url.drivername == "postgresql":
        sa_url = sa_url.set(drivername="postgresql+asyncpg")
    return str(sa_url), connect_args


DATABASE_URL, DATABASE_CONNECT_ARGS = _normalize_asyncpg_url(RAW_DATABASE_URL)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args=DATABASE_CONNECT_ARGS,
)
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
