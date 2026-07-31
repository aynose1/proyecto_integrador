# pi_movil — App de recolectores

App móvil (Expo + React Native, JavaScript) para que los recolectores
consulten sus rutas asignadas, vean qué contenedores les faltan por
recolectar, y confirmen la recolección escaneando el código QR del
contenedor.

## Primeros pasos

```bash
npm install
npx expo install expo-secure-store expo-camera
cp .env.example .env
# edita .env con la URL/IP real de tu backend
npx expo start
```

Si `npm install` truena con un error `ERESOLVE`, ya está resuelto de
antemano con el `.npmrc` incluido — solo vuelve a correr `npm install`.

## Estructura

```
app/                    Expo Router (rutas de navegación, archivos delgados)
  _layout.js            Stack raíz
  index.js              Pantalla "puerta" (decide login vs tabs)
  login.js
  (tabs)/
    _layout.js           Barra de Tabs: Rutas / Escanear QR / Perfil
    rutas/
      _layout.js          Stack interno de la tab Rutas
      index.js            Lista de rutas
      [rutaId].js         Detalle de ruta (contenedores pendientes)
      contenedor/
        [contenedorId].js  Detalle de un contenedor
    escanear.js
    perfil.js

screens/                Las pantallas reales (lo que renderiza cada archivo de app/)
components/             Componentes reutilizables (NivelBar, EmptyState, PageHeader)
theme/                  Colores de marca (mismos tokens que la web)
config/                 URL de la API (lee EXPO_PUBLIC_API_BASE_URL del .env)
services/                Llamadas a la API (apiClient, authService, rutasService, contenedoresService)
```

## Flujo de la app

1. **Login** — solo recolectores pueden entrar (se valida `tipo_usuario.tipo === "recolector"` contra `GET /usuarios/me`).
2. **Rutas** — lista las rutas de HOY del recolector (`GET /rutas/me?fecha=...`).
3. **Detalle de ruta** — solo muestra los contenedores en estado `pendiente` (los ya `recolectado` no aparecen).
4. **Detalle de contenedor** — info completa, incluido el nivel de llenado actual.
5. **Escanear QR** — escanea cualquier contenedor, busca automáticamente en cuál ruta de HOY está pendiente, y ofrece confirmarlo ahí mismo (`POST /rutas/{id}/recolectar`).
6. **Perfil** — datos del recolector + cerrar sesión.

## Notas

- Los íconos en `assets/` son placeholders generados automáticamente (fondo teal `#0b3b38`, iniciales "PI") — reemplázalos cuando tengas el arte final.
- La sesión se guarda con `expo-secure-store` (más seguro que `AsyncStorage` para tokens).
- El escaneo QR usa `expo-camera` (`CameraView` + `useCameraPermissions`), no `expo-barcode-scanner` (deprecado).
