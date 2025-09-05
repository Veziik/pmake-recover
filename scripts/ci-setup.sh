#!/bin/bash
# CI/CD Setup Script for pmake-recover
# Sets up the environment for continuous integration

set -euo pipefail  # Exit on any error, undefined variables, or pipe failures

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_VERSION="${PYTHON_VERSION:-3.12}"
VENV_DIR="${PROJECT_ROOT}/.venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    local version
    version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
    log_info "Detected Python version: $version"
    
    if [[ $(echo "$version 3.11" | awk '{print ($1 >= $2)}') -eq 0 ]]; then
        log_error "Python 3.11 or higher required, found $version"
        exit 1
    fi
}

# Function to create virtual environment
setup_virtual_environment() {
    log_info "Setting up virtual environment..."
    
    if [[ -d "$VENV_DIR" ]]; then
        log_warning "Virtual environment already exists, removing..."
        rm -rf "$VENV_DIR"
    fi
    
    python3 -m venv "$VENV_DIR"
    
    # Activate virtual environment
    # shellcheck source=/dev/null
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    log_success "Virtual environment created and activated"
}

# Function to install dependencies
install_dependencies() {
    log_info "Installing project dependencies..."
    
    # Install runtime dependencies
    if [[ -f "$PROJECT_ROOT/requirements.txt" ]]; then
        pip install -r "$PROJECT_ROOT/requirements.txt"
        log_success "Runtime dependencies installed"
    else
        log_warning "requirements.txt not found, skipping runtime dependencies"
    fi
    
    # Install development dependencies
    if [[ -f "$PROJECT_ROOT/requirements-dev.txt" ]]; then
        pip install -r "$PROJECT_ROOT/requirements-dev.txt"
        log_success "Development dependencies installed"
    else
        log_warning "requirements-dev.txt not found, skipping development dependencies"
    fi
}

# Function to setup pre-commit hooks
setup_pre_commit() {
    log_info "Setting up pre-commit hooks..."
    
    if command_exists pre-commit; then
        pre-commit install --install-hooks
        pre-commit install --hook-type pre-push
        log_success "Pre-commit hooks installed"
    else
        log_warning "pre-commit not found, installing..."
        pip install pre-commit
        pre-commit install --install-hooks
        pre-commit install --hook-type pre-push
        log_success "Pre-commit installed and hooks set up"
    fi
}

# Function to create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    local dirs=(
        "$PROJECT_ROOT/test-results"
        "$PROJECT_ROOT/reports"
        "$PROJECT_ROOT/htmlcov"
        "$PROJECT_ROOT/files"
    )
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_info "Created directory: $dir"
        fi
    done
    
    # Set secure permissions for files directory
    if [[ -d "$PROJECT_ROOT/files" ]]; then
        chmod 700 "$PROJECT_ROOT/files"
        log_info "Set secure permissions (700) for files directory"
    fi
    
    log_success "Directory structure created"
}

# Function to validate environment
validate_environment() {
    log_info "Validating CI/CD environment..."
    
    # Check required tools
    local tools=("python3" "pip" "git")
    for tool in "${tools[@]}"; do
        if command_exists "$tool"; then
            log_success "$tool is available"
        else
            log_error "$tool is not available"
            exit 1
        fi
    done
    
    # Check Python modules
    local modules=("pytest" "coverage" "bandit" "black" "isort")
    for module in "${modules[@]}"; do
        if python3 -c "import $module" 2>/dev/null; then
            log_success "Python module $module is available"
        else
            log_warning "Python module $module is not available"
        fi
    done
}

# Function to run initial tests
run_initial_tests() {
    log_info "Running initial test validation..."
    
    # Quick syntax check
    if python3 -m py_compile makepin.py recoverpin.py helpers.py words.py 2>/dev/null; then
        log_success "Python syntax validation passed"
    else
        log_error "Python syntax validation failed"
        return 1
    fi
    
    # Run fast tests if they exist
    if [[ -d "tests" ]]; then
        pytest tests/ --collect-only --quiet >/dev/null 2>&1 || {
            log_warning "Test collection failed, but continuing setup"
        }
        log_success "Test discovery completed"
    else
        log_warning "Tests directory not found"
    fi
}

# Function to generate CI environment info
generate_ci_info() {
    log_info "Generating CI environment information..."
    
    cat > "$PROJECT_ROOT/ci-environment.json" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "python_version": "$(python3 --version | cut -d' ' -f2)",
    "pip_version": "$(pip --version | cut -d' ' -f2)",
    "git_version": "$(git --version | cut -d' ' -f3)",
    "platform": "$(uname -s)",
    "architecture": "$(uname -m)",
    "user": "$(whoami)",
    "working_directory": "$PROJECT_ROOT",
    "virtual_env": "$VENV_DIR",
    "dependencies": {
        "runtime": "requirements.txt",
        "development": "requirements-dev.txt"
    },
    "test_framework": "pytest",
    "coverage_tool": "coverage.py",
    "pre_commit": "$(command_exists pre-commit && echo 'installed' || echo 'not installed')"
}
EOF
    
    log_success "CI environment information saved to ci-environment.json"
}

# Main execution
main() {
    log_info "Starting CI/CD environment setup for pmake-recover"
    log_info "Project root: $PROJECT_ROOT"
    
    # Change to project directory
    cd "$PROJECT_ROOT"
    
    # Run setup steps
    check_python_version
    setup_virtual_environment
    install_dependencies
    create_directories
    setup_pre_commit
    validate_environment
    run_initial_tests
    generate_ci_info
    
    log_success "CI/CD environment setup completed successfully!"
    log_info "Next steps:"
    log_info "  1. Activate virtual environment: source .venv/bin/activate"
    log_info "  2. Run tests: pytest tests/"
    log_info "  3. Run security scan: bandit -r ."
    log_info "  4. Check code quality: pre-commit run --all-files"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi