.PHONY: test-scraping-agent

-include .env
export $(shell sed 's/=.*//' .env)
APP_MODULE = main:app
PORT = 8081
RELOAD = --reload
UVICORN_CMD = PYTHONDONTWRITEBYTECODE=1 python -m uvicorn $(APP_MODULE) --host 0.0.0.0 --port $(PORT) $(RELOAD)

test-scraping-agent:
	@echo "<========== Validating ScrapingAgent Service ==========>"
	@curl -fs ${SCRAPING_AGENT_API_URL} > /dev/null \
		&& echo "<=========== ScrapingAgent Service is Started ===========>" \
		|| (echo "<=========== ScrapingAgent is NOT running! =========>" && exit 1)

run: start-redis start-mongo start-celery-beats
	@echo "<========== Starting Data Ingestor Service ===========>"
	@echo "Starting Uvicorn app: $(APP_MODULE) on 0.0.0.0:$(PORT) $(RELOAD)"
	@{ \
		$(UVICORN_CMD) & \
		echo $$! > .uvicorn_pid; \
		echo "Uvicorn app started. PID: $$(cat .uvicorn_pid)"; \
	}
	@echo "<========== Started Data Ingestor Service ===========>"

start-celery-beats:
	@echo "<========== Starting Celery Beats and Workers ==========>"
	@echo "<---------- Starting Celery Worker ---------->"; \
	celery -A app.celery_worker worker -Q data_ingestor_queue --loglevel=info & echo $$! > .celery_worker_pid; \
	echo "Celery Worker started with PID $$(cat .celery_worker_pid)"; \
	echo "<---------- Starting Celery Beat ---------->"; \
	celery -A app.celery_worker beat --loglevel=info & echo $$! > .celery_beat_pid; \
	echo "Celery Beat started with PID $$(cat .celery_beat_pid)"; \
	echo "<========== Started Celery Beats and Workers Successfully ==========>"

kill-celery-workers:
	@echo "<========== Stopping Celery Workers and Beat ===========>"
	@if [ -f .celery_worker_pid ]; then \
		PID=$$(cat .celery_worker_pid); \
		echo "Killing Celery Worker PID: $$PID"; \
		kill $$PID || kill -9 $$PID; \
		rm -f .celery_worker_pid; \
	else \
		echo "No Celery Worker PID file found."; \
	fi
	@if [ -f .celery_beat_pid ]; then \
		PID=$$(cat .celery_beat_pid); \
		echo "Killing Celery Beat PID: $$PID"; \
		kill $$PID || kill -9 $$PID; \
		rm -f .celery_beat_pid; \
	else \
		echo "No Celery Beat PID file found."; \
	fi
	@echo "<========== Celery Processes Stopped ===========>"

stop: kill-celery-workers stop-redis stop-mongo 
	@echo "<========== Stopping Data Ingestor Service ===========>"
	@if [ -f .uvicorn_pid ]; then \
		PID=$$(cat .uvicorn_pid); \
		if ps -p $$PID > /dev/null 2>&1; then \
			echo "Stopping Uvicorn app with PID $$PID..."; \
			kill $$PID; \
			sleep 2; \
			if ps -p $$PID > /dev/null 2>&1; then \
				echo "Force killing PID $$PID"; \
				kill -9 $$PID; \
			fi; \
		fi; \
		rm -f .uvicorn_pid; \
		echo "Uvicorn app stopped."; \
	else \
		echo "No PID file found. Is the service running?"; \
	fi
	@echo "<========== Cleaning Up Files ==========>"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "<========== Clean Up Completed ==========>"

start-mongo:
	@echo "<========== Starting MongoDB Server ===========>"
	@command -v brew >/dev/null && brew services start mongodb-community || echo "Brew not available; please start MongoDB manually."
	@echo "<========== MongoDB Server Started (if available) ===========>"

start-redis:
	@echo "<========== Starting Redis Server ===========>"
	@command -v brew >/dev/null && brew services start redis || echo "Brew not available; please start Redis manually."
	@echo "<========== Redis Server Started (if available) ===========>"

stop-redis:
	@echo "<========== Stopping Redis Server ===========>"
	@command -v brew >/dev/null && brew services stop redis || echo "Brew not available; please stop Redis manually."
	@echo "<========== Redis Server Stopped (if available) ===========>"

stop-mongo:
	@echo "<========== Stopping MongoDB Server ===========>"
	@command -v brew >/dev/null && brew services stop mongodb-community || echo "Brew not available; please stop MongoDB manually."
	@echo "<========== MongoDB Server Stopped (if available) ===========>"

