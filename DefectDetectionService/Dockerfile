FROM python:3.10.18-slim-bookworm AS builder

RUN pip install uv

COPY pyproject.toml ./

RUN uv pip install --system -r pyproject.toml

FROM python:3.10.18-slim-bookworm

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY /app/ /app/

WORKDIR /app