#!/bin/bash
# CI/CD Integration Testing Script
# Validates the Coverage Guardian system across different simulated CI environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 CI/CD INTEGRATION TESTING SUITE${NC}"
echo "============================================================"
echo "Timestamp: $(date)"
echo "Testing Coverage Guardian across multiple CI environments"
echo "============================================================"

# Function to log and display
log_test() {
    echo -e "${CYAN}🔍 $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    log_test "Test $TESTS_RUN: $test_name"
    
    if eval "$test_command" >/dev/null 2>&1; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        log_success "$test_name"
        return 0
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        log_error "$test_name"
        return 1
    fi
}

# Test 1: Environment Detection
log_test "Testing CI Environment Detection..."

run_test "Local Environment Detection" "python3 scripts/ci_environment_detector.py >/dev/null"

# Simulate different CI environments
export CI=true
run_test "Generic CI Detection" "python3 scripts/ci_environment_detector.py | grep -q 'Generic CI Environment'"
unset CI

export GITHUB_ACTIONS=true
export GITHUB_WORKFLOW=test
run_test "GitHub Actions Detection" "python3 scripts/ci_environment_detector.py | grep -q 'GitHub Actions'"
unset GITHUB_ACTIONS GITHUB_WORKFLOW

export GITLAB_CI=true
export CI_PIPELINE_ID=123
run_test "GitLab CI Detection" "python3 scripts/ci_environment_detector.py | grep -q 'GitLab CI'"
unset GITLAB_CI CI_PIPELINE_ID

export JENKINS_URL=http://jenkins
export BUILD_NUMBER=42
run_test "Jenkins Detection" "python3 scripts/ci_environment_detector.py | grep -q 'Jenkins'"
unset JENKINS_URL BUILD_NUMBER

# Test 2: Script Dependencies
log_test "Testing Script Dependencies..."

run_test "CI Coverage Check Script Exists" "[ -f scripts/ci_coverage_check.sh ]"
run_test "CI Coverage Check Is Executable" "[ -x scripts/ci_coverage_check.sh ]"
run_test "Complete Test Suite Script Exists" "[ -f scripts/run_complete_test_suite.sh ]"
run_test "Complete Test Suite Is Executable" "[ -x scripts/run_complete_test_suite.sh ]"
run_test "Coverage Validator Exists" "[ -f scripts/coverage_validator.py ]"
run_test "Guardian Enforcer Exists" "[ -f scripts/guardian_enforcer.py ]"

# Test 3: CI Configuration Files
log_test "Testing CI Configuration Files..."

run_test "GitHub Actions Workflow Exists" "[ -f .github/workflows/coverage-guardian.yml ]"
run_test "GitHub Actions Multi-Platform Workflow Exists" "[ -f .github/workflows/multi-platform-coverage.yml ]"
run_test "GitLab CI Configuration Exists" "[ -f .gitlab-ci.yml ]"
run_test "Azure DevOps Pipeline Exists" "[ -f azure-pipelines.yml ]"
run_test "Jenkinsfile Exists" "[ -f Jenkinsfile ]"

# Test 4: Configuration File Syntax
log_test "Testing Configuration File Syntax..."

run_test "GitHub Actions YAML Syntax" "python3 -c 'import yaml; yaml.safe_load(open(\".github/workflows/coverage-guardian.yml\"))'"
run_test "GitLab CI YAML Syntax" "python3 -c 'import yaml; yaml.safe_load(open(\".gitlab-ci.yml\"))'"
run_test "Azure Pipelines YAML Syntax" "python3 -c 'import yaml; yaml.safe_load(open(\"azure-pipelines.yml\"))'"

# Test 5: Environment Variable Handling
log_test "Testing Environment Variable Handling..."

export COVERAGE_THRESHOLD=90
run_test "Custom Coverage Threshold" "python3 scripts/ci_environment_detector.py | grep -q '90'"
export COVERAGE_THRESHOLD=100

export PROJECT_DIR=/tmp
run_test "Custom Project Directory" "python3 scripts/ci_environment_detector.py >/dev/null"
unset PROJECT_DIR

# Test 6: Docker Integration Test
log_test "Testing Docker Integration..."

if command -v docker >/dev/null 2>&1; then
    run_test "Docker Available" "docker --version >/dev/null"
    
    # Create minimal Dockerfile for testing
    cat > Dockerfile.test << EOF
FROM python:3.12-slim
WORKDIR /app
RUN pip install pytest coverage
COPY scripts/ scripts/
COPY tests/ tests/
RUN chmod +x scripts/*.sh
CMD ["python3", "scripts/ci_environment_detector.py"]
EOF
    
    if run_test "Docker Build Test" "docker build -f Dockerfile.test -t ci-test . >/dev/null"; then
        run_test "Docker Run Test" "docker run --rm ci-test >/dev/null"
    fi
    
    # Cleanup
    rm -f Dockerfile.test
    docker rmi ci-test >/dev/null 2>&1 || true
else
    log_warning "Docker not available - skipping Docker integration tests"
fi

# Test 7: Pre-commit Integration
log_test "Testing Pre-commit Integration..."

run_test "Pre-commit Config Exists" "[ -f .pre-commit-config.yaml ]"
if command -v pre-commit >/dev/null 2>&1; then
    run_test "Pre-commit Config Valid" "pre-commit validate-config"
else
    log_warning "Pre-commit not installed - skipping validation"
fi

# Test 8: Python Module Imports
log_test "Testing Python Module Imports..."

run_test "Coverage Validator Import" "python3 -c 'import sys; sys.path.append(\"scripts\"); import coverage_validator'"
run_test "Guardian Enforcer Import" "python3 -c 'import sys; sys.path.append(\"scripts\"); import guardian_enforcer'"
run_test "CI Environment Detector Import" "python3 -c 'import sys; sys.path.append(\"scripts\"); import ci_environment_detector'"

# Test 9: File Permissions
log_test "Testing File Permissions..."

run_test "Scripts Directory Readable" "[ -r scripts/ ]"
run_test "All Shell Scripts Executable" "find scripts/ -name '*.sh' -not -executable | wc -l | grep -q '^0$'"
run_test "All Python Scripts Readable" "find scripts/ -name '*.py' -not -readable | wc -l | grep -q '^0$'"

# Test 10: Integration Documentation
log_test "Testing Integration Documentation..."

run_test "CI/CD Integration Guide Exists" "[ -f CICD_INTEGRATION_GUIDE.md ]"
run_test "Integration Guide Not Empty" "[ -s CICD_INTEGRATION_GUIDE.md ]"

# Test 11: Artifact Generation Simulation
log_test "Testing Artifact Generation..."

# Create temporary test environment
TEST_ENV_DIR="/tmp/ci_test_$$"
mkdir -p "$TEST_ENV_DIR"
cd "$TEST_ENV_DIR"

# Copy essential files
cp -r $OLDPWD/scripts .
cp -r $OLDPWD/tests . 2>/dev/null || mkdir -p tests
cp $OLDPWD/requirements.txt . 2>/dev/null || echo "pytest>=6.0" > requirements.txt
cp $OLDPWD/.coveragerc . 2>/dev/null || echo "[run]\nsource = ." > .coveragerc

# Create minimal test file if none exist
if [ ! -f tests/test_basic.py ]; then
    cat > tests/test_basic.py << EOF
def test_always_passes():
    assert True
EOF
fi

# Create minimal source file
echo "def hello(): return 'world'" > main.py

if python3 -m venv test_env && source test_env/bin/activate; then
    pip install pytest coverage >/dev/null 2>&1
    
    if run_test "Coverage Collection" "coverage run -m pytest tests/ >/dev/null"; then
        run_test "Coverage HTML Generation" "coverage html >/dev/null && [ -f htmlcov/index.html ]"
        run_test "Coverage XML Generation" "coverage xml >/dev/null && [ -f coverage.xml ]"
        run_test "Coverage JSON Generation" "coverage json >/dev/null && [ -f coverage.json ]"
    fi
    
    deactivate
fi

# Cleanup
cd "$OLDPWD"
rm -rf "$TEST_ENV_DIR"

# Test 12: Security Validation
log_test "Testing Security Validation Features..."

run_test "Security Files List Defined" "grep -q 'SECURITY_FILES.*makepin.py' scripts/ci_coverage_check.sh"
run_test "Security Coverage Check" "grep -q '100% coverage' scripts/ci_coverage_check.sh"
run_test "Security Risk Detection" "grep -q 'SECURITY RISK' scripts/ci_coverage_check.sh"

# Final Results
echo ""
echo "============================================================"
echo -e "${PURPLE}📊 CI/CD INTEGRATION TEST RESULTS${NC}"
echo "============================================================"
echo "Tests Run:    $TESTS_RUN"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ ALL TESTS PASSED - CI/CD INTEGRATION VALIDATED${NC}"
    echo ""
    echo "🎉 The Coverage Guardian system is ready for CI/CD deployment!"
    echo ""
    echo "Next steps:"
    echo "1. Choose your CI/CD platform from the configuration files"
    echo "2. Copy the appropriate workflow/pipeline file to your repository"
    echo "3. Commit and push to trigger the first Guardian-protected build"
    echo "4. Monitor coverage reports and security validations"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}❌ SOME TESTS FAILED - REVIEW CI/CD INTEGRATION${NC}"
    echo ""
    echo "Failed tests indicate potential issues with:"
    echo "- Script permissions or dependencies"
    echo "- Configuration file syntax"
    echo "- Missing files or documentation"
    echo ""
    echo "Please review the output above and fix any issues before deployment."
    exit 1
fi