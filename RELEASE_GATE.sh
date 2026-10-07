#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
cd "$ROOT"

fail=0
need_file() { [ -f "$1" ] || { echo "MISSING: $1"; fail=1; }; }
need_file backend/manage.py
need_file backend/config/asgi.py
need_file backend/apps/realtime/jwt_middleware.py
need_file infra/docker-compose.staging.yml
need_file web/package.json
need_file web/vite.config.ts
need_file mobile/package.json
need_file mobile/eas.json

python -m compileall -q backend || fail=1
python - <<'PY' || exit 1
import json
for p in ['web/package.json','mobile/package.json','mobile/eas.json']:
    with open(p, encoding='utf-8') as f: json.load(f)
print('JSON validation: PASS')
PY

if grep -R '"latest"' web/package.json mobile/package.json >/dev/null 2>&1; then
  echo 'BLOCKER: unpinned latest dependency found'; fail=1
else
  echo 'Dependency pinning: PASS'
fi

if grep -R 'staging-only-change-me' infra/docker-compose.staging.yml >/dev/null; then
  echo 'Staging secrets are intentionally non-production placeholders.'
fi

if [ "$fail" -ne 0 ]; then
  echo 'RELEASE GATE: FAIL'
  exit 1
fi
echo 'RELEASE GATE: STATIC PASS (runtime builds/E2E require Docker/Node/EAS environment)'
