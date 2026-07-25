"""
Script de prueba: simula lecturas del sistema embebido (sensor ultrasónico)
mandándolas al endpoint real de la API, tal como lo haría un dispositivo
físico. No inserta directo a la base de datos: así se prueba también la
validación (API Key, formato del payload, existencia del contenedor, etc.)
igual que en producción.

Uso:
    python simular_lecturas_sensor.py --codigo QR-A1 --lecturas 12

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


def enviar_lectura(codigo_contenedor: str, nivel_porcentaje: float, fecha_hora: datetime) -> None:
    resp = requests.post(
        f"{API_BASE_URL}/registros-nivel",
        headers={"X-API-Key": DEVICE_API_KEY},
        json={
            "codigo_contenedor": codigo_contenedor,
            "nivel_porcentaje": round(nivel_porcentaje, 2),
            "fecha_hora": fecha_hora.isoformat(),
        },
        timeout=10,
    )
    if resp.status_code != 201:
        print(f"  [ERROR {resp.status_code}] {resp.text}")
        return
    data = resp.json()
    print(f"  [OK] {fecha_hora:%Y-%m-%d %H:%M} -> {data['nivel_porcentaje']}% (id={data['id']})")


def simular_llenado_progresivo(codigo_contenedor: str, num_lecturas: int, horas_entre_lecturas: int) -> None:
    """
    Simula un llenado gradual y creciente, con algo de ruido, como se
    vería un contenedor llenándose durante varios días — útil para
    probar gráficas de frecuencia de llenado en el dashboard.
    """
    print(f"Simulando {num_lecturas} lecturas para el contenedor '{codigo_contenedor}'...")
    ahora = datetime.now()
    nivel = random.uniform(5, 15)

    for i in range(num_lecturas):
        fecha_hora = ahora - timedelta(hours=(num_lecturas - i) * horas_entre_lecturas)
        nivel += random.uniform(3, 9)
        if nivel >= 95:
            # El contenedor se "vació" (simula que alguien lo recolectó)
            nivel = random.uniform(0, 8)
        enviar_lectura(codigo_contenedor, min(nivel, 100), fecha_hora)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simula lecturas del sensor de un contenedor.")
    parser.add_argument("--codigo", required=True, help="codigo_contenedor ya registrado en el sistema")
    parser.add_argument("--lecturas", type=int, default=10, help="cuántas lecturas simular (default: 10)")
    parser.add_argument("--intervalo-horas", type=int, default=4, help="horas entre cada lectura (default: 4)")
    args = parser.parse_args()

    print(f"API: {API_BASE_URL}")
    try:
        simular_llenado_progresivo(args.codigo, args.lecturas, args.intervalo_horas)
    except requests.exceptions.ConnectionError:
        print(f"No se pudo conectar a {API_BASE_URL}. ¿Está corriendo el backend?")
        sys.exit(1)

    print("\nListo. Verifica en la web (Contenedores) que el nivel se haya actualizado,")
    print("o consulta GET /contenedores/{id}/registros-nivel para ver el historial completo.")
