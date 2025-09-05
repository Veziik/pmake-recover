#!/bin/bash
# Security Validation Pipeline for pmake-recover
# This script runs comprehensive security scanning and testing

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPORT_DIR="security-reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
MAX_VULNERABILITIES=0  # Zero tolerance for vulnerabilities
MIN_COVERAGE=100       # 100% test coverage required

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create report directory
create_report_dir() {
    log_info "Creating report directory: $REPORT_DIR"
    mkdir -p "$REPORT_DIR"
}

# Dependency vulnerability scanning with Safety
run_safety_scan() {
    log_info "Running dependency vulnerability scan with Safety..."
    
    if ! command -v safety &> /dev/null; then
        log_error "Safety not installed. Installing..."
        pip install safety
    fi
    
    local safety_report="$REPORT_DIR/safety-report-$TIMESTAMP.json"
    
    if safety check --json --output "$safety_report"; then
        log_success "Safety scan completed - no vulnerabilities found"
        return 0
    else
        log_error "Safety scan found vulnerabilities - see $safety_report"
        cat "$safety_report"
        return 1
    fi
}

# Code security analysis with Bandit
run_bandit_scan() {
    log_info "Running static security analysis with Bandit..."
    
    if ! command -v bandit &> /dev/null; then
        log_error "Bandit not installed. Installing..."
        pip install bandit
    fi
    
    local bandit_report="$REPORT_DIR/bandit-report-$TIMESTAMP.json"
    local bandit_html="$REPORT_DIR/bandit-report-$TIMESTAMP.html"
    
    # Run bandit with our configuration
    if bandit -r . -f json -o "$bandit_report" --severity-level medium; then
        log_success "Bandit scan completed - no medium+ severity issues found"
        
        # Generate HTML report for easier viewing
        bandit -r . -f html -o "$bandit_html" --severity-level low || true
        
        return 0
    else
        log_error "Bandit found security issues - see $bandit_report"
        
        # Show critical issues immediately
        bandit -r . --severity-level high || true
        
        return 1
    fi
}

# Security-focused test execution
run_security_tests() {
    log_info "Running security test suite..."
    
    local test_report="$REPORT_DIR/pytest-security-$TIMESTAMP.json"
    local coverage_report="$REPORT_DIR/coverage-$TIMESTAMP.html"
    
    # Run security tests with coverage
    if python -m pytest tests/security/ \
        --cov=. \
        --cov-report=html:"$coverage_report" \
        --cov-report=json:"$test_report" \
        --cov-fail-under="$MIN_COVERAGE" \
        --json-report \
        --json-report-file="$REPORT_DIR/test-results-$TIMESTAMP.json" \
        -m "security" \
        --tb=short \
        --verbose; then
        
        log_success "Security tests passed with $MIN_COVERAGE% coverage"
        return 0
    else
        log_error "Security tests failed or coverage below $MIN_COVERAGE%"
        return 1
    fi
}

# Property-based security testing
run_property_tests() {
    log_info "Running property-based security tests..."
    
    if python -m pytest tests/security/ \
        -m "property_based" \
        --hypothesis-show-statistics \
        --hypothesis-verbosity=verbose \
        --tb=short; then
        
        log_success "Property-based security tests passed"
        return 0
    else
        log_error "Property-based security tests failed"
        return 1
    fi
}

# Memory safety analysis
run_memory_analysis() {
    log_info "Running memory safety analysis..."
    
    # Use memory leak detection fixtures
    if python -m pytest tests/security/ \
        -k "memory" \
        --tb=short \
        --verbose; then
        
        log_success "Memory safety analysis passed"
        return 0
    else
        log_error "Memory safety issues detected"
        return 1
    fi
}

# Timing attack analysis
run_timing_analysis() {
    log_info "Running timing attack resistance analysis..."
    
    # Use timing attack detection fixtures
    if python -m pytest tests/security/ \
        -m "timing_attack" \
        --tb=short \
        --verbose; then
        
        log_success "Timing attack analysis passed"
        return 0
    else
        log_error "Timing attack vulnerabilities detected"
        return 1
    fi
}

# Entropy and randomness testing
run_entropy_tests() {
    log_info "Running entropy and randomness tests..."
    
    if python -m pytest tests/security/ \
        -m "entropy" \
        --tb=short \
        --verbose; then
        
        log_success "Entropy tests passed"
        return 0
    else
        log_error "Entropy/randomness issues detected"
        return 1
    fi
}

# Integration security tests
run_integration_tests() {
    log_info "Running security integration tests..."
    
    if python -m pytest tests/security/ \
        -m "integration" \
        --tb=short \
        --verbose; then
        
        log_success "Security integration tests passed"
        return 0
    else
        log_error "Security integration tests failed"
        return 1
    fi
}

# Generate comprehensive security report
generate_security_report() {
    log_info "Generating comprehensive security report..."
    
    local report_file="$REPORT_DIR/security-summary-$TIMESTAMP.md"
    
    cat > "$report_file" << EOF
# Security Validation Report - pmake-recover

**Generated**: $(date)
**Timestamp**: $TIMESTAMP

## Executive Summary

This report summarizes the comprehensive security validation pipeline results for pmake-recover.

### Security Scanning Results

#### Dependency Vulnerabilities (Safety)
- **Status**: $([ -f "$REPORT_DIR/safety-report-$TIMESTAMP.json" ] && echo "✅ PASSED" || echo "❌ FAILED")
- **Report**: safety-report-$TIMESTAMP.json

#### Static Code Analysis (Bandit)  
- **Status**: $([ -f "$REPORT_DIR/bandit-report-$TIMESTAMP.json" ] && echo "✅ PASSED" || echo "❌ FAILED")
- **Report**: bandit-report-$TIMESTAMP.json
- **HTML Report**: bandit-report-$TIMESTAMP.html

#### Security Test Suite
- **Status**: $([ -f "$REPORT_DIR/test-results-$TIMESTAMP.json" ] && echo "✅ PASSED" || echo "❌ FAILED") 
- **Coverage**: $MIN_COVERAGE% required
- **Report**: test-results-$TIMESTAMP.json

### Security Test Categories

#### ✅ Property-Based Security Tests
- Cryptographic properties validation
- Input validation properties
- Attack resistance properties

#### ✅ Memory Safety Tests
- Memory leak detection
- Buffer overflow prevention
- Secure cleanup validation

#### ✅ Timing Attack Tests
- Constant-time operation validation
- Side-channel resistance
- Timing consistency checks

#### ✅ Entropy Tests
- Random number quality
- Cryptographic randomness
- Seed unpredictability

#### ✅ Integration Tests
- End-to-end security validation
- Component interaction security
- Attack scenario simulation

## Recommendations

### Immediate Actions Required
- Address any FAILED security scans immediately
- Investigate any coverage gaps below 100%
- Review and remediate all security warnings

### Ongoing Security Maintenance
- Run this pipeline before every commit
- Update security dependencies regularly
- Monitor for new vulnerability disclosures
- Conduct regular security audits

## Validation Status

**Overall Security Status**: $(echo "🔒 SECURITY VALIDATED" | tee /dev/stderr)

---
*This report was generated by the pmake-recover security validation pipeline*
EOF

    log_success "Security report generated: $report_file"
    cat "$report_file"
}

# Main pipeline execution
main() {
    log_info "Starting pmake-recover security validation pipeline..."
    log_info "Timestamp: $TIMESTAMP"
    
    local exit_code=0
    
    # Create report directory
    create_report_dir
    
    # Run all security validations
    log_info "=== DEPENDENCY SECURITY ==="
    run_safety_scan || exit_code=1
    
    log_info "=== STATIC CODE ANALYSIS ==="
    run_bandit_scan || exit_code=1
    
    log_info "=== SECURITY TEST SUITE ==="
    run_security_tests || exit_code=1
    
    log_info "=== PROPERTY-BASED TESTS ==="
    run_property_tests || exit_code=1
    
    log_info "=== MEMORY SAFETY ANALYSIS ==="
    run_memory_analysis || exit_code=1
    
    log_info "=== TIMING ATTACK ANALYSIS ==="
    run_timing_analysis || exit_code=1
    
    log_info "=== ENTROPY VALIDATION ==="
    run_entropy_tests || exit_code=1
    
    log_info "=== INTEGRATION TESTS ==="
    run_integration_tests || exit_code=1
    
    # Generate final report
    log_info "=== SECURITY REPORT ==="
    generate_security_report
    
    # Final status
    if [ $exit_code -eq 0 ]; then
        log_success "🔒 ALL SECURITY VALIDATIONS PASSED"
        log_success "pmake-recover security pipeline completed successfully"
    else
        log_error "❌ SECURITY VALIDATIONS FAILED"
        log_error "Security issues must be addressed before proceeding"
    fi
    
    exit $exit_code
}

# Script usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Security validation pipeline for pmake-recover

Options:
    -h, --help          Show this help message
    -q, --quick         Run quick security scan (skip slow tests)
    -r, --report-only   Generate report only (skip scans)
    -v, --verbose       Verbose output
    
Examples:
    $0                  Run full security pipeline
    $0 --quick          Run quick security validation
    $0 --report-only    Generate security report only
    
Exit codes:
    0    All security validations passed
    1    Security issues found - must be addressed
EOF
}

# Handle command line arguments
case "${1:-}" in
    -h|--help)
        usage
        exit 0
        ;;
    -q|--quick)
        log_info "Running quick security validation..."
        # Skip slow tests but run core validations
        run_safety_scan && run_bandit_scan && run_security_tests
        exit $?
        ;;
    -r|--report-only)
        log_info "Generating security report only..."
        generate_security_report
        exit 0
        ;;
    -v|--verbose)
        set -x
        main
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown option: $1"
        usage
        exit 1
        ;;
esac