# CI/CD Integration Guide for Coverage Guardian System

## 🎯 Overview

This document provides comprehensive guidance for integrating the Coverage Guardian system with various CI/CD platforms. The system enforces 100% test coverage across all codebases with security-focused validation.

## 📋 Table of Contents

1. [Supported CI/CD Platforms](#supported-cicd-platforms)
2. [Quick Start](#quick-start)
3. [Platform-Specific Configuration](#platform-specific-configuration)
4. [Advanced Integration](#advanced-integration)
5. [Monitoring and Alerting](#monitoring-and-alerting)
6. [Troubleshooting](#troubleshooting)

## 🔧 Supported CI/CD Platforms

### ✅ Fully Supported
- **GitHub Actions** - Complete integration with workflows, artifacts, and PR comments
- **GitLab CI/CD** - Full pipeline support with coverage reporting and security scanning
- **Azure DevOps** - Multi-platform testing with comprehensive artifact management
- **Jenkins** - Declarative and scripted pipelines with HTML publishing

### 🔄 Partially Supported  
- **CircleCI** - Basic coverage validation (configuration not included)
- **Travis CI** - Basic coverage validation (configuration not included)
- **TeamCity** - Script-based integration (configuration not included)

## 🚀 Quick Start

### 1. Basic Integration

Add the Coverage Guardian to any CI/CD pipeline with three simple steps:

```bash
# Step 1: Install dependencies
pip install pytest coverage pytest-cov

# Step 2: Run Coverage Guardian
chmod +x scripts/ci_coverage_check.sh
./scripts/ci_coverage_check.sh

# Step 3: Validate results
python scripts/guardian_enforcer.py --threshold 100
```

### 2. Environment Detection

The system automatically detects your CI/CD environment:

```bash
# Check current environment capabilities
python scripts/ci_environment_detector.py
```

### 3. Complete Test Suite

For comprehensive validation:

```bash
# Run full test suite with Guardian enforcement
chmod +x scripts/run_complete_test_suite.sh
./scripts/run_complete_test_suite.sh
```

## 🔌 Platform-Specific Configuration

### GitHub Actions

**File:** `.github/workflows/coverage-guardian.yml`

```yaml
name: Coverage Guardian Enforcement
on: [push, pull_request]

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install pytest coverage pytest-cov
          pip install -r requirements.txt
      
      - name: Run Coverage Guardian
        run: |
          chmod +x scripts/ci_coverage_check.sh
          scripts/ci_coverage_check.sh
      
      - name: Upload coverage reports
        uses: actions/upload-artifact@v3
        with:
          name: coverage-reports
          path: coverage_artifacts/
```

**Key Features:**
- ✅ Automatic artifact upload
- ✅ PR comment with coverage status
- ✅ Codecov integration
- ✅ Multi-platform matrix testing
- ✅ Security-critical file validation

### GitLab CI/CD

**File:** `.gitlab-ci.yml`

```yaml
stages:
  - test
  - coverage-validation

coverage-guardian:
  stage: coverage-validation
  image: python:3.12
  script:
    - pip install pytest coverage pytest-cov
    - pip install -r requirements.txt
    - chmod +x scripts/ci_coverage_check.sh
    - scripts/ci_coverage_check.sh
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - coverage_artifacts/
    expire_in: 30 days
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

**Key Features:**
- ✅ Coverage visualization in merge requests
- ✅ GitLab Pages integration for reports
- ✅ Pipeline artifacts with retention
- ✅ Security scanning integration

### Azure DevOps

**File:** `azure-pipelines.yml`

```yaml
trigger: [main, develop]

variables:
  COVERAGE_THRESHOLD: 100

jobs:
- job: CoverageGuardian
  displayName: 'Coverage Guardian Enforcement'
  pool:
    vmImage: 'ubuntu-latest'
  
  steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.12'
  
  - script: |
      pip install pytest coverage pytest-cov
      pip install -r requirements.txt
      chmod +x scripts/ci_coverage_check.sh
      scripts/ci_coverage_check.sh
    displayName: 'Run Coverage Guardian'
  
  - task: PublishCodeCoverageResults@1
    inputs:
      codeCoverageTool: 'Cobertura'
      summaryFileLocation: 'coverage.xml'
      reportDirectory: 'htmlcov'
```

**Key Features:**
- ✅ Multi-platform testing (Windows, macOS, Linux)
- ✅ Code coverage visualization
- ✅ Build artifact publishing
- ✅ Email notifications

### Jenkins

**File:** `Jenkinsfile`

```groovy
pipeline {
    agent any
    
    environment {
        COVERAGE_THRESHOLD = '100'
    }
    
    stages {
        stage('Coverage Guardian') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install pytest coverage pytest-cov
                    pip install -r requirements.txt
                    chmod +x scripts/ci_coverage_check.sh
                    scripts/ci_coverage_check.sh
                '''
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }
    }
}
```

**Key Features:**
- ✅ HTML coverage report publishing
- ✅ Email notifications on failure
- ✅ Build artifact archiving
- ✅ Multi-branch support

## 🔍 Advanced Integration

### Environment Variables

Configure the Coverage Guardian using these environment variables:

```bash
# Core Configuration
COVERAGE_THRESHOLD=100          # Required coverage percentage
PROJECT_DIR=.                   # Project root directory
COVERAGE_REPORTS_DIR=.          # Coverage reports output directory

# CI/CD Integration
CI=true                         # Enable CI mode
GITHUB_ACTIONS=true            # GitHub Actions detection
GITLAB_CI=true                 # GitLab CI detection
AZURE_HTTP_USER_AGENT=true     # Azure DevOps detection
JENKINS_URL=http://jenkins     # Jenkins detection

# Security Settings
SECURITY_FILES="makepin.py recoverpin.py helpers.py"  # Critical files
ENFORCE_SECURITY_COVERAGE=true  # Require 100% on security files
```

### Docker Integration

Create a Docker-based CI pipeline:

```dockerfile
# Dockerfile.ci
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install pytest coverage pytest-cov

# Copy source code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV COVERAGE_THRESHOLD=100

# Run Coverage Guardian by default
CMD ["./scripts/ci_coverage_check.sh"]
```

**Usage in CI:**
```bash
# Build and run coverage validation
docker build -f Dockerfile.ci -t coverage-guardian .
docker run --rm -v $(pwd)/coverage-output:/app/coverage-output coverage-guardian
```

### Parallel Testing

Configure parallel testing for faster CI execution:

```yaml
# GitHub Actions parallel matrix
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.10', '3.11', '3.12']
  fail-fast: false

# GitLab CI parallel jobs
test-parallel:
  parallel: 4
  script:
    - pytest tests/ --tb=short -x -q
```

### Security Integration

Integrate security scanning with coverage validation:

```bash
# Security-focused coverage validation
scripts/ci_coverage_check.sh

# Additional security scans
bandit -r . -x tests/ -f json -o security-bandit.json
safety check --json --output security-safety.json
semgrep --config=auto --json --output security-semgrep.json .
```

## 📊 Monitoring and Alerting

### Coverage Metrics

The system generates comprehensive metrics:

```json
{
  "timestamp": "2024-09-05T00:00:00Z",
  "total_coverage": "100%",
  "line_coverage": "100%",
  "branch_coverage": "100%",
  "security_files_coverage": {
    "makepin.py": "100%",
    "recoverpin.py": "100%", 
    "helpers.py": "100%"
  },
  "guardian_status": "APPROVED"
}
```

### Alerting Configuration

Set up alerts for coverage violations:

```bash
# Slack notification on failure
if [ "$COVERAGE_STATUS" != "100" ]; then
    curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"🚨 Coverage Guardian Alert: Coverage dropped below 100%"}' \
    $SLACK_WEBHOOK_URL
fi

# Email notification
if [ "$GUARDIAN_STATUS" != "APPROVED" ]; then
    echo "Coverage violation detected" | mail -s "Guardian Alert" team@company.com
fi
```

### Dashboard Integration

Integrate with monitoring dashboards:

```python
# Prometheus metrics
from prometheus_client import Gauge, Counter

coverage_gauge = Gauge('test_coverage_percentage', 'Current test coverage percentage')
guardian_counter = Counter('guardian_enforcements_total', 'Total guardian enforcement actions')

# Update metrics
coverage_gauge.set(coverage_percentage)
guardian_counter.inc()
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Package Installation Failures

**Problem:** `pip install` fails in CI environment

**Solutions:**
```bash
# Use virtual environment
python3 -m venv ci-env
source ci-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Or use system packages
sudo apt-get update
sudo apt-get install python3-pytest python3-coverage

# Or use user installation
pip install --user pytest coverage
```

#### 2. Permission Denied on Scripts

**Problem:** `Permission denied: ./scripts/ci_coverage_check.sh`

**Solution:**
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Or run with bash
bash scripts/ci_coverage_check.sh
```

#### 3. Coverage Below Threshold

**Problem:** Tests pass but coverage is below 100%

**Debugging Steps:**
```bash
# Generate detailed coverage report
coverage report --show-missing

# Check specific file coverage
coverage report --include="filename.py"

# Generate HTML report for visual inspection
coverage html
open htmlcov/index.html
```

#### 4. Import Errors in Tests

**Problem:** `ImportError: cannot import name 'MODULE' from 'module'`

**Solution:**
```bash
# Set PYTHONPATH
export PYTHONPATH=$PWD:$PYTHONPATH

# Or use pytest with path
python -m pytest tests/

# Or install package in development mode
pip install -e .
```

### Debug Mode

Enable debug mode for detailed troubleshooting:

```bash
# Enable debug output
export DEBUG=true
export VERBOSE=true

# Run with debug information
./scripts/ci_coverage_check.sh
```

### Support and Maintenance

For issues and support:

1. **Check Logs:** Review CI/CD pipeline logs for specific error messages
2. **Validate Environment:** Run `scripts/ci_environment_detector.py` to check configuration
3. **Manual Testing:** Test scripts locally before CI/CD integration
4. **Update Dependencies:** Ensure all dependencies are up to date

## 📚 Best Practices

### 1. Incremental Integration

Start with basic coverage validation and gradually add features:

```bash
# Phase 1: Basic coverage
coverage run -m pytest
coverage report --fail-under=100

# Phase 2: Add Guardian validation
python scripts/coverage_validator.py --enforce

# Phase 3: Complete integration
./scripts/ci_coverage_check.sh
```

### 2. Performance Optimization

Optimize CI/CD pipeline performance:

- Use dependency caching
- Implement parallel testing
- Optimize test execution order
- Use minimal base images for Docker

### 3. Security Best Practices

- Never store secrets in code or logs
- Use encrypted environment variables
- Validate all user inputs
- Implement proper access controls
- Regularly update dependencies

## 🎉 Success Metrics

Track these metrics to measure integration success:

- **Coverage Consistency:** 100% coverage maintained across all builds
- **Build Reliability:** Green builds with Guardian approval
- **Security Validation:** All security-critical files at 100% coverage
- **Performance Impact:** CI/CD execution time within acceptable limits
- **Developer Experience:** Minimal friction in development workflow

---

*This integration guide ensures comprehensive coverage validation across all CI/CD platforms with security-focused enforcement and comprehensive monitoring capabilities.*