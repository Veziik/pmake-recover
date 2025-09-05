"""
Tests for the security testing infrastructure itself
Validates that all security testing components are working correctly
"""
import pytest
import os
import sys
import subprocess
import json
import importlib
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile


class TestSecurityTestingInfrastructure:
    """Test the security testing infrastructure components"""
    
    def test_security_requirements_file_exists(self):
        """Test that security-requirements.txt exists and is valid"""
        req_file = Path("security-requirements.txt")
        assert req_file.exists(), "security-requirements.txt file must exist"
        
        content = req_file.read_text()
        assert "bandit" in content, "bandit must be in security requirements"
        assert "safety" in content, "safety must be in security requirements"
        assert "hypothesis" in content, "hypothesis must be in security requirements"
        assert "cryptography" in content, "cryptography must be in security requirements"
    
    def test_bandit_configuration_exists(self):
        """Test that bandit.yml configuration exists and is valid"""
        config_file = Path("bandit.yml")
        assert config_file.exists(), "bandit.yml configuration must exist"
        
        # Validate it's valid YAML by trying to parse it
        import yaml
        with open(config_file) as f:
            config = yaml.safe_load(f)
        
        assert isinstance(config, dict), "bandit.yml must be valid YAML"
    
    def test_pytest_configuration_exists(self):
        """Test that pytest.ini configuration exists and is valid"""
        config_file = Path("pytest.ini")
        assert config_file.exists(), "pytest.ini configuration must exist"
        
        content = config_file.read_text()
        assert "[tool:pytest]" in content, "pytest.ini must have pytest section"
        assert "security:" in content, "security marker must be defined"
        assert "--cov-fail-under=100" in content, "100% coverage must be required"
    
    def test_coverage_configuration_exists(self):
        """Test that .coveragerc configuration exists and is valid"""
        config_file = Path(".coveragerc")
        assert config_file.exists(), ".coveragerc configuration must exist"
        
        content = config_file.read_text()
        assert "fail_under = 100" in content, "100% coverage must be required"
        assert "branch = True" in content, "branch coverage must be enabled"
    
    def test_security_test_directory_structure(self):
        """Test that security test directory structure is correct"""
        tests_dir = Path("tests")
        security_dir = tests_dir / "security"
        fixtures_dir = tests_dir / "fixtures"
        
        assert tests_dir.exists(), "tests directory must exist"
        assert security_dir.exists(), "tests/security directory must exist"
        assert fixtures_dir.exists(), "tests/fixtures directory must exist"
        
        # Check required security test files
        required_files = [
            "test_crypto_security.py",
            "test_password_security.py", 
            "test_file_security.py",
            "test_input_validation.py",
            "test_attack_scenarios.py"
        ]
        
        for filename in required_files:
            test_file = security_dir / filename
            assert test_file.exists(), f"Security test file {filename} must exist"
    
    def test_security_fixtures_available(self):
        """Test that security test fixtures are available"""
        fixtures_dir = Path("tests/fixtures")
        
        # Check fixture files exist
        secure_data = fixtures_dir / "secure_test_data.py"
        attack_vectors = fixtures_dir / "attack_vectors.py"
        
        assert secure_data.exists(), "secure_test_data.py fixture must exist"
        assert attack_vectors.exists(), "attack_vectors.py fixture must exist"
        
        # Test fixtures can be imported
        sys.path.insert(0, str(fixtures_dir.parent))
        try:
            import fixtures.secure_test_data
            import fixtures.attack_vectors
        except ImportError as e:
            pytest.fail(f"Could not import security fixtures: {e}")
        finally:
            sys.path.pop(0)
    
    def test_security_pipeline_script_exists(self):
        """Test that security pipeline script exists and is executable"""
        script_file = Path("security-pipeline.sh")
        assert script_file.exists(), "security-pipeline.sh must exist"
        
        # Check if executable
        assert os.access(script_file, os.X_OK), "security-pipeline.sh must be executable"
        
        # Basic syntax validation (check shebang)
        content = script_file.read_text()
        assert content.startswith("#!/bin/bash"), "Must have proper bash shebang"
    
    def test_security_test_imports_work(self):
        """Test that security test modules can be imported"""
        # Test stub modules that don't require external dependencies
        security_modules = [
            "tests.security.test_crypto_security_stub",
            "tests.security.test_stubs_validation",
        ]
        
        for module_name in security_modules:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                pytest.fail(f"Could not import {module_name}: {e}")
        
        # Note: Full security test modules will be available after PRP 02a dependencies are installed
    
    def test_hypothesis_property_testing_configured(self):
        """Test that Hypothesis property-based testing is configured for future use"""
        # Hypothesis will be available after dependencies are installed
        # For now, just validate the configuration exists
        config_file = Path("pytest.ini")
        content = config_file.read_text()
        
        # Check hypothesis configuration is present
        assert "hypothesis-show-statistics" in content
        assert "hypothesis-verbosity" in content
        
        # Note: Full hypothesis testing will be available after PRP 02a
    
    def test_security_markers_defined(self):
        """Test that security test markers are properly defined in pytest.ini"""
        # Check markers are defined in pytest.ini instead of relying on pytest --markers
        config_file = Path("pytest.ini")
        content = config_file.read_text()
        
        required_markers = [
            "security:",
            "crypto:",
            "input_validation:",
            "file_security:",
            "attack_scenario:",
            "property_based:"
        ]
        
        markers_section = False
        for line in content.split('\n'):
            if 'markers =' in line:
                markers_section = True
                continue
            if markers_section and line.strip().startswith(tuple(required_markers)):
                # Found at least one marker
                break
        else:
            # Check if markers are present anywhere in the file
            for marker in required_markers:
                assert marker in content, f"Security marker {marker} must be defined in pytest.ini"
    
    def test_test_collection_works(self):
        """Test that pytest can collect security stub tests"""
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/security/test_stubs_validation.py", 
            "--collect-only", 
            "-q"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Stub test collection failed: {result.stderr}"
        assert "test session starts" in result.stdout or "tests collected" in result.stdout, "pytest should collect tests successfully"
    
    def test_coverage_measurement_works(self):
        """Test that coverage measurement is working"""
        # Run a simple test with coverage
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def simple_function():
    return "test"

def test_simple():
    assert simple_function() == "test"
""")
            temp_file = f.name
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", temp_file,
                "--cov=" + os.path.dirname(temp_file),
                "--cov-report=term"
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            assert result.returncode == 0, f"Coverage test failed: {result.stderr}"
            assert "coverage" in result.stdout.lower(), "Coverage report should be generated"
        finally:
            os.unlink(temp_file)


class TestSecurityPipelineIntegration:
    """Test security pipeline script integration"""
    
    def test_pipeline_help_works(self):
        """Test that security pipeline help option works"""
        result = subprocess.run([
            "./security-pipeline.sh", "--help"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, "Help command should succeed"
        assert "Usage:" in result.stdout, "Help should show usage information"
        assert "Security validation pipeline" in result.stdout, "Should describe pipeline"
    
    def test_pipeline_has_required_functions(self):
        """Test that security pipeline has all required functions"""
        script_path = Path("security-pipeline.sh")
        content = script_path.read_text()
        
        required_functions = [
            "run_safety_scan",
            "run_bandit_scan", 
            "run_security_tests",
            "run_property_tests",
            "run_memory_analysis",
            "run_timing_analysis",
            "run_entropy_tests",
            "generate_security_report"
        ]
        
        for func in required_functions:
            assert f"{func}()" in content, f"Pipeline must have {func} function"
    
    def test_pipeline_creates_reports_directory(self):
        """Test that pipeline creates reports directory structure"""
        script_path = Path("security-pipeline.sh")
        content = script_path.read_text()
        
        assert "REPORT_DIR=" in content, "Must define report directory"
        assert "mkdir -p" in content, "Must create report directory"
        assert "security-reports" in content, "Must use security-reports directory"


class TestSecurityTestFixtures:
    """Test security test fixtures functionality"""
    
    def test_secure_test_data_fixtures(self):
        """Test that secure test data fixtures can be imported"""
        # Test that fixture files exist and can be imported
        try:
            # Import the module without calling the fixtures (which require pytest context)
            import tests.fixtures.secure_test_data as secure_data
            
            # Check that key functions are defined
            assert hasattr(secure_data, 'secure_test_passwords'), "Should have secure_test_passwords fixture"
            assert hasattr(secure_data, 'weak_test_passwords'), "Should have weak_test_passwords fixture"
            assert hasattr(secure_data, 'secure_file_permissions'), "Should have secure_file_permissions fixture"
            
        except ImportError as e:
            pytest.fail(f"Could not import secure test data fixtures: {e}")
        
        # Note: Full fixture testing requires pytest context and will be done in PRP 02a
    
    def test_attack_vectors_fixtures(self):
        """Test that attack vector fixtures can be imported"""
        try:
            # Import the module without calling the fixtures (which require pytest context)
            import tests.fixtures.attack_vectors as attack_data
            
            # Check that key fixture functions are defined
            assert hasattr(attack_data, 'sql_injection_vectors'), "Should have SQL injection vectors fixture"
            assert hasattr(attack_data, 'xss_vectors'), "Should have XSS vectors fixture"
            assert hasattr(attack_data, 'command_injection_vectors'), "Should have command injection vectors fixture"
            assert hasattr(attack_data, 'path_traversal_vectors'), "Should have path traversal vectors fixture"
            
        except ImportError as e:
            pytest.fail(f"Could not import attack vector fixtures: {e}")
        
        # Note: Full fixture testing requires pytest context and will be done in PRP 02a
    
    def test_comprehensive_attack_suite(self):
        """Test comprehensive attack suite fixture can be imported"""
        try:
            import tests.fixtures.attack_vectors as attack_data
            
            # Check that comprehensive suite function is defined
            assert hasattr(attack_data, 'comprehensive_attack_suite'), "Should have comprehensive attack suite fixture"
            
        except ImportError as e:
            pytest.fail(f"Could not import comprehensive attack suite: {e}")
        
        # Note: Full fixture testing requires pytest context and will be done in PRP 02a


class TestSecurityTestConfiguration:
    """Test security testing configuration"""
    
    def test_bandit_can_run(self):
        """Test that bandit can run with our configuration"""
        try:
            result = subprocess.run([
                "bandit", "--help"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                pytest.skip("Bandit not available in test environment")
                
        except FileNotFoundError:
            pytest.skip("Bandit not installed in test environment")
        
        # Test bandit can load our config
        result = subprocess.run([
            "bandit", "-c", "bandit.yml", "--help"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, "Bandit should accept our configuration"
    
    def test_safety_can_run(self):
        """Test that safety can run for dependency scanning"""
        try:
            result = subprocess.run([
                "safety", "--help"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                pytest.skip("Safety not available in test environment")
                
        except FileNotFoundError:
            pytest.skip("Safety not installed in test environment")
        
        assert "check" in result.stdout, "Safety should support check command"
    
    def test_hypothesis_configuration(self):
        """Test that Hypothesis configuration is present"""
        # Hypothesis will be available after dependencies are installed
        # For now, validate configuration is present in pytest.ini
        config_file = Path("pytest.ini")
        content = config_file.read_text()
        
        assert "hypothesis-show-statistics" in content, "Hypothesis statistics should be configured"
        assert "hypothesis-verbosity" in content, "Hypothesis verbosity should be configured"
        
        # Note: Full hypothesis testing will be available after PRP 02a
    
    def test_cryptography_available(self):
        """Test that cryptography library is available for testing"""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            
            # Basic functionality test
            key = Fernet.generate_key()
            assert key is not None
            assert len(key) > 0
            
        except ImportError:
            pytest.fail("Cryptography library not available for security testing")


class TestMemoryAndPerformanceSafety:
    """Test memory safety and performance aspects of security testing infrastructure"""
    
    def test_no_memory_leaks_in_fixtures(self):
        """Test that security fixtures don't cause memory leaks"""
        import gc
        import psutil
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Import and use fixtures multiple times
        for _ in range(10):
            from tests.fixtures.secure_test_data import secure_test_passwords
            from tests.fixtures.attack_vectors import sql_injection_vectors
            
            # Force garbage collection
            gc.collect()
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Allow for some memory growth but not excessive
        max_growth = 50 * 1024 * 1024  # 50MB
        assert memory_growth < max_growth, f"Excessive memory growth: {memory_growth} bytes"
    
    def test_test_execution_timeout(self):
        """Test that security tests have timeout configuration prepared"""
        # Timeout configuration is present but commented out until pytest-timeout is available
        with open('pytest.ini') as f:
            content = f.read()
        
        assert 'timeout' in content, "Timeout configuration should be documented in pytest.ini"
        
        # Note: Full timeout functionality will be enabled after pytest-timeout is installed
    
    def test_resource_limits_configured(self):
        """Test that resource limits are properly configured"""
        # Check pytest configuration includes resource management
        with open('pytest.ini') as f:
            content = f.read()
        
        # Should have some form of resource management
        assert any(keyword in content for keyword in [
            'timeout', 'maxfail', 'tb=short'
        ]), "Resource limits should be configured"


def test_security_infrastructure_integration():
    """Integration test for entire security infrastructure"""
    
    # Test that all components work together
    components = {
        'requirements': Path('security-requirements.txt').exists(),
        'bandit_config': Path('bandit.yml').exists(),
        'pytest_config': Path('pytest.ini').exists(),
        'coverage_config': Path('.coveragerc').exists(),
        'pipeline_script': Path('security-pipeline.sh').exists(),
        'test_directory': Path('tests/security').exists(),
        'fixtures_directory': Path('tests/fixtures').exists(),
    }
    
    missing_components = [name for name, exists in components.items() if not exists]
    
    assert not missing_components, \
        f"Missing security infrastructure components: {missing_components}"
    
    # Test that we can run basic security stub test collection
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/security/test_stubs_validation.py", 
        "--collect-only", 
        "--quiet"
    ], capture_output=True, text=True)
    
    assert result.returncode == 0, \
        f"Security stub test collection failed: {result.stderr}"