FROM python:3.13-slim AS builder

RUN pip install uv

WORKDIR /app

COPY apps/core/pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

FROM python:3.13-slim AS runtime

RUN pip install uv

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY apps/core/app/ ./app/

RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]