#!/usr/bin/env bash
#
# EC2 startup script: fetch MySQL credentials from AWS Secrets Manager,
# write /opt/baytemps/mysql.env, then run the baytemps Docker container.
#
# Prerequisites on the instance:
#   - IAM role with secretsmanager:GetSecretValue on the secret
#   - Docker installed and running
#   - jq installed (yum install jq / apt install jq)
#
# Configure via environment or pass as arguments:
#   SECRET_ID    (or $1) - Secrets Manager secret name or ARN
#   AWS_REGION   (or $2) - AWS region, e.g. us-east-1
#   DOCKER_IMAGE (optional) - image to run, default: baytemps:latest
#
# Usage:
#   SECRET_ID=my-mysql-secret AWS_REGION=us-east-1 ./ec2-start-baytemps.sh
#   ./ec2-start-baytemps.sh my-mysql-secret us-east-1
#
# Copy to EC2 and run from /opt/baytemps, or run via systemd (see baytemps.service).

set -e

SECRET_ID="${SECRET_ID:-${1:?SECRET_ID or first argument required}}"
AWS_REGION="${AWS_REGION:-${2:?AWS_REGION or second argument required}}"
DOCKER_IMAGE="${DOCKER_IMAGE:-baytemps:latest}"
ENV_FILE="${ENV_FILE:-/opt/baytemps/mysql.env}"
CONTAINER_NAME="${CONTAINER_NAME:-baytemps}"
DOCKER_CMD="${DOCKER_CMD:-docker}"

# Optional: secret key names if your secret uses different keys
SECRET_KEY_HOST="${SECRET_KEY_HOST:-host}"
SECRET_KEY_PORT="${SECRET_KEY_PORT:-port}"
SECRET_KEY_USER="${SECRET_KEY_USER:-username}"
SECRET_KEY_PASS="${SECRET_KEY_PASS:-password}"
SECRET_KEY_DB="${SECRET_KEY_DB:-database}"

mkdir -p "$(dirname "$ENV_FILE")"

echo "Fetching secret ${SECRET_ID} from ${AWS_REGION}..."
SECRET_JSON=$(aws secretsmanager get-secret-value \
  --secret-id "$SECRET_ID" \
  --region "$AWS_REGION" \
  --query SecretString \
  --output text)

echo "Writing ${ENV_FILE}..."
cat > "$ENV_FILE" << EOF
MYSQL_HOST=$(echo "$SECRET_JSON" | jq -r ".${SECRET_KEY_HOST}")
MYSQL_PORT=$(echo "$SECRET_JSON" | jq -r ".${SECRET_KEY_PORT}")
MYSQL_USER=$(echo "$SECRET_JSON" | jq -r ".${SECRET_KEY_USER}")
MYSQL_PASSWORD=$(echo "$SECRET_JSON" | jq -r ".${SECRET_KEY_PASS}")
MYSQL_DATABASE=$(echo "$SECRET_JSON" | jq -r ".${SECRET_KEY_DB}")
EOF
chmod 600 "$ENV_FILE"

echo "Starting container ${CONTAINER_NAME}..."
$DOCKER_CMD stop "$CONTAINER_NAME" 2>/dev/null || true
$DOCKER_CMD rm "$CONTAINER_NAME" 2>/dev/null || true
$DOCKER_CMD run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  -p 8501:8501 \
  --env-file "$ENV_FILE" \
  "$DOCKER_IMAGE"

echo "Done. App should be available on port 8501."
