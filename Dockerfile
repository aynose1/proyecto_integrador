# Contenedor SOLO para el servidor de desarrollo de Expo (Metro), no para
# "correr la app" -- eso solo puede pasar en un celular/emulador real.
# Este contenedor sirve el bundle de JS y el bundler por LAN, para que
# Expo Go (en el celular) se conecte a él.
FROM node:20-bookworm-slim

ENV NODE_ENV=development

WORKDIR /app

# .npmrc primero: trae legacy-peer-deps=true, necesario para que
# "npm install" no truene con el conflicto de peer deps de expo-router
# (@radix-ui / react-dom, ver README del proyecto).
COPY package.json package-lock.json .npmrc ./
RUN npm install

COPY . .

EXPOSE 8081

# --host lan: el bundler escucha en todas las interfaces, no solo
# localhost -- imprescindible para que el celular (fuera del contenedor)
# lo alcance. La IP que se anuncia en el QR la controla la variable de
# entorno REACT_NATIVE_PACKAGER_HOSTNAME (ver compose.private.yaml).
CMD ["npx", "expo", "start", "--host", "lan"]
