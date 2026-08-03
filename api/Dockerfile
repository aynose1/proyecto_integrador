FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=America/Mexico_City

WORKDIR /app

# tzdata: sin este paquete, la imagen "slim" no trae la base de datos de
# zonas horarias -- ENV TZ=... por sí sola no basta, Python (date.today(),
# datetime.now()) seguiría calculando todo en UTC. Con tzdata instalado
# Y TZ fijo, "hoy" coincide con la hora real de México en vez de
# adelantarse hasta 6 horas (justo el bug: de noche, en UTC ya es
# "mañana", así que /rutas/me?fecha=hoy devolvía la ruta equivocada).
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl tzdata \
    && ln -fs /usr/share/zoneinfo/$TZ /etc/localtime \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
