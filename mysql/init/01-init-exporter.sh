#!/bin/bash
set -euo pipefail

# Crea un usuario de SOLO MONITOREO para mysqld_exporter (Prometheus).
# Se ejecuta automáticamente la primera vez que arranca el contenedor de
# MySQL (docker-entrypoint corre los .sh de esta carpeta con el volumen
# de datos vacío). Las credenciales salen de variables de entorno del
# .env raíz -- deben coincidir con lo que tengas en mysql/exporter.my.cnf.
mysql -u root -p"${MYSQL_ROOT_PASSWORD}" <<-EOSQL
    CREATE USER IF NOT EXISTS '${MYSQL_EXPORTER_USER}'@'%' IDENTIFIED BY '${MYSQL_EXPORTER_PASSWORD}';
    GRANT PROCESS, REPLICATION CLIENT ON *.* TO '${MYSQL_EXPORTER_USER}'@'%';
    FLUSH PRIVILEGES;
EOSQL
