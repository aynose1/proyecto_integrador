"""
Script de prueba: simula lecturas de AMBOS sensores de un contenedor
(nivel por ultrasonido + peso por celda de carga), mandándolas a los
endpoints reales de la API, tal como lo haría el sistema embebido de
verdad. No inserta directo a la base de datos: así se prueba también la
validación (API Key, altura_cm configurada, existencia del contenedor,
etc.) igual que en producción.

Uso local (backend corriendo en tu propia máquina):
    python simular_lecturas_sensor.py --codigo QR-A1 --altura 80 --capacidad 40 --lecturas 12

Uso contra la API ya desplegada (sin tocar el script, solo cambia dónde
apunta): pon las variables de entorno ANTES de correrlo, apuntando al
servidor real:
    # PowerShell
    $env:API_BASE_URL = "https://tu-dominio-o-ip-real:8080"
    $env:DEVICE_API_KEY = "la-device-api-key-real-de-ese-entorno"
    python simular_lecturas_sensor.py --codigo QR-A1 --altura 80 --capacidad 40

    # bash
    API_BASE_URL="https://tu-dominio-o-ip-real:8080" DEVICE_API_KEY="..." \
        python simular_lecturas_sensor.py --codigo QR-A1 --altura 80 --capacidad 40

El contenedor debe existir y tener capturada su altura_cm desde la web
antes de correr esto (si no, /registros-nivel responde 422). capacidad
debe coincidir con el capacidad_max real del contenedor (no hay
validación de eso en el backend, solo se usa aquí para que el peso
simulado tenga sentido con el % de llenado).

Variables de entorno (si no se ponen, usa estos valores por defecto,
pensados para desarrollo local):
    API_BASE_URL      default: http://localhost:8000
    DEVICE_API_KEY     default: cambia-esto-tambien
"""
import argparse
import os
import random
import sys
from datetime import datetime, timedelta

import requests

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
DEVICE_API_KEY = os.environ.get("DEVICE_API_KEY", "cambia-esto-tambien")


def enviar_lectura_nivel(codigo_contenedor: str, distancia_cm: float, fecha_hora: datetime) -> dict | None:
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
        print(f"  [ERROR nivel {resp.status_code}] {resp.text}")
        return None
    data = resp.json()
    print(f"  [OK nivel]  {fecha_hora:%Y-%m-%d %H:%M} -> distancia {distancia_cm:.1f}cm => {data['nivel_porcentaje']}%")
    return data


def enviar_lectura_peso(codigo_contenedor: str, peso_kg: float, fecha_hora: datetime) -> dict | None:
    resp = requests.post(
        f"{API_BASE_URL}/registros-peso",
        headers={"X-API-Key": DEVICE_API_KEY},
        json={
            "codigo_contenedor": codigo_contenedor,
            "peso_kg": round(peso_kg, 2),
            "fecha_hora": fecha_hora.isoformat(),
        },
        timeout=10,
    )
    if resp.status_code != 201:
        print(f"  [ERROR peso {resp.status_code}] {resp.text}")
        return None
    data = resp.json()
    print(f"  [OK peso]   {fecha_hora:%Y-%m-%d %H:%M} -> {peso_kg:.1f} Kg")
    return data


def simular_llenado_progresivo(
    codigo_contenedor: str,
    altura_cm: float,
    capacidad_max_kg: float,
    num_lecturas: int,
    horas_entre_lecturas: int,
) -> None:
    """
    Simula un contenedor llenándose con el tiempo: la distancia medida
    va BAJANDO (la basura se acerca al sensor de nivel) mientras el peso
    va SUBIENDO, hasta que se "recolecta" y ambos vuelven a su punto de
    vacío. Nivel y peso se mandan como dos lecturas separadas (dos
    sensores físicos distintos, ver módulo de peso) pero correlacionadas
    a la misma fracción de llenado en cada paso, con ruido independiente
    para que no queden idénticas — así se parece más a sensores reales.
    """
    print(
        f"Simulando {num_lecturas} lecturas (nivel + peso) para '{codigo_contenedor}' "
        f"(altura: {altura_cm}cm, capacidad: {capacidad_max_kg}Kg)...\n"
    )
    ahora = datetime.now()
    fraccion_llenado = random.uniform(0.05, 0.15)  # arranca casi vacío

    for i in range(num_lecturas):
        fecha_hora = ahora - timedelta(hours=(num_lecturas - i) * horas_entre_lecturas)

        fraccion_llenado += random.uniform(0.06, 0.14)
        if fraccion_llenado >= 0.95:
            # Ya casi lleno: simula que lo recolectaron y volvió a vaciarse
            fraccion_llenado = random.uniform(0.02, 0.15)

        # Nivel: a mayor llenado, MENOR distancia medida por el sensor ultrasónico
        distancia_cm = altura_cm * (1 - fraccion_llenado) + random.uniform(-1.5, 1.5)
        # Peso: a mayor llenado, MAYOR peso medido por la celda de carga
        peso_kg = capacidad_max_kg * fraccion_llenado + random.uniform(-0.5, 0.5)

        enviar_lectura_nivel(codigo_contenedor, max(0.0, distancia_cm), fecha_hora)
        enviar_lectura_peso(codigo_contenedor, max(0.0, peso_kg), fecha_hora)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simula lecturas de nivel y peso de un contenedor.")
    parser.add_argument("--codigo", required=True, help="codigo_contenedor ya registrado en el sistema")
    parser.add_argument(
        "--altura", type=float, required=True,
        help="altura_cm configurada para ese contenedor (debe coincidir con la que capturaste en la web)",
    )
    parser.add_argument(
        "--capacidad", type=float, required=True,
        help="capacidad_max (Kg) de ese contenedor (debe coincidir con la que capturaste en la web)",
    )
    parser.add_argument("--lecturas", type=int, default=10, help="cuántas lecturas simular (default: 10)")
    parser.add_argument("--intervalo-horas", type=int, default=4, help="horas entre cada lectura (default: 4)")
    args = parser.parse_args()

    print(f"API: {API_BASE_URL}\n")
    try:
        simular_llenado_progresivo(args.codigo, args.altura, args.capacidad, args.lecturas, args.intervalo_horas)
    except requests.exceptions.ConnectionError:
        print(f"No se pudo conectar a {API_BASE_URL}. ¿Está corriendo el backend?")
        sys.exit(1)

    print("\nListo. Verifica en la web (Contenedores) que nivel y peso se hayan actualizado,")
    print("o consulta GET /contenedores/{id}/registros-nivel y /registros-peso para ver el historial.")
