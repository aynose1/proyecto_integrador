"""
Script de prueba: simula lecturas del sistema embebido (sensor ultrasónico)
mandándolas al endpoint real de la API, tal como lo haría un dispositivo
físico. Manda la DISTANCIA cruda medida (cm desde el sensor hasta la
basura) — el backend calcula el porcentaje de llenado usando la
altura_cm configurada para ese contenedor. No inserta directo a la base
de datos: así se prueba también la validación (API Key, altura_cm
configurada, existencia del contenedor, etc.) igual que en producción.

Uso:
    python simular_lecturas_sensor.py --codigo QR-A1 --altura 80 --lecturas 12

El contenedor debe existir y tener capturada su altura_cm desde la web
antes de correr esto (si no, el endpoint responde 422).

Requiere las variables de entorno (o edítalas abajo):
    API_BASE_URL     ej. http://localhost:8000
    DEVICE_API_KEY    la misma que configuraste en el backend (.env)
"""
import argparse
import os
import random
import sys
from datetime import datetime, timedelta

import requests

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
DEVICE_API_KEY = os.environ.get("DEVICE_API_KEY", "cambia-esto-tambien")


def enviar_lectura(codigo_contenedor: str, distancia_cm: float, fecha_hora: datetime) -> None:
    resp = requests.post(
        f"{API_BASE_URL}/registros-nivel",
        headers={"X-API-Key": DEVICE_API_KEY},
        json={
            "codigo_contenedor": codigo_contenedor,
            "distancia_cm": round(distancia_cm, 2),
            "fecha_hora": fecha_hora.isoformat(),
        },
        timeout=10,
    )
    if resp.status_code != 201:
        print(f"  [ERROR {resp.status_code}] {resp.text}")
        return
    data = resp.json()
    print(
        f"  [OK] {fecha_hora:%Y-%m-%d %H:%M} -> distancia {distancia_cm:.1f}cm "
        f"=> nivel {data['nivel_porcentaje']}% (id={data['id']})"
    )


def simular_llenado_progresivo(codigo_contenedor: str, altura_cm: float, num_lecturas: int, horas_entre_lecturas: int) -> None:
    """
    Simula un contenedor llenándose con el tiempo: la distancia medida
    va BAJANDO (la basura se acerca al sensor) hasta que se "recolecta"
    y la distancia vuelve a subir cerca de altura_cm (vacío). Incluye
    algo de ruido, como se comportaría un sensor real.
    """
    print(f"Simulando {num_lecturas} lecturas para '{codigo_contenedor}' (altura configurada: {altura_cm}cm)...")
    ahora = datetime.now()
    distancia = altura_cm * random.uniform(0.85, 0.95)  # arranca casi vacío

    for i in range(num_lecturas):
        fecha_hora = ahora - timedelta(hours=(num_lecturas - i) * horas_entre_lecturas)
        distancia -= altura_cm * random.uniform(0.06, 0.14)
        if distancia <= altura_cm * 0.05:
            # Ya casi tocaba el fondo: simula que lo recolectaron y volvió a vaciarse
            distancia = altura_cm * random.uniform(0.85, 0.98)
        distancia += random.uniform(-1.5, 1.5)  # ruido del sensor
        enviar_lectura(codigo_contenedor, max(0.0, distancia), fecha_hora)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simula lecturas del sensor de un contenedor.")
    parser.add_argument("--codigo", required=True, help="codigo_contenedor ya registrado en el sistema")
    parser.add_argument("--altura", type=float, required=True, help="altura_cm configurada para ese contenedor (debe coincidir con la que capturaste en la web)")
    parser.add_argument("--lecturas", type=int, default=10, help="cuántas lecturas simular (default: 10)")
    parser.add_argument("--intervalo-horas", type=int, default=4, help="horas entre cada lectura (default: 4)")
    args = parser.parse_args()

    print(f"API: {API_BASE_URL}")
    try:
        simular_llenado_progresivo(args.codigo, args.altura, args.lecturas, args.intervalo_horas)
    except requests.exceptions.ConnectionError:
        print(f"No se pudo conectar a {API_BASE_URL}. ¿Está corriendo el backend?")
        sys.exit(1)

    print("\nListo. Verifica en la web (Contenedores) que el nivel se haya actualizado,")
    print("o consulta GET /contenedores/{id}/registros-nivel para ver el historial completo.")
