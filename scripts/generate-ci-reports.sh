#!/bin/bash
# CI-friendly Report Generation Script
# Generates standardized reports for various CI/CD platforms

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
REPORTS_DIR="${PROJECT_ROOT}/reports"
BADGES_DIR="${PROJECT_ROOT}/badges"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Function to setup directories
setup_directories() {
    log_info "Setting up report directories..."
    mkdir -p "$REPORTS_DIR" "$BADGES_DIR"
    log_success "Directories ready"
}

# Function to generate coverage badge
generate_coverage_badge() {
    log_info "Generating coverage badge..."
    
    if [[ ! -f "$REPORTS_DIR/coverage-combined.json" ]]; then
        log_warning "Coverage report not found, skipping badge generation"
        return 0
    fi
    
    # Extract coverage percentage
    local coverage_percent
    coverage_percent=$(python3 -c "
import json
try:
    with open('$REPORTS_DIR/coverage-combined.json', 'r') as f:
        data = json.load(f)
        print(f\"{data['totals']['percent_covered']:.1f}\")
except Exception as e:
    print('0.0')
" 2>/dev/null)
    
    # Determine badge color
    local color="red"
    if (( $(echo "$coverage_percent >= 90" | bc -l) )); then
        color="brightgreen"
    elif (( $(echo "$coverage_percent >= 80" | bc -l) )); then
        color="yellow"
    elif (( $(echo "$coverage_percent >= 70" | bc -l) )); then
        color="orange"
    fi
    
    # Generate badge URL
    local badge_url="https://img.shields.io/badge/coverage-${coverage_percent}%25-${color}"
    
    # Save badge information
    cat > "$BADGES_DIR/coverage.json" << EOF
{
    "schemaVersion": 1,
    "label": "coverage",
    "message": "${coverage_percent}%",
    "color": "$color",
    "namedLogo": "python",
    "logoColor": "white"
}
EOF
    
    echo "$badge_url" > "$BADGES_DIR/coverage-url.txt"
    
    log_success "Coverage badge generated: ${coverage_percent}%"
}

# Function to generate test results badge
generate_test_badge() {
    log_info "Generating test results badge..."
    
    local total_tests=0
    local failed_tests=0
    
    # Count tests from JUnit XML files
    for junit_file in "$PROJECT_ROOT"/test-results/junit-*.xml; do
        if [[ -f "$junit_file" ]]; then
            local tests failures
            tests=$(grep -o 'tests="[0-9]*"' "$junit_file" | cut -d'"' -f2 || echo "0")
            failures=$(grep -o 'failures="[0-9]*"' "$junit_file" | cut -d'"' -f2 || echo "0")
            total_tests=$((total_tests + tests))
            failed_tests=$((failed_tests + failures))
        fi
    done
    
    local status="passing"
    local color="brightgreen"
    
    if [[ $failed_tests -gt 0 ]]; then
        status="failing"
        color="red"
    elif [[ $total_tests -eq 0 ]]; then
        status="unknown"
        color="lightgrey"
    fi
    
    # Generate badge
    cat > "$BADGES_DIR/tests.json" << EOF
{
    "schemaVersion": 1,
    "label": "tests",
    "message": "$total_tests tests, $failed_tests failed",
    "color": "$color",
    "namedLogo": "pytest"
}
EOF
    
    local badge_url="https://img.shields.io/badge/tests-${total_tests}%20tests%2C%20${failed_tests}%20failed-${color}"
    echo "$badge_url" > "$BADGES_DIR/tests-url.txt"
    
    log_success "Test badge generated: $total_tests tests, $failed_tests failed"
}

# Function to generate security badge
generate_security_badge() {
    log_info "Generating security badge..."
    
    local security_issues=0
    local color="brightgreen"
    local message="secure"
    
    # Check Bandit report
    if [[ -f "$REPORTS_DIR/bandit-report.json" ]]; then
        security_issues=$(python3 -c "
import json
try:
    with open('$REPORTS_DIR/bandit-report.json', 'r') as f:
        data = json.load(f)
        print(len(data.get('results', [])))
except:
    print(0)
" 2>/dev/null)
    fi
    
    # Check Safety report
    local vulnerability_count=0
    if [[ -f "$REPORTS_DIR/safety-report.json" ]]; then
        vulnerability_count=$(python3 -c "
import json
try:
    with open('$REPORTS_DIR/safety-report.json', 'r') as f:
        data = json.load(f)
        print(len(data))
except:
    print(0)
" 2>/dev/null)
    fi
    
    local total_security_issues=$((security_issues + vulnerability_count))
    
    if [[ $total_security_issues -gt 0 ]]; then
        color="red"
        message="${total_security_issues} issues"
    fi
    
    # Generate badge
    cat > "$BADGES_DIR/security.json" << EOF
{
    "schemaVersion": 1,
    "label": "security",
    "message": "$message",
    "color": "$color",
    "namedLogo": "security"
}
EOF
    
    local badge_url="https://img.shields.io/badge/security-${message// /%20}-${color}"
    echo "$badge_url" > "$BADGES_DIR/security-url.txt"
    
    log_success "Security badge generated: $message"
}

# Function to generate code quality badge
generate_quality_badge() {
    log_info "Generating code quality badge..."
    
    local pylint_score="10.0"
    local color="brightgreen"
    
    # Try to extract Pylint score
    if [[ -f "$REPORTS_DIR/pylint-report.txt" ]]; then
        pylint_score=$(grep "Your code has been rated at" "$REPORTS_DIR/pylint-report.txt" | grep -o '[0-9]*\.[0-9]*' | head -1 || echo "10.0")
    fi
    
    # Determine color based on score
    if (( $(echo "$pylint_score >= 9.0" | bc -l) )); then
        color="brightgreen"
    elif (( $(echo "$pylint_score >= 7.0" | bc -l) )); then
        color="yellow"
    elif (( $(echo "$pylint_score >= 5.0" | bc -l) )); then
        color="orange"
    else
        color="red"
    fi
    
    # Generate badge
    cat > "$BADGES_DIR/quality.json" << EOF
{
    "schemaVersion": 1,
    "label": "code quality",
    "message": "${pylint_score}/10",
    "color": "$color",
    "namedLogo": "python"
}
EOF
    
    local badge_url="https://img.shields.io/badge/code%20quality-${pylint_score}%2F10-${color}"
    echo "$badge_url" > "$BADGES_DIR/quality-url.txt"
    
    log_success "Code quality badge generated: ${pylint_score}/10"
}

# Function to generate comprehensive report
generate_comprehensive_report() {
    log_info "Generating comprehensive CI report..."
    
    local report_file="$REPORTS_DIR/ci-comprehensive-report.md"
    
    cat > "$report_file" << 'EOF'
# CI/CD Comprehensive Report

## Test Results Summary

EOF
    
    # Add test statistics
    local total_tests=0
    local failed_tests=0
    
    for junit_file in "$PROJECT_ROOT"/test-results/junit-*.xml; do
        if [[ -f "$junit_file" ]]; then
            local tests failures
            tests=$(grep -o 'tests="[0-9]*"' "$junit_file" | cut -d'"' -f2 || echo "0")
            failures=$(grep -o 'failures="[0-9]*"' "$junit_file" | cut -d'"' -f2 || echo "0")
            total_tests=$((total_tests + tests))
            failed_tests=$((failed_tests + failures))
        fi
    done
    
    cat >> "$report_file" << EOF
- **Total Tests**: $total_tests
- **Failed Tests**: $failed_tests  
- **Success Rate**: $(( (total_tests - failed_tests) * 100 / (total_tests > 0 ? total_tests : 1) ))%

## Coverage Analysis

EOF
    
    # Add coverage information
    if [[ -f "$REPORTS_DIR/coverage-combined.json" ]]; then
        local coverage_percent
        coverage_percent=$(python3 -c "
import json
try:
    with open('$REPORTS_DIR/coverage-combined.json', 'r') as f:
        data = json.load(f)
        total_lines = data['totals']['num_statements']
        covered_lines = data['totals']['covered_lines']
        missing_lines = data['totals']['missing_lines']
        print(f'''- **Coverage**: {data['totals']['percent_covered']:.1f}%
- **Total Lines**: {total_lines}
- **Covered Lines**: {covered_lines}  
- **Missing Lines**: {missing_lines}''')
except:
    print('- **Coverage**: N/A')
")
        echo "$coverage_percent" >> "$report_file"
    else
        echo "- **Coverage**: N/A" >> "$report_file"
    fi
    
    cat >> "$report_file" << 'EOF'

## Security Analysis

EOF
    
    # Add security information
    local security_issues=0
    local vulnerability_count=0
    
    if [[ -f "$REPORTS_DIR/bandit-report.json" ]]; then
        security_issues=$(python3 -c "
import json
try:
    with open('$REPORTS_DIR/bandit-report.json', 'r') as f:
        data = json.load(f)
        print(len(data.get('results', [])))
except:
    print(0)
" 2>/dev/null)
    fi
    
    if [[ -f "$REPORTS_DIR/safety-report.json" ]]; then
        vulnerability_count=$(python3 -c "
import json
try:
    with open('$REPORTS_DIR/safety-report.json', 'r') as f:
        data = json.load(f)
        print(len(data))
except:
    print(0)
" 2>/dev/null)
    fi
    
    cat >> "$report_file" << EOF
- **Security Issues (Bandit)**: $security_issues
- **Dependency Vulnerabilities (Safety)**: $vulnerability_count
- **Total Security Concerns**: $((security_issues + vulnerability_count))

## Code Quality

EOF
    
    # Add code quality information
    local pylint_score="N/A"
    if [[ -f "$REPORTS_DIR/pylint-report.txt" ]]; then
        pylint_score=$(grep "Your code has been rated at" "$REPORTS_DIR/pylint-report.txt" | grep -o '[0-9]*\.[0-9]*' | head -1 || echo "N/A")
    fi
    
    cat >> "$report_file" << EOF
- **Pylint Score**: ${pylint_score}/10
- **Code Style**: $(test -f "$REPORTS_DIR/flake8-report.txt" && echo "Checked" || echo "N/A")

## Artifacts

- **Test Results**: test-results/
- **Coverage Reports**: reports/htmlcov-combined/
- **Security Reports**: reports/bandit-report.txt, reports/safety-report.txt
- **Badges**: badges/

---
*Report generated on $(date -u +%Y-%m-%dT%H:%M:%SZ)*
EOF
    
    log_success "Comprehensive report generated: $report_file"
}

# Function to generate JUnit summary
generate_junit_summary() {
    log_info "Generating JUnit XML summary..."
    
    local summary_file="$REPORTS_DIR/junit-summary.xml"
    local total_tests=0
    local total_failures=0
    local total_time=0
    
    # Collect statistics from all JUnit files
    for junit_file in "$PROJECT_ROOT"/test-results/junit-*.xml; do
        if [[ -f "$junit_file" ]]; then
            local tests failures time
            tests=$(grep -o 'tests="[0-9]*"' "$junit_file" | cut -d'"' -f2 || echo "0")
            failures=$(grep -o 'failures="[0-9]*"' "$junit_file" | cut -d'"' -f2 || echo "0")
            time=$(grep -o 'time="[0-9]*\.[0-9]*"' "$junit_file" | cut -d'"' -f2 || echo "0.0")
            
            total_tests=$((total_tests + tests))
            total_failures=$((total_failures + failures))
            total_time=$(echo "$total_time + $time" | bc -l)
        fi
    done
    
    # Generate summary XML
    cat > "$summary_file" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="pmake-recover-summary" 
           tests="$total_tests" 
           failures="$total_failures" 
           errors="0" 
           time="$total_time" 
           timestamp="$(date -u +%Y-%m-%dT%H:%M:%S)">
    <properties>
        <property name="project" value="pmake-recover"/>
        <property name="ci-system" value="github-actions"/>
        <property name="python-version" value="$(python3 --version | cut -d' ' -f2)"/>
    </properties>
    <!-- Individual test results are in separate junit-*.xml files -->
</testsuite>
EOF
    
    log_success "JUnit summary generated: $summary_file"
}

# Function to validate reports
validate_reports() {
    log_info "Validating generated reports..."
    
    local validation_errors=0
    
    # Check required files
    local required_files=(
        "$REPORTS_DIR/coverage-combined.xml"
        "$REPORTS_DIR/junit-summary.xml"
        "$REPORTS_DIR/ci-comprehensive-report.md"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_warning "Required file missing: $file"
            ((validation_errors++))
        fi
    done
    
    # Check XML file validity
    for xml_file in "$REPORTS_DIR"/*.xml; do
        if [[ -f "$xml_file" ]]; then
            if ! xmllint --noout "$xml_file" 2>/dev/null; then
                log_warning "Invalid XML file: $xml_file"
                ((validation_errors++))
            fi
        fi
    done
    
    if [[ $validation_errors -eq 0 ]]; then
        log_success "All reports validated successfully"
    else
        log_warning "$validation_errors validation issues found"
    fi
    
    return $validation_errors
}

# Function to upload artifacts (placeholder for CI systems)
prepare_artifacts() {
    log_info "Preparing artifacts for CI/CD upload..."
    
    # Create artifact manifest
    cat > "$REPORTS_DIR/artifact-manifest.json" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "artifacts": {
        "coverage": {
            "xml": "reports/coverage-combined.xml",
            "html": "reports/htmlcov-combined/",
            "json": "reports/coverage-combined.json"
        },
        "tests": {
            "junit": "test-results/junit-*.xml",
            "html": "test-results/report-*.html",
            "json": "test-results/report-*.json"
        },
        "security": {
            "bandit": "reports/bandit-report.json",
            "safety": "reports/safety-report.json"
        },
        "quality": {
            "pylint": "reports/pylint-report.json",
            "flake8": "reports/flake8-report.txt"
        },
        "badges": {
            "coverage": "badges/coverage.json",
            "tests": "badges/tests.json",
            "security": "badges/security.json",
            "quality": "badges/quality.json"
        },
        "reports": {
            "comprehensive": "reports/ci-comprehensive-report.md",
            "junit-summary": "reports/junit-summary.xml"
        }
    }
}
EOF
    
    log_success "Artifact manifest created"
}

# Main execution
main() {
    log_info "Starting CI report generation for pmake-recover"
    
    cd "$PROJECT_ROOT"
    
    setup_directories
    generate_coverage_badge
    generate_test_badge
    generate_security_badge
    generate_quality_badge
    generate_comprehensive_report
    generate_junit_summary
    prepare_artifacts
    validate_reports
    
    log_success "CI reports generated successfully!"
    log_info "Reports available in: $REPORTS_DIR"
    log_info "Badges available in: $BADGES_DIR"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi