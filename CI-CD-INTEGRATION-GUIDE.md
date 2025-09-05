# CI/CD Integration Guide for pmake-recover

## Overview

This guide provides comprehensive instructions for integrating the pmake-recover project with various CI/CD platforms. The test infrastructure is designed to be CI/CD-ready with standardized reporting, security scanning, and quality gates.

## 🏗️ Architecture

### Components Created

1. **GitHub Actions Workflow** (`.github/workflows/ci.yml`)
2. **Pre-commit Hooks** (`.pre-commit-config.yaml`)
3. **CI Setup Scripts** (`scripts/ci-setup.sh`)
4. **Test Runner Scripts** (`scripts/run-tests-ci.sh`)
5. **Report Generation** (`scripts/generate-ci-reports.sh`)
6. **Makefile** for standardized commands
7. **Docker Configuration** for containerized testing
8. **Configuration Files** for all tools

## 🚀 Quick Start

### Local Development Setup

```bash
# Complete development environment setup
make dev-setup

# Or step by step:
make setup-ci           # Set up CI/CD environment
make setup-pre-commit   # Install pre-commit hooks
make install-dev        # Install development dependencies
```

### Running Tests Locally

```bash
# Quick CI pipeline (unit tests + linting)
make ci-quick

# Full CI pipeline (all tests + security + reports)
make ci-full

# Individual test suites
make test-unit          # Unit tests with coverage
make test-integration   # Integration tests
make test-security      # Security tests
make test-performance   # Performance benchmarks
```

## 🔧 CI/CD Platform Integration

### GitHub Actions

The project includes a comprehensive GitHub Actions workflow (`.github/workflows/ci.yml`) that provides:

#### Features
- **Multi-platform testing** (Ubuntu, Windows, macOS)
- **Multi-version Python support** (3.11, 3.12)
- **Security scanning** (Bandit, Safety, Semgrep)
- **Code quality checks** (Black, isort, flake8, pylint, mypy)
- **100% test coverage enforcement**
- **Performance benchmarking**
- **Artifact collection**
- **Automatic reporting**

#### Setup
1. Push the repository to GitHub
2. The workflow will automatically run on:
   - Push to `main`, `develop`, or `feature/*` branches
   - Pull requests to `main` or `develop`
   - Manual triggers
   - Weekly security scans (Sundays at 2 AM UTC)

#### Environment Variables
Set these secrets in GitHub repository settings:
```yaml
CODECOV_TOKEN: your_codecov_token  # Optional for coverage reporting
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
# GitLab CI configuration for pmake-recover
image: python:3.12-slim

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
  PYTHONPATH: "$CI_PROJECT_DIR"
  COVERAGE_THRESHOLD: "100"

cache:
  paths:
    - .cache/pip/
    - .venv/

stages:
  - setup
  - test
  - quality
  - security
  - reports

before_script:
  - apt-get update && apt-get install -y make git libxml2-utils
  - make setup-ci

unit-tests:
  stage: test
  script:
    - make test-unit
  coverage: '/TOTAL.+?(\d+\%)$/'
  artifacts:
    reports:
      junit: test-results/junit-unit.xml
      coverage_report:
        coverage_format: cobertura
        path: reports/coverage-combined.xml
    paths:
      - test-results/
      - reports/
    expire_in: 1 week

integration-tests:
  stage: test
  script:
    - make test-integration
  artifacts:
    reports:
      junit: test-results/junit-integration.xml

security-scan:
  stage: security
  script:
    - make security-scan
  artifacts:
    reports:
      sast: reports/bandit-report.json
    paths:
      - reports/
    expire_in: 1 week
  allow_failure: false

code-quality:
  stage: quality
  script:
    - make lint
  artifacts:
    paths:
      - reports/
    expire_in: 1 week

generate-reports:
  stage: reports
  script:
    - make reports
  artifacts:
    paths:
      - reports/
      - badges/
    expire_in: 1 month
  only:
    - main
```

### Jenkins

Create `Jenkinsfile`:

```groovy
pipeline {
    agent any
    
    environment {
        PYTHONPATH = "${WORKSPACE}"
        COVERAGE_THRESHOLD = "100"
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'make setup-ci'
            }
        }
        
        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh 'make test-unit'
                    }
                    post {
                        always {
                            junit 'test-results/junit-unit.xml'
                            publishCoverage adapters: [
                                coberturaAdapter('reports/coverage-combined.xml')
                            ], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                        }
                    }
                }
                
                stage('Integration Tests') {
                    steps {
                        sh 'make test-integration'
                    }
                    post {
                        always {
                            junit 'test-results/junit-integration.xml'
                        }
                    }
                }
                
                stage('Security Tests') {
                    steps {
                        sh 'make test-security'
                    }
                    post {
                        always {
                            junit 'test-results/junit-security.xml'
                        }
                    }
                }
            }
        }
        
        stage('Quality Gates') {
            parallel {
                stage('Code Quality') {
                    steps {
                        sh 'make lint'
                    }
                    post {
                        always {
                            recordIssues enabledForFailure: true, tools: [
                                pyLint(pattern: 'reports/pylint-report.txt'),
                                flake8(pattern: 'reports/flake8-report.txt')
                            ]
                        }
                    }
                }
                
                stage('Security Scan') {
                    steps {
                        sh 'make security-scan'
                    }
                    post {
                        always {
                            recordIssues enabledForFailure: true, tools: [
                                pyLint(pattern: 'reports/bandit-report.txt')
                            ]
                        }
                    }
                }
            }
        }
        
        stage('Reports') {
            steps {
                sh 'make reports'
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports/htmlcov-combined',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                    
                    archiveArtifacts artifacts: 'reports/**,badges/**', allowEmptyArchive: true
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        failure {
            emailext (
                subject: "Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Build failed. Check console output at ${env.BUILD_URL}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}
```

### Azure DevOps

Create `azure-pipelines.yml`:

```yaml
trigger:
  branches:
    include:
    - main
    - develop
    - feature/*

pool:
  vmImage: 'ubuntu-latest'

variables:
  python.version: '3.12'
  PYTHONPATH: '$(System.DefaultWorkingDirectory)'
  COVERAGE_THRESHOLD: '100'

stages:
- stage: Test
  jobs:
  - job: TestJob
    strategy:
      matrix:
        Python311:
          python.version: '3.11'
        Python312:
          python.version: '3.12'
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(python.version)'
    
    - script: make setup-ci
      displayName: 'Setup CI Environment'
    
    - script: make test-unit
      displayName: 'Unit Tests'
    
    - script: make test-integration
      displayName: 'Integration Tests'
    
    - script: make test-security
      displayName: 'Security Tests'
    
    - task: PublishTestResults@2
      inputs:
        testResultsFiles: 'test-results/junit-*.xml'
        testRunTitle: 'Python $(python.version)'
    
    - task: PublishCodeCoverageResults@1
      inputs:
        codeCoverageTool: 'Cobertura'
        summaryFileLocation: 'reports/coverage-combined.xml'
        pathToSources: '$(System.DefaultWorkingDirectory)'

- stage: Quality
  dependsOn: Test
  jobs:
  - job: QualityGates
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(python.version)'
    
    - script: make setup-ci
      displayName: 'Setup CI Environment'
    
    - script: make lint
      displayName: 'Code Quality Check'
    
    - script: make security-scan
      displayName: 'Security Analysis'
    
    - script: make reports
      displayName: 'Generate Reports'
    
    - task: PublishBuildArtifacts@1
      inputs:
        pathToPublish: 'reports'
        artifactName: 'reports'
```

## 🐋 Docker Integration

### Building Test Container

```bash
# Build the testing image
make docker-build

# Run tests in container
make docker-test

# Run security scan in container
make docker-security
```

### Multi-stage Docker Builds

The provided `Dockerfile` supports multiple targets:

```bash
# Build for testing
docker build --target testing -t pmake-recover:test .

# Build for security scanning
docker build --target security -t pmake-recover:security .

# Build for development
docker build --target development -t pmake-recover:dev .

# Build for production
docker build --target production -t pmake-recover:prod .
```

## 📊 Reporting and Badges

### Coverage Reporting

The CI setup generates multiple coverage report formats:

- **XML**: `reports/coverage-combined.xml` (for CI systems)
- **HTML**: `reports/htmlcov-combined/` (for human reading)
- **JSON**: `reports/coverage-combined.json` (for processing)

### Badge Generation

Badges are automatically generated in `badges/` directory:

- **Coverage Badge**: `badges/coverage.json`
- **Test Status**: `badges/tests.json`
- **Security Status**: `badges/security.json`
- **Code Quality**: `badges/quality.json`

### Integration with Badge Services

For Shields.io integration:

```markdown
![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/your-org/pmake-recover/main/badges/coverage.json)
![Tests](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/your-org/pmake-recover/main/badges/tests.json)
![Security](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/your-org/pmake-recover/main/badges/security.json)
![Quality](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/your-org/pmake-recover/main/badges/quality.json)
```

## 🔒 Security Integration

### Security Scanning Tools

The CI pipeline includes comprehensive security scanning:

1. **Bandit**: Python security linter
2. **Safety**: Dependency vulnerability scanner
3. **Semgrep**: Static analysis security scanner
4. **detect-secrets**: Secret detection

### Security Quality Gates

All security scans are configured as **blocking** quality gates:

- **No high-severity vulnerabilities** allowed
- **No hardcoded secrets** permitted
- **All dependencies** must be vulnerability-free
- **Security test cases** must pass 100%

### Custom Security Tests

Add security-focused tests with the `@pytest.mark.security` decorator:

```python
import pytest
import secrets
import os

@pytest.mark.security
def test_secure_random_generation():
    """Test that secure random number generation is used."""
    # Test entropy and randomness quality
    random_bytes = os.urandom(32)
    assert len(random_bytes) == 32
    assert random_bytes != os.urandom(32)  # Should be different

@pytest.mark.security  
def test_no_predictable_passwords():
    """Test that password generation is not predictable."""
    from makepin import generate_password
    
    # Generate multiple passwords and ensure they're different
    passwords = [generate_password() for _ in range(10)]
    assert len(set(passwords)) == 10  # All unique
```

## 📈 Performance Monitoring

### Benchmark Integration

Performance tests are automatically tracked:

```python
@pytest.mark.slow
def test_password_generation_performance(benchmark):
    """Benchmark password generation performance."""
    from makepin import generate_password
    
    result = benchmark(generate_password, length=16)
    assert len(result) == 16
```

### CI Performance Tracking

The GitHub Actions workflow includes benchmark tracking that:

- Stores performance results over time
- Alerts on performance regressions (>150% slowdown)
- Generates performance trend reports

## 🛠️ Customization

### Environment Variables

Control CI behavior with environment variables:

```bash
export COVERAGE_THRESHOLD=95     # Lower coverage requirement
export PARALLEL_WORKERS=4        # Limit parallel test workers
export MAX_FAILURES=5           # Allow more test failures
export TIMEOUT=600              # Increase test timeout
```

### Custom Quality Gates

Modify quality thresholds in configuration files:

- **Coverage**: `.coveragerc` → `fail_under`
- **Security**: `.bandit` → `severity`
- **Code Quality**: `.flake8` → `max-complexity`
- **Performance**: `Makefile` → benchmark thresholds

### Adding New CI Platforms

To integrate with additional CI platforms:

1. Create platform-specific configuration file
2. Use standardized `make` commands
3. Adapt artifact publishing to platform requirements
4. Ensure proper environment variable handling

## 🔧 Troubleshooting

### Common Issues

**Coverage not reaching 100%:**
```bash
# Generate detailed coverage report
make coverage
# Check the HTML report in reports/htmlcov-combined/
```

**Pre-commit hooks failing:**
```bash
# Run hooks manually to debug
pre-commit run --all-files
# Or specific hook
pre-commit run bandit --all-files
```

**Docker build issues:**
```bash
# Build with verbose output
docker build --no-cache --progress=plain .
```

**CI timeout issues:**
```bash
# Increase timeout in environment
export TIMEOUT=900  # 15 minutes
make test
```

### Getting Help

1. Check the comprehensive test output: `test-results/`
2. Review detailed reports: `reports/`
3. Examine CI logs for specific error messages
4. Validate configuration files: `make validate-reports`

## 📚 Best Practices

### For Development Teams

1. **Run tests locally** before pushing: `make ci-quick`
2. **Keep coverage at 100%** for all new code
3. **Address security issues** immediately
4. **Use pre-commit hooks** to catch issues early
5. **Review CI reports** regularly

### For DevOps Teams

1. **Monitor CI performance** trends
2. **Keep dependencies updated** with security patches
3. **Review security scan results** weekly
4. **Backup CI artifacts** for compliance
5. **Scale CI resources** based on team size

### For Security Teams

1. **Review security test results** before releases
2. **Validate security scanning tools** regularly
3. **Implement security policy as code**
4. **Monitor for new vulnerability patterns**
5. **Audit CI/CD pipeline security**

---

This CI/CD integration provides enterprise-grade quality gates while maintaining developer productivity. The security-first approach ensures that vulnerabilities are caught early in the development process.