#!/usr/bin/env python3
"""
Coverage Validation Script for CI/CD Integration
Guardian Agent Enforcement for 100% Coverage Requirement
"""
import sys
import os
import json
import xml.etree.ElementTree as ET
import argparse
import subprocess
from pathlib import Path


class CoverageValidator:
    """Validates coverage reports and enforces 100% requirement"""
    
    def __init__(self, coverage_dir=".", threshold=100):
        self.coverage_dir = Path(coverage_dir)
        self.threshold = threshold
        self.reports = {}
    
    def validate_html_report(self):
        """Validate HTML coverage report exists and has correct content"""
        html_dir = self.coverage_dir / "htmlcov"
        index_file = html_dir / "index.html"
        
        if not index_file.exists():
            raise FileNotFoundError(f"HTML coverage report not found: {index_file}")
        
        # Parse HTML for coverage percentage
        with open(index_file, 'r') as f:
            content = f.read()
            if "100%" not in content:
                # Look for actual percentage
                import re
                match = re.search(r'(\d+)%</span>\s*</td>\s*</tr>\s*</tfoot>', content)
                if match:
                    coverage = int(match.group(1))
                    self.reports['html'] = coverage
                    return coverage >= self.threshold
                else:
                    raise ValueError("Could not parse coverage percentage from HTML report")
            else:
                self.reports['html'] = 100
                return True
    
    def validate_xml_report(self):
        """Validate XML coverage report exists and has correct content"""
        xml_file = self.coverage_dir / "coverage.xml"
        
        if not xml_file.exists():
            raise FileNotFoundError(f"XML coverage report not found: {xml_file}")
        
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Get coverage from XML
        coverage_elem = root.find('.//coverage')
        if coverage_elem is not None:
            line_rate = float(coverage_elem.get('line-rate', 0))
            coverage = int(line_rate * 100)
        else:
            # Alternative parsing for different XML formats
            coverage_elem = root.find('.[@line-rate]')
            if coverage_elem is not None:
                line_rate = float(coverage_elem.get('line-rate', 0))
                coverage = int(line_rate * 100)
            else:
                raise ValueError("Could not parse coverage from XML report")
        
        self.reports['xml'] = coverage
        return coverage >= self.threshold
    
    def validate_json_report(self):
        """Validate JSON coverage report exists and has correct content"""
        json_file = self.coverage_dir / "coverage.json"
        
        if not json_file.exists():
            raise FileNotFoundError(f"JSON coverage report not found: {json_file}")
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Get overall coverage percentage
        totals = data.get('totals', {})
        covered_lines = totals.get('covered_lines', 0)
        num_statements = totals.get('num_statements', 1)
        
        coverage = int((covered_lines / max(num_statements, 1)) * 100) if num_statements > 0 else 0
        
        self.reports['json'] = coverage
        return coverage >= self.threshold
    
    def validate_console_output(self):
        """Run coverage report command and validate console output"""
        try:
            # Try different ways to run coverage
            coverage_commands = [
                ['python', '-m', 'coverage', 'report', '--show-missing'],
                ['python3', '-m', 'coverage', 'report', '--show-missing'],
                ['coverage', 'report', '--show-missing']
            ]
            
            result = None
            for cmd in coverage_commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        cwd=self.coverage_dir,
                        timeout=30
                    )
                    if result.returncode == 0:
                        break
                except (subprocess.SubprocessError, FileNotFoundError):
                    continue
            
            if result is None or result.returncode != 0:
                raise RuntimeError(f"Coverage report failed: Unable to run coverage command")
            
            output = result.stdout
            
            # Parse the total line (last line usually)
            lines = output.strip().split('\n')
            total_line = None
            for line in reversed(lines):
                if 'TOTAL' in line:
                    total_line = line
                    break
            
            if not total_line:
                raise ValueError("Could not find TOTAL line in coverage output")
            
            # Extract percentage from TOTAL line
            import re
            match = re.search(r'(\d+)%', total_line)
            if match:
                coverage = int(match.group(1))
                self.reports['console'] = coverage
                return coverage >= self.threshold
            else:
                raise ValueError("Could not parse coverage percentage from console output")
                
        except subprocess.SubprocessError as e:
            raise RuntimeError(f"Failed to run coverage report: {e}")
    
    def validate_all_formats(self):
        """Validate all coverage report formats"""
        results = {}
        errors = []
        
        # Test each format
        formats = [
            ('html', self.validate_html_report),
            ('xml', self.validate_xml_report),
            ('json', self.validate_json_report),
            ('console', self.validate_console_output)
        ]
        
        for format_name, validator in formats:
            try:
                results[format_name] = validator()
            except Exception as e:
                results[format_name] = False
                errors.append(f"{format_name}: {str(e)}")
        
        return results, errors
    
    def enforce_guardian_policy(self):
        """Enforce the guardian policy - BLOCKS code without meeting threshold"""
        results, errors = self.validate_all_formats()
        
        # Check if all formats pass AND meet the actual coverage threshold
        all_pass = all(results.values())
        
        # Additional check: ensure all coverage percentages meet the threshold
        coverage_meets_threshold = all(
            self.reports.get(fmt, 0) >= self.threshold 
            for fmt in results.keys()
        )
        
        if not all_pass or not coverage_meets_threshold:
            print("🚨 TEST GUARDIAN ENFORCEMENT - BLOCKING CODE DEPLOYMENT 🚨")
            print("=" * 60)
            print(f"COVERAGE REQUIREMENT: {self.threshold}%")
            print("COVERAGE RESULTS:")
            
            for format_name, passed in results.items():
                coverage = self.reports.get(format_name, "N/A")
                status = "✅ PASS" if passed and coverage >= self.threshold else "❌ FAIL"
                print(f"  {format_name.upper()}: {coverage}% - {status}")
            
            if errors:
                print("\nERRORS:")
                for error in errors:
                    print(f"  - {error}")
            
            print("\n🛑 DEPLOYMENT BLOCKED - FIX COVERAGE BEFORE PROCEEDING 🛑")
            return False
        
        print(f"✅ COVERAGE GUARDIAN: All formats pass {self.threshold}% requirement")
        print(f"Coverage reports: {self.reports}")
        return True
    
    def generate_coverage_summary(self):
        """Generate a comprehensive coverage summary"""
        results, errors = self.validate_all_formats()
        
        summary = {
            "timestamp": subprocess.check_output(['date', '-Iseconds']).decode().strip(),
            "threshold": self.threshold,
            "results": results,
            "coverage_percentages": self.reports,
            "errors": errors,
            "overall_pass": all(results.values()) and not errors
        }
        
        # Write summary to file
        summary_file = self.coverage_dir / "coverage_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary


def main():
    parser = argparse.ArgumentParser(description="Coverage Validation Script")
    parser.add_argument("--threshold", type=int, default=100, help="Coverage threshold (default: 100)")
    parser.add_argument("--coverage-dir", default=".", help="Coverage directory (default: current)")
    parser.add_argument("--enforce", action="store_true", help="Enforce guardian policy (blocks on failure)")
    parser.add_argument("--summary", action="store_true", help="Generate coverage summary")
    
    args = parser.parse_args()
    
    validator = CoverageValidator(args.coverage_dir, args.threshold)
    
    if args.enforce:
        success = validator.enforce_guardian_policy()
        sys.exit(0 if success else 1)
    
    if args.summary:
        summary = validator.generate_coverage_summary()
        print(json.dumps(summary, indent=2))
    
    # Default: validate all formats and report
    results, errors = validator.validate_all_formats()
    
    print(f"Coverage Validation Results (Threshold: {args.threshold}%):")
    for format_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        coverage = validator.reports.get(format_name, "N/A")
        print(f"  {format_name}: {coverage}% - {status}")
    
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
    
    # Exit with error code if any validation fails
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()