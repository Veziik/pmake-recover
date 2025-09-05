#!/usr/bin/env python3
"""
Guardian Enforcer - MANDATORY 100% Coverage Enforcement
VETO POWER AGENT - Blocks ALL progress without comprehensive test coverage
"""
import sys
import os
import subprocess
import json
import argparse
from pathlib import Path
from datetime import datetime


class TestGuardianEnforcer:
    """
    GUARDIAN AGENT WITH VETO POWER
    Blocks ALL development without 100% test coverage
    """
    
    def __init__(self, project_dir=".", threshold=100, strict_mode=True):
        self.project_dir = Path(project_dir)
        self.threshold = threshold
        self.strict_mode = strict_mode
        self.coverage_data = {}
        self.violations = []
        self.security_critical_files = [
            "makepin.py", "recoverpin.py", "helpers.py", "words.py"
        ]
    
    def run_coverage_analysis(self):
        """Run comprehensive coverage analysis"""
        print("🛡️ TEST GUARDIAN ENFORCER - COVERAGE ANALYSIS STARTING...")
        print("=" * 70)
        
        # Clean previous coverage data
        self._clean_coverage_data()
        
        # Run tests with coverage
        success = self._run_tests_with_coverage()
        if not success:
            self._block_with_error("TESTS FAILED - Cannot proceed with coverage analysis")
            return False
        
        # Generate all report formats
        self._generate_coverage_reports()
        
        # Analyze coverage data
        self._analyze_coverage_data()
        
        # Validate security-critical files
        self._validate_security_files()
        
        # Make final decision
        return self._make_enforcement_decision()
    
    def _clean_coverage_data(self):
        """Clean previous coverage data"""
        print("🧹 Cleaning previous coverage data...")
        cleanup_files = [
            ".coverage", "coverage.xml", "coverage.json", 
            "htmlcov", "coverage_artifacts"
        ]
        
        for item in cleanup_files:
            item_path = self.project_dir / item
            if item_path.exists():
                if item_path.is_dir():
                    import shutil
                    shutil.rmtree(item_path)
                else:
                    item_path.unlink()
        print("✅ Coverage data cleaned")
    
    def _run_tests_with_coverage(self):
        """Run tests with coverage collection"""
        print("🧪 Running tests with coverage collection...")
        
        try:
            # Run pytest with coverage
            result = subprocess.run([
                "coverage", "run", "--source=.", "-m", "pytest", 
                "--tb=short", "-v"
            ], 
            cwd=self.project_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                print(f"❌ Tests failed with return code {result.returncode}")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False
            
            print("✅ Tests completed successfully")
            return True
            
        except subprocess.TimeoutExpired:
            self._block_with_error("TEST TIMEOUT - Tests took too long to complete")
            return False
        except Exception as e:
            self._block_with_error(f"TEST EXECUTION FAILED - {str(e)}")
            return False
    
    def _generate_coverage_reports(self):
        """Generate all coverage report formats"""
        print("📊 Generating coverage reports...")
        
        report_commands = [
            (["coverage", "html", "--directory", "htmlcov"], "HTML"),
            (["coverage", "xml", "--output", "coverage.xml"], "XML"),
            (["coverage", "json", "--output", "coverage.json"], "JSON"),
        ]
        
        for command, format_name in report_commands:
            try:
                result = subprocess.run(
                    command, 
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    self.violations.append(f"Failed to generate {format_name} report: {result.stderr}")
                else:
                    print(f"✅ {format_name} report generated")
                    
            except Exception as e:
                self.violations.append(f"Error generating {format_name} report: {str(e)}")
        
        # Generate console report
        try:
            result = subprocess.run([
                "coverage", "report", "--show-missing"
            ], 
            cwd=self.project_dir,
            capture_output=True,
            text=True
            )
            
            self.coverage_data['console_output'] = result.stdout
            print("✅ Console report generated")
            
        except Exception as e:
            self.violations.append(f"Error generating console report: {str(e)}")
    
    def _analyze_coverage_data(self):
        """Analyze coverage data from all formats"""
        print("🔍 Analyzing coverage data...")
        
        # Analyze JSON report (most detailed)
        self._analyze_json_coverage()
        
        # Analyze XML report  
        self._analyze_xml_coverage()
        
        # Analyze console output
        self._analyze_console_coverage()
        
        # Cross-validate results
        self._cross_validate_coverage()
    
    def _analyze_json_coverage(self):
        """Analyze JSON coverage report"""
        json_file = self.project_dir / "coverage.json"
        
        if not json_file.exists():
            self.violations.append("JSON coverage report missing")
            return
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            totals = data.get('totals', {})
            overall_coverage = (totals.get('covered_lines', 0) / 
                              max(totals.get('num_statements', 1), 1)) * 100
            
            self.coverage_data['json_coverage'] = overall_coverage
            
            # Analyze per-file coverage
            files = data.get('files', {})
            file_coverages = {}
            
            for filename, file_data in files.items():
                if filename.endswith('.py') and not filename.startswith('test_'):
                    summary = file_data.get('summary', {})
                    covered = summary.get('covered_lines', 0)
                    total = summary.get('num_statements', 1)
                    file_coverage = (covered / max(total, 1)) * 100
                    file_coverages[filename] = file_coverage
                    
                    if file_coverage < self.threshold:
                        self.violations.append(
                            f"File {filename} has {file_coverage:.1f}% coverage (below {self.threshold}%)"
                        )
            
            self.coverage_data['file_coverages'] = file_coverages
            
        except Exception as e:
            self.violations.append(f"Error analyzing JSON coverage: {str(e)}")
    
    def _analyze_xml_coverage(self):
        """Analyze XML coverage report"""
        xml_file = self.project_dir / "coverage.xml"
        
        if not xml_file.exists():
            self.violations.append("XML coverage report missing")
            return
        
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Get overall coverage
            coverage_elem = root.find('.//coverage')
            if coverage_elem is not None:
                line_rate = float(coverage_elem.get('line-rate', 0))
                xml_coverage = int(line_rate * 100)
                self.coverage_data['xml_coverage'] = xml_coverage
            
        except Exception as e:
            self.violations.append(f"Error analyzing XML coverage: {str(e)}")
    
    def _analyze_console_coverage(self):
        """Analyze console coverage output"""
        console_output = self.coverage_data.get('console_output', '')
        
        if not console_output:
            self.violations.append("Console coverage output missing")
            return
        
        try:
            # Find TOTAL line
            lines = console_output.strip().split('\n')
            total_line = None
            
            for line in reversed(lines):
                if 'TOTAL' in line:
                    total_line = line
                    break
            
            if total_line:
                import re
                match = re.search(r'(\d+)%', total_line)
                if match:
                    console_coverage = int(match.group(1))
                    self.coverage_data['console_coverage'] = console_coverage
        
        except Exception as e:
            self.violations.append(f"Error analyzing console coverage: {str(e)}")
    
    def _cross_validate_coverage(self):
        """Cross-validate coverage results from different formats"""
        coverages = [
            self.coverage_data.get('json_coverage'),
            self.coverage_data.get('xml_coverage'), 
            self.coverage_data.get('console_coverage')
        ]
        
        # Filter out None values
        valid_coverages = [c for c in coverages if c is not None]
        
        if len(valid_coverages) < 2:
            self.violations.append("Insufficient coverage data for cross-validation")
            return
        
        # Check if all formats agree (within 1%)
        max_coverage = max(valid_coverages)
        min_coverage = min(valid_coverages)
        
        if max_coverage - min_coverage > 1:
            self.violations.append(
                f"Coverage formats disagree: {valid_coverages} (difference > 1%)"
            )
        
        # Use the most conservative (lowest) coverage
        self.coverage_data['final_coverage'] = min_coverage
    
    def _validate_security_files(self):
        """Validate that security-critical files have 100% coverage"""
        print("🔒 Validating security-critical files coverage...")
        
        file_coverages = self.coverage_data.get('file_coverages', {})
        
        for critical_file in self.security_critical_files:
            if critical_file in file_coverages:
                coverage = file_coverages[critical_file]
                if coverage < 100:
                    self.violations.append(
                        f"🚨 SECURITY RISK: {critical_file} has {coverage:.1f}% coverage (MUST be 100%)"
                    )
                    print(f"❌ SECURITY VIOLATION: {critical_file} - {coverage:.1f}%")
                else:
                    print(f"✅ Security file {critical_file} - 100% coverage")
            else:
                self.violations.append(f"🚨 SECURITY FILE NOT TESTED: {critical_file}")
                print(f"❌ SECURITY VIOLATION: {critical_file} - NOT TESTED")
    
    def _make_enforcement_decision(self):
        """Make final enforcement decision - BLOCKS if requirements not met"""
        print("\n" + "=" * 70)
        print("🛡️ GUARDIAN ENFORCEMENT DECISION")
        print("=" * 70)
        
        final_coverage = self.coverage_data.get('final_coverage', 0)
        
        # Print coverage summary
        print(f"COVERAGE THRESHOLD: {self.threshold}%")
        print(f"ACHIEVED COVERAGE: {final_coverage}%")
        
        if self.coverage_data.get('json_coverage'):
            print(f"  - JSON Report: {self.coverage_data['json_coverage']:.1f}%")
        if self.coverage_data.get('xml_coverage'):
            print(f"  - XML Report: {self.coverage_data['xml_coverage']:.1f}%")
        if self.coverage_data.get('console_coverage'):
            print(f"  - Console Report: {self.coverage_data['console_coverage']:.1f}%")
        
        # Check violations
        if self.violations:
            print(f"\n❌ VIOLATIONS DETECTED ({len(self.violations)}):")
            for i, violation in enumerate(self.violations, 1):
                print(f"  {i}. {violation}")
        
        # Make decision
        coverage_ok = final_coverage >= self.threshold
        no_violations = len(self.violations) == 0
        
        if coverage_ok and no_violations:
            print("\n✅ GUARDIAN APPROVAL - DEPLOYMENT ALLOWED")
            print("   - Coverage meets requirements")
            print("   - No security violations detected")
            print("   - All report formats generated successfully")
            self._generate_approval_certificate()
            return True
        else:
            print("\n🛑 GUARDIAN BLOCK - DEPLOYMENT DENIED")
            print("   REASONS FOR BLOCKING:")
            
            if not coverage_ok:
                print(f"   - Coverage {final_coverage:.1f}% < Required {self.threshold}%")
            
            if self.violations:
                print(f"   - {len(self.violations)} violation(s) detected")
            
            print("\n   📋 REQUIRED ACTIONS:")
            print("   1. Fix all failing tests")
            print("   2. Add tests to achieve 100% coverage")
            print("   3. Ensure all security-critical files have 100% coverage")
            print("   4. Re-run guardian enforcement")
            
            self._generate_violation_report()
            return False
    
    def _generate_approval_certificate(self):
        """Generate approval certificate for successful validation"""
        certificate = {
            "guardian_approval": True,
            "timestamp": datetime.now().isoformat(),
            "coverage_achieved": self.coverage_data.get('final_coverage', 0),
            "threshold_required": self.threshold,
            "security_files_validated": self.security_critical_files,
            "report_formats_generated": ["html", "xml", "json", "console"],
            "violations_count": len(self.violations),
            "certificate_id": f"GUARD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        }
        
        cert_file = self.project_dir / "coverage_guardian_approval.json"
        with open(cert_file, 'w') as f:
            json.dump(certificate, f, indent=2)
        
        print(f"📜 Guardian approval certificate generated: {cert_file}")
    
    def _generate_violation_report(self):
        """Generate detailed violation report for failed validation"""
        report = {
            "guardian_blocked": True,
            "timestamp": datetime.now().isoformat(),
            "coverage_achieved": self.coverage_data.get('final_coverage', 0),
            "threshold_required": self.threshold,
            "violations": self.violations,
            "coverage_data": self.coverage_data,
            "required_actions": [
                "Fix all failing tests",
                "Add comprehensive tests for uncovered code",
                "Ensure 100% coverage for security-critical files",
                "Validate all coverage report formats",
                "Re-run guardian enforcement"
            ]
        }
        
        report_file = self.project_dir / "coverage_guardian_violations.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📋 Guardian violation report generated: {report_file}")
    
    def _block_with_error(self, error_message):
        """Block execution with error message"""
        print(f"\n🚨 GUARDIAN BLOCK: {error_message}")
        self.violations.append(error_message)
        return False


def main():
    """Main guardian enforcer entry point"""
    parser = argparse.ArgumentParser(
        description="Guardian Enforcer - MANDATORY 100% Coverage Enforcement"
    )
    parser.add_argument(
        "--threshold", type=int, default=100,
        help="Coverage threshold percentage (default: 100)"
    )
    parser.add_argument(
        "--project-dir", default=".",
        help="Project directory (default: current directory)"
    )
    parser.add_argument(
        "--strict", action="store_true", default=True,
        help="Strict mode - no exceptions allowed"
    )
    parser.add_argument(
        "--report-only", action="store_true",
        help="Report mode - don't block, just report status"
    )
    
    args = parser.parse_args()
    
    # Create guardian enforcer
    guardian = TestGuardianEnforcer(
        project_dir=args.project_dir,
        threshold=args.threshold,
        strict_mode=args.strict
    )
    
    # Run enforcement
    success = guardian.run_coverage_analysis()
    
    if args.report_only:
        # Just report, don't exit with error
        print(f"\nGuardian Report: {'APPROVED' if success else 'VIOLATIONS DETECTED'}")
        sys.exit(0)
    else:
        # Exit with appropriate code
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()