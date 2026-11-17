# API FastAPI de ShareU. Contexto de build: raíz del repositorio.
#
# Es el mismo contenedor que usa `Dockploy/compose.lab.yml` en el servidor del
# laboratorio. Se versiona también en la raíz para que `docker compose up`
# funcione sin rutas especiales (README, ADR 0006).
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

FROM base AS dependencias
COPY requirements.txt .
RUN pip install --only-binary=:all: --require-hashes --prefix=/instalado -r requirements.txt

FROM base
COPY --from=dependencias /instalado /usr/local
COPY app ./app
RUN useradd --uid 10001 --no-create-home app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
