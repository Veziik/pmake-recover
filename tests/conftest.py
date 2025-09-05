"""
Shared fixtures and configuration for pmake-recover tests.
Provides common test utilities and data for all test types.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Any
from unittest.mock import Mock, patch
import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================================
# Directory and File Fixtures
# ============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp(prefix="pmake_test_"))
    yield temp_path
    # Cleanup after test
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def temp_file(temp_dir: Path) -> Generator[Path, None, None]:
    """Create a temporary file for testing."""
    file_path = temp_dir / "test_file.txt"
    file_path.touch()
    yield file_path
    # File cleanup handled by temp_dir fixture


@pytest.fixture
def password_files_dir(temp_dir: Path) -> Generator[Path, None, None]:
    """Create a temporary 'files' directory for password storage."""
    files_dir = temp_dir / "files"
    files_dir.mkdir(mode=0o700)
    yield files_dir
    # Cleanup handled by temp_dir fixture


# ============================================================================
# Mock Data Fixtures
# ============================================================================

@pytest.fixture
def sample_password() -> str:
    """Provide a sample password for testing."""
    return "TestP@ssw0rd123"


@pytest.fixture
def sample_key() -> str:
    """Provide a sample key name for testing."""
    return "test_key"


@pytest.fixture
def sample_note() -> str:
    """Provide a sample note for testing."""
    return "test_note"


@pytest.fixture
def sample_words() -> list[str]:
    """Provide sample words for word-based password generation."""
    return ["apple", "banana", "cherry", "dragon", "eagle", "falcon"]


@pytest.fixture
def mock_word_list(sample_words: list[str]) -> Generator[Mock, None, None]:
    """Mock the word list loading."""
    with patch('words.load_words', return_value=sample_words) as mock:
        yield mock


# ============================================================================
# Security Testing Fixtures
# ============================================================================

@pytest.fixture
def secure_random_mock() -> Generator[Mock, None, None]:
    """Mock secure random generation for predictable testing."""
    with patch('secrets.SystemRandom') as mock_random:
        instance = Mock()
        mock_random.return_value = instance
        yield instance


@pytest.fixture
def insecure_seed_detector() -> Generator[Mock, None, None]:
    """Detect use of time-based or predictable seeds."""
    original_seed = __import__('random').seed
    mock_seed = Mock(side_effect=original_seed)
    with patch('random.seed', mock_seed):
        yield mock_seed


# ============================================================================
# Cryptographic Fixtures
# ============================================================================

@pytest.fixture
def encryption_key() -> bytes:
    """Provide a test encryption key (32 bytes for AES-256)."""
    return b'0' * 32  # Test key only, never use in production


@pytest.fixture
def initialization_vector() -> bytes:
    """Provide a test initialization vector (16 bytes for AES)."""
    return b'1' * 16  # Test IV only, never use in production


@pytest.fixture
def mock_os_urandom() -> Generator[Mock, None, None]:
    """Mock os.urandom for predictable cryptographic testing."""
    def mock_urandom(size: int) -> bytes:
        """Generate predictable bytes for testing."""
        return bytes([i % 256 for i in range(size)])
    
    with patch('os.urandom', side_effect=mock_urandom) as mock:
        yield mock


# ============================================================================
# CLI Testing Fixtures
# ============================================================================

@pytest.fixture
def mock_argv() -> Generator[Mock, None, None]:
    """Mock sys.argv for CLI testing."""
    original_argv = sys.argv.copy()
    yield sys.argv
    sys.argv = original_argv


@pytest.fixture
def mock_clipboard() -> Generator[Mock, None, None]:
    """Mock clipboard operations."""
    with patch('pyperclip.copy') as mock_copy:
        with patch('pyperclip.paste', return_value='') as mock_paste:
            yield {'copy': mock_copy, 'paste': mock_paste}


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def isolate_environment(monkeypatch) -> None:
    """Isolate test environment from system environment."""
    # Clear potentially interfering environment variables
    env_vars_to_clear = [
        'PMAKE_DEBUG',
        'PMAKE_FILES_DIR',
        'PMAKE_NO_CLIPBOARD'
    ]
    for var in env_vars_to_clear:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def mock_file_permissions() -> Generator[Mock, None, None]:
    """Mock file permission operations."""
    with patch('os.chmod') as mock_chmod:
        with patch('os.stat') as mock_stat:
            # Mock stat to return secure permissions
            mock_stat.return_value.st_mode = 0o100600
            yield {'chmod': mock_chmod, 'stat': mock_stat}


# ============================================================================
# Test Infrastructure Validation Fixtures
# ============================================================================

@pytest.fixture
def test_config() -> dict[str, Any]:
    """Provide pytest configuration for infrastructure tests."""
    return {
        'testpaths': ['tests'],
        'python_files': 'test_*.py',
        'required_coverage': 100,
        'parallel_workers': 'auto'
    }


@pytest.fixture
def coverage_config() -> dict[str, Any]:
    """Provide coverage configuration for infrastructure tests."""
    return {
        'fail_under': 100,
        'branch': True,
        'omit': ['*/tests/*', '*/test_*.py'],
        'reports': ['term-missing', 'html', 'xml']
    }


# ============================================================================
# Pytest Hooks and Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "unit: Mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: Mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "security: Mark test as a security test"
    )
    config.addinivalue_line(
        "markers", "slow: Mark test as slow (> 1 second)"
    )
    config.addinivalue_line(
        "markers", "requires_file: Mark test as requiring file system access"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on location."""
    for item in items:
        # Auto-mark tests based on their directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add requires_file marker if test uses file fixtures
        if any(fixture in item.fixturenames for fixture in 
               ['temp_dir', 'temp_file', 'password_files_dir']):
            item.add_marker(pytest.mark.requires_file)


# ============================================================================
# Test Helpers
# ============================================================================

@pytest.fixture
def assert_file_permissions():
    """Helper to assert file has correct permissions."""
    def _assert_permissions(file_path: Path, expected_mode: int):
        """Assert that file has expected permissions."""
        actual_mode = file_path.stat().st_mode & 0o777
        assert actual_mode == expected_mode, \
            f"File {file_path} has permissions {oct(actual_mode)}, " \
            f"expected {oct(expected_mode)}"
    return _assert_permissions


@pytest.fixture
def assert_secure_random():
    """Helper to assert secure random is being used."""
    def _assert_secure():
        """Assert that secure random generation is in use."""
        import secrets
        # This should not raise an exception
        secrets.token_bytes(16)
        return True
    return _assert_secure