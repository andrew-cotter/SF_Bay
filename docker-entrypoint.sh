#!/usr/bin/env bash
set -e

# Write .streamlit/secrets.toml from env if MySQL connection env vars are set.
# Uses mysql+pymysql:// so PyMySQL is used (works on Streamlit Community Cloud and Docker).
if [[ -n "${MYSQL_HOST:-}" ]]; then
  mkdir -p .streamlit
  # URL-encode password in case it contains special characters
  MYSQL_PASSWORD_ESCAPED=$(python3 -c "import os, urllib.parse; print(urllib.parse.quote(os.environ.get('MYSQL_PASSWORD', '')))")
  MYSQL_URL="mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD_ESCAPED}@${MYSQL_HOST}:${MYSQL_PORT:-3306}/${MYSQL_DATABASE:-defaultdb}"
  QUERY_LINE=""
  if [[ -n "${MYSQL_QUERY_CHARSET:-}" ]]; then
    QUERY_LINE="query = { charset = \"${MYSQL_QUERY_CHARSET}\" }"
  fi
  cat > .streamlit/secrets.toml << EOF
[connections.mysql]
url = "${MYSQL_URL}"
${QUERY_LINE}
EOF
fi

exec "$@"
