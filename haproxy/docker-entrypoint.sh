#!/bin/sh
set -e

# Genera el haproxy.cfg real a partir de la plantilla, sustituyendo
# ${PRIVATE_HOST_IP} por el valor real de la variable de entorno.
# Así, el mismo haproxy.cfg.template sirve tanto para pruebas locales
# (PRIVATE_HOST_IP=host.docker.internal) como para el despliegue real
# en la nube (PRIVATE_HOST_IP=<IP privada real de la VM del backend>),
# sin tener que editar el archivo a mano en cada entorno.
envsubst '${PRIVATE_HOST_IP}' \
  < /usr/local/etc/haproxy/haproxy.cfg.template \
  > /usr/local/etc/haproxy/haproxy.cfg

exec "$@"
