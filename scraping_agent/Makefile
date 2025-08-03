.PHONY: all run stop clean

APP_MODULE = main:app
PORT = 8000
RELOAD = 

all: run

run:
	@echo "Starting Uvicorn app: $(APP_MODULE) on 0.0.0.0:$(PORT) $(RELOAD)"
	@{ \
		PYTHONDONTWRITEBYTECODE=1 uvicorn $(APP_MODULE) --host 0.0.0.0 --port $(PORT) $(RELOAD) & \
		echo $$! > .uvicorn_pid; \
		echo "Uvicorn app started. PID: $$(cat .uvicorn_pid)"; \
	}


setup:
	@echo "Creating virtual environment for the ScrapingAgent"
	python3 -m venv venv
	@echo "Installing all dependencies for the ScrapingAgent"
	./venv/bin/pip install -r requirements.txt

stop:
	@if [ -f .uvicorn_pid ]; then \
		PID=$$(cat .uvicorn_pid); \
		echo "Stopping Uvicorn app with PID: $$PID"; \
		kill $$PID; \
		rm .uvicorn_pid; \
	else \
		echo "No Uvicorn PID file found. Is the app running?"; \
	fi

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__
	rm -f .uvicorn_pid
	@echo "Cleanup complete."

