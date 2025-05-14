.PHONY: setup run run-chrome run-app run-raw run-structured run-both stop-chrome clean help install

# Default target
help:
	@echo "Portfolio Scraper Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  setup          - Install dependencies"
	@echo "  run            - Run Chrome in debug mode and the portfolio scraper (both raw and structured data)"
	@echo "  run-raw        - Run the portfolio scraper with raw data only"
	@echo "  run-structured - Run the portfolio scraper with structured data only"
	@echo "  run-both       - Run the portfolio scraper with both raw and structured data"
	@echo "  run-chrome     - Run Chrome in debug mode only"
	@echo "  run-app        - Run the portfolio scraper only (Chrome must be running)"
	@echo "  stop-chrome    - Stop Chrome debug instance"
	@echo "  clean          - Remove temporary files and Chrome debug profile"
	@echo "  install        - Install dependencies"
	@echo ""
	@echo "Options (can be passed to any run-* target):"
	@echo "  LOG_LEVEL=DEBUG|INFO|WARNING|ERROR|CRITICAL - Set logging level (default: INFO)"
	@echo "  NO_INFLUXDB=1                               - Skip storing data in InfluxDB"
	@echo ""
	@echo "Example usage:"
	@echo "  make run                      - Run the complete application"
	@echo "  make run-raw LOG_LEVEL=DEBUG  - Run with raw data only and debug logging"
	@echo "  make run-structured NO_INFLUXDB=1 - Run with structured data only, skip InfluxDB"

# Setup the environment
setup: install

# Install dependencies
install:
	@echo "Installing dependencies..."
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv venv; \
	fi
	@echo "Activating virtual environment and installing dependencies..."
	source venv/bin/activate && pip install -r requirements.txt

# Run Chrome in debug mode and the portfolio scraper (both data types)
run: run-both

# Run Chrome in debug mode and the portfolio scraper with raw data only
run-raw:
	@echo "Starting Chrome in debug mode and running the portfolio scraper (raw data)..."
	@make run-chrome
	@sleep 5  # Wait for Chrome to start properly
	@make _run-app-raw

# Run Chrome in debug mode and the portfolio scraper with structured data only
run-structured:
	@echo "Starting Chrome in debug mode and running the portfolio scraper (structured data)..."
	@make run-chrome
	@sleep 5  # Wait for Chrome to start properly
	@make _run-app-structured

# Run Chrome in debug mode and the portfolio scraper with both data types
run-both:
	@echo "Starting Chrome in debug mode and running the portfolio scraper (both data types)..."
	@make run-chrome
	@sleep 5  # Wait for Chrome to start properly
	@make _run-app-both

# Run Chrome in debug mode only
run-chrome:
	@echo "Starting Chrome in debug mode..."
	@chmod +x ./launch_chrome_debug.sh
	@./launch_chrome_debug.sh &
	@echo "Chrome debug started in background. PID saved."
	@sleep 2
	@echo "Chrome debug URL: http://localhost:9222"

# Helper function to check if Chrome is running
define check_chrome
	@if ! curl -s http://localhost:9222/json/version > /dev/null; then \
		echo "Error: Chrome debug port is not accessible. Please run 'make run-chrome' first."; \
		exit 1; \
	fi
endef

# Run the portfolio scraper only (default to both data types)
run-app: _run-app-both

# Internal targets for running different data types
_run-app-raw:
	@echo "Running portfolio scraper (raw data)..."
	$(call check_chrome)
	@INFLUXDB_ARGS=""; \
	if [ "$(NO_INFLUXDB)" = "1" ]; then \
		INFLUXDB_ARGS="--no-influxdb"; \
	fi; \
	LOG_LEVEL_ARG=""; \
	if [ "$(LOG_LEVEL)" != "" ]; then \
		LOG_LEVEL_ARG="--log-level $(LOG_LEVEL)"; \
	fi; \
	source venv/bin/activate && python portfolio_scraper.py --data-type raw $$INFLUXDB_ARGS $$LOG_LEVEL_ARG

_run-app-structured:
	@echo "Running portfolio scraper (structured data)..."
	$(call check_chrome)
	@INFLUXDB_ARGS=""; \
	if [ "$(NO_INFLUXDB)" = "1" ]; then \
		INFLUXDB_ARGS="--no-influxdb"; \
	fi; \
	LOG_LEVEL_ARG=""; \
	if [ "$(LOG_LEVEL)" != "" ]; then \
		LOG_LEVEL_ARG="--log-level $(LOG_LEVEL)"; \
	fi; \
	source venv/bin/activate && python portfolio_scraper.py --data-type structured $$INFLUXDB_ARGS $$LOG_LEVEL_ARG

_run-app-both:
	@echo "Running portfolio scraper (both data types)..."
	$(call check_chrome)
	@INFLUXDB_ARGS=""; \
	if [ "$(NO_INFLUXDB)" = "1" ]; then \
		INFLUXDB_ARGS="--no-influxdb"; \
	fi; \
	LOG_LEVEL_ARG=""; \
	if [ "$(LOG_LEVEL)" != "" ]; then \
		LOG_LEVEL_ARG="--log-level $(LOG_LEVEL)"; \
	fi; \
	source venv/bin/activate && python portfolio_scraper.py --data-type both $$INFLUXDB_ARGS $$LOG_LEVEL_ARG

# Stop Chrome debug instance
stop-chrome:
	@echo "Stopping Chrome debug instance..."
	@pkill -f "Google Chrome" || echo "No Chrome instances found."
	@echo "Chrome stopped."

# Clean temporary files and Chrome debug profile
clean:
	@echo "Cleaning up..."
	@make stop-chrome
	@rm -rf ~/chrome-debug-profile
	@echo "Chrome debug profile removed."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "Cleanup complete."
