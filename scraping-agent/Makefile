.PHONY: all run stop clean setup start-redis stop-redis start-mongo stop-mongo start-celery-workers kill-celery-workers delete-cache

# ========== ScrapingAgent Service ==========
APP_MODULE = main:app
PORT = 8080
RELOAD = --reload

UVICORN_CMD = PYTHONDONTWRITEBYTECODE=1 python -m uvicorn $(APP_MODULE) --host 0.0.0.0 --port $(PORT) $(RELOAD)

all: run

run: start-redis start-mongo start-celery-workers
	@echo "<========== Starting ScrapingAgent Service ===========>"
	@echo "Starting Uvicorn app: $(APP_MODULE) on 0.0.0.0:$(PORT) $(RELOAD)"
	@{ \
		$(UVICORN_CMD) & \
		echo $$! > .uvicorn_pid; \
		echo "Uvicorn app started. PID: $$(cat .uvicorn_pid)"; \
	}
	@echo "<========== Started ScrapingAgent Service ===========>"

start-mongo:
	@echo "<========== Starting MongoDB Server ===========>"
	@command -v brew >/dev/null && brew services start mongodb-community || echo "Brew not available; please start MongoDB manually."
	@echo "<========== MongoDB Server Started (if available) ===========>"

start-redis:
	@echo "<========== Starting Redis Server ===========>"
	@command -v brew >/dev/null && brew services start redis || echo "Brew not available; please start Redis manually."
	@echo "<========== Redis Server Started (if available) ===========>"

start-celery-workers:
	@echo "<========== Starting Celery Workers ===========>"
	@celery -A api.celery_worker.celery_app worker -Q scraping_agent_scrape_low --loglevel=info --concurrency=2 & \
	celery -A api.celery_worker.celery_app worker -Q scraping_agent_scrape_medium --loglevel=info --concurrency=5 & \
	celery -A api.celery_worker.celery_app worker -Q scraping_agent_scrape_high --loglevel=info --concurrency=10 &
	@echo "<========== Celery Workers Started ===========>"

stop: kill-celery-workers stop-redis stop-mongo
	@echo "<========== Stopping ScrapingAgent Service ===========>"
	@if [ -f .uvicorn_pid ]; then \
		PID=$$(cat .uvicorn_pid); \
		echo "Stopping Uvicorn app with PID: $$PID"; \
		kill -TERM $$PID || kill -KILL $$PID; \
		rm .uvicorn_pid; \
		echo "Uvicorn app stopped."; \
	else \
		echo "No Uvicorn PID file found. Is the app running?"; \
	fi
	@echo "Deleting PyCache Files......"
	find . -type d -name '__pycache__' -exec rm -r {} +
	@echo "<========== Stopped ScrapingAgent Service ===========>"

stop-redis:
	@echo "<========== Stopping Redis Server ===========>"
	@command -v brew >/dev/null && brew services stop redis || echo "Brew not available; please stop Redis manually."
	@echo "<========== Redis Server Stopped (if available) ===========>"

stop-mongo:
	@echo "<========== Stopping MongoDB Server ===========>"
	@command -v brew >/dev/null && brew services stop mongodb-community || echo "Brew not available; please stop MongoDB manually."
	@echo "<========== MongoDB Server Stopped (if available) ===========>"

kill-celery-workers:
	@echo "<========== Stopping Celery Workers ===========>"
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
	@echo "<========== Celery Workers Stopped ===========>"

setup:
	@echo "<========== Installing Dependencies ===========>"
	pip install -r requirements.txt
	@echo "<========== Dependencies Installed ===========>"

clean:
	@echo "<========== Cleaning up ScrapingAgent Project ===========>"
	rm -rf __pycache__ .uvicorn_pid
	@echo "<========== Cleanup Complete ===========>"

delete-cache:
	@echo "<========== Deleting PyCache Files ===========>"
	find . -type d -name '__pycache__' -exec rm -r {} +
	@echo "<========== PyCache Deleted ===========>"
