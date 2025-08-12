.PHONY: all run stop clean setup start-redis stop-redis

APP_MODULE = main:app
PORT = 8080
RELOAD = --reload

UVICORN_CMD = PYTHONDONTWRITEBYTECODE=1 python -m uvicorn $(APP_MODULE) --host 0.0.0.0 --port $(PORT) $(RELOAD)

all: run

run: start-redis start-mongo start-celery-workers 
	@echo "Starting Uvicorn app: $(APP_MODULE) on 0.0.0.0:$(PORT) $(RELOAD)"
	@{ \
		$(UVICORN_CMD) & \
		echo $$! > .uvicorn_pid; \
		echo "Uvicorn app started. PID: $$(cat .uvicorn_pid)"; \
	}

start-mongo:
	@echo "Starting MongoDB Server"
	@command -v brew >/dev/null && brew services start mongodb-community@8.0 || echo "Brew not available; please start MongoDB manually."

start-redis:
	@echo "Starting Redis Server"
	@command -v brew >/dev/null && brew services start redis || echo "Brew not available; please start Redis manually."

start-celery-workers:
	@echo "Starting Celery Workers"
	@celery -A api.celery_worker.celery_app worker -Q scrape_low --loglevel=info --concurrency=2 & \
	celery -A api.celery_worker.celery_app worker -Q scrape_medium --loglevel=info --concurrency=5 & \
	celery -A api.celery_worker.celery_app worker -Q scrape_high --loglevel=info --concurrency=10 &
	
stop: kill-celery-workers stop-redis stop-mongo
	@if [ -f .uvicorn_pid ]; then \
		PID=$$(cat .uvicorn_pid); \
		echo "Stopping Uvicorn app with PID: $$PID"; \
		kill -TERM $$PID || kill -KILL $$PID; \
		rm .uvicorn_pid; \
	else \
		echo "No Uvicorn PID file found. Is the app running?"; \
	fi

stop-redis:
	@echo "Stopping Redis Server"
	@command -v brew >/dev/null && brew services stop redis || echo "Brew not available; please stop Redis manually."

stop-mongo:
	@echo "Stopping MongoDB Server"
	@command -v brew >/dev/null && brew services stop mongodb-community@8.0 || echo "Brew not available; please stop MongoDB manually."

kill-celery-workers:
	@echo "Finding all Celery processes..."
	@PIDS=$$(ps aux | grep 'celery' | grep -v 'grep' | awk '{print $$2}'); \
	if [ -z "$$PIDS" ]; then \
		echo "No Celery processes found."; \
	else \
		echo "Killing Celery PIDs: $$PIDS"; \
		kill $$PIDS; \
		sleep 2; \
		for PID in $$PIDS; do \
			if ps -p $$PID > /dev/null; then \
				echo "Force killing PID: $$PID"; \
				kill -9 $$PID; \
			fi; \
		done; \
		echo "All Celery processes terminated."; \
	fi

setup:
	@echo "Installing all dependencies"
	pip install -r requirements.txt

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__ .uvicorn_pid
	@echo "Cleanup complete."

delete-chache:
	find . -type d -name '__pycache__' -exec rm -r {} +
