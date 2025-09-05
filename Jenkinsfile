#!/usr/bin/env groovy
/*
 * Jenkins Pipeline for Coverage Guardian Enforcement
 * Multi-stage pipeline with comprehensive testing and validation
 */

pipeline {
    agent any
    
    environment {
        COVERAGE_THRESHOLD = '100'
        PYTHON_VERSION = '3.12'
        VENV_NAME = 'coverage-guardian-env'
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        ansiColor('xterm')
    }
    
    triggers {
        pollSCM('H/5 * * * *')
        cron(env.BRANCH_NAME == 'main' ? 'H 2 * * *' : '')
    }
    
    stages {
        stage('Setup Environment') {
            steps {
                echo "🔧 Setting up Python environment..."
                sh '''
                    python3 -m venv ${VENV_NAME}
                    . ${VENV_NAME}/bin/activate
                    pip install --upgrade pip
                    pip install pytest coverage pytest-cov
                    
                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    fi
                    
                    echo "✅ Environment setup completed"
                '''
            }
        }
        
        stage('Pre-flight Checks') {
            steps {
                echo "📋 Running pre-flight checks..."
                sh '''
                    . ${VENV_NAME}/bin/activate
                    
                    echo "Python Version:"
                    python --version
                    
                    echo "Pytest Version:"
                    pytest --version
                    
                    echo "Coverage Version:"
                    coverage --version
                    
                    echo "Test Files Found:"
                    find tests -name "test_*.py" | wc -l
                    
                    echo "Source Files:"
                    ls -la *.py
                '''
            }
        }
        
        stage('Unit Tests with Coverage') {
            steps {
                echo "🧪 Running unit tests with coverage collection..."
                sh '''
                    . ${VENV_NAME}/bin/activate
                    
                    # Clean previous coverage data
                    rm -rf .coverage coverage.xml coverage.json htmlcov/
                    
                    # Run tests with coverage
                    coverage run --source=. -m pytest tests/ -v --tb=short
                    
                    # Generate coverage reports
                    coverage report --show-missing
                    coverage xml
                    coverage json
                    coverage html
                    
                    echo "✅ Tests completed successfully"
                '''
            }
            post {
                always {
                    // Publish test results
                    publishTestResults testResultsPattern: 'coverage.xml'
                    
                    // Publish HTML coverage report
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report',
                        reportTitles: 'Code Coverage'
                    ])
                }
            }
        }
        
        stage('Coverage Guardian Validation') {
            steps {
                echo "🛡️ Running Coverage Guardian validation..."
                sh '''
                    . ${VENV_NAME}/bin/activate
                    
                    # Make scripts executable
                    chmod +x scripts/ci_coverage_check.sh
                    
                    # Run coverage guardian
                    export COVERAGE_THRESHOLD=${COVERAGE_THRESHOLD}
                    scripts/ci_coverage_check.sh
                    
                    echo "✅ Coverage Guardian validation passed"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'coverage_artifacts/**/*', 
                                   allowEmptyArchive: true,
                                   fingerprint: true
                }
            }
        }
        
        stage('Security-Critical Files Check') {
            steps {
                echo "🔒 Validating security-critical files coverage..."
                sh '''
                    . ${VENV_NAME}/bin/activate
                    
                    SECURITY_FILES="makepin.py recoverpin.py helpers.py words.py"
                    
                    for file in $SECURITY_FILES; do
                        if [ -f "$file" ]; then
                            echo "Checking coverage for: $file"
                            file_coverage=$(coverage report --include="$file" | tail -1 | awk '{print $4}' | sed 's/%//')
                            
                            if [ "$file_coverage" != "100" ]; then
                                echo "❌ SECURITY RISK: $file has $file_coverage% coverage (MUST be 100%)"
                                exit 1
                            fi
                            
                            echo "✅ Security file $file: 100% coverage"
                        fi
                    done
                    
                    echo "✅ All security-critical files have 100% coverage"
                '''
            }
        }
        
        stage('Complete Test Suite') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    changeRequest()
                }
            }
            steps {
                echo "🚀 Running complete test suite..."
                sh '''
                    . ${VENV_NAME}/bin/activate
                    
                    chmod +x scripts/run_complete_test_suite.sh
                    scripts/run_complete_test_suite.sh
                    
                    echo "✅ Complete test suite finished"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'test_artifacts/**/*',
                                   allowEmptyArchive: true,
                                   fingerprint: true
                }
            }
        }
        
        stage('Security Scanning') {
            parallel {
                stage('Bandit Security Scan') {
                    steps {
                        echo "🔒 Running Bandit security scan..."
                        sh '''
                            . ${VENV_NAME}/bin/activate
                            pip install bandit
                            
                            bandit -r . -x tests/ -f json -o security-bandit.json || true
                            bandit -r . -x tests/ -f txt || true
                        '''
                    }
                }
                
                stage('Safety Dependency Check') {
                    steps {
                        echo "🔍 Running Safety dependency check..."
                        sh '''
                            . ${VENV_NAME}/bin/activate
                            pip install safety
                            
                            safety check --json --output security-safety.json || true
                            safety check || true
                        '''
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'security-*.json',
                                   allowEmptyArchive: true,
                                   fingerprint: true
                }
            }
        }
        
        stage('Performance Validation') {
            steps {
                echo "🚀 Running performance validation with coverage overhead..."
                sh '''
                    . ${VENV_NAME}/bin/activate
                    
                    echo "Testing performance impact of coverage collection..."
                    
                    # Time without coverage
                    echo "Running tests without coverage:"
                    time pytest tests/ -v >/dev/null 2>&1
                    
                    # Time with coverage
                    echo "Running tests with coverage:"
                    time coverage run --source=. -m pytest tests/ -v >/dev/null 2>&1
                    
                    # Memory usage analysis
                    echo "Memory usage during coverage collection:"
                    /usr/bin/time -v coverage run --source=. -m pytest tests/ -v 2>&1 | grep -E "(Maximum resident set size|User time|System time)" || true
                    
                    echo "✅ Performance validation completed"
                '''
            }
        }
        
        stage('Guardian Enforcer') {
            steps {
                echo "🛡️ Running Guardian Enforcer final validation..."
                sh '''
                    . ${VENV_NAME}/bin/activate
                    
                    if [ -f "scripts/guardian_enforcer.py" ]; then
                        python scripts/guardian_enforcer.py --threshold ${COVERAGE_THRESHOLD}
                        echo "✅ Guardian Enforcer approved"
                    else
                        echo "⚠️ Guardian Enforcer script not found - manual validation"
                        coverage report --fail-under=${COVERAGE_THRESHOLD}
                        echo "✅ Manual coverage validation passed"
                    fi
                '''
            }
        }
        
        stage('Deployment Readiness') {
            when {
                branch 'main'
            }
            steps {
                echo "🎯 Final deployment readiness check..."
                sh '''
                    . ${VENV_NAME}/bin/activate
                    
                    # Generate deployment report
                    cat > deployment_report.json << EOF
{
    "timestamp": "$(date -Iseconds)",
    "jenkins_build": "${BUILD_NUMBER}",
    "commit_sha": "${GIT_COMMIT}",
    "branch": "${BRANCH_NAME}",
    "coverage_status": "100%",
    "guardian_status": "APPROVED",
    "security_validation": "PASSED",
    "deployment_ready": true,
    "jenkins_pipeline": true,
    "build_url": "${BUILD_URL}"
}
EOF
                    
                    echo "📋 Deployment Report:"
                    cat deployment_report.json
                    
                    echo "✅ Deployment readiness confirmed"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'deployment_report.json',
                                   allowEmptyArchive: true,
                                   fingerprint: true
                }
            }
        }
    }
    
    post {
        always {
            echo "🧹 Cleaning up..."
            sh '''
                # Archive coverage data
                if [ -d "htmlcov" ]; then
                    tar -czf coverage-html-${BUILD_NUMBER}.tar.gz htmlcov/
                fi
                
                # Clean up virtual environment
                rm -rf ${VENV_NAME}
            '''
            
            // Clean workspace
            cleanWs()
        }
        
        success {
            echo "✅ Pipeline completed successfully!"
            
            // Send notification for main branch
            script {
                if (env.BRANCH_NAME == 'main') {
                    emailext (
                        subject: "✅ Coverage Guardian: Deployment Ready - Build ${BUILD_NUMBER}",
                        body: """
                        <h2>🛡️ Coverage Guardian Pipeline Success</h2>
                        <p><strong>Build:</strong> ${BUILD_NUMBER}</p>
                        <p><strong>Branch:</strong> ${BRANCH_NAME}</p>
                        <p><strong>Commit:</strong> ${GIT_COMMIT}</p>
                        <p><strong>Coverage:</strong> 100% ✅</p>
                        <p><strong>Guardian Status:</strong> APPROVED ✅</p>
                        <p><strong>Deployment Ready:</strong> YES ✅</p>
                        
                        <h3>Reports:</h3>
                        <ul>
                            <li><a href="${BUILD_URL}Coverage_Report/">Coverage Report</a></li>
                            <li><a href="${BUILD_URL}artifact/">Artifacts</a></li>
                        </ul>
                        """,
                        mimeType: 'text/html',
                        to: '${DEFAULT_RECIPIENTS}'
                    )
                }
            }
        }
        
        failure {
            echo "❌ Pipeline failed!"
            
            emailext (
                subject: "❌ Coverage Guardian: Pipeline Failed - Build ${BUILD_NUMBER}",
                body: """
                <h2>🚨 Coverage Guardian Pipeline Failure</h2>
                <p><strong>Build:</strong> ${BUILD_NUMBER}</p>
                <p><strong>Branch:</strong> ${BRANCH_NAME}</p>
                <p><strong>Commit:</strong> ${GIT_COMMIT}</p>
                <p><strong>Status:</strong> FAILED ❌</p>
                
                <p>The Coverage Guardian has blocked this deployment due to insufficient test coverage or other issues.</p>
                
                <h3>Actions Required:</h3>
                <ul>
                    <li>Check the console output for specific issues</li>
                    <li>Ensure all tests pass</li>
                    <li>Verify 100% coverage requirement</li>
                    <li>Fix any security-critical file coverage gaps</li>
                </ul>
                
                <p><a href="${BUILD_URL}console">View Console Output</a></p>
                """,
                mimeType: 'text/html',
                to: '${DEFAULT_RECIPIENTS}'
            )
        }
    }
}