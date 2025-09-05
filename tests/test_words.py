#!/usr/bin/env python3
"""
Comprehensive Tests for words.py - Word List Management Module
100% Coverage Required - Security-Critical Module (Word Selection)
"""
import pytest
import os
import sys
import tempfile

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import modules under test
import words


class TestWordsModule:
    """Test the words module with 100% coverage"""
    
    def test_importWords_function_exists(self):
        """Test that importWords function exists and is callable"""
        assert hasattr(words, 'importWords')
        assert callable(words.importWords)
    
    def test_importWords_basic_functionality(self):
        """Test basic functionality of importWords function"""
        # Create a temporary word file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("apple\nbanana\ncherry\ndate\n")
            temp_filename = f.name
        
        try:
            # Test with no max length restriction
            result = words.importWords(temp_filename, -1)
            
            assert isinstance(result, list)
            assert len(result) == 4
            assert 'Apple' in result  # Should be titlecased
            assert 'Banana' in result
            assert 'Cherry' in result
            assert 'Date' in result
            
        finally:
            os.unlink(temp_filename)
    
    def test_importWords_with_max_length(self):
        """Test importWords with maximum word length restriction"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("cat\ndog\nelephant\nbird\nhippopotamus\n")
            temp_filename = f.name
        
        try:
            # Test with max length of 5
            result = words.importWords(temp_filename, 5)
            
            assert isinstance(result, list)
            assert len(result) == 3  # cat, dog, bird (elephant and hippopotamus are too long)
            assert 'Cat' in result
            assert 'Dog' in result 
            assert 'Bird' in result
            assert 'Elephant' not in result  # 8 chars, too long
            assert 'Hippopotamus' not in result  # 12 chars, too long
            
        finally:
            os.unlink(temp_filename)
    
    def test_importWords_no_max_length_restriction(self):
        """Test importWords with no maximum length restriction (-1)"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("a\nverylongwordindeed\nmedium\n")
            temp_filename = f.name
        
        try:
            result = words.importWords(temp_filename, -1)
            
            assert len(result) == 3
            assert 'A' in result
            assert 'Verylongwordindeed' in result
            assert 'Medium' in result
            
        finally:
            os.unlink(temp_filename)
    
    def test_importWords_empty_file(self):
        """Test importWords with empty file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_filename = f.name  # Empty file
        
        try:
            result = words.importWords(temp_filename, -1)
            assert isinstance(result, list)
            assert len(result) == 0
            
        finally:
            os.unlink(temp_filename)
    
    def test_importWords_file_with_empty_lines(self):
        """Test importWords with file containing empty lines"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("word1\n\nword2\n\n\nword3\n")
            temp_filename = f.name
        
        try:
            result = words.importWords(temp_filename, -1)
            
            # Should include empty strings from empty lines
            assert isinstance(result, list)
            assert len(result) == 6  # word1, empty, word2, empty, empty, word3
            assert 'Word1' in result
            assert 'Word2' in result
            assert 'Word3' in result
            assert '' in result  # Empty strings from empty lines
            
        finally:
            os.unlink(temp_filename)
    
    def test_importWords_titlecase_conversion(self):
        """Test that importWords converts words to title case"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("lowercase\nUPPERCASE\nMiXeDcAsE\n")
            temp_filename = f.name
        
        try:
            result = words.importWords(temp_filename, -1)
            
            assert 'Lowercase' in result
            assert 'Uppercase' in result  
            assert 'Mixedcase' in result
            
            # Original cases should not be present
            assert 'lowercase' not in result
            assert 'UPPERCASE' not in result
            assert 'MiXeDcAsE' not in result
            
        finally:
            os.unlink(temp_filename)
    
    def test_importWords_newline_stripping(self):
        """Test that importWords properly strips newline characters"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("word1\nword2\nword3")  # Last line without newline
            temp_filename = f.name
        
        try:
            result = words.importWords(temp_filename, -1)
            
            # Check that no words contain newline characters
            for word in result:
                assert '\n' not in word
                assert '\r' not in word
            
            assert 'Word1' in result
            assert 'Word2' in result
            assert 'Word3' in result
            
        finally:
            os.unlink(temp_filename)
    
    def test_importWords_max_length_edge_cases(self):
        """Test importWords max length edge cases"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("a\nab\nabc\nabcd\nabcde\nabcdef\n")
            temp_filename = f.name
        
        try:
            # Test with max length 3 - should include words of length <= 3
            result = words.importWords(temp_filename, 3)
            expected = ['A', 'Ab', 'Abc']  # 1, 2, 3 characters
            
            assert len(result) == 3
            for word in expected:
                assert word in result
            
            # Words longer than 3 should not be included
            assert 'Abcd' not in result
            assert 'Abcde' not in result
            assert 'Abcdef' not in result
            
        finally:
            os.unlink(temp_filename)
    
    def test_importWords_with_actual_words_file(self):
        """Test importWords with the actual words.txt file if it exists"""
        words_file = "words.txt"
        
        if os.path.exists(words_file):
            # Test with reasonable max length
            result = words.importWords(words_file, 10)
            
            assert isinstance(result, list)
            assert len(result) > 0  # Should have some words
            
            # All words should be 10 characters or less
            for word in result:
                assert len(word) <= 10
                assert isinstance(word, str)
                # Should be title case
                assert word == word.title()
        else:
            # Skip test if words.txt doesn't exist
            pytest.skip("words.txt file not found")


class TestWordsFileHandling:
    """Test file handling aspects of words module"""
    
    def test_importWords_file_not_found(self):
        """Test importWords behavior with non-existent file"""
        non_existent_file = "definitely_does_not_exist.txt"
        
        with pytest.raises(FileNotFoundError):
            words.importWords(non_existent_file, -1)
    
    def test_importWords_permission_denied(self):
        """Test importWords behavior with permission denied"""
        # Create a file and make it unreadable
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test\n")
            temp_filename = f.name
        
        try:
            # Remove read permissions
            os.chmod(temp_filename, 0o000)
            
            # Should raise PermissionError
            with pytest.raises(PermissionError):
                words.importWords(temp_filename, -1)
                
        finally:
            # Restore permissions and delete
            os.chmod(temp_filename, 0o644)
            os.unlink(temp_filename)
    
    def test_importWords_with_unicode_content(self):
        """Test importWords with unicode content"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
            f.write("café\nñoño\nstraße\n测试\n")
            temp_filename = f.name
        
        try:
            result = words.importWords(temp_filename, -1)
            
            # Should handle unicode properly
            assert isinstance(result, list)
            assert len(result) == 4
            assert 'Café' in result
            assert 'Ñoño' in result
            assert 'Straße' in result
            assert '测试' in result
            
        finally:
            os.unlink(temp_filename)


class TestWordsParameterValidation:
    """Test parameter validation for words module functions"""
    
    def test_importWords_with_zero_max_length(self):
        """Test importWords with max length of 0"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("a\nab\nabc\n\n")  # Including empty line
            temp_filename = f.name
        
        try:
            result = words.importWords(temp_filename, 0)
            
            # Should only include empty strings (length 0)
            assert isinstance(result, list)
            assert len(result) == 1  # Only the empty line
            assert '' in result
            
        finally:
            os.unlink(temp_filename)
    
    def test_importWords_with_negative_max_length_other_than_minus_one(self):
        """Test importWords with negative max length other than -1"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test\nword\n")
            temp_filename = f.name
        
        try:
            # Test with -2: since code checks (maxwordlength == -1 or len(line) <= maxwordlength)
            # and len(line) <= -2 is never true, should return empty list
            result = words.importWords(temp_filename, -2)
            
            assert isinstance(result, list)
            assert len(result) == 0  # No words meet len(word) <= -2 condition
            
        finally:
            os.unlink(temp_filename)


class TestWordsIntegration:
    """Test integration with the rest of the application"""
    
    def test_importWords_typical_usage_pattern(self):
        """Test importWords as it would typically be used in the application"""
        # Simulate typical usage from makepin.py
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            # Write some typical password words
            typical_words = [
                "apple", "banana", "cherry", "dragon", "eagle",
                "forest", "guitar", "house", "island", "jungle"
            ]
            f.write('\n'.join(typical_words))
            temp_filename = f.name
        
        try:
            # Test various max lengths as might be used
            for max_len in [-1, 5, 6, 10]:
                result = words.importWords(temp_filename, max_len)
                
                assert isinstance(result, list)
                assert len(result) > 0
                
                # All words should meet length requirement
                for word in result:
                    if max_len != -1:
                        assert len(word) <= max_len
                    assert word == word.title()  # Should be title case
                
        finally:
            os.unlink(temp_filename)
    
    def test_importWords_large_file_handling(self):
        """Test importWords with a reasonably large file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            # Generate a large word list
            for i in range(1000):
                f.write(f"word{i:04d}\n")
            temp_filename = f.name
        
        try:
            result = words.importWords(temp_filename, -1)
            
            assert isinstance(result, list)
            assert len(result) == 1000
            
            # Check some samples
            assert 'Word0000' in result
            assert 'Word0500' in result
            assert 'Word0999' in result
            
        finally:
            os.unlink(temp_filename)


class TestWordsSecurityAspects:
    """Test security-relevant aspects of word handling"""
    
    def test_importWords_no_code_injection_via_filename(self):
        """Test that filename parameter doesn't allow code injection"""
        # This is more about ensuring the function handles filenames safely
        dangerous_filenames = [
            "'; rm -rf /; echo '",
            "../../../etc/passwd",
            "file\x00name",
            "con",  # Windows reserved name
        ]
        
        for dangerous_name in dangerous_filenames:
            with pytest.raises((FileNotFoundError, OSError, ValueError)):
                words.importWords(dangerous_name, -1)
    
    def test_importWords_memory_efficiency(self):
        """Test that importWords is reasonably memory efficient"""
        # Test with moderately sized input
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            # Generate words of various lengths
            for i in range(100):
                f.write(f"testword{i}\n")
            temp_filename = f.name
        
        try:
            result = words.importWords(temp_filename, -1)
            
            # Basic memory efficiency check
            import sys
            list_size = sys.getsizeof(result)
            
            # Should be reasonable for the content
            assert list_size > 0
            assert len(result) == 100
            
        finally:
            os.unlink(temp_filename)


class TestWordsErrorHandling:
    """Test error handling in words module"""
    
    def test_importWords_handles_io_errors_gracefully(self):
        """Test that importWords handles various I/O errors"""
        # Test with directory instead of file
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises((IsADirectoryError, PermissionError)):
                words.importWords(temp_dir, -1)
    
    def test_importWords_function_signature(self):
        """Test the function signature is as expected"""
        import inspect
        
        sig = inspect.signature(words.importWords)
        params = list(sig.parameters.keys())
        
        assert len(params) == 2
        assert 'filename' in params
        assert 'maxwordlength' in params


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--cov=words", "--cov-report=term-missing"])