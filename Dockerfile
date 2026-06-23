# Backend FastAPI para Railway. Dockerfile explícito para evitar que nixpacks
# autodetecte el proyecto .NET (servicio_biometrico/) y corra `dotnet restore`.

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias (psycopg[binary] y boto3 no requieren libs del sistema).
COPY requirements.txt .
RUN pip install -r requirements.txt

# Solo el backend; el frontend y el bridge no van en esta imagen.
COPY backend/ ./backend/

WORKDIR /app/backend

# Railway inyecta $PORT en runtime.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
