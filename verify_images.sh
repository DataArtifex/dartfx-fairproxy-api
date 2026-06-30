#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="dartfx/fairproxy-api:latest"

echo "=== Verifying Docker Image: ${IMAGE_NAME} ==="

# Check that the container starts up and serves the status endpoint
echo -n "Checking API HTTP /status endpoint... "
CONTAINER_NAME="fairproxy-api-verify-temp"
TEST_PORT=8099

cleanup() {
  docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Run in background with mapped port
docker run -d --name "${CONTAINER_NAME}" -p "${TEST_PORT}":8000 "${IMAGE_NAME}" >/dev/null

MAX_ATTEMPTS=20
ATTEMPT=0
SUCCESS=false

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  if RESPONSE=$(curl -s --fail "http://localhost:${TEST_PORT}/status" 2>/dev/null); then
    # Verify we get a valid status response containing version
    if echo "$RESPONSE" | grep -q '"status"'; then
      SUCCESS=true
      break
    fi
  fi
  ATTEMPT=$((ATTEMPT + 1))
  sleep 0.5
done

if [ "$SUCCESS" = true ]; then
  echo "OK"
else
  echo "FAILED"
  echo "=== Container logs ==="
  docker logs "${CONTAINER_NAME}"
  exit 1
fi

echo "=== All checks passed successfully! ==="
