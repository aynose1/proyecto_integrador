# Imagen de HAProxy con "envsubst" agregado, para poder sustituir
# ${PRIVATE_HOST_IP} en haproxy.cfg.template al arrancar el contenedor
# (ver docker-entrypoint.sh). HAProxy en sí no soporta variables de
# entorno dentro de su propio archivo de configuración.
FROM haproxy:3.2-alpine

USER root
RUN apk add --no-cache gettext

COPY haproxy.cfg.template /usr/local/etc/haproxy/haproxy.cfg.template
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["haproxy", "-f", "/usr/local/etc/haproxy/haproxy.cfg", "-db"]
