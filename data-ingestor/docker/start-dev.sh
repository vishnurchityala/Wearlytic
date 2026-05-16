#!/usr/bin/env bash
set -euo pipefail

export REDIS_URL="${REDIS_URL:-redis://127.0.0.1:6379/0}"

pids=()

shutdown() {
  if [ "${#pids[@]}" -gt 0 ]; then
    kill "${pids[@]}" 2>/dev/null || true
    wait "${pids[@]}" 2>/dev/null || true
  fi
}

trap shutdown EXIT INT TERM

redis-server --bind 127.0.0.1 --port 6379 --save "" --appendonly no &
pids+=("$!")

until redis-cli -u "$REDIS_URL" ping >/dev/null 2>&1; do
  sleep 0.2
done

celery -A app.celery_worker worker \
  -Q data_ingestor_queue \
  -P solo \
  -c "${DATA_INGESTOR_CONCURRENCY:-1}" \
  -n data_ingestor@%h \
  --loglevel=info &
pids+=("$!")

celery -A app.celery_worker beat \
  --loglevel=info \
  --schedule /tmp/celerybeat-schedule &
pids+=("$!")

python -m uvicorn main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8081}" \
  --reload &
pids+=("$!")

wait -n "${pids[@]}"
