FROM python:3.13.7-slim-bookworm AS builder

RUN pip install uv

COPY pyproject.toml ./

RUN uv pip install --system -r pyproject.toml

FROM python:3.13.7-slim-bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends osm2pgsql && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY /app/ /app/

WORKDIR /app