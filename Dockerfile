FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

RUN apt update && apt install -y git

WORKDIR /app

# Copy only dependency files first — this layer is cached until lockfile changes
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-editable

# Now copy the rest of the source and build
COPY ./ ./
RUN uv build


FROM python:3.13-alpine

RUN addgroup -S app && adduser -S app -G app && mkdir /app && chown app:app /app

COPY --from=builder /app/dist/depot_server*.tar.gz /tmp
RUN pip install /tmp/depot_server*.tar.gz && rm /tmp/depot_server*.tar.gz

USER app
WORKDIR app

CMD ["uvicorn", "depot_server.api:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "info"]
