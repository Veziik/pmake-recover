#!/bin/bash
# CI/CD Coverage Check Script
# Guardian Enforcement for 100% Coverage in CI Pipeline

set -e  # Exit on any error

# Configuration
COVERAGE_THRESHOLD=100
PROJECT_DIR="${1:-.}"
COVERAGE_REPORTS_DIR="$PROJECT_DIR"

echo "🔍 COVERAGE GUARDIAN - CI/CD ENFORCEMENT STARTING..."
echo "============================================================="
echo "Timestamp: $(date)"
echo "Project Directory: $PROJECT_DIR"
echo "Coverage Threshold: $COVERAGE_THRESHOLD%"
echo "============================================================="

# Ensure we're in the right directory
cd "$PROJECT_DIR"

# Install dependencies if needed
echo "📦 Checking dependencies..."

# Handle different CI environments and Python package management
if [ -f "requirements.txt" ]; then
    # Check if we're in a virtual environment or CI
    if [[ -n "$VIRTUAL_ENV" ]] || [[ -n "$GITHUB_ACTIONS" ]] || [[ -n "$CI" ]]; then
        echo "   Installing in CI/virtual environment..."
        pip install -r requirements.txt --quiet
    else
        # Check if system packages are available
        echo "   Attempting to install dependencies..."
        pip install -r requirements.txt --quiet --user 2>/dev/null || {
            echo "   ⚠️  Could not install via pip, checking system packages..."
            # For Ubuntu/Debian systems, try to install pytest and coverage via apt
            if command -v apt-get >/dev/null 2>&1; then
                sudo apt-get update -qq >/dev/null 2>&1 || true
                sudo apt-get install -qq python3-pytest python3-coverage >/dev/null 2>&1 || true
            fi
        }
    fi
fi

# Ensure pytest and coverage are available
echo "📋 Verifying test tools availability..."
if ! command -v pytest >/dev/null 2>&1; then
    echo "   Installing pytest..."
    pip install pytest --user --quiet 2>/dev/null || pip install pytest --quiet || {
        echo "❌ Could not install pytest - cannot proceed"
        exit 1
    }
fi

if ! command -v coverage >/dev/null 2>&1; then
    echo "   Installing coverage..."
    pip install coverage --user --quiet 2>/dev/null || pip install coverage --quiet || {
        echo "❌ Could not install coverage - cannot proceed"
        exit 1
    }
fi

echo "✅ Dependencies verified"

# Clean previous coverage data
echo "🧹 Cleaning previous coverage data..."
rm -rf htmlcov/ coverage.xml coverage.json .coverage 2>/dev/null || true

# Run tests with coverage
echo "🧪 Running tests with coverage collection..."
coverage run --source=. -m pytest --tb=short || {
    echo "❌ Tests failed - cannot proceed with coverage validation"
    exit 1
}

# Generate all coverage report formats
echo "📊 Generating coverage reports..."
coverage html --directory htmlcov
coverage xml --output coverage.xml
coverage json --output coverage.json
coverage report --show-missing

# Validate coverage using the Python validator
echo "🛡️ GUARDIAN VALIDATION - ENFORCING 100% COVERAGE..."
python scripts/coverage_validator.py --enforce --threshold $COVERAGE_THRESHOLD || {
    echo "❌ COVERAGE GUARDIAN BLOCKED DEPLOYMENT"
    echo "🚨 CRITICAL: Coverage below required threshold of $COVERAGE_THRESHOLD%"
    exit 1
}

# Generate summary report
echo "📋 Generating coverage summary..."
python scripts/coverage_validator.py --summary > coverage_ci_summary.json

# Check for security-critical files coverage
echo "🔒 Validating security-critical files coverage..."
SECURITY_FILES="makepin.py recoverpin.py helpers.py"
for file in $SECURITY_FILES; do
    if [ -f "$file" ]; then
        coverage report --include="$file" | tail -1 | grep -q "100%" || {
            echo "❌ SECURITY RISK: $file does not have 100% coverage"
            exit 1
        }
        echo "✅ Security file $file has 100% coverage"
    fi
done

# Validate all report formats exist
echo "📁 Validating coverage report files..."
REQUIRED_REPORTS="htmlcov/index.html coverage.xml coverage.json"
for report in $REQUIRED_REPORTS; do
    if [ ! -f "$report" ]; then
        echo "❌ Missing required coverage report: $report"
        exit 1
    fi
    echo "✅ Coverage report found: $report"
done

# Archive coverage reports for CI artifacts
echo "🗃️ Archiving coverage reports..."
mkdir -p coverage_artifacts
cp -r htmlcov coverage_artifacts/
cp coverage.xml coverage.json coverage_artifacts/
cp coverage_ci_summary.json coverage_artifacts/
echo "✅ Coverage artifacts ready in coverage_artifacts/"

# Final success message
echo "============================================================="
echo "✅ COVERAGE GUARDIAN APPROVED - ALL CHECKS PASSED"
echo "   - Tests: PASSED"
echo "   - Coverage: 100% (All formats validated)"
echo "   - Security files: 100% coverage confirmed"
echo "   - Reports: All formats generated successfully"
echo "   - Artifacts: Archived for CI/CD pipeline"
echo "============================================================="

# Output summary for CI logs
echo "COVERAGE_STATUS=PASSED" >> coverage_status.env
echo "COVERAGE_PERCENTAGE=100" >> coverage_status.env
echo "REPORTS_GENERATED=html,xml,json,console" >> coverage_status.env