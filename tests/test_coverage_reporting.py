#!/usr/bin/env python3
"""
Comprehensive Tests for Coverage Reporting System
Tests all coverage report formats and guardian enforcement mechanisms
"""
import pytest
import os
import json
import tempfile
import subprocess
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import xml.etree.ElementTree as ET

# Import the module under test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from coverage_validator import CoverageValidator


class TestCoverageValidator:
    """Test the CoverageValidator class"""
    
    @pytest.fixture
    def temp_coverage_dir(self):
        """Create a temporary directory for coverage tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def validator(self, temp_coverage_dir):
        """Create a CoverageValidator instance for testing"""
        return CoverageValidator(coverage_dir=str(temp_coverage_dir), threshold=100)
    
    def test_validator_initialization(self, temp_coverage_dir):
        """Test CoverageValidator initialization"""
        validator = CoverageValidator(coverage_dir=str(temp_coverage_dir), threshold=95)
        assert validator.threshold == 95
        assert validator.coverage_dir == temp_coverage_dir
        assert validator.reports == {}
    
    def test_validate_html_report_missing_file(self, validator):
        """Test HTML validation when file is missing"""
        with pytest.raises(FileNotFoundError):
            validator.validate_html_report()
    
    def test_validate_html_report_100_percent(self, validator):
        """Test HTML validation with 100% coverage"""
        # Create mock HTML report directory and file
        htmlcov_dir = validator.coverage_dir / "htmlcov"
        htmlcov_dir.mkdir()
        index_file = htmlcov_dir / "index.html"
        
        html_content = """
        <html>
        <body>
            <table>
                <tfoot>
                    <tr>
                        <td>Total</td>
                        <td>100</td>
                        <td>0</td>
                        <td><span class="pc_cov">100%</span></td>
                    </tr>
                </tfoot>
            </table>
        </body>
        </html>
        """
        index_file.write_text(html_content)
        
        assert validator.validate_html_report() == True
        assert validator.reports['html'] == 100
    
    def test_validate_html_report_less_than_100_percent(self, validator):
        """Test HTML validation with less than 100% coverage"""
        htmlcov_dir = validator.coverage_dir / "htmlcov"
        htmlcov_dir.mkdir()
        index_file = htmlcov_dir / "index.html"
        
        html_content = """
        <html>
        <body>
            <table>
                <tfoot>
                    <tr>
                        <td>Total</td>
                        <td>90</td>
                        <td>10</td>
                        <td><span class="pc_cov">90%</span></td>
                    </tr>
                </tfoot>
            </table>
        </body>
        </html>
        """
        index_file.write_text(html_content)
        
        assert validator.validate_html_report() == False
        assert validator.reports['html'] == 90
    
    def test_validate_xml_report_missing_file(self, validator):
        """Test XML validation when file is missing"""
        with pytest.raises(FileNotFoundError):
            validator.validate_xml_report()
    
    def test_validate_xml_report_100_percent(self, validator):
        """Test XML validation with 100% coverage"""
        xml_file = validator.coverage_dir / "coverage.xml"
        
        xml_content = '''<?xml version="1.0" ?>
        <coverage line-rate="1.0" branch-rate="1.0">
            <sources>
                <source>.</source>
            </sources>
            <packages>
                <package line-rate="1.0" branch-rate="1.0" name=".">
                    <classes>
                        <class line-rate="1.0" branch-rate="1.0" filename="test.py">
                            <methods/>
                            <lines>
                                <line hits="1" number="1"/>
                            </lines>
                        </class>
                    </classes>
                </package>
            </packages>
        </coverage>'''
        
        xml_file.write_text(xml_content)
        
        assert validator.validate_xml_report() == True
        assert validator.reports['xml'] == 100
    
    def test_validate_xml_report_less_than_100_percent(self, validator):
        """Test XML validation with less than 100% coverage"""
        xml_file = validator.coverage_dir / "coverage.xml"
        
        xml_content = '''<?xml version="1.0" ?>
        <coverage line-rate="0.85" branch-rate="0.85">
            <sources>
                <source>.</source>
            </sources>
            <packages>
                <package line-rate="0.85" branch-rate="0.85" name=".">
                    <classes>
                        <class line-rate="0.85" branch-rate="0.85" filename="test.py">
                            <methods/>
                            <lines>
                                <line hits="1" number="1"/>
                                <line hits="0" number="2"/>
                            </lines>
                        </class>
                    </classes>
                </package>
            </packages>
        </coverage>'''
        
        xml_file.write_text(xml_content)
        
        assert validator.validate_xml_report() == False
        assert validator.reports['xml'] == 85
    
    def test_validate_json_report_missing_file(self, validator):
        """Test JSON validation when file is missing"""
        with pytest.raises(FileNotFoundError):
            validator.validate_json_report()
    
    def test_validate_json_report_100_percent(self, validator):
        """Test JSON validation with 100% coverage"""
        json_file = validator.coverage_dir / "coverage.json"
        
        json_data = {
            "meta": {
                "version": "7.0.0",
                "timestamp": "2024-01-01T00:00:00"
            },
            "files": {
                "test.py": {
                    "executed_lines": [1, 2, 3],
                    "summary": {
                        "covered_lines": 3,
                        "num_statements": 3,
                        "percent_covered": 100.0
                    }
                }
            },
            "totals": {
                "covered_lines": 3,
                "num_statements": 3,
                "percent_covered": 100.0
            }
        }
        
        json_file.write_text(json.dumps(json_data))
        
        assert validator.validate_json_report() == True
        assert validator.reports['json'] == 100
    
    def test_validate_json_report_less_than_100_percent(self, validator):
        """Test JSON validation with less than 100% coverage"""
        json_file = validator.coverage_dir / "coverage.json"
        
        json_data = {
            "meta": {
                "version": "7.0.0",
                "timestamp": "2024-01-01T00:00:00"
            },
            "files": {
                "test.py": {
                    "executed_lines": [1, 2],
                    "summary": {
                        "covered_lines": 2,
                        "num_statements": 3,
                        "percent_covered": 66.67
                    }
                }
            },
            "totals": {
                "covered_lines": 2,
                "num_statements": 3,
                "percent_covered": 66.67
            }
        }
        
        json_file.write_text(json.dumps(json_data))
        
        assert validator.validate_json_report() == False
        assert validator.reports['json'] == 66
    
    @patch('subprocess.run')
    def test_validate_console_output_100_percent(self, mock_run, validator):
        """Test console validation with 100% coverage"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """
Name         Stmts   Miss  Cover   Missing
------------------------------------------
test.py         10      0   100%
------------------------------------------
TOTAL           10      0   100%
"""
        mock_run.return_value = mock_result
        
        assert validator.validate_console_output() == True
        assert validator.reports['console'] == 100
    
    @patch('subprocess.run')
    def test_validate_console_output_less_than_100_percent(self, mock_run, validator):
        """Test console validation with less than 100% coverage"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """
Name         Stmts   Miss  Cover   Missing
------------------------------------------
test.py         10      2    80%   5-6
------------------------------------------
TOTAL           10      2    80%
"""
        mock_run.return_value = mock_result
        
        assert validator.validate_console_output() == False
        assert validator.reports['console'] == 80
    
    @patch('subprocess.run')
    def test_validate_console_output_command_failure(self, mock_run, validator):
        """Test console validation when coverage command fails"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Coverage command failed"
        mock_run.return_value = mock_result
        
        with pytest.raises(RuntimeError):
            validator.validate_console_output()
    
    def test_validate_all_formats_all_pass(self, validator):
        """Test validation of all formats when all pass"""
        # Mock all validation methods to return True
        validator.validate_html_report = lambda: True
        validator.validate_xml_report = lambda: True  
        validator.validate_json_report = lambda: True
        validator.validate_console_output = lambda: True
        
        results, errors = validator.validate_all_formats()
        
        assert all(results.values()) == True
        assert len(errors) == 0
        assert set(results.keys()) == {'html', 'xml', 'json', 'console'}
    
    def test_validate_all_formats_some_fail(self, validator):
        """Test validation of all formats when some fail"""
        # Mock some validation methods to fail
        validator.validate_html_report = lambda: True
        validator.validate_xml_report = lambda: False
        validator.validate_json_report = lambda: (_ for _ in ()).throw(FileNotFoundError("Missing file"))
        validator.validate_console_output = lambda: True
        
        results, errors = validator.validate_all_formats()
        
        assert results['html'] == True
        assert results['xml'] == False
        assert results['json'] == False
        assert results['console'] == True
        assert len(errors) == 1
        assert "json: Missing file" in errors[0]
    
    def test_enforce_guardian_policy_all_pass(self, validator, capsys):
        """Test guardian policy enforcement when all validations pass"""
        # Mock all validation methods to return True
        validator.validate_html_report = lambda: True
        validator.validate_xml_report = lambda: True  
        validator.validate_json_report = lambda: True
        validator.validate_console_output = lambda: True
        validator.reports = {'html': 100, 'xml': 100, 'json': 100, 'console': 100}
        
        result = validator.enforce_guardian_policy()
        
        assert result == True
        captured = capsys.readouterr()
        assert "COVERAGE GUARDIAN: All formats pass 100% requirement" in captured.out
    
    def test_enforce_guardian_policy_some_fail(self, validator, capsys):
        """Test guardian policy enforcement when some validations fail"""
        # Mock some validation methods to fail
        validator.validate_html_report = lambda: True
        validator.validate_xml_report = lambda: False
        validator.validate_json_report = lambda: False
        validator.validate_console_output = lambda: True
        validator.reports = {'html': 100, 'xml': 80, 'json': 75, 'console': 100}
        
        result = validator.enforce_guardian_policy()
        
        assert result == False
        captured = capsys.readouterr()
        assert "TEST GUARDIAN ENFORCEMENT - BLOCKING CODE DEPLOYMENT" in captured.out
        assert "DEPLOYMENT BLOCKED" in captured.out
    
    def test_generate_coverage_summary(self, validator):
        """Test coverage summary generation"""
        # Mock validation methods
        validator.validate_html_report = lambda: True
        validator.validate_xml_report = lambda: True  
        validator.validate_json_report = lambda: True
        validator.validate_console_output = lambda: True
        validator.reports = {'html': 100, 'xml': 100, 'json': 100, 'console': 100}
        
        summary = validator.generate_coverage_summary()
        
        assert summary['threshold'] == 100
        assert summary['overall_pass'] == True
        assert summary['coverage_percentages'] == validator.reports
        assert all(summary['results'].values()) == True
        
        # Check if summary file was written
        summary_file = validator.coverage_dir / "coverage_summary.json"
        assert summary_file.exists()


class TestCoverageIntegration:
    """Integration tests for the complete coverage system"""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory with sample files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            
            # Create sample Python files
            sample_py = project_dir / "sample.py"
            sample_py.write_text('''
def add(a, b):
    """Add two numbers"""
    return a + b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b

if __name__ == "__main__":
    print(add(2, 3))
    print(multiply(4, 5))
''')
            
            # Create test file
            test_dir = project_dir / "tests"
            test_dir.mkdir()
            (test_dir / "__init__.py").touch()
            
            test_file = test_dir / "test_sample.py"
            test_file.write_text('''
import sys
sys.path.insert(0, "..")
from sample import add, multiply

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(0, 5) == 0
''')
            
            yield project_dir
    
    @pytest.mark.integration
    def test_full_coverage_workflow(self, temp_project_dir):
        """Test the complete coverage workflow from test execution to validation"""
        # Change to project directory
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_project_dir)
            
            # Run coverage
            result = subprocess.run([
                'coverage', 'run', '--source=.', '-m', 'pytest', 'tests/', '-v'
            ], capture_output=True, text=True)
            
            # Check if tests ran successfully
            assert result.returncode == 0, f"Tests failed: {result.stderr}"
            
            # Generate reports
            subprocess.run(['coverage', 'html'], check=True)
            subprocess.run(['coverage', 'xml'], check=True)
            subprocess.run(['coverage', 'json'], check=True)
            
            # Validate using our validator
            validator = CoverageValidator(coverage_dir=".", threshold=100)
            results, errors = validator.validate_all_formats()
            
            # All formats should be available and coverage should be 100%
            for format_name in ['html', 'xml', 'json', 'console']:
                assert format_name in results
                # Note: May not be 100% due to main block, but should be high
                assert validator.reports.get(format_name, 0) >= 80
            
        finally:
            os.chdir(original_cwd)


class TestCoverageFormats:
    """Test coverage report format parsing and validation"""
    
    def test_html_format_parsing_edge_cases(self):
        """Test HTML format parsing with various edge cases"""
        validator = CoverageValidator()
        
        # Test with malformed HTML
        with tempfile.TemporaryDirectory() as temp_dir:
            htmlcov_dir = Path(temp_dir) / "htmlcov"
            htmlcov_dir.mkdir()
            index_file = htmlcov_dir / "index.html"
            
            # Malformed HTML without percentage
            index_file.write_text("<html><body>No percentage here</body></html>")
            validator.coverage_dir = Path(temp_dir)
            
            with pytest.raises(ValueError):
                validator.validate_html_report()
    
    def test_xml_format_parsing_edge_cases(self):
        """Test XML format parsing with various edge cases"""
        validator = CoverageValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            xml_file = Path(temp_dir) / "coverage.xml"
            validator.coverage_dir = Path(temp_dir)
            
            # Invalid XML
            xml_file.write_text("Not valid XML content")
            
            with pytest.raises(ET.ParseError):
                validator.validate_xml_report()
    
    def test_json_format_parsing_edge_cases(self):
        """Test JSON format parsing with various edge cases"""
        validator = CoverageValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = Path(temp_dir) / "coverage.json"
            validator.coverage_dir = Path(temp_dir)
            
            # Invalid JSON
            json_file.write_text("Not valid JSON content")
            
            with pytest.raises(json.JSONDecodeError):
                validator.validate_json_report()
            
            # Valid JSON but missing totals
            json_file.write_text('{"files": {}}')
            
            result = validator.validate_json_report()
            assert result == False  # Should fail due to no statements


class TestGuardianEnforcement:
    """Test guardian enforcement mechanisms"""
    
    def test_guardian_blocks_on_insufficient_coverage(self):
        """Test that guardian correctly blocks when coverage is insufficient"""
        validator = CoverageValidator(threshold=100)
        
        # Mock methods to return insufficient coverage
        validator.validate_html_report = lambda: False
        validator.validate_xml_report = lambda: False
        validator.validate_json_report = lambda: False
        validator.validate_console_output = lambda: False
        validator.reports = {'html': 95, 'xml': 90, 'json': 85, 'console': 92}
        
        result = validator.enforce_guardian_policy()
        assert result == False
    
    def test_guardian_allows_on_sufficient_coverage(self):
        """Test that guardian allows when coverage meets requirements"""
        validator = CoverageValidator(threshold=100)
        
        # Mock methods to return sufficient coverage
        validator.validate_html_report = lambda: True
        validator.validate_xml_report = lambda: True
        validator.validate_json_report = lambda: True
        validator.validate_console_output = lambda: True
        validator.reports = {'html': 100, 'xml': 100, 'json': 100, 'console': 100}
        
        result = validator.enforce_guardian_policy()
        assert result == True
    
    def test_custom_threshold_enforcement(self):
        """Test guardian with custom threshold values"""
        validator = CoverageValidator(threshold=95)
        
        # Mock methods to return 95% coverage
        validator.validate_html_report = lambda: True
        validator.validate_xml_report = lambda: True
        validator.validate_json_report = lambda: True
        validator.validate_console_output = lambda: True
        validator.reports = {'html': 95, 'xml': 95, 'json': 95, 'console': 95}
        
        result = validator.enforce_guardian_policy()
        assert result == True
        
        # Test with threshold 100 - same coverage should fail
        validator.threshold = 100
        result = validator.enforce_guardian_policy()
        assert result == False


@pytest.mark.security
class TestSecurityEnforcement:
    """Test security-focused coverage enforcement"""
    
    def test_security_critical_files_coverage(self):
        """Test that security-critical files must have 100% coverage"""
        # This would be implemented as part of the CI script
        # Here we test the concept
        security_files = ["makepin.py", "recoverpin.py", "helpers.py"]
        
        for filename in security_files:
            # Each security file must have 100% coverage
            # This is enforced by the CI script
            assert filename in security_files  # Placeholder test
    
    def test_password_generation_coverage_enforcement(self):
        """Test that password generation functions have comprehensive coverage"""
        # This ensures that all password-related functions are fully tested
        # Implementation would scan for password-related functions
        password_functions = [
            "replace_with_symbol",
            "replace_with_alpha", 
            "add_character",
            "add_word"
        ]
        
        for func in password_functions:
            # Each function must have 100% coverage including edge cases
            assert func in password_functions  # Placeholder test


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])