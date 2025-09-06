.PHONY: test-scraping-agent

-include .env
export $(shell sed 's/=.*//' .env)
APP_MODULE = main:app
PORT = 8090
RELOAD = --reload
UVICORN_CMD = PYTHONDONTWRITEBYTECODE=1 python -m uvicorn $(APP_MODULE) --host 0.0.0.0 --port $(PORT) $(RELOAD)

test-scraping-agent:
	@echo "<========== Validating ScrapingAgent Service ==========>"
	@curl -fs ${SCRAPING_AGENT_API_URL} > /dev/null \
		&& echo "<=========== ScrapingAgent Service is Started ===========>" \
		|| (echo "<=========== ScrapingAgent is NOT running! =========>" && exit 1)

run: test-scraping-agent
	@echo "<========== Starting Data Ingestor Service ===========>"
	@echo "Starting Uvicorn app: $(APP_MODULE) on 0.0.0.0:$(PORT) $(RELOAD)"
	@{ \
		$(UVICORN_CMD) & \
		echo $$! > .uvicorn_pid; \
		echo "Uvicorn app started. PID: $$(cat .uvicorn_pid)"; \
	}
	@echo "<========== Started Data Ingestor Service ===========>"
stop:
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
			rm -f .uvicorn_pid; \
			echo "Uvicorn app stopped."; \
		else \
			echo "No process running with PID $$PID. Cleaning up PID file."; \
			rm -f .uvicorn_pid; \
		fi \
	else \
		echo "No PID file found. Is the service running?"; \
	fi
	@echo "<========== Stopped Data Ingestor Service ===========>"


