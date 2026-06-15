"""Core application package."""

__all__ = ["app"]

# Delay app import to avoid side-effects during config-less imports (e.g. Alembic).
def __getattr__(name: str) -> object:
    if name == "app":
        from app.main import app as _app
        return _app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
