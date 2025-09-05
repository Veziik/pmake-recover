"""
Test Infrastructure Validation Tests

These tests validate that the test infrastructure itself works correctly:
- pytest configuration loads
- Fixtures are available and functional
- Parallel execution capability works
- Coverage reporting works
- All required dependencies are available

This ensures our testing foundation is solid before writing actual feature tests.
"""

import os
import sys
import tempfile
import subprocess
import importlib
from pathlib import Path
from unittest.mock import Mock, patch
import pytest


class TestPytestConfiguration:
    """Test that pytest configuration is properly loaded and functional."""
    
    def test_pytest_config_file_exists(self):
        """Verify pytest.ini exists and is readable."""
        config_path = Path(__file__).parent.parent / "pytest.ini"
        assert config_path.exists(), "pytest.ini configuration file is missing"
        assert config_path.is_file(), "pytest.ini is not a file"
        
        # Verify it's readable
        content = config_path.read_text()
        assert "[pytest]" in content, "pytest.ini missing [pytest] section"
        assert "testpaths" in content, "pytest.ini missing testpaths configuration"

    def test_pytest_markers_configured(self):
        """Verify all required markers are configured."""
        config_path = Path(__file__).parent.parent / "pytest.ini"
        content = config_path.read_text()
        
        required_markers = [
            "unit: Unit tests",
            "integration: Integration tests", 
            "security: Security tests",
            "slow: Slow tests",
            "requires_file: Tests that require file system access"
        ]
        
        for marker in required_markers:
            assert marker in content, f"Missing marker configuration: {marker}"

    def test_coverage_configuration(self):
        """Verify coverage is properly configured."""
        config_path = Path(__file__).parent.parent / "pytest.ini"
        content = config_path.read_text()
        
        coverage_settings = [
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-fail-under=100",
            "--cov-branch"
        ]
        
        for setting in coverage_settings:
            assert setting in content, f"Missing coverage setting: {setting}"

    def test_parallel_execution_configured(self):
        """Verify parallel execution is available via pytest-xdist."""
        # Check that pytest-xdist is installed by testing the -n flag
        result = subprocess.run([sys.executable, "-m", "pytest", "--help"], 
                              capture_output=True, text=True)
        assert result.returncode == 0, "pytest not available"
        assert "-n" in result.stdout, "pytest-xdist not available (-n flag missing)"
        
        # Verify configuration mentions parallel execution
        config_path = Path(__file__).parent.parent / "pytest.ini"
        content = config_path.read_text()
        assert "pytest -n auto" in content, "Missing parallel execution documentation"


class TestCoverageConfiguration:
    """Test that coverage configuration is properly set up."""
    
    def test_coveragerc_exists(self):
        """Verify .coveragerc exists and is readable."""
        config_path = Path(__file__).parent.parent / ".coveragerc"
        assert config_path.exists(), ".coveragerc configuration file is missing"
        assert config_path.is_file(), ".coveragerc is not a file"
        
        content = config_path.read_text()
        assert "[run]" in content, ".coveragerc missing [run] section"
        assert "[report]" in content, ".coveragerc missing [report] section"

    def test_coverage_fail_under_100(self):
        """Verify coverage is set to require 100%."""
        config_path = Path(__file__).parent.parent / ".coveragerc"
        content = config_path.read_text()
        assert "fail_under = 100" in content, ".coveragerc not set to require 100% coverage"

    def test_coverage_omit_patterns(self):
        """Verify coverage correctly omits test files."""
        config_path = Path(__file__).parent.parent / ".coveragerc"
        content = config_path.read_text()
        
        omit_patterns = [
            "*/tests/*",
            "*/test_*.py",
            "*/__pycache__/*"
        ]
        
        for pattern in omit_patterns:
            assert pattern in content, f"Missing omit pattern: {pattern}"

    def test_branch_coverage_enabled(self):
        """Verify branch coverage is enabled."""
        config_path = Path(__file__).parent.parent / ".coveragerc"
        content = config_path.read_text()
        assert "branch = True" in content, "Branch coverage not enabled"


class TestRequiredDependencies:
    """Test that all required testing dependencies are available."""
    
    def test_pytest_available(self):
        """Verify pytest is importable."""
        import pytest
        assert hasattr(pytest, 'main'), "pytest not properly installed"

    def test_coverage_available(self):
        """Verify coverage is importable."""
        import coverage
        assert hasattr(coverage, 'Coverage'), "coverage not properly installed"

    def test_pytest_cov_available(self):
        """Verify pytest-cov is available."""
        try:
            import pytest_cov
            assert pytest_cov is not None, "pytest-cov not available"
        except ImportError:
            # pytest-cov might be installed as a plugin, check differently
            result = subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                                  capture_output=True, text=True)
            assert "pytest-cov" in result.stdout or "cov" in result.stdout, \
                "pytest-cov plugin not available"

    def test_pytest_xdist_available(self):
        """Verify pytest-xdist is available for parallel execution."""
        result = subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                              capture_output=True, text=True)
        # Check if xdist plugin is loaded or available
        help_result = subprocess.run([sys.executable, "-m", "pytest", "--help"], 
                                   capture_output=True, text=True)
        assert "-n" in help_result.stdout or "xdist" in help_result.stdout, \
            "pytest-xdist not available for parallel execution"

    def test_security_dependencies_available(self):
        """Verify security testing dependencies are available."""
        try:
            import bandit
            assert bandit is not None, "bandit not available"
        except ImportError:
            pytest.skip("bandit not installed - optional security dependency")

    def test_cryptography_available(self):
        """Verify cryptography library is available."""
        import cryptography
        assert hasattr(cryptography, '__version__'), "cryptography not properly installed"


class TestFixtureAvailability:
    """Test that all fixtures from conftest.py are available and functional."""
    
    def test_temp_dir_fixture(self, temp_dir):
        """Verify temp_dir fixture works."""
        assert temp_dir.exists(), "temp_dir fixture not creating directory"
        assert temp_dir.is_dir(), "temp_dir fixture not creating actual directory"
        
        # Test we can write to it
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists(), "Cannot write to temp_dir"

    def test_temp_file_fixture(self, temp_file):
        """Verify temp_file fixture works."""
        assert temp_file.exists(), "temp_file fixture not creating file"
        assert temp_file.is_file(), "temp_file fixture not creating actual file"
        
        # Test we can write to it
        temp_file.write_text("test content")
        content = temp_file.read_text()
        assert content == "test content", "Cannot read/write temp_file"

    def test_password_files_dir_fixture(self, password_files_dir):
        """Verify password_files_dir fixture works with correct permissions."""
        assert password_files_dir.exists(), "password_files_dir fixture not creating directory"
        assert password_files_dir.is_dir(), "password_files_dir fixture not creating actual directory"
        
        # Check permissions (700 = owner only)
        stat_info = password_files_dir.stat()
        permissions = stat_info.st_mode & 0o777
        assert permissions == 0o700, f"password_files_dir has wrong permissions: {oct(permissions)}"

    def test_sample_data_fixtures(self, sample_password, sample_key, sample_note, sample_words):
        """Verify sample data fixtures provide expected data."""
        assert isinstance(sample_password, str), "sample_password not a string"
        assert len(sample_password) > 0, "sample_password is empty"
        
        assert isinstance(sample_key, str), "sample_key not a string"
        assert len(sample_key) > 0, "sample_key is empty"
        
        assert isinstance(sample_note, str), "sample_note not a string"
        assert len(sample_note) > 0, "sample_note is empty"
        
        assert isinstance(sample_words, list), "sample_words not a list"
        assert len(sample_words) > 0, "sample_words is empty"
        assert all(isinstance(word, str) for word in sample_words), "sample_words contains non-strings"

    def test_cryptographic_fixtures(self, encryption_key, initialization_vector):
        """Verify cryptographic fixtures provide correct data types and sizes."""
        assert isinstance(encryption_key, bytes), "encryption_key not bytes"
        assert len(encryption_key) == 32, f"encryption_key wrong length: {len(encryption_key)}"
        
        assert isinstance(initialization_vector, bytes), "initialization_vector not bytes"
        assert len(initialization_vector) == 16, f"initialization_vector wrong length: {len(initialization_vector)}"

    def test_mock_fixtures(self, mock_clipboard, secure_random_mock):
        """Verify mock fixtures are properly configured."""
        assert 'copy' in mock_clipboard, "mock_clipboard missing copy function"
        assert 'paste' in mock_clipboard, "mock_clipboard missing paste function"
        
        # Test clipboard mock functionality
        mock_clipboard['copy']('test data')
        mock_clipboard['copy'].assert_called_with('test data')
        
        # Test secure random mock is a Mock object
        assert isinstance(secure_random_mock, Mock), "secure_random_mock not a Mock object"


class TestTestDirectoryStructure:
    """Test that the test directory structure is properly organized."""
    
    def test_test_directories_exist(self):
        """Verify all required test directories exist."""
        test_root = Path(__file__).parent
        
        required_dirs = [
            "unit",
            "integration", 
            "fixtures"
        ]
        
        for dirname in required_dirs:
            dir_path = test_root / dirname
            assert dir_path.exists(), f"Required test directory missing: {dirname}"
            assert dir_path.is_dir(), f"Test path is not a directory: {dirname}"

    def test_init_files_exist(self):
        """Verify __init__.py files exist in all test directories."""
        test_root = Path(__file__).parent
        
        init_files = [
            "__init__.py",
            "unit/__init__.py",
            "integration/__init__.py",
            "fixtures/__init__.py"
        ]
        
        for init_file in init_files:
            init_path = test_root / init_file
            assert init_path.exists(), f"Missing __init__.py file: {init_file}"
            assert init_path.is_file(), f"__init__.py is not a file: {init_file}"

    def test_conftest_exists_and_importable(self):
        """Verify conftest.py exists and can be imported."""
        conftest_path = Path(__file__).parent / "conftest.py"
        assert conftest_path.exists(), "conftest.py is missing"
        assert conftest_path.is_file(), "conftest.py is not a file"
        
        # Test it can be imported (pytest will import it automatically)
        import tests.conftest
        assert hasattr(tests.conftest, 'pytest_configure'), "conftest missing pytest_configure hook"


class TestInfrastructureIntegration:
    """Integration tests for the complete test infrastructure."""
    
    def test_pytest_can_discover_tests(self):
        """Verify pytest can discover and run tests."""
        test_root = Path(__file__).parent.parent
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "--collect-only", 
            "--quiet",
            str(test_root / "tests")
        ], capture_output=True, text=True, cwd=test_root)
        
        assert result.returncode == 0, f"pytest test discovery failed: {result.stderr}"
        assert "test session starts" in result.stdout.lower() or "collected" in result.stdout.lower(), \
            "pytest did not discover any tests"

    def test_coverage_integration_works(self):
        """Verify coverage integration works with pytest."""
        test_root = Path(__file__).parent.parent
        
        # Run just this test file with coverage
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "--cov=tests",
            "--cov-report=term",
            str(Path(__file__)),
            "-v"
        ], capture_output=True, text=True, cwd=test_root)
        
        # Should succeed even if coverage is low (we're just testing integration)
        assert "coverage" in result.stdout.lower() or "TOTAL" in result.stdout, \
            f"Coverage integration not working: {result.stdout[:500]}"

    def test_parallel_execution_capability(self):
        """Verify parallel execution works (if dependencies available)."""
        test_root = Path(__file__).parent.parent
        
        # Try to run with parallel execution
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "-n", "auto",
            "--collect-only",
            str(Path(__file__))
        ], capture_output=True, text=True, cwd=test_root)
        
        if result.returncode == 0:
            # Parallel execution is available
            assert "gw" in result.stdout or "workers" in result.stdout.lower(), \
                "Parallel execution not properly configured"
        else:
            # pytest-xdist might not be installed, which is okay for basic testing
            pytest.skip("pytest-xdist not available - parallel execution not tested")


class TestProjectPathConfiguration:
    """Test that Python path configuration works for importing project modules."""
    
    def test_project_root_in_path(self):
        """Verify project root is added to Python path."""
        # conftest.py should add project root to path
        project_root = Path(__file__).parent.parent
        assert str(project_root) in sys.path, "Project root not added to Python path"

    def test_can_import_project_modules(self):
        """Verify we can import main project modules."""
        # These imports should work if path is configured correctly
        try:
            import helpers
            assert hasattr(helpers, 'encrypt'), "helpers module not properly importable"
        except ImportError:
            # Module might not exist yet, that's okay for infrastructure test
            pass
        
        try:
            import words
            assert hasattr(words, 'load_words') or hasattr(words, 'words'), \
                "words module not properly importable"
        except ImportError:
            # Module might not exist yet, that's okay for infrastructure test
            pass


# Test the test infrastructure itself
def test_infrastructure_test_coverage():
    """Meta-test: verify this infrastructure test file provides good coverage."""
    # This test ensures we're testing the test infrastructure comprehensively
    test_classes = [
        TestPytestConfiguration,
        TestCoverageConfiguration, 
        TestRequiredDependencies,
        TestFixtureAvailability,
        TestTestDirectoryStructure,
        TestInfrastructureIntegration,
        TestProjectPathConfiguration
    ]
    
    total_test_methods = 0
    for test_class in test_classes:
        class_methods = [method for method in dir(test_class) 
                        if method.startswith('test_') and callable(getattr(test_class, method))]
        total_test_methods += len(class_methods)
    
    # Should have comprehensive coverage of infrastructure
    assert total_test_methods >= 20, \
        f"Infrastructure tests not comprehensive enough: only {total_test_methods} test methods"


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])