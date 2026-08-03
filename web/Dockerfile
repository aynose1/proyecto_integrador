FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=America/Mexico_City

WORKDIR /app

# Ver el mismo comentario en api/Dockerfile: sin tzdata, ENV TZ no hace
# nada por sí sola. Este contenedor también calcula "hoy" (ej. el
# default de fecha en el listado de Rutas) -- necesita la misma
# corrección para no desincronizarse con la hora real de México.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl tzdata \
    && ln -fs /usr/share/zoneinfo/$TZ /etc/localtime \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--access-logfile", "-", "--error-logfile", "-", "run:app"]
