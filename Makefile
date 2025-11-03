# VidGear Docker Streamer Makefile
# ==================================

# Variables
DOCKER_IMAGE := vidgear-streamer
DOCKER_TAG := latest
DOCKER_REGISTRY ?= docker.io
DOCKER_NAMESPACE ?= yourusername
FULL_IMAGE_NAME := $(DOCKER_REGISTRY)/$(DOCKER_NAMESPACE)/$(DOCKER_IMAGE):$(DOCKER_TAG)
OUTPUT_DIR := output
ENV_FILE := .env

# Build variables
BUILD_DATE := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
VCS_REF := $(shell git rev-parse --short HEAD 2>/dev/null || echo "dev")

# Colors for output
COLOR_RESET := \033[0m
COLOR_BOLD := \033[1m
COLOR_GREEN := \033[32m
COLOR_YELLOW := \033[33m
COLOR_BLUE := \033[34m

.PHONY: help
help: ## Show this help message
	@echo "$(COLOR_BOLD)VidGear Docker Streamer - Available Commands$(COLOR_RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_BLUE)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ""

.PHONY: setup
setup: ## Initial setup (create .env and output directory)
	@echo "$(COLOR_GREEN)Setting up project...$(COLOR_RESET)"
	@if [ ! -f $(ENV_FILE) ]; then \
		cp .env.example $(ENV_FILE); \
		echo "$(COLOR_YELLOW)Created $(ENV_FILE) from .env.example$(COLOR_RESET)"; \
		echo "$(COLOR_YELLOW)Please edit $(ENV_FILE) with your settings$(COLOR_RESET)"; \
	else \
		echo "$(ENV_FILE) already exists"; \
	fi
	@mkdir -p $(OUTPUT_DIR)
	@echo "$(COLOR_GREEN)Setup complete!$(COLOR_RESET)"

.PHONY: build
build: ## Build Docker image
	@echo "$(COLOR_GREEN)Building Docker image...$(COLOR_RESET)"
	docker build \
		--build-arg BUILD_DATE=$(BUILD_DATE) \
		--build-arg VCS_REF=$(VCS_REF) \
		-t $(DOCKER_IMAGE):$(DOCKER_TAG) \
		-t $(DOCKER_IMAGE):latest \
		.
	@echo "$(COLOR_GREEN)Build complete!$(COLOR_RESET)"

.PHONY: build-no-cache
build-no-cache: ## Build Docker image without cache
	@echo "$(COLOR_GREEN)Building Docker image (no cache)...$(COLOR_RESET)"
	docker build --no-cache \
		--build-arg BUILD_DATE=$(BUILD_DATE) \
		--build-arg VCS_REF=$(VCS_REF) \
		-t $(DOCKER_IMAGE):$(DOCKER_TAG) \
		-t $(DOCKER_IMAGE):latest \
		.
	@echo "$(COLOR_GREEN)Build complete!$(COLOR_RESET)"

.PHONY: run
run: ## Run the container
	@echo "$(COLOR_GREEN)Starting container...$(COLOR_RESET)"
	docker run --rm \
		-v "$(shell pwd)/$(OUTPUT_DIR):/app/output" \
		--env-file $(ENV_FILE) \
		$(DOCKER_IMAGE):$(DOCKER_TAG)

.PHONY: run-interactive
run-interactive: ## Run container in interactive mode
	@echo "$(COLOR_GREEN)Starting container in interactive mode...$(COLOR_RESET)"
	docker run --rm -it \
		-v "$(shell pwd)/$(OUTPUT_DIR):/app/output" \
		--env-file $(ENV_FILE) \
		--entrypoint /bin/bash \
		$(DOCKER_IMAGE):$(DOCKER_TAG)

.PHONY: compose-up
compose-up: ## Start services with docker-compose
	@echo "$(COLOR_GREEN)Starting services with docker-compose...$(COLOR_RESET)"
	docker-compose up

.PHONY: compose-up-detached
compose-up-detached: ## Start services in background
	@echo "$(COLOR_GREEN)Starting services in background...$(COLOR_RESET)"
	docker-compose up -d

.PHONY: compose-down
compose-down: ## Stop and remove containers
	@echo "$(COLOR_YELLOW)Stopping services...$(COLOR_RESET)"
	docker-compose down

.PHONY: compose-logs
compose-logs: ## View service logs
	docker-compose logs -f

.PHONY: compose-build
compose-build: ## Build services with docker-compose
	@echo "$(COLOR_GREEN)Building services...$(COLOR_RESET)"
	docker-compose build

.PHONY: test
test: ## Run tests
	@echo "$(COLOR_GREEN)Running tests...$(COLOR_RESET)"
	@if [ -f "docker-compose.test.yml" ]; then \
		docker-compose -f docker-compose.test.yml up --abort-on-container-exit; \
		docker-compose -f docker-compose.test.yml down; \
	else \
		pytest tests/ -v; \
	fi

.PHONY: test-local
test-local: ## Run tests locally (requires pytest)
	@echo "$(COLOR_GREEN)Running tests locally...$(COLOR_RESET)"
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

.PHONY: lint
lint: ## Run linting
	@echo "$(COLOR_GREEN)Running linters...$(COLOR_RESET)"
	@command -v ruff >/dev/null 2>&1 && ruff check app/ tests/ || echo "ruff not installed, skipping"
	@command -v black >/dev/null 2>&1 && black --check app/ tests/ || echo "black not installed, skipping"
	@command -v mypy >/dev/null 2>&1 && mypy app/ || echo "mypy not installed, skipping"

.PHONY: format
format: ## Format code
	@echo "$(COLOR_GREEN)Formatting code...$(COLOR_RESET)"
	@command -v black >/dev/null 2>&1 && black app/ tests/ || echo "black not installed"
	@command -v ruff >/dev/null 2>&1 && ruff check --fix app/ tests/ || echo "ruff not installed"

.PHONY: clean
clean: ## Clean up generated files and containers
	@echo "$(COLOR_YELLOW)Cleaning up...$(COLOR_RESET)"
	docker-compose down -v 2>/dev/null || true
	rm -rf $(OUTPUT_DIR)/*.mp4 $(OUTPUT_DIR)/*.aac 2>/dev/null || true
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage 2>/dev/null || true
	@echo "$(COLOR_GREEN)Cleanup complete!$(COLOR_RESET)"

.PHONY: clean-all
clean-all: clean ## Clean everything including Docker images
	@echo "$(COLOR_YELLOW)Removing Docker images...$(COLOR_RESET)"
	docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) 2>/dev/null || true
	docker rmi $(DOCKER_IMAGE):latest 2>/dev/null || true
	@echo "$(COLOR_GREEN)Full cleanup complete!$(COLOR_RESET)"

.PHONY: push
push: ## Push Docker image to registry
	@echo "$(COLOR_GREEN)Pushing image to registry...$(COLOR_RESET)"
	docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $(FULL_IMAGE_NAME)
	docker push $(FULL_IMAGE_NAME)
	@echo "$(COLOR_GREEN)Push complete!$(COLOR_RESET)"

.PHONY: pull
pull: ## Pull Docker image from registry
	@echo "$(COLOR_GREEN)Pulling image from registry...$(COLOR_RESET)"
	docker pull $(FULL_IMAGE_NAME)
	docker tag $(FULL_IMAGE_NAME) $(DOCKER_IMAGE):$(DOCKER_TAG)
	@echo "$(COLOR_GREEN)Pull complete!$(COLOR_RESET)"

.PHONY: shell
shell: ## Open shell in running container
	@echo "$(COLOR_GREEN)Opening shell...$(COLOR_RESET)"
	docker-compose exec vidgear-streamer /bin/bash

.PHONY: logs
logs: compose-logs ## Alias for compose-logs

.PHONY: ps
ps: ## Show running containers
	docker-compose ps

.PHONY: version
version: ## Show version information
	@echo "$(COLOR_BOLD)Version Information$(COLOR_RESET)"
	@echo "Build Date: $(BUILD_DATE)"
	@echo "VCS Ref:    $(VCS_REF)"
	@echo "Image:      $(DOCKER_IMAGE):$(DOCKER_TAG)"

.PHONY: install-deps
install-deps: ## Install Python dependencies locally
	@echo "$(COLOR_GREEN)Installing dependencies...$(COLOR_RESET)"
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-mock black ruff mypy

.PHONY: dev-setup
dev-setup: setup install-deps ## Complete development setup
	@echo "$(COLOR_GREEN)Development environment ready!$(COLOR_RESET)"

.PHONY: check-env
check-env: ## Check if .env file exists
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "$(COLOR_YELLOW)Warning: $(ENV_FILE) not found!$(COLOR_RESET)"; \
		echo "$(COLOR_YELLOW)Run 'make setup' to create it$(COLOR_RESET)"; \
		exit 1; \
	fi

.PHONY: validate
validate: check-env ## Validate configuration
	@echo "$(COLOR_GREEN)Validating configuration...$(COLOR_RESET)"
	@echo "Environment file: $(ENV_FILE)"
	@echo "Output directory: $(OUTPUT_DIR)"
	@if [ ! -d $(OUTPUT_DIR) ]; then \
		mkdir -p $(OUTPUT_DIR); \
		echo "$(COLOR_YELLOW)Created output directory$(COLOR_RESET)"; \
	fi
	@echo "$(COLOR_GREEN)Configuration valid!$(COLOR_RESET)"

# Default target
.DEFAULT_GOAL := help
