"""
Script para comprobar cómo se ve representado el nivel de llenado en la
web (la barra de progreso y su color) sin tener que esperar a que un
sensor real mande lecturas. Manda una lectura a la vez, con pausa entre
cada una, para que puedas refrescar la página de Contenedores y ver
cómo cambia la barra en cada paso.

La web colorea la barra así (según web/app/templates/contenedores/list.html):
    nivel >= 80%  -> rojo   (bg-danger)
    nivel >= 50%  -> amarillo (bg-warning)
    nivel < 50%   -> verde  (bg-success)

Por default recorre una secuencia que cruza justo esos dos umbrales, para
que veas el cambio de color en el momento exacto en que ocurre.

Uso (secuencia por defecto):
    python probar_visualizacion_nivel.py --codigo QR-A1 --altura 100

Uso (niveles específicos, ej. para revisar un caso puntual):
    python probar_visualizacion_nivel.py --codigo QR-A1 --altura 100 --niveles 10,49,50,79,80,100

Uso (sin pausas, para dejarlo correr solo):
    python probar_visualizacion_nivel.py --codigo QR-A1 --altura 100 --sin-pausa

Requiere las variables de entorno (o edítalas abajo):
    API_BASE_URL     ej. http://localhost:8000
    DEVICE_API_KEY    la misma que configuraste en el backend (.env)

El contenedor debe tener altura_cm ya configurada desde la web, y
--altura debe coincidir con ese mismo valor.
"""
import argparse
import os
import sys
from datetime import datetime

import requests

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
DEVICE_API_KEY = os.environ.get("DEVICE_API_KEY", "cambia-esto-tambien")

# Secuencia por defecto: cruza los dos umbrales de color (50% y 80%)
# justo antes y justo después, para ver el cambio en el momento exacto.
NIVELES_POR_DEFECTO = [0, 10, 25, 49, 50, 51, 65, 79, 80, 81, 95, 100]


def color_esperado(nivel: float) -> str:
    if nivel >= 80:
        return "ROJO (bg-danger)"
    if nivel >= 50:
        return "AMARILLO (bg-warning)"
    return "VERDE (bg-success)"


def enviar_nivel(codigo_contenedor: str, altura_cm: float, nivel_objetivo: float) -> dict | None:
    # nivel% = 100 - (distancia / altura * 100)  =>  distancia = altura * (1 - nivel/100)
    distancia_cm = altura_cm * (1 - nivel_objetivo / 100)

    resp = requests.post(
        f"{API_BASE_URL}/registros-nivel",
        headers={"X-API-Key": DEVICE_API_KEY},
        json={
            "codigo_contenedor": codigo_contenedor,
            "distancia_cm": round(distancia_cm, 2),
            "fecha_hora": datetime.now().isoformat(),
        },
        timeout=10,
    )
    if resp.status_code != 201:
        print(f"  [ERROR {resp.status_code}] {resp.text}")
        return None
    return resp.json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prueba visual del nivel de llenado en la web.")
    parser.add_argument("--codigo", required=True, help="codigo_contenedor ya registrado")
    parser.add_argument("--altura", type=float, required=True, help="altura_cm configurada para ese contenedor")
    parser.add_argument("--niveles", default=None, help="lista de porcentajes separados por coma, ej. 10,50,90 (si no se manda, usa la secuencia por defecto)")
    parser.add_argument("--sin-pausa", action="store_true", help="no esperar Enter entre cada nivel")
    args = parser.parse_args()

    niveles = (
        [float(n.strip()) for n in args.niveles.split(",")]
        if args.niveles
        else NIVELES_POR_DEFECTO
    )

    print(f"API: {API_BASE_URL}")
    print(f"Contenedor: {args.codigo} (altura configurada: {args.altura}cm)")
    print(f"Se van a mandar {len(niveles)} niveles: {niveles}\n")

    try:
        for i, nivel in enumerate(niveles, start=1):
            print(f"[{i}/{len(niveles)}] Mandando nivel objetivo {nivel}% -> esperado: {color_esperado(nivel)}")
            data = enviar_nivel(args.codigo, args.altura, nivel)
            if data:
                print(f"        Confirmado por la API: nivel_porcentaje={data['nivel_porcentaje']}%")

            if not args.sin_pausa and i < len(niveles):
                input("        Revisa la web (Contenedores) y presiona Enter para el siguiente nivel...")
            print()
    except requests.exceptions.ConnectionError:
        print(f"No se pudo conectar a {API_BASE_URL}. ¿Está corriendo el backend?")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
        sys.exit(0)

    print("Listo. El último nivel mandado quedó como nivel_actual del contenedor en la web.")
