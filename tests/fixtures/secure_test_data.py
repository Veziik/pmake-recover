"""
Secure test data fixtures for security testing
Provides known-safe test data for various security scenarios
"""
import pytest
import secrets
import string
import os
import tempfile
import hashlib
from typing import Dict, List, Any, Generator
from contextlib import contextmanager


@pytest.fixture
def secure_random_generator():
    """Fixture providing cryptographically secure random generator"""
    return secrets.SystemRandom()


@pytest.fixture
def secure_test_passwords(secure_random_generator) -> List[str]:
    """Generate secure test passwords with known entropy characteristics"""
    passwords = []
    # Different complexity levels for testing
    for length in [8, 16, 32, 64]:
        for _ in range(3):  # 3 passwords per length
            password = ''.join(
                secure_random_generator.choices(
                    string.ascii_letters + string.digits + string.punctuation,
                    k=length
                )
            )
            passwords.append(password)
    return passwords


@pytest.fixture
def weak_test_passwords() -> List[str]:
    """Known weak passwords for negative testing"""
    return [
        "password",
        "123456",
        "password123",
        "admin",
        "qwerty",
        "letmein",
        "welcome",
        "monkey",
        "dragon",
        "123456789",
        "password1",
        "abc123",
        "",  # empty password
        "a",  # single character
        "12",  # too short numeric
        "aaa",  # repeated characters
        "123",  # sequential
    ]


@pytest.fixture
def secure_file_permissions() -> List[int]:
    """Secure file permission modes for testing"""
    return [
        0o600,  # Owner read/write only
        0o400,  # Owner read only
        0o200,  # Owner write only
        0o000,  # No permissions
    ]


@pytest.fixture
def insecure_file_permissions() -> List[int]:
    """Insecure file permission modes for negative testing"""
    return [
        0o666,  # World readable/writable
        0o644,  # World readable
        0o755,  # World readable/executable
        0o777,  # World everything
        0o622,  # Group/other writable
    ]


@pytest.fixture
def secure_encryption_keys(secure_random_generator) -> Dict[str, bytes]:
    """Generate secure encryption keys for testing"""
    return {
        'aes_128': secure_random_generator.randbytes(16),
        'aes_256': secure_random_generator.randbytes(32),
        'hmac_key': secure_random_generator.randbytes(32),
        'salt': secure_random_generator.randbytes(16),
    }


@pytest.fixture
def secure_test_data() -> Dict[str, Any]:
    """Comprehensive secure test data collection"""
    return {
        'entropy_sources': [
            os.urandom(32),
            secrets.token_bytes(32),
            hashlib.pbkdf2_hmac('sha256', b'password', b'salt', 100000),
        ],
        'safe_filenames': [
            'test_file.txt',
            'secure_data.enc',
            'backup_2024.bak',
            'config.json',
            'log_file.log',
        ],
        'safe_paths': [
            '/tmp/secure_test',
            './test_data',
            'files/test',
            'backup/secure',
        ],
        'safe_inputs': [
            'normal_username',
            'test@example.com',
            'SecurePassword123!',
            'valid_filename.txt',
            'safe content here',
        ],
    }


@pytest.fixture
@contextmanager
def secure_temp_directory():
    """Create a secure temporary directory for testing"""
    temp_dir = tempfile.mkdtemp(prefix='pmake_security_test_')
    os.chmod(temp_dir, 0o700)  # Owner only
    try:
        yield temp_dir
    finally:
        # Secure cleanup
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                # Overwrite file before deletion (basic secure delete)
                if os.path.exists(file_path):
                    with open(file_path, 'wb') as f:
                        f.write(os.urandom(os.path.getsize(file_path)))
                    os.remove(file_path)
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(temp_dir)


@pytest.fixture
def cryptographic_test_vectors():
    """Known cryptographic test vectors for validation"""
    return {
        'sha256_vectors': [
            {
                'input': b'abc',
                'expected': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
            },
            {
                'input': b'',
                'expected': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
            },
        ],
        'pbkdf2_vectors': [
            {
                'password': b'password',
                'salt': b'salt',
                'iterations': 1,
                'expected_length': 32,
            },
        ],
        'aes_vectors': [
            {
                'key': bytes.fromhex('2b7e151628aed2a6abf7158809cf4f3c'),
                'plaintext': bytes.fromhex('6bc1bee22e409f96e93d7e117393172a'),
                'iv': bytes.fromhex('000102030405060708090a0b0c0d0e0f'),
            },
        ],
    }


@pytest.fixture
def memory_leak_detector():
    """Fixture to detect memory leaks during security tests"""
    import gc
    import psutil
    
    def get_memory_usage():
        process = psutil.Process()
        return process.memory_info().rss
    
    initial_memory = get_memory_usage()
    gc.collect()
    
    yield
    
    gc.collect()
    final_memory = get_memory_usage()
    
    # Allow for some variance in memory usage
    memory_growth = final_memory - initial_memory
    max_allowed_growth = 10 * 1024 * 1024  # 10MB
    
    assert memory_growth < max_allowed_growth, \
        f"Memory leak detected: {memory_growth} bytes growth"


@pytest.fixture
def timing_attack_detector():
    """Fixture to detect timing attack vulnerabilities"""
    import time
    import statistics
    
    timings = []
    
    def measure_time(func, *args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        timings.append(end - start)
        return result
    
    yield measure_time
    
    if len(timings) > 1:
        # Check for timing consistency (constant-time operations)
        variance = statistics.variance(timings)
        mean_time = statistics.mean(timings)
        
        # Coefficient of variation should be low for constant-time ops
        cv = (variance ** 0.5) / mean_time if mean_time > 0 else 0
        
        # Allow some variance due to system noise
        max_cv = 0.1  # 10% coefficient of variation
        
        assert cv < max_cv, \
            f"Timing attack vulnerability detected: CV={cv:.3f}, timings={timings}"


@pytest.fixture
def entropy_validator():
    """Fixture to validate entropy of generated data"""
    import math
    from collections import Counter
    
    def validate_entropy(data: bytes, min_entropy_per_byte: float = 7.0):
        """
        Validate entropy of byte data
        min_entropy_per_byte: minimum Shannon entropy per byte (max is 8.0)
        """
        if len(data) == 0:
            return False
        
        # Calculate Shannon entropy
        counts = Counter(data)
        entropy = 0.0
        
        for count in counts.values():
            probability = count / len(data)
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy >= min_entropy_per_byte
    
    return validate_entropy


@pytest.fixture
def secure_comparison():
    """Fixture providing secure comparison functions"""
    import hmac
    
    def constant_time_compare(a: bytes, b: bytes) -> bool:
        """Constant-time comparison to prevent timing attacks"""
        return hmac.compare_digest(a, b)
    
    def secure_string_compare(a: str, b: str) -> bool:
        """Secure string comparison"""
        return hmac.compare_digest(a.encode('utf-8'), b.encode('utf-8'))
    
    return {
        'bytes': constant_time_compare,
        'strings': secure_string_compare,
    }


@pytest.fixture(scope="session")
def security_test_configuration():
    """Session-wide security test configuration"""
    return {
        'max_test_time': 30.0,  # Maximum time per test (seconds)
        'entropy_threshold': 7.0,  # Minimum entropy per byte
        'memory_limit': 100 * 1024 * 1024,  # 100MB memory limit
        'secure_temp_prefix': 'pmake_sec_',
        'min_password_length': 8,
        'max_password_length': 128,
        'allowed_crypto_algorithms': ['AES-256-GCM', 'ChaCha20-Poly1305'],
        'forbidden_algorithms': ['DES', 'RC4', 'MD5', 'SHA1'],
    }


@pytest.fixture
def attack_pattern_detector():
    """Fixture to detect known attack patterns in data"""
    import re
    
    attack_patterns = {
        'sql_injection': [
            r"('\s*(or|and)\s*')",
            r"(union\s+select)",
            r"(drop\s+table)",
            r"(insert\s+into)",
            r"(delete\s+from)",
        ],
        'xss': [
            r"<script[^>]*>",
            r"javascript:",
            r"on\w+\s*=",
            r"data:\s*text/html",
        ],
        'command_injection': [
            r"[;&|`$()]",
            r"(rm\s+-rf)",
            r"(\|\s*nc\s+)",
            r"(wget|curl)\s+",
        ],
        'path_traversal': [
            r"\.\./",
            r"\.\.\\",
            r"/etc/passwd",
            r"C:\\Windows",
        ],
    }
    
    def detect_attack(data: str) -> Dict[str, List[str]]:
        """Detect attack patterns in input data"""
        detected = {}
        for attack_type, patterns in attack_patterns.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, data, re.IGNORECASE):
                    matches.append(pattern)
            if matches:
                detected[attack_type] = matches
        return detected
    
    return detect_attack