import re

# Lista negra de contraseñas comunes/filtradas -- la recomendación
# vigente de NIST 800-63B es rechazar contraseñas conocidas/comunes en
# vez de (o además de) exigir reglas de composición rígidas. Incluye
# variantes obvias en español, ya que el sistema es para México.
CONTRASENAS_COMUNES = frozenset(
    {
        "12345678", "123456789", "1234567890", "password", "password1",
        "contraseña", "contrasena", "contrasena1", "qwerty123", "qwertyuiop",
        "11111111", "00000000", "administrador", "admin1234", "admin12345",
        "letmein123", "welcome123", "iloveyou1", "abc123456", "123123123",
        "1q2w3e4r5t", "passw0rd1", "trustno1", "football1", "monkey123",
        "dragon123", "master123", "shadow123", "superman1", "batman123",
        "princess1", "sunshine1", "aaaaaaaa", "zxcvbnm12", "changeme1",
        "temporal1", "bienvenido1", "usuario123", "cambiar123",
        "recolector1", "administrador1", "guest1234", "test12345",
        "demo12345", "root12345", "12345678a", "a12345678", "qazwsxedc",
    }
)


def validar_password_fuerte(valor: str) -> str:
    """
    Política de contraseñas para cualquier lugar del sistema donde se
    capture una (crear usuario, editar usuario, auto-registro de admin):
    - Rechaza contraseñas de la lista negra (sin importar mayúsculas).
    - Exige al menos una mayúscula, un número y un símbolo.
    La longitud mínima (8) ya se valida aparte con Field(min_length=8)
    en cada schema que use esto.
    """
    if valor.lower() in CONTRASENAS_COMUNES:
        raise ValueError("Esa contraseña es demasiado común/insegura. Elige una distinta.")
    if not re.search(r"[A-Z]", valor):
        raise ValueError("La contraseña debe incluir al menos una letra mayúscula.")
    if not re.search(r"[0-9]", valor):
        raise ValueError("La contraseña debe incluir al menos un número.")
    if not re.search(r"[^A-Za-z0-9]", valor):
        raise ValueError("La contraseña debe incluir al menos un símbolo (ej. !@#$%&*).")
    return valor
