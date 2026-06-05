.PHONY: dev tunnel install test

# Start development server
dev:
	PYTHONPATH=$(shell dirname $(CURDIR)) uvicorn api.app:app --port 8003 --reload

# Start ngrok tunnel for webhook development
tunnel:
	@echo "Starting ngrok tunnel on port 8003..."
	@echo "Copy the HTTPS URL and set it as your GitHub webhook URL"
	ngrok http 8003

# Install dependencies
install:
	pip install -e .
	pip install 'python-jose[cryptography]' 'passlib[bcrypt]' aiohttp

# Run tests
test:
	python -m pytest tests/ -v
