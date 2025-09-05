#!/bin/bash
# CI/CD Setup Validation Script
# Validates that all CI/CD components are properly configured

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[⚠]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

validation_errors=0

# Function to check file exists
check_file() {
    local file="$1"
    local description="$2"
    
    if [[ -f "$file" ]]; then
        log_success "$description exists: $file"
    else
        log_error "$description missing: $file"
        ((validation_errors++))
    fi
}

# Function to check directory exists
check_directory() {
    local dir="$1"
    local description="$2"
    
    if [[ -d "$dir" ]]; then
        log_success "$description exists: $dir"
    else
        log_error "$description missing: $dir"
        ((validation_errors++))
    fi
}

# Function to check file is executable
check_executable() {
    local file="$1"
    local description="$2"
    
    if [[ -f "$file" ]] && [[ -x "$file" ]]; then
        log_success "$description is executable: $file"
    else
        log_error "$description not executable: $file"
        ((validation_errors++))
    fi
}

# Function to validate YAML
validate_yaml() {
    local file="$1"
    local description="$2"
    
    if [[ -f "$file" ]]; then
        if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
            log_success "$description is valid YAML: $file"
        else
            log_error "$description has invalid YAML syntax: $file"
            ((validation_errors++))
        fi
    fi
}

# Function to validate JSON
validate_json() {
    local file="$1"
    local description="$2"
    
    if [[ -f "$file" ]]; then
        if python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
            log_success "$description is valid JSON: $file"
        else
            log_error "$description has invalid JSON syntax: $file"
            ((validation_errors++))
        fi
    fi
}

main() {
    log_info "Validating CI/CD setup for pmake-recover"
    log_info "Project root: $PROJECT_ROOT"
    
    cd "$PROJECT_ROOT"
    
    # Check core configuration files
    log_info "Checking core configuration files..."
    check_file "pyproject.toml" "Python project configuration"
    check_file "pytest.ini" "Pytest configuration"
    check_file ".coveragerc" "Coverage configuration"
    check_file ".flake8" "Flake8 configuration"
    check_file "Makefile" "Makefile"
    check_file "Dockerfile" "Docker configuration"
    check_file ".dockerignore" "Docker ignore file"
    
    # Check CI/CD configuration files
    log_info "Checking CI/CD configuration files..."
    check_file ".github/workflows/ci.yml" "GitHub Actions workflow"
    check_file ".pre-commit-config.yaml" "Pre-commit configuration"
    check_file ".secrets.baseline" "Secrets baseline"
    
    # Check scripts
    log_info "Checking CI/CD scripts..."
    check_executable "scripts/ci-setup.sh" "CI setup script"
    check_executable "scripts/run-tests-ci.sh" "Test runner script"
    check_executable "scripts/generate-ci-reports.sh" "Report generation script"
    
    # Check directories
    log_info "Checking directory structure..."
    check_directory ".github" "GitHub directory"
    check_directory ".github/workflows" "GitHub workflows directory"
    check_directory "scripts" "Scripts directory"
    check_directory "tests" "Tests directory"
    
    # Validate YAML files
    log_info "Validating YAML syntax..."
    validate_yaml ".github/workflows/ci.yml" "GitHub Actions workflow"
    validate_yaml ".pre-commit-config.yaml" "Pre-commit configuration"
    
    # Validate JSON files
    log_info "Validating JSON syntax..."
    validate_json ".secrets.baseline" "Secrets baseline"
    
    # Check Python syntax
    log_info "Checking Python syntax..."
    shopt -s nullglob
    for py_file in *.py scripts/*.py; do
        if [[ -f "$py_file" ]]; then
            if python3 -m py_compile "$py_file" 2>/dev/null; then
                log_success "Python syntax valid: $py_file"
            else
                log_error "Python syntax error: $py_file"
                ((validation_errors++))
            fi
        fi
    done
    shopt -u nullglob
    
    # Check requirements files
    log_info "Checking requirements files..."
    if [[ -f "requirements.txt" ]]; then
        if python3 -c "
import pkg_resources
try:
    pkg_resources.parse_requirements(open('requirements.txt'))
    print('✓ requirements.txt format valid')
except Exception as e:
    print(f'✗ requirements.txt format error: {e}')
    exit(1)
" 2>/dev/null; then
            log_success "requirements.txt format is valid"
        else
            log_error "requirements.txt format is invalid"
            ((validation_errors++))
        fi
    fi
    
    if [[ -f "requirements-dev.txt" ]]; then
        if python3 -c "
import pkg_resources
try:
    # Filter out comments and empty lines
    reqs = [line for line in open('requirements-dev.txt') if line.strip() and not line.strip().startswith('#')]
    pkg_resources.parse_requirements(reqs)
    print('✓ requirements-dev.txt format valid')
except Exception as e:
    print(f'✗ requirements-dev.txt format error: {e}')
    exit(1)
" 2>/dev/null; then
            log_success "requirements-dev.txt format is valid"
        else
            log_warning "requirements-dev.txt format has issues (may contain commented packages)"
        fi
    fi
    
    # Check Makefile targets
    log_info "Checking Makefile targets..."
    essential_targets=("help" "test" "lint" "security-scan" "coverage" "ci-quick" "ci-full")
    
    for target in "${essential_targets[@]}"; do
        if grep -q "^$target:" Makefile; then
            log_success "Makefile target available: $target"
        else
            log_error "Makefile target missing: $target"
            ((validation_errors++))
        fi
    done
    
    # Check Docker configuration
    log_info "Checking Docker configuration..."
    if command -v docker >/dev/null 2>&1; then
        if docker build --dry-run . >/dev/null 2>&1; then
            log_success "Dockerfile syntax is valid"
        else
            log_warning "Dockerfile syntax validation failed (docker not available or build issues)"
        fi
    else
        log_warning "Docker not available for validation"
    fi
    
    # Final summary
    echo
    log_info "=== VALIDATION SUMMARY ==="
    
    if [[ $validation_errors -eq 0 ]]; then
        log_success "All validations passed! CI/CD setup is complete and ready."
        log_info "Next steps:"
        log_info "  1. Run: make dev-setup    # Complete development setup"
        log_info "  2. Run: make ci-quick     # Test the CI pipeline locally"
        log_info "  3. Push to GitHub to trigger automated CI/CD"
    else
        log_error "$validation_errors validation errors found!"
        log_info "Please fix the errors above before using the CI/CD pipeline."
        return 1
    fi
    
    # Show available commands
    echo
    log_info "Available Make commands:"
    make help | grep -E "^\s+\[" | head -10
    log_info "  ... and more (run 'make help' for full list)"
    
    return 0
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi