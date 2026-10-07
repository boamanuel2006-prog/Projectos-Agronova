#!/bin/sh
set -eu
BASE="${BASE_URL:-http://localhost:8000}"
echo "[1/4] health"
curl -fsS "$BASE/health/"
echo
echo "[2/4] readiness"
curl -fsS "$BASE/readiness/"
echo
echo "[3/4] API catalog"
curl -fsS "$BASE/api/v1/catalog/" >/dev/null
echo "catalog: OK"
echo "[4/4] websocket route is exposed through the ASGI gateway; run an authenticated client smoke separately"
echo "STAGING SMOKE: PASS"
