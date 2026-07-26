# Backend — Sistema de Gestión de Residuos Sólidos

## 1. Instalación

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # y llena los valores reales
```

## 2. Generar la migración inicial del esquema

Con la base de datos vacía ya montada y `.env` apuntando a ella:

```bash
alembic revision --autogenerate -m "esquema inicial"
```

Esto crea un archivo en `alembic/versions/` (Alembic le pondrá un id
automático, ej. `alembic/versions/a1b2c3d4_esquema_inicial.py`).

**Importante:** abre `alembic/versions/0002_seed_catalogos.py` y actualiza
la línea `down_revision = "0001_esquema_inicial"` con el id real que
Alembic acaba de generar para tu migración de esquema. También puedes
renombrar el archivo autogenerado a `0001_esquema_inicial.py` y fijar
`revision = "0001_esquema_inicial"` dentro de él, para que coincida
directamente sin tener que editar el seeder.

## 3. Aplicar migraciones (esquema + seed de catálogos)

```bash
alembic upgrade head
```

Esto crea todas las tablas y siembra:
- `tipos_usuarios`: administrador, recolector
- `estados`: activo, inactivo, mantenimiento, pendiente, recolectado, atendido
- `motivos_incidencia`: Lectura errónea, Sensor dañado, Contenedor dañado, Otro
- `tipos_notificacion`: Nivel alto, Incidencia reportada
- `zonas`: Edificio A, Edificio B, Edificio C (el administrador puede agregar más desde `/zonas`)
- Un primer usuario administrador: `codigo_usuario=ADMIN001`,
  contraseña temporal `CambiaEstaClave123!` — **cámbiala en cuanto
  inicies sesión por primera vez.**

## 4. Levantar el servidor

```bash
uvicorn app.main:app --reload
```

Documentación interactiva en `http://localhost:8000/docs`.

## 5. Estructura del proyecto

```
app/
  core/
    config.py         # Settings desde variables de entorno
    security.py        # Hashing de contraseñas, creación/validación de JWT
    rate_limit.py        # Instancia compartida de slowapi
  db/
    base_class.py     # Base declarativa de SQLAlchemy
    session.py         # Engine + SessionLocal + dependencia get_db
  models/              # Modelos SQLAlchemy, un archivo por entidad (o grupo de catálogos)
  schemas/             # Esquemas Pydantic (input/output), un archivo por entidad
  crud/                # Acceso a datos: un archivo por entidad, hereda de CRUDBase
  api/
    deps.py             # get_current_user, require_admin, require_recolector, verify_device_api_key
    router.py            # Agrega todos los routers en uno solo
    routes/               # Un archivo de endpoints por entidad
      auth.py
      usuarios.py
      contenedores.py
      rutas.py
      registros_nivel.py
      incidencias.py
      notificaciones.py
      catalogos.py
  main.py              # Instancia la app, registra el rate limiter y el router
alembic/
  env.py
  versions/
requirements.txt
.env.example
```

Cada capa se importa hacia abajo únicamente: `routes` usa `crud`, `crud`
usa `models`, `routes` valida con `schemas`. Así, si mañana cambian una
regla de negocio (ej. cómo se calcula `nivel_actual`), el cambio vive en
un solo lugar (`crud/registro_nivel.py`) sin tocar los endpoints.

## 6. Endpoints principales

| Método | Ruta | Quién | Descripción |
|---|---|---|---|
| POST | `/auth/register` | público | Auto-registro de administrador (plataforma web) |
| POST | `/auth/login` | público | Login con `codigo_usuario` + `contrasena` (rate limited) |
| POST | `/auth/refresh` | público | Renueva access token con el refresh token |
| GET | `/usuarios/me` | autenticado | Perfil propio |
| GET/POST/PUT/DELETE | `/usuarios` | admin | CRUD de administradores/recolectores |
| GET/POST/PUT/DELETE | `/contenedores` | admin (lectura: cualquiera autenticado) | CRUD de contenedores |
| GET | `/contenedores/qr/{codigo}` | autenticado | Consulta por código QR |
| POST | `/contenedores/{id}/vaciar` | recolector | Marca vaciado (registro manual, nivel 0%) |
| GET/POST/PUT/DELETE | `/rutas` | admin | CRUD de rutas de recolección |
| GET | `/rutas/me` | recolector | Solo sus rutas asignadas |
| GET | `/rutas/{id}` | admin o dueño | Detalle de ruta (protegido contra BOLA) |
| POST | `/registros-nivel` | dispositivo (API Key) | Ingesta de lectura del sensor, identificado por `codigo_contenedor` |
| GET | `/contenedores/{id}/registros-nivel` | autenticado | Historial para el dashboard |
| POST | `/incidencias` | recolector | Reporta falso positivo del sensor |
| GET/PATCH | `/incidencias` | admin | Lista y atiende incidencias |
| GET | `/notificaciones/me` | autenticado | Notificaciones propias |
| GET/POST/PUT/DELETE | `/zonas` | admin (lectura: cualquiera) | Ej. "Edificio A/B/C"; el admin da de alta más |
| GET/POST/PUT/DELETE | `/sectores` | admin (lectura: cualquiera) | Cada sector pertenece a una zona (`?id_zona=` filtra) |
| GET/POST/PUT/DELETE | `/ubicaciones` | admin (lectura: cualquiera) | Une un sector para poder asignarlo a un contenedor |
| GET | `/catalogos/*` | autenticado | Catálogos de solo lectura (estados, motivos, tipos) |

**Nota sobre el sensor:** se identifica con `codigo_contenedor` (el mismo
código impreso/QR del contenedor), no con el id interno de la base de
datos — así el firmware no necesita conocer IDs autogenerados.

## 7. Pendiente para siguientes etapas

- Definir y construir el dashboard (gráficas de frecuencia de llenado, KPIs)
- Reportes descargables en PDF/Excel
- Generación de notificaciones automáticas (ej. cuando `nivel_actual` supera un umbral)
- Tests automatizados con pytest (por ahora se probó manualmente el flujo completo con TestClient)
