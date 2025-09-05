#!/usr/bin/env python3
"""
Comprehensive Tests for helpers.py - Cryptographic Helper Functions
100% Coverage Required - Security-Critical Module
"""
import pytest
import os
import sys
import tempfile
import secrets
from unittest.mock import patch, mock_open

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import modules under test
import helpers


class TestEncryptionFunctions:
    """Test encryption and decryption functions with 100% coverage"""
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test that encrypt/decrypt is a proper roundtrip"""
        original_data = "test password 123"
        password = "encryption_key"
        
        # Encrypt the data
        encrypted = helpers.encrypt_data(original_data, password)
        
        # Verify encrypted data is different from original
        assert encrypted != original_data
        assert isinstance(encrypted, str)
        assert len(encrypted) > len(original_data)
        
        # Decrypt the data
        decrypted = helpers.decrypt_data(encrypted, password)
        
        # Verify roundtrip works
        assert decrypted == original_data
    
    def test_encrypt_different_passwords_produce_different_results(self):
        """Test that different passwords produce different encrypted results"""
        data = "same data"
        password1 = "password1"
        password2 = "password2"
        
        encrypted1 = helpers.encrypt_data(data, password1)
        encrypted2 = helpers.encrypt_data(data, password2)
        
        assert encrypted1 != encrypted2
    
    def test_encrypt_same_data_different_results(self):
        """Test that encrypting same data twice produces different results (due to random IV)"""
        data = "test data"
        password = "test password"
        
        encrypted1 = helpers.encrypt_data(data, password)
        encrypted2 = helpers.encrypt_data(data, password)
        
        # Should be different due to random IV
        assert encrypted1 != encrypted2
        
        # But both should decrypt to same original data
        decrypted1 = helpers.decrypt_data(encrypted1, password)
        decrypted2 = helpers.decrypt_data(encrypted2, password)
        
        assert decrypted1 == data
        assert decrypted2 == data
    
    def test_decrypt_with_wrong_password(self):
        """Test decryption with wrong password raises exception"""
        data = "secret data"
        correct_password = "correct"
        wrong_password = "wrong"
        
        encrypted = helpers.encrypt_data(data, correct_password)
        
        with pytest.raises(Exception):
            helpers.decrypt_data(encrypted, wrong_password)
    
    def test_decrypt_invalid_data(self):
        """Test decryption with invalid encrypted data"""
        password = "test password"
        
        # Test with completely invalid data
        with pytest.raises(Exception):
            helpers.decrypt_data("not encrypted data", password)
        
        # Test with invalid base64
        with pytest.raises(Exception):
            helpers.decrypt_data("invalid!base64!", password)
    
    def test_encrypt_empty_data(self):
        """Test encryption of empty data"""
        data = ""
        password = "test password"
        
        encrypted = helpers.encrypt_data(data, password)
        decrypted = helpers.decrypt_data(encrypted, password)
        
        assert decrypted == data
    
    def test_encrypt_empty_password(self):
        """Test encryption with empty password"""
        data = "test data"
        password = ""
        
        # Should still work (though not secure)
        encrypted = helpers.encrypt_data(data, password)
        decrypted = helpers.decrypt_data(encrypted, password)
        
        assert decrypted == data
    
    def test_encrypt_long_data(self):
        """Test encryption of long data"""
        data = "x" * 10000  # Long string
        password = "test password"
        
        encrypted = helpers.encrypt_data(data, password)
        decrypted = helpers.decrypt_data(encrypted, password)
        
        assert decrypted == data
    
    def test_encrypt_unicode_data(self):
        """Test encryption of unicode data"""
        data = "Test with ñ, é, 中文, 🔐, and other unicode"
        password = "unicode password ñ"
        
        encrypted = helpers.encrypt_data(data, password)
        decrypted = helpers.decrypt_data(encrypted, password)
        
        assert decrypted == data
    
    def test_encryption_produces_base64_output(self):
        """Test that encryption produces valid base64 output"""
        data = "test data"
        password = "test password"
        
        encrypted = helpers.encrypt_data(data, password)
        
        # Should be valid base64
        import base64
        try:
            base64.b64decode(encrypted)
            base64_valid = True
        except Exception:
            base64_valid = False
        
        assert base64_valid


class TestPaddingFunctions:
    """Test padding functions with 100% coverage"""
    
    def test_pad_data_basic(self):
        """Test basic padding functionality"""
        data = "test"
        padded = helpers.pad_data(data, 10)
        
        assert len(padded) == 10
        assert padded.startswith(data)
        
        # The padding should be random characters
        padding = padded[len(data):]
        assert len(padding) == 6
    
    def test_pad_data_exact_length(self):
        """Test padding when data is exact target length"""
        data = "exactten!!"  # 10 characters
        padded = helpers.pad_data(data, 10)
        
        assert padded == data
        assert len(padded) == 10
    
    def test_pad_data_longer_than_target(self):
        """Test padding when data is longer than target"""
        data = "this is longer than target"
        padded = helpers.pad_data(data, 10)
        
        # Should return original data unchanged
        assert padded == data
        assert len(padded) > 10
    
    def test_pad_data_zero_length(self):
        """Test padding with zero target length"""
        data = "test"
        padded = helpers.pad_data(data, 0)
        
        # Should return original data
        assert padded == data
    
    def test_pad_data_negative_length(self):
        """Test padding with negative target length"""
        data = "test"
        padded = helpers.pad_data(data, -5)
        
        # Should return original data
        assert padded == data
    
    def test_pad_data_empty_string(self):
        """Test padding empty string"""
        data = ""
        padded = helpers.pad_data(data, 10)
        
        assert len(padded) == 10
        # Should be all padding characters
        assert len(padded.strip()) >= 0  # All padding chars
    
    def test_pad_data_large_padding(self):
        """Test padding with large target length"""
        data = "small"
        padded = helpers.pad_data(data, 1000)
        
        assert len(padded) == 1000
        assert padded.startswith(data)
        
        # Verify padding is added
        padding = padded[len(data):]
        assert len(padding) == 995
    
    def test_padding_character_randomness(self):
        """Test that padding characters are random"""
        data = "test"
        target_length = 20
        
        # Generate multiple padded strings
        padded_strings = []
        for _ in range(10):
            padded = helpers.pad_data(data, target_length)
            padded_strings.append(padded)
        
        # All should start with original data
        for padded in padded_strings:
            assert padded.startswith(data)
            assert len(padded) == target_length
        
        # Padding portions should be different (with high probability)
        padding_portions = [s[len(data):] for s in padded_strings]
        unique_paddings = set(padding_portions)
        
        # Should have multiple unique padding sequences
        assert len(unique_paddings) > 1
    
    def test_padding_character_types(self):
        """Test the types of characters used in padding"""
        data = "test"
        padded = helpers.pad_data(data, 100)
        padding = padded[len(data):]
        
        # Check that padding contains expected character types
        # Based on the code, it should use random characters
        assert len(padding) > 0
        
        # All characters should be printable or at least valid
        for char in padding:
            assert isinstance(char, str)
            assert len(char) == 1


class TestKeyDerivation:
    """Test key derivation functions if they exist"""
    
    def test_key_derivation_consistency(self):
        """Test that key derivation is consistent for same inputs"""
        # This tests the internal key derivation used in encryption
        password = "test password"
        data = "test data"
        
        # Encrypt twice with same password
        encrypted1 = helpers.encrypt_data(data, password)
        encrypted2 = helpers.encrypt_data(data, password)
        
        # Decrypt both
        decrypted1 = helpers.decrypt_data(encrypted1, password)
        decrypted2 = helpers.decrypt_data(encrypted2, password)
        
        # Both should decrypt correctly (proving key derivation works)
        assert decrypted1 == data
        assert decrypted2 == data
    
    def test_different_passwords_different_keys(self):
        """Test that different passwords result in different encryption"""
        data = "same data for both"
        password1 = "password1"
        password2 = "password2"
        
        encrypted1 = helpers.encrypt_data(data, password1)
        encrypted2 = helpers.encrypt_data(data, password2)
        
        # Should be different due to different keys
        assert encrypted1 != encrypted2
        
        # Each should decrypt with correct password
        assert helpers.decrypt_data(encrypted1, password1) == data
        assert helpers.decrypt_data(encrypted2, password2) == data
        
        # Cross-decryption should fail
        with pytest.raises(Exception):
            helpers.decrypt_data(encrypted1, password2)
        
        with pytest.raises(Exception):
            helpers.decrypt_data(encrypted2, password1)


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_malformed_encrypted_data(self):
        """Test various forms of malformed encrypted data"""
        password = "test"
        
        malformed_data = [
            "not base64 at all!",
            "dmFsaWRiYXNlNjQ=",  # Valid base64 but wrong format
            "",  # Empty string
            "a",  # Too short
            "validbase64butnotencrypteddata==",
        ]
        
        for bad_data in malformed_data:
            with pytest.raises(Exception):
                helpers.decrypt_data(bad_data, password)
    
    def test_none_inputs(self):
        """Test handling of None inputs"""
        with pytest.raises((TypeError, AttributeError)):
            helpers.encrypt_data(None, "password")
        
        with pytest.raises((TypeError, AttributeError)):
            helpers.encrypt_data("data", None)
        
        with pytest.raises((TypeError, AttributeError)):
            helpers.decrypt_data(None, "password")
        
        with pytest.raises((TypeError, AttributeError)):
            helpers.pad_data(None, 10)


class TestSecurityProperties:
    """Test security properties of the helper functions"""
    
    def test_iv_randomness(self):
        """Test that initialization vectors are random"""
        data = "test data"
        password = "test password"
        
        # Generate multiple encrypted versions
        encrypted_versions = []
        for _ in range(10):
            encrypted = helpers.encrypt_data(data, password)
            encrypted_versions.append(encrypted)
        
        # All should be different (due to random IV)
        unique_versions = set(encrypted_versions)
        assert len(unique_versions) == len(encrypted_versions)
    
    def test_padding_unpredictability(self):
        """Test that padding is unpredictable"""
        data = "test"
        
        # Generate multiple padded versions
        padded_versions = []
        for _ in range(20):
            padded = helpers.pad_data(data, 50)
            padded_versions.append(padded)
        
        # All should start with original data
        for padded in padded_versions:
            assert padded.startswith(data)
        
        # Padding portions should be different
        padding_portions = [p[len(data):] for p in padded_versions]
        unique_paddings = set(padding_portions)
        
        # Should have many unique padding sequences
        assert len(unique_paddings) > len(padding_portions) * 0.8  # At least 80% unique
    
    def test_encryption_indistinguishability(self):
        """Test that encrypted data looks random/indistinguishable"""
        data1 = "aaaaaaaaaa"  # Repetitive data
        data2 = "bbbbbbbbbb"  # Different repetitive data
        password = "test"
        
        encrypted1 = helpers.encrypt_data(data1, password)
        encrypted2 = helpers.encrypt_data(data2, password)
        
        # Encrypted versions should be different
        assert encrypted1 != encrypted2
        
        # Should not reveal patterns from original data
        # (This is a basic check - real cryptanalysis would be more complex)
        assert "aaaa" not in encrypted1
        assert "bbbb" not in encrypted2


class TestModuleStructure:
    """Test module structure and imports"""
    
    def test_required_functions_exist(self):
        """Test that required functions are available in helpers module"""
        assert hasattr(helpers, 'encrypt_data')
        assert hasattr(helpers, 'decrypt_data') 
        assert hasattr(helpers, 'pad_data')
        
        assert callable(helpers.encrypt_data)
        assert callable(helpers.decrypt_data)
        assert callable(helpers.pad_data)
    
    def test_function_signatures(self):
        """Test that functions have expected signatures"""
        import inspect
        
        # Test encrypt_data signature
        sig = inspect.signature(helpers.encrypt_data)
        assert len(sig.parameters) == 2  # data, password
        
        # Test decrypt_data signature  
        sig = inspect.signature(helpers.decrypt_data)
        assert len(sig.parameters) == 2  # encrypted_data, password
        
        # Test pad_data signature
        sig = inspect.signature(helpers.pad_data)
        assert len(sig.parameters) == 2  # data, target_length


class TestCompatibility:
    """Test compatibility with different Python versions and environments"""
    
    def test_string_encoding_handling(self):
        """Test proper handling of string encoding"""
        # Test with various string types
        test_strings = [
            "ascii string",
            "unicode string with ñ and é",
            "emoji test 🔐🔑",
            "mixed: ascii + unicode ñ + emoji 🚀"
        ]
        
        password = "test password"
        
        for test_string in test_strings:
            encrypted = helpers.encrypt_data(test_string, password)
            decrypted = helpers.decrypt_data(encrypted, password)
            assert decrypted == test_string
    
    def test_binary_data_handling(self):
        """Test handling of binary-like data"""
        # Test with strings that contain various characters
        binary_like_strings = [
            "\x00\x01\x02\x03",  # Null bytes and control characters
            "\n\r\t",  # Whitespace characters
            "\\x41\\x42\\x43",  # Escaped hex representation
        ]
        
        password = "binary test"
        
        for data in binary_like_strings:
            try:
                encrypted = helpers.encrypt_data(data, password)
                decrypted = helpers.decrypt_data(encrypted, password)
                assert decrypted == data
            except Exception as e:
                # Some binary data might not be handled - that's okay
                # as long as it fails gracefully
                assert isinstance(e, (UnicodeError, ValueError, TypeError))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--cov=helpers", "--cov-report=term-missing"])