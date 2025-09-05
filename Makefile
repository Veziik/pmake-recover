# Makefile for pmake-recover CI/CD operations
# Provides standardized commands for development and CI/CD

.PHONY: help install install-dev test test-unit test-integration test-security test-performance
.PHONY: lint format security-scan coverage clean setup-ci setup-pre-commit
.PHONY: reports badges validate-reports ci-full ci-quick
.PHONY: docker-build docker-test docker-security

# Default Python interpreter
PYTHON := python3
PIP := pip
PYTEST := pytest

# Project directories
PROJECT_ROOT := $(shell pwd)
TESTS_DIR := tests
REPORTS_DIR := reports
TEST_RESULTS_DIR := test-results
SCRIPTS_DIR := scripts

# Configuration
COVERAGE_THRESHOLD := 100
PARALLEL_WORKERS := auto
MAX_FAILURES := 3

# Colors for output
BOLD := $(shell tput bold)
RED := $(shell tput setaf 1)
GREEN := $(shell tput setaf 2)
YELLOW := $(shell tput setaf 3)
BLUE := $(shell tput setaf 4)
RESET := $(shell tput sgr0)

# Help target
help: ## Show this help message
	@echo "$(BOLD)pmake-recover CI/CD Commands$(RESET)"
	@echo
	@echo "$(BOLD)Setup Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(install|setup)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo
	@echo "$(BOLD)Testing Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(test|coverage)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo
	@echo "$(BOLD)Quality Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(lint|format|security)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo
	@echo "$(BOLD)CI/CD Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(ci|reports|badges)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo
	@echo "$(BOLD)Docker Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep docker | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo
	@echo "$(BOLD)Other Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -v -E '(install|setup|test|coverage|lint|format|security|ci|reports|badges|docker)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'

# Setup commands
install: ## Install runtime dependencies
	@echo "$(GREEN)Installing runtime dependencies...$(RESET)"
	$(PIP) install -r requirements.txt

install-dev: ## Install development dependencies
	@echo "$(GREEN)Installing development dependencies...$(RESET)"
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

setup-ci: ## Set up CI/CD environment
	@echo "$(GREEN)Setting up CI/CD environment...$(RESET)"
	@chmod +x $(SCRIPTS_DIR)/*.sh
	@$(SCRIPTS_DIR)/ci-setup.sh

setup-pre-commit: ## Set up pre-commit hooks
	@echo "$(GREEN)Setting up pre-commit hooks...$(RESET)"
	pre-commit install
	pre-commit install --hook-type pre-push

# Testing commands
test: test-unit test-integration test-security ## Run all tests
	@echo "$(GREEN)All tests completed$(RESET)"

test-unit: ## Run unit tests with coverage
	@echo "$(BLUE)Running unit tests...$(RESET)"
	@mkdir -p $(TEST_RESULTS_DIR) $(REPORTS_DIR)
	$(PYTEST) $(TESTS_DIR)/unit/ \
		--verbose \
		--cov=. \
		--cov-report=xml:$(REPORTS_DIR)/coverage-unit.xml \
		--cov-report=html:$(REPORTS_DIR)/htmlcov-unit \
		--cov-report=term-missing:skip-covered \
		--junit-xml=$(TEST_RESULTS_DIR)/junit-unit.xml \
		--html=$(TEST_RESULTS_DIR)/report-unit.html \
		--self-contained-html \
		-n $(PARALLEL_WORKERS)

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(RESET)"
	@mkdir -p $(TEST_RESULTS_DIR) $(REPORTS_DIR)
	$(PYTEST) $(TESTS_DIR)/integration/ \
		--verbose \
		--cov=. \
		--cov-append \
		--cov-report=xml:$(REPORTS_DIR)/coverage-integration.xml \
		--cov-report=html:$(REPORTS_DIR)/htmlcov-integration \
		--cov-report=term-missing:skip-covered \
		--junit-xml=$(TEST_RESULTS_DIR)/junit-integration.xml \
		--html=$(TEST_RESULTS_DIR)/report-integration.html \
		--self-contained-html

test-security: ## Run security tests
	@echo "$(BLUE)Running security tests...$(RESET)"
	@mkdir -p $(TEST_RESULTS_DIR)
	$(PYTEST) $(TESTS_DIR)/ \
		-m security \
		--verbose \
		--junit-xml=$(TEST_RESULTS_DIR)/junit-security.xml \
		--html=$(TEST_RESULTS_DIR)/report-security.html \
		--self-contained-html

test-performance: ## Run performance benchmarks
	@echo "$(BLUE)Running performance benchmarks...$(RESET)"
	@mkdir -p $(TEST_RESULTS_DIR)
	$(PYTEST) $(TESTS_DIR)/ \
		-m slow \
		--benchmark-only \
		--benchmark-json=$(TEST_RESULTS_DIR)/benchmark-performance.json \
		--junit-xml=$(TEST_RESULTS_DIR)/junit-performance.xml

coverage: ## Generate combined coverage report
	@echo "$(BLUE)Generating coverage report...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	coverage combine
	coverage report --show-missing --fail-under=$(COVERAGE_THRESHOLD)
	coverage html -d $(REPORTS_DIR)/htmlcov-combined
	coverage xml -o $(REPORTS_DIR)/coverage-combined.xml
	coverage json -o $(REPORTS_DIR)/coverage-combined.json

# Code quality commands
lint: ## Run all linting tools
	@echo "$(BLUE)Running linting tools...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	-flake8 . --statistics --tee --output-file=$(REPORTS_DIR)/flake8-report.txt
	-pylint --output-format=json:$(REPORTS_DIR)/pylint-report.json,text:$(REPORTS_DIR)/pylint-report.txt *.py
	-mypy .

format: ## Format code with Black and isort
	@echo "$(BLUE)Formatting code...$(RESET)"
	black .
	isort .

format-check: ## Check code formatting without making changes
	@echo "$(BLUE)Checking code formatting...$(RESET)"
	black --check --diff .
	isort --check-only --diff .

security-scan: ## Run security analysis
	@echo "$(BLUE)Running security analysis...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	-bandit -r . -f json -o $(REPORTS_DIR)/bandit-report.json -x $(TESTS_DIR)/
	-bandit -r . -f txt -o $(REPORTS_DIR)/bandit-report.txt -x $(TESTS_DIR)/
	-safety check --json --output $(REPORTS_DIR)/safety-report.json

# CI/CD commands
ci-quick: clean setup-ci test-unit lint ## Quick CI pipeline (unit tests + linting)
	@echo "$(GREEN)Quick CI pipeline completed$(RESET)"

ci-full: clean setup-ci test coverage security-scan lint reports ## Full CI pipeline
	@echo "$(GREEN)Full CI pipeline completed$(RESET)"

reports: ## Generate all CI reports and badges
	@echo "$(BLUE)Generating CI reports...$(RESET)"
	@$(SCRIPTS_DIR)/generate-ci-reports.sh

badges: ## Generate status badges
	@echo "$(BLUE)Generating badges...$(RESET)"
	@$(SCRIPTS_DIR)/generate-ci-reports.sh

validate-reports: ## Validate generated reports
	@echo "$(BLUE)Validating reports...$(RESET)"
	@for xml_file in $(REPORTS_DIR)/*.xml; do \
		if [ -f "$$xml_file" ]; then \
			xmllint --noout "$$xml_file" 2>/dev/null || echo "$(RED)Invalid XML: $$xml_file$(RESET)"; \
		fi; \
	done
	@echo "$(GREEN)Report validation completed$(RESET)"

# Docker commands
docker-build: ## Build Docker image for testing
	@echo "$(BLUE)Building Docker image...$(RESET)"
	docker build -t pmake-recover:test .

docker-test: docker-build ## Run tests in Docker container
	@echo "$(BLUE)Running tests in Docker...$(RESET)"
	docker run --rm -v $(PROJECT_ROOT)/test-results:/app/test-results pmake-recover:test make test

docker-security: docker-build ## Run security scan in Docker
	@echo "$(BLUE)Running security scan in Docker...$(RESET)"
	docker run --rm -v $(PROJECT_ROOT)/reports:/app/reports pmake-recover:test make security-scan

# Utility commands
clean: ## Clean build artifacts and temporary files
	@echo "$(YELLOW)Cleaning build artifacts...$(RESET)"
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".coverage*" -delete 2>/dev/null || true
	@rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .tox/ 2>/dev/null || true
	@rm -rf $(REPORTS_DIR)/* $(TEST_RESULTS_DIR)/* 2>/dev/null || true

check: ## Check project configuration and dependencies
	@echo "$(BLUE)Checking project configuration...$(RESET)"
	@$(PYTHON) --version
	@$(PIP) --version
	@$(PYTEST) --version
	@echo "$(GREEN)Configuration check completed$(RESET)"

install-tools: ## Install additional development tools
	@echo "$(BLUE)Installing additional tools...$(RESET)"
	$(PIP) install pre-commit tox wheel build twine
	@echo "$(GREEN)Tools installed$(RESET)"

requirements: ## Update requirements files
	@echo "$(BLUE)Updating requirements...$(RESET)"
	pip-compile requirements.in
	pip-compile requirements-dev.in

# Environment-specific commands
dev-setup: install-dev setup-pre-commit ## Complete development environment setup
	@echo "$(GREEN)Development environment ready$(RESET)"

ci-setup-github: ## Setup for GitHub Actions
	@echo "$(BLUE)Setting up for GitHub Actions...$(RESET)"
	@echo "PYTHONPATH=$(PROJECT_ROOT)" >> $$GITHUB_ENV
	@echo "$(GREEN)GitHub Actions setup completed$(RESET)"

ci-setup-gitlab: ## Setup for GitLab CI
	@echo "$(BLUE)Setting up for GitLab CI...$(RESET)"
	@export PYTHONPATH=$(PROJECT_ROOT)
	@echo "$(GREEN)GitLab CI setup completed$(RESET)"

# Advanced testing commands
test-parallel: ## Run tests in parallel with maximum workers
	@echo "$(BLUE)Running tests in parallel...$(RESET)"
	$(PYTEST) $(TESTS_DIR)/ -n auto --dist loadfile

test-random: ## Run tests in random order
	@echo "$(BLUE)Running tests in random order...$(RESET)"
	$(PYTEST) $(TESTS_DIR)/ --random-order

test-stress: ## Run stress tests with multiple repetitions
	@echo "$(BLUE)Running stress tests...$(RESET)"
	$(PYTEST) $(TESTS_DIR)/ --count=10

# Debugging commands
debug-test: ## Run tests with debugging enabled
	@echo "$(BLUE)Running tests with debugging...$(RESET)"
	$(PYTEST) $(TESTS_DIR)/ --pdb --pdbcls=IPython.terminal.debugger:Pdb -s

profile-tests: ## Profile test execution
	@echo "$(BLUE)Profiling test execution...$(RESET)"
	$(PYTEST) $(TESTS_DIR)/ --profile --profile-svg

# Documentation commands (if needed)
docs-build: ## Build documentation
	@echo "$(BLUE)Building documentation...$(RESET)"
	@echo "$(YELLOW)Documentation not yet implemented$(RESET)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(RESET)"
	@echo "$(YELLOW)Documentation not yet implemented$(RESET)"

.DEFAULT_GOAL := help