#!/usr/bin/env python3
"""
Security Infrastructure Validation Script
Validates that all security testing infrastructure components are properly set up
"""
import os
import sys
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple
import configparser


class SecurityInfrastructureValidator:
    """Validates security testing infrastructure"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.successes = []
        self.root_dir = Path.cwd()
    
    def log_success(self, message: str):
        """Log a successful validation"""
        print(f"✅ {message}")
        self.successes.append(message)
    
    def log_warning(self, message: str):
        """Log a warning"""
        print(f"⚠️  {message}")
        self.warnings.append(message)
    
    def log_error(self, message: str):
        """Log an error"""
        print(f"❌ {message}")
        self.errors.append(message)
    
    def validate_security_requirements(self) -> bool:
        """Validate security-requirements.txt file"""
        print("\n🔍 Validating security requirements...")
        
        req_file = self.root_dir / "security-requirements.txt"
        if not req_file.exists():
            self.log_error("security-requirements.txt not found")
            return False
        
        content = req_file.read_text()
        required_packages = [
            'bandit', 'safety', 'cryptography', 'hypothesis'
        ]
        
        missing_packages = []
        for package in required_packages:
            if package not in content:
                missing_packages.append(package)
        
        if missing_packages:
            self.log_error(f"Missing required packages: {missing_packages}")
            return False
        
        self.log_success("Security requirements file is valid")
        return True
    
    def validate_bandit_config(self) -> bool:
        """Validate bandit.yml configuration"""
        print("\n🔍 Validating Bandit configuration...")
        
        config_file = self.root_dir / "bandit.yml"
        if not config_file.exists():
            self.log_error("bandit.yml not found")
            return False
        
        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)
            
            if not isinstance(config, dict):
                self.log_error("bandit.yml is not valid YAML")
                return False
            
            # Check for required sections
            if 'tests' not in config:
                self.log_warning("bandit.yml missing 'tests' section")
            if 'skips' not in config:
                self.log_warning("bandit.yml missing 'skips' section")
            
            self.log_success("Bandit configuration is valid")
            return True
        
        except yaml.YAMLError as e:
            self.log_error(f"Invalid YAML in bandit.yml: {e}")
            return False
    
    def validate_pytest_config(self) -> bool:
        """Validate pytest.ini configuration"""
        print("\n🔍 Validating pytest configuration...")
        
        config_file = self.root_dir / "pytest.ini"
        if not config_file.exists():
            self.log_error("pytest.ini not found")
            return False
        
        config = configparser.ConfigParser()
        try:
            config.read(config_file)
        except configparser.Error as e:
            self.log_error(f"Invalid pytest.ini format: {e}")
            return False
        
        if 'tool:pytest' not in config:
            self.log_error("pytest.ini missing [tool:pytest] section")
            return False
        
        pytest_section = config['tool:pytest']
        
        # Check for security markers
        if 'markers' not in pytest_section:
            self.log_error("pytest.ini missing markers configuration")
            return False
        
        markers = pytest_section['markers']
        required_markers = ['security:', 'crypto:', 'input_validation:', 'file_security:']
        
        for marker in required_markers:
            if marker not in markers:
                self.log_warning(f"Missing security marker: {marker}")
        
        # Check for 100% coverage requirement
        if 'addopts' in pytest_section:
            addopts = pytest_section['addopts']
            if '--cov-fail-under=100' not in addopts:
                self.log_warning("100% coverage requirement not found in addopts")
        
        self.log_success("Pytest configuration is valid")
        return True
    
    def validate_coverage_config(self) -> bool:
        """Validate .coveragerc configuration"""
        print("\n🔍 Validating coverage configuration...")
        
        config_file = self.root_dir / ".coveragerc"
        if not config_file.exists():
            self.log_error(".coveragerc not found")
            return False
        
        config = configparser.ConfigParser()
        try:
            config.read(config_file)
        except configparser.Error as e:
            self.log_error(f"Invalid .coveragerc format: {e}")
            return False
        
        # Check for 100% coverage requirement
        if 'report' in config:
            report_section = config['report']
            if 'fail_under' in report_section:
                fail_under = int(report_section['fail_under'])
                if fail_under != 100:
                    self.log_warning(f"Coverage fail_under is {fail_under}, should be 100")
                else:
                    self.log_success("100% coverage requirement configured")
            else:
                self.log_warning("No fail_under setting in coverage config")
        
        if 'run' in config:
            run_section = config['run']
            if 'branch' in run_section:
                branch = run_section.getboolean('branch')
                if not branch:
                    self.log_warning("Branch coverage is disabled")
                else:
                    self.log_success("Branch coverage is enabled")
        
        self.log_success("Coverage configuration is valid")
        return True
    
    def validate_test_structure(self) -> bool:
        """Validate test directory structure"""
        print("\n🔍 Validating test directory structure...")
        
        tests_dir = self.root_dir / "tests"
        if not tests_dir.exists():
            self.log_error("tests/ directory not found")
            return False
        
        security_dir = tests_dir / "security"
        if not security_dir.exists():
            self.log_error("tests/security/ directory not found")
            return False
        
        fixtures_dir = tests_dir / "fixtures"
        if not fixtures_dir.exists():
            self.log_error("tests/fixtures/ directory not found")
            return False
        
        # Check for required security test files
        required_files = [
            "test_crypto_security.py",
            "test_password_security.py",
            "test_file_security.py", 
            "test_input_validation.py",
            "test_attack_scenarios.py"
        ]
        
        missing_files = []
        for filename in required_files:
            test_file = security_dir / filename
            if not test_file.exists():
                missing_files.append(filename)
        
        if missing_files:
            self.log_error(f"Missing security test files: {missing_files}")
            return False
        
        # Check for fixture files
        fixture_files = ["secure_test_data.py", "attack_vectors.py"]
        missing_fixtures = []
        for filename in fixture_files:
            fixture_file = fixtures_dir / filename
            if not fixture_file.exists():
                missing_fixtures.append(filename)
        
        if missing_fixtures:
            self.log_error(f"Missing fixture files: {missing_fixtures}")
            return False
        
        self.log_success("Test directory structure is valid")
        return True
    
    def validate_security_pipeline(self) -> bool:
        """Validate security pipeline script"""
        print("\n🔍 Validating security pipeline script...")
        
        script_file = self.root_dir / "security-pipeline.sh"
        if not script_file.exists():
            self.log_error("security-pipeline.sh not found")
            return False
        
        # Check if executable
        if not os.access(script_file, os.X_OK):
            self.log_error("security-pipeline.sh is not executable")
            return False
        
        content = script_file.read_text()
        
        # Check shebang
        if not content.startswith("#!/bin/bash"):
            self.log_warning("security-pipeline.sh missing proper bash shebang")
        
        # Check for required functions
        required_functions = [
            "run_safety_scan",
            "run_bandit_scan",
            "run_security_tests",
            "generate_security_report"
        ]
        
        missing_functions = []
        for func in required_functions:
            if f"{func}()" not in content:
                missing_functions.append(func)
        
        if missing_functions:
            self.log_error(f"Missing pipeline functions: {missing_functions}")
            return False
        
        self.log_success("Security pipeline script is valid")
        return True
    
    def validate_file_contents(self) -> bool:
        """Validate key file contents have expected structure"""
        print("\n🔍 Validating file contents...")
        
        # Check security test files have proper structure
        security_dir = self.root_dir / "tests" / "security"
        
        for test_file in security_dir.glob("test_*.py"):
            content = test_file.read_text()
            
            if "import pytest" not in content:
                self.log_warning(f"{test_file.name} missing pytest import")
            
            if "def test_" not in content and "class Test" not in content:
                self.log_warning(f"{test_file.name} has no test functions or classes")
        
        # Check fixture files have proper structure
        fixtures_dir = self.root_dir / "tests" / "fixtures"
        
        for fixture_file in fixtures_dir.glob("*.py"):
            if fixture_file.name == "__init__.py":
                continue
            
            content = fixture_file.read_text()
            
            if "@pytest.fixture" not in content:
                self.log_warning(f"{fixture_file.name} may be missing fixture decorators")
        
        self.log_success("File contents validation completed")
        return True
    
    def test_basic_imports(self) -> bool:
        """Test that basic imports work"""
        print("\n🔍 Testing basic imports...")
        
        try:
            # Test pytest import
            import pytest
            self.log_success("pytest import successful")
        except ImportError:
            self.log_error("pytest not available")
            return False
        
        try:
            # Test basic test collection
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/test_security_infrastructure.py",
                "--collect-only", "--quiet"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.log_success("Infrastructure tests can be collected")
            else:
                self.log_warning(f"Infrastructure test collection issues: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.log_error("Test collection timed out")
            return False
        except Exception as e:
            self.log_warning(f"Could not test collection: {e}")
        
        return True
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report"""
        return {
            'successes': self.successes,
            'warnings': self.warnings,
            'errors': self.errors,
            'total_checks': len(self.successes) + len(self.warnings) + len(self.errors),
            'success_rate': len(self.successes) / (len(self.successes) + len(self.warnings) + len(self.errors)) if (self.successes or self.warnings or self.errors) else 0
        }
    
    def run_validation(self) -> bool:
        """Run complete validation suite"""
        print("🔒 Security Infrastructure Validation")
        print("=" * 50)
        
        validations = [
            self.validate_security_requirements,
            self.validate_bandit_config,
            self.validate_pytest_config,
            self.validate_coverage_config,
            self.validate_test_structure,
            self.validate_security_pipeline,
            self.validate_file_contents,
            self.test_basic_imports,
        ]
        
        all_passed = True
        for validation in validations:
            try:
                if not validation():
                    all_passed = False
            except Exception as e:
                self.log_error(f"Validation failed with exception: {e}")
                all_passed = False
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 VALIDATION SUMMARY")
        print("=" * 50)
        
        report = self.generate_report()
        
        print(f"✅ Successes: {len(self.successes)}")
        print(f"⚠️  Warnings:  {len(self.warnings)}")
        print(f"❌ Errors:    {len(self.errors)}")
        print(f"📈 Success Rate: {report['success_rate']:.1%}")
        
        if self.errors:
            print("\n❌ ERRORS TO ADDRESS:")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS TO CONSIDER:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        # Final status
        if not self.errors:
            print(f"\n🎉 SECURITY INFRASTRUCTURE VALIDATION PASSED!")
            print("All critical components are properly configured.")
            if self.warnings:
                print("Address warnings for optimal security testing.")
        else:
            print(f"\n🚫 SECURITY INFRASTRUCTURE VALIDATION FAILED!")
            print("Address all errors before proceeding.")
        
        return all_passed and len(self.errors) == 0


def main():
    """Main validation entry point"""
    validator = SecurityInfrastructureValidator()
    success = validator.run_validation()
    
    # Save report
    report = validator.generate_report()
    with open('security-infrastructure-validation.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())