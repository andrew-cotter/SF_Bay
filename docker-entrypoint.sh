#!/usr/bin/env bash
set -e

# Write .streamlit/secrets.toml from env if MySQL connection env vars are set.
# Use this when secrets come from the environment (e.g. ECS task def, AWS Secrets Manager).
if [[ -n "${MYSQL_HOST:-}" ]]; then
  mkdir -p .streamlit
  QUERY_LINE=""
  if [[ -n "${MYSQL_QUERY_CHARSET:-}" ]]; then
    QUERY_LINE="query = { charset = \"${MYSQL_QUERY_CHARSET}\" }"
  fi
  cat > .streamlit/secrets.toml << EOF
[connections.mysql]
dialect = "mysql"
driver = "pymysql"
host = "${MYSQL_HOST}"
port = ${MYSQL_PORT:-3306}
dbname = "${MYSQL_DATABASE:-defaultdb}"
username = "${MYSQL_USER}"
password = "${MYSQL_PASSWORD}"
${QUERY_LINE}
EOF
fi

exec "$@"
