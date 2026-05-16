#!/usr/bin/env bash
set -euo pipefail

export PLATFORM="${PLATFORM:-linux64}"
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

celery -A api.celery_worker.celery_app worker \
  -Q scraping_agent_scrape_low \
  --loglevel=info \
  --concurrency="${SCRAPING_AGENT_LOW_CONCURRENCY:-2}" &
pids+=("$!")

celery -A api.celery_worker.celery_app worker \
  -Q scraping_agent_scrape_medium \
  --loglevel=info \
  --concurrency="${SCRAPING_AGENT_MEDIUM_CONCURRENCY:-5}" &
pids+=("$!")

celery -A api.celery_worker.celery_app worker \
  -Q scraping_agent_scrape_high \
  --loglevel=info \
  --concurrency="${SCRAPING_AGENT_HIGH_CONCURRENCY:-10}" &
pids+=("$!")

python -m uvicorn main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8080}" \
  --reload &
pids+=("$!")

wait -n "${pids[@]}"
