#!/usr/bin/env python3
"""
CI/CD Environment Detection and Adaptation Script
Automatically detects and configures for different CI/CD platforms
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CIEnvironmentDetector:
    """Detects and adapts to different CI/CD environments"""
    
    def __init__(self):
        self.environment_info = {}
        self.detected_ci = None
        self.capabilities = {}
        
    def detect_ci_environment(self) -> Dict[str, any]:
        """Detect the current CI/CD environment"""
        ci_indicators = {
            'github_actions': {
                'vars': ['GITHUB_ACTIONS', 'GITHUB_WORKFLOW'],
                'name': 'GitHub Actions'
            },
            'gitlab_ci': {
                'vars': ['GITLAB_CI', 'CI_PIPELINE_ID'],
                'name': 'GitLab CI/CD'
            },
            'azure_devops': {
                'vars': ['AZURE_HTTP_USER_AGENT', 'TF_BUILD'],
                'name': 'Azure DevOps'
            },
            'jenkins': {
                'vars': ['JENKINS_URL', 'BUILD_NUMBER'],
                'name': 'Jenkins'
            },
            'circleci': {
                'vars': ['CIRCLECI', 'CIRCLE_WORKFLOW_ID'],
                'name': 'CircleCI'
            },
            'travis': {
                'vars': ['TRAVIS', 'TRAVIS_BUILD_NUMBER'],
                'name': 'Travis CI'
            },
            'appveyor': {
                'vars': ['APPVEYOR', 'APPVEYOR_BUILD_ID'],
                'name': 'AppVeyor'
            },
            'bamboo': {
                'vars': ['bamboo_buildKey', 'bamboo_buildNumber'],
                'name': 'Atlassian Bamboo'
            },
            'teamcity': {
                'vars': ['TEAMCITY_VERSION', 'BUILD_NUMBER'],
                'name': 'TeamCity'
            }
        }
        
        detected = []
        
        for ci_type, config in ci_indicators.items():
            if any(os.getenv(var) for var in config['vars']):
                detected.append({
                    'type': ci_type,
                    'name': config['name'],
                    'confidence': 'high' if all(os.getenv(var) for var in config['vars']) else 'medium'
                })
        
        # Check for generic CI indicators
        if not detected and (os.getenv('CI') or os.getenv('CONTINUOUS_INTEGRATION')):
            detected.append({
                'type': 'generic_ci',
                'name': 'Generic CI Environment',
                'confidence': 'low'
            })
        
        self.detected_ci = detected[0] if detected else None
        return {
            'detected_environments': detected,
            'primary': self.detected_ci,
            'is_ci': bool(detected)
        }
    
    def get_environment_capabilities(self) -> Dict[str, any]:
        """Get capabilities of the current CI environment"""
        capabilities = {
            'artifact_upload': False,
            'parallel_jobs': False,
            'docker_support': False,
            'coverage_reporting': False,
            'notification_support': False,
            'deployment_support': False,
            'secret_management': False
        }
        
        if not self.detected_ci:
            return capabilities
        
        ci_type = self.detected_ci['type']
        
        # Define capabilities for each CI platform
        capability_map = {
            'github_actions': {
                'artifact_upload': True,
                'parallel_jobs': True,
                'docker_support': True,
                'coverage_reporting': True,
                'notification_support': True,
                'deployment_support': True,
                'secret_management': True
            },
            'gitlab_ci': {
                'artifact_upload': True,
                'parallel_jobs': True,
                'docker_support': True,
                'coverage_reporting': True,
                'notification_support': True,
                'deployment_support': True,
                'secret_management': True
            },
            'azure_devops': {
                'artifact_upload': True,
                'parallel_jobs': True,
                'docker_support': True,
                'coverage_reporting': True,
                'notification_support': True,
                'deployment_support': True,
                'secret_management': True
            },
            'jenkins': {
                'artifact_upload': True,
                'parallel_jobs': True,
                'docker_support': True,
                'coverage_reporting': True,
                'notification_support': True,
                'deployment_support': True,
                'secret_management': True
            },
            'generic_ci': {
                'artifact_upload': False,
                'parallel_jobs': False,
                'docker_support': False,
                'coverage_reporting': True,
                'notification_support': False,
                'deployment_support': False,
                'secret_management': False
            }
        }
        
        self.capabilities = capability_map.get(ci_type, capabilities)
        return self.capabilities
    
    def get_build_info(self) -> Dict[str, any]:
        """Extract build information from CI environment"""
        build_info = {
            'build_id': None,
            'build_number': None,
            'commit_sha': None,
            'branch': None,
            'pull_request': None,
            'repository': None,
            'build_url': None
        }
        
        if not self.detected_ci:
            return build_info
        
        ci_type = self.detected_ci['type']
        
        # GitHub Actions
        if ci_type == 'github_actions':
            build_info.update({
                'build_id': os.getenv('GITHUB_RUN_ID'),
                'build_number': os.getenv('GITHUB_RUN_NUMBER'),
                'commit_sha': os.getenv('GITHUB_SHA'),
                'branch': os.getenv('GITHUB_REF_NAME'),
                'pull_request': os.getenv('GITHUB_EVENT_NAME') == 'pull_request',
                'repository': os.getenv('GITHUB_REPOSITORY'),
                'build_url': f"https://github.com/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/{os.getenv('GITHUB_RUN_ID')}"
            })
        
        # GitLab CI
        elif ci_type == 'gitlab_ci':
            build_info.update({
                'build_id': os.getenv('CI_PIPELINE_ID'),
                'build_number': os.getenv('CI_PIPELINE_IID'),
                'commit_sha': os.getenv('CI_COMMIT_SHA'),
                'branch': os.getenv('CI_COMMIT_REF_NAME'),
                'pull_request': os.getenv('CI_MERGE_REQUEST_ID') is not None,
                'repository': os.getenv('CI_PROJECT_PATH'),
                'build_url': os.getenv('CI_PIPELINE_URL')
            })
        
        # Azure DevOps
        elif ci_type == 'azure_devops':
            build_info.update({
                'build_id': os.getenv('BUILD_BUILDID'),
                'build_number': os.getenv('BUILD_BUILDNUMBER'),
                'commit_sha': os.getenv('BUILD_SOURCEVERSION'),
                'branch': os.getenv('BUILD_SOURCEBRANCH', '').replace('refs/heads/', ''),
                'pull_request': os.getenv('BUILD_REASON') == 'PullRequest',
                'repository': os.getenv('BUILD_REPOSITORY_NAME'),
                'build_url': f"{os.getenv('SYSTEM_TEAMFOUNDATIONSERVERURI', '')}{os.getenv('SYSTEM_TEAMPROJECT', '')}/_build/results?buildId={os.getenv('BUILD_BUILDID', '')}"
            })
        
        # Jenkins
        elif ci_type == 'jenkins':
            build_info.update({
                'build_id': os.getenv('BUILD_ID'),
                'build_number': os.getenv('BUILD_NUMBER'),
                'commit_sha': os.getenv('GIT_COMMIT'),
                'branch': os.getenv('BRANCH_NAME'),
                'pull_request': os.getenv('CHANGE_ID') is not None,
                'repository': os.getenv('JOB_NAME'),
                'build_url': os.getenv('BUILD_URL')
            })
        
        return build_info
    
    def configure_coverage_reporting(self) -> Dict[str, any]:
        """Configure coverage reporting for the detected CI environment"""
        if not self.detected_ci:
            return {'enabled': False, 'formats': ['console']}
        
        ci_type = self.detected_ci['type']
        
        coverage_config = {
            'enabled': True,
            'formats': ['console', 'html', 'xml', 'json'],
            'upload_artifacts': self.capabilities.get('artifact_upload', False),
            'codecov_upload': ci_type in ['github_actions', 'gitlab_ci', 'azure_devops'],
            'coverage_comment': ci_type in ['github_actions', 'gitlab_ci'] and self.get_build_info().get('pull_request', False)
        }
        
        return coverage_config
    
    def generate_ci_commands(self) -> Dict[str, List[str]]:
        """Generate CI-specific commands for coverage validation"""
        commands = {
            'setup': [],
            'test': [],
            'coverage': [],
            'validation': [],
            'artifact_upload': []
        }
        
        if not self.detected_ci:
            # Generic commands for local development
            commands.update({
                'setup': [
                    'python -m pip install --upgrade pip',
                    'pip install pytest coverage pytest-cov',
                    'pip install -r requirements.txt'
                ],
                'test': [
                    'coverage run --source=. -m pytest tests/ -v'
                ],
                'coverage': [
                    'coverage report --show-missing',
                    'coverage html',
                    'coverage xml',
                    'coverage json'
                ],
                'validation': [
                    'coverage report --fail-under=100'
                ]
            })
            return commands
        
        ci_type = self.detected_ci['type']
        
        # GitHub Actions specific
        if ci_type == 'github_actions':
            commands['artifact_upload'] = [
                'echo "COVERAGE_ARTIFACTS=htmlcov/" >> $GITHUB_OUTPUT',
                'echo "COVERAGE_XML=coverage.xml" >> $GITHUB_OUTPUT'
            ]
        
        # GitLab CI specific
        elif ci_type == 'gitlab_ci':
            commands['artifact_upload'] = [
                'cp -r htmlcov/ coverage_artifacts/',
                'cp coverage.xml coverage.json coverage_artifacts/'
            ]
        
        # Azure DevOps specific
        elif ci_type == 'azure_devops':
            commands['artifact_upload'] = [
                'echo "##vso[task.addattachment type=Distributedtask.Core.Summary;name=Coverage Report;]htmlcov/index.html"'
            ]
        
        # Jenkins specific
        elif ci_type == 'jenkins':
            commands['artifact_upload'] = [
                'tar -czf coverage-html-${BUILD_NUMBER}.tar.gz htmlcov/',
                'cp coverage.xml coverage.json .'
            ]
        
        return commands
    
    def create_environment_report(self) -> Dict[str, any]:
        """Create comprehensive environment report"""
        ci_info = self.detect_ci_environment()
        capabilities = self.get_environment_capabilities()
        build_info = self.get_build_info()
        coverage_config = self.configure_coverage_reporting()
        commands = self.generate_ci_commands()
        
        report = {
            'timestamp': str(subprocess.run(['date', '-Iseconds'], 
                                          capture_output=True, text=True).stdout.strip()),
            'ci_environment': ci_info,
            'capabilities': capabilities,
            'build_info': build_info,
            'coverage_configuration': coverage_config,
            'recommended_commands': commands,
            'python_version': sys.version,
            'platform': sys.platform
        }
        
        return report


def main():
    """Main execution function"""
    detector = CIEnvironmentDetector()
    
    # Generate comprehensive environment report
    report = detector.create_environment_report()
    
    # Output as JSON for consumption by other scripts
    print(json.dumps(report, indent=2))
    
    # Save to file for CI artifacts
    with open('ci_environment_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary to stderr for logging
    ci_info = report['ci_environment']
    if ci_info['primary']:
        print(f"✅ Detected CI Environment: {ci_info['primary']['name']}", file=sys.stderr)
        print(f"🔧 Coverage reporting configured for: {ci_info['primary']['type']}", file=sys.stderr)
    else:
        print("ℹ️  No CI environment detected - using local development configuration", file=sys.stderr)
    
    return 0 if ci_info['is_ci'] else 1


if __name__ == '__main__':
    sys.exit(main())