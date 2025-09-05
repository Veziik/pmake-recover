#!/bin/bash
# Comprehensive Test Runner for CI/CD Pipeline
# Runs all tests with proper reporting and coverage analysis

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_RESULTS_DIR="${PROJECT_ROOT}/test-results"
REPORTS_DIR="${PROJECT_ROOT}/reports"

# Test execution parameters
COVERAGE_THRESHOLD="${COVERAGE_THRESHOLD:-100}"
PARALLEL_WORKERS="${PARALLEL_WORKERS:-auto}"
MAX_FAILURES="${MAX_FAILURES:-3}"
TIMEOUT="${TIMEOUT:-300}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_debug() { echo -e "${PURPLE}[DEBUG]${NC} $1"; }
log_test() { echo -e "${CYAN}[TEST]${NC} $1"; }

# Function to setup test environment
setup_test_environment() {
    log_info "Setting up test environment..."
    
    # Create directories
    mkdir -p "$TEST_RESULTS_DIR" "$REPORTS_DIR"
    
    # Clear previous results
    rm -rf "${TEST_RESULTS_DIR:?}"/* "${REPORTS_DIR:?}"/* 2>/dev/null || true
    
    # Set environment variables for testing
    export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"
    export COVERAGE_PROCESS_START="${PROJECT_ROOT}/.coveragerc"
    
    log_success "Test environment ready"
}

# Function to run unit tests
run_unit_tests() {
    log_test "Running unit tests..."
    
    local start_time
    start_time=$(date +%s)
    
    pytest tests/unit/ \
        --verbose \
        --tb=short \
        --maxfail="$MAX_FAILURES" \
        --timeout="$TIMEOUT" \
        --cov=. \
        --cov-config=.coveragerc \
        --cov-report=xml:"$REPORTS_DIR/coverage-unit.xml" \
        --cov-report=html:"$REPORTS_DIR/htmlcov-unit" \
        --cov-report=json:"$REPORTS_DIR/coverage-unit.json" \
        --cov-report=term-missing:skip-covered \
        --junit-xml="$TEST_RESULTS_DIR/junit-unit.xml" \
        --html="$TEST_RESULTS_DIR/report-unit.html" \
        --self-contained-html \
        --json-report --json-report-file="$TEST_RESULTS_DIR/report-unit.json" \
        --benchmark-json="$TEST_RESULTS_DIR/benchmark-unit.json" \
        -n "$PARALLEL_WORKERS" \
        2>&1 | tee "$TEST_RESULTS_DIR/unit-output.log"
    
    local exit_code=${PIPESTATUS[0]}
    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "Unit tests completed in ${duration}s"
    else
        log_error "Unit tests failed (exit code: $exit_code) after ${duration}s"
        return $exit_code
    fi
}

# Function to run integration tests
run_integration_tests() {
    log_test "Running integration tests..."
    
    local start_time
    start_time=$(date +%s)
    
    pytest tests/integration/ \
        --verbose \
        --tb=short \
        --maxfail="$MAX_FAILURES" \
        --timeout="$TIMEOUT" \
        --cov=. \
        --cov-config=.coveragerc \
        --cov-append \
        --cov-report=xml:"$REPORTS_DIR/coverage-integration.xml" \
        --cov-report=html:"$REPORTS_DIR/htmlcov-integration" \
        --cov-report=json:"$REPORTS_DIR/coverage-integration.json" \
        --cov-report=term-missing:skip-covered \
        --junit-xml="$TEST_RESULTS_DIR/junit-integration.xml" \
        --html="$TEST_RESULTS_DIR/report-integration.html" \
        --self-contained-html \
        --json-report --json-report-file="$TEST_RESULTS_DIR/report-integration.json" \
        --benchmark-json="$TEST_RESULTS_DIR/benchmark-integration.json" \
        2>&1 | tee "$TEST_RESULTS_DIR/integration-output.log"
    
    local exit_code=${PIPESTATUS[0]}
    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "Integration tests completed in ${duration}s"
    else
        log_error "Integration tests failed (exit code: $exit_code) after ${duration}s"
        return $exit_code
    fi
}

# Function to run security tests
run_security_tests() {
    log_test "Running security tests..."
    
    local start_time
    start_time=$(date +%s)
    
    # Run security-specific test cases
    pytest tests/ \
        -m security \
        --verbose \
        --tb=short \
        --maxfail="$MAX_FAILURES" \
        --timeout="$TIMEOUT" \
        --junit-xml="$TEST_RESULTS_DIR/junit-security.xml" \
        --html="$TEST_RESULTS_DIR/report-security.html" \
        --self-contained-html \
        --json-report --json-report-file="$TEST_RESULTS_DIR/report-security.json" \
        2>&1 | tee "$TEST_RESULTS_DIR/security-output.log"
    
    local exit_code=${PIPESTATUS[0]}
    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "Security tests completed in ${duration}s"
    else
        log_error "Security tests failed (exit code: $exit_code) after ${duration}s"
        return $exit_code
    fi
}

# Function to run performance benchmarks
run_performance_tests() {
    log_test "Running performance benchmarks..."
    
    local start_time
    start_time=$(date +%s)
    
    # Run benchmarking tests
    pytest tests/ \
        -m slow \
        --benchmark-only \
        --benchmark-sort=mean \
        --benchmark-json="$TEST_RESULTS_DIR/benchmark-performance.json" \
        --benchmark-histogram="$TEST_RESULTS_DIR/benchmark-histogram" \
        --junit-xml="$TEST_RESULTS_DIR/junit-performance.xml" \
        --html="$TEST_RESULTS_DIR/report-performance.html" \
        --self-contained-html \
        2>&1 | tee "$TEST_RESULTS_DIR/performance-output.log"
    
    local exit_code=${PIPESTATUS[0]}
    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "Performance benchmarks completed in ${duration}s"
    else
        log_warning "Performance benchmarks had issues (exit code: $exit_code) after ${duration}s"
        # Don't fail the entire test suite for benchmark issues
    fi
}

# Function to generate combined coverage report
generate_coverage_report() {
    log_info "Generating combined coverage report..."
    
    # Combine coverage data
    coverage combine 2>/dev/null || true
    
    # Generate reports
    coverage report --show-missing --skip-covered > "$REPORTS_DIR/coverage-summary.txt"
    coverage html -d "$REPORTS_DIR/htmlcov-combined"
    coverage xml -o "$REPORTS_DIR/coverage-combined.xml"
    coverage json -o "$REPORTS_DIR/coverage-combined.json"
    
    # Check coverage threshold
    if ! coverage report --fail-under="$COVERAGE_THRESHOLD" --show-missing; then
        log_error "Coverage below threshold of ${COVERAGE_THRESHOLD}%"
        return 1
    fi
    
    log_success "Coverage report generated and meets threshold"
}

# Function to run security static analysis
run_security_analysis() {
    log_info "Running security static analysis..."
    
    # Run Bandit security linter
    bandit -r . \
        -f json -o "$REPORTS_DIR/bandit-report.json" \
        -f txt -o "$REPORTS_DIR/bandit-report.txt" \
        -x tests/ || {
        log_warning "Bandit found security issues (see reports)"
    }
    
    # Run Safety dependency check
    safety check \
        --json --output "$REPORTS_DIR/safety-report.json" || {
        log_warning "Safety found dependency vulnerabilities (see reports)"
    }
    
    log_success "Security analysis completed"
}

# Function to validate test infrastructure
validate_infrastructure() {
    log_info "Validating test infrastructure..."
    
    # Check if infrastructure validation script exists and run it
    if [[ -f "$PROJECT_ROOT/validate_infrastructure.py" ]]; then
        python "$PROJECT_ROOT/validate_infrastructure.py" 2>&1 | tee "$TEST_RESULTS_DIR/infrastructure-validation.log"
        log_success "Infrastructure validation completed"
    else
        log_warning "Infrastructure validation script not found"
    fi
}

# Function to generate test summary
generate_test_summary() {
    log_info "Generating test summary report..."
    
    local summary_file="$TEST_RESULTS_DIR/test-summary.json"
    
    cat > "$summary_file" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "project": "pmake-recover",
    "test_run_id": "$(date +%s)",
    "environment": {
        "python_version": "$(python --version | cut -d' ' -f2)",
        "pytest_version": "$(pytest --version | head -1 | cut -d' ' -f2)",
        "coverage_threshold": "$COVERAGE_THRESHOLD",
        "parallel_workers": "$PARALLEL_WORKERS"
    },
    "results": {
        "unit_tests": "$(test -f $TEST_RESULTS_DIR/junit-unit.xml && echo 'completed' || echo 'failed')",
        "integration_tests": "$(test -f $TEST_RESULTS_DIR/junit-integration.xml && echo 'completed' || echo 'failed')",
        "security_tests": "$(test -f $TEST_RESULTS_DIR/junit-security.xml && echo 'completed' || echo 'failed')",
        "performance_tests": "$(test -f $TEST_RESULTS_DIR/junit-performance.xml && echo 'completed' || echo 'failed')",
        "coverage_report": "$(test -f $REPORTS_DIR/coverage-combined.xml && echo 'generated' || echo 'missing')",
        "security_analysis": "$(test -f $REPORTS_DIR/bandit-report.json && echo 'completed' || echo 'missing')"
    },
    "artifacts": {
        "test_results": "$TEST_RESULTS_DIR",
        "coverage_reports": "$REPORTS_DIR",
        "logs": "$TEST_RESULTS_DIR/*.log"
    }
}
EOF
    
    log_success "Test summary generated: $summary_file"
}

# Function to cleanup test environment
cleanup_test_environment() {
    log_info "Cleaning up test environment..."
    
    # Remove temporary files
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name ".coverage*" -delete 2>/dev/null || true
    
    log_success "Test environment cleaned up"
}

# Function to display results summary
display_summary() {
    log_info "=== TEST EXECUTION SUMMARY ==="
    
    local total_tests=0
    local failed_tests=0
    
    # Count tests from JUnit XML files
    for junit_file in "$TEST_RESULTS_DIR"/junit-*.xml; do
        if [[ -f "$junit_file" ]]; then
            local tests
            local failures
            tests=$(grep -o 'tests="[0-9]*"' "$junit_file" | cut -d'"' -f2 || echo "0")
            failures=$(grep -o 'failures="[0-9]*"' "$junit_file" | cut -d'"' -f2 || echo "0")
            total_tests=$((total_tests + tests))
            failed_tests=$((failed_tests + failures))
        fi
    done
    
    log_info "Total tests executed: $total_tests"
    log_info "Failed tests: $failed_tests"
    log_info "Success rate: $(( (total_tests - failed_tests) * 100 / (total_tests > 0 ? total_tests : 1) ))%"
    
    # Coverage summary
    if [[ -f "$REPORTS_DIR/coverage-combined.json" ]]; then
        local coverage_percent
        coverage_percent=$(python -c "import json; print(json.load(open('$REPORTS_DIR/coverage-combined.json'))['totals']['percent_covered'])" 2>/dev/null || echo "N/A")
        log_info "Coverage: ${coverage_percent}%"
    fi
    
    log_info "Test results directory: $TEST_RESULTS_DIR"
    log_info "Coverage reports directory: $REPORTS_DIR"
    log_info "==============================="
}

# Main execution function
main() {
    local start_time
    start_time=$(date +%s)
    
    log_info "Starting comprehensive test execution for pmake-recover"
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Initialize exit code tracker
    local overall_exit_code=0
    
    # Setup environment
    setup_test_environment
    
    # Run test suites
    run_unit_tests || overall_exit_code=$?
    run_integration_tests || overall_exit_code=$?
    run_security_tests || overall_exit_code=$?
    run_performance_tests  # Don't fail on performance test issues
    
    # Generate reports
    generate_coverage_report || overall_exit_code=$?
    run_security_analysis
    validate_infrastructure
    generate_test_summary
    
    # Display summary
    display_summary
    
    # Cleanup
    cleanup_test_environment
    
    # Final timing
    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ $overall_exit_code -eq 0 ]]; then
        log_success "All tests completed successfully in ${duration}s"
    else
        log_error "Test execution completed with failures in ${duration}s (exit code: $overall_exit_code)"
    fi
    
    return $overall_exit_code
}

# Handle script arguments
case "${1:-all}" in
    unit)
        setup_test_environment && run_unit_tests
        ;;
    integration)
        setup_test_environment && run_integration_tests
        ;;
    security)
        setup_test_environment && run_security_tests
        ;;
    performance)
        setup_test_environment && run_performance_tests
        ;;
    coverage)
        generate_coverage_report
        ;;
    analysis)
        run_security_analysis
        ;;
    all|*)
        main
        ;;
esac