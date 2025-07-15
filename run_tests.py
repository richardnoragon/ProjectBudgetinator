#!/usr/bin/env python3
"""
Test runner for ProjectBudgetinator test suite.

This script provides comprehensive testing capabilities including:
- Unit tests
- Integration tests  
- Performance benchmarks
- Coverage reporting
- Test result analysis

Usage:
    python run_tests.py [options]

Options:
    --unit          Run only unit tests
    --integration   Run only integration tests
    --performance   Run only performance tests
    --coverage      Generate coverage report
    --html          Generate HTML coverage report
    --benchmark     Run benchmark tests
    --verbose       Verbose output
    --fast          Skip slow tests
    --help          Show this help message
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
import time
from typing import List, Optional


class TestRunner:
    """Comprehensive test runner for ProjectBudgetinator."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.src_path = self.project_root / "src"
        self.tests_path = self.project_root / "tests"
        self.build_path = self.project_root / "build"
        
        # Ensure build directory exists
        self.build_path.mkdir(exist_ok=True)
    
    def run_command(self, command: List[str], capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        print(f"Running: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=capture_output,
                text=True,
                check=False
            )
            return result
        except FileNotFoundError as e:
            print(f"Error: Command not found - {e}")
            print("Make sure pytest is installed: pip install pytest pytest-cov pytest-benchmark")
            sys.exit(1)
    
    def check_dependencies(self) -> bool:
        """Check if required testing dependencies are installed."""
        required_packages = [
            'pytest',
            'pytest-cov', 
            'pytest-benchmark',
            'openpyxl'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print("Missing required packages:")
            for package in missing_packages:
                print(f"  - {package}")
            print(f"\nInstall with: pip install {' '.join(missing_packages)}")
            return False
        
        return True
    
    def run_unit_tests(self, verbose: bool = False, coverage: bool = False) -> bool:
        """Run unit tests."""
        print("\n" + "="*50)
        print("RUNNING UNIT TESTS")
        print("="*50)
        
        command = ["python", "-m", "pytest"]
        
        # Add test markers
        command.extend(["-m", "unit or not (integration or performance)"])
        
        # Add test paths
        command.extend([
            "tests/test_base_handlers.py",
            "tests/test_partner_handler.py",
            "tests/test_workpackage_handler.py"
        ])
        
        if verbose:
            command.append("-v")
        
        if coverage:
            command.extend([
                "--cov=src",
                "--cov-report=term-missing",
                f"--cov-report=html:{self.build_path}/coverage_html_unit"
            ])
        
        result = self.run_command(command)
        return result.returncode == 0
    
    def run_integration_tests(self, verbose: bool = False, coverage: bool = False) -> bool:
        """Run integration tests."""
        print("\n" + "="*50)
        print("RUNNING INTEGRATION TESTS")
        print("="*50)
        
        command = ["python", "-m", "pytest"]
        
        # Add test markers
        command.extend(["-m", "integration"])
        
        # Add test paths
        command.extend([
            "tests/test_excel_integration.py",
            "tests/test_partner_handler.py::TestPartnerIntegration",
            "tests/test_workpackage_handler.py::TestWorkpackageIntegration"
        ])
        
        if verbose:
            command.append("-v")
        
        if coverage:
            command.extend([
                "--cov=src",
                "--cov-report=term-missing",
                f"--cov-report=html:{self.build_path}/coverage_html_integration"
            ])
        
        result = self.run_command(command)
        return result.returncode == 0
    
    def run_performance_tests(self, verbose: bool = False) -> bool:
        """Run performance tests and benchmarks."""
        print("\n" + "="*50)
        print("RUNNING PERFORMANCE TESTS")
        print("="*50)
        
        command = ["python", "-m", "pytest"]
        
        # Add test markers
        command.extend(["-m", "performance"])
        
        # Add benchmark options
        command.extend([
            "--benchmark-only",
            "--benchmark-sort=mean",
            f"--benchmark-json={self.build_path}/benchmark_results.json",
            f"--benchmark-histogram={self.build_path}/benchmark_histogram"
        ])
        
        if verbose:
            command.append("-v")
        
        result = self.run_command(command)
        return result.returncode == 0
    
    def run_all_tests(self, verbose: bool = False, coverage: bool = False, 
                     fast: bool = False) -> dict:
        """Run all test categories."""
        print("\n" + "="*60)
        print("RUNNING COMPLETE TEST SUITE")
        print("="*60)
        
        results = {}
        
        # Prepare pytest command
        command = ["python", "-m", "pytest", "tests/"]
        
        if fast:
            command.extend(["-m", "not slow"])
        
        if verbose:
            command.append("-v")
        
        if coverage:
            command.extend([
                "--cov=src",
                "--cov-report=term-missing",
                "--cov-report=html:build/coverage_html",
                "--cov-fail-under=80"
            ])
        
        # Add benchmark options for performance tests
        command.extend([
            "--benchmark-skip",  # Skip benchmarks in regular run
            "--tb=short"
        ])
        
        start_time = time.time()
        result = self.run_command(command)
        end_time = time.time()
        
        results['all_tests'] = {
            'success': result.returncode == 0,
            'duration': end_time - start_time,
            'return_code': result.returncode
        }
        
        return results
    
    def generate_coverage_report(self, html: bool = True) -> bool:
        """Generate coverage report."""
        print("\n" + "="*50)
        print("GENERATING COVERAGE REPORT")
        print("="*50)
        
        # Run tests with coverage
        command = [
            "python", "-m", "pytest", "tests/",
            "--cov=src",
            "--cov-report=term-missing"
        ]
        
        if html:
            command.append(f"--cov-report=html:{self.build_path}/coverage_html")
        
        result = self.run_command(command)
        
        if html and result.returncode == 0:
            html_report = self.build_path / "coverage_html" / "index.html"
            if html_report.exists():
                print(f"\nHTML coverage report generated: {html_report}")
        
        return result.returncode == 0
    
    def run_specific_test(self, test_path: str, verbose: bool = False) -> bool:
        """Run a specific test file or test function."""
        print(f"\nRunning specific test: {test_path}")
        
        command = ["python", "-m", "pytest", test_path]
        
        if verbose:
            command.append("-v")
        
        result = self.run_command(command)
        return result.returncode == 0
    
    def lint_code(self) -> bool:
        """Run code linting on source and test files."""
        print("\n" + "="*50)
        print("RUNNING CODE LINTING")
        print("="*50)
        
        # Check if flake8 is available
        try:
            result = self.run_command(["flake8", "--version"], capture_output=True)
            if result.returncode != 0:
                print("flake8 not available, skipping linting")
                return True
        except FileNotFoundError:
            print("flake8 not installed, skipping linting")
            return True
        
        # Run flake8 on source code
        print("Linting source code...")
        command = [
            "flake8", "src/", 
            "--max-line-length=88",
            "--ignore=E203,W503",
            "--exclude=__pycache__"
        ]
        
        result = self.run_command(command)
        src_success = result.returncode == 0
        
        # Run flake8 on test code
        print("Linting test code...")
        command = [
            "flake8", "tests/",
            "--max-line-length=88", 
            "--ignore=E203,W503",
            "--exclude=__pycache__"
        ]
        
        result = self.run_command(command)
        test_success = result.returncode == 0
        
        return src_success and test_success
    
    def print_summary(self, results: dict):
        """Print test execution summary."""
        print("\n" + "="*60)
        print("TEST EXECUTION SUMMARY")
        print("="*60)
        
        total_duration = 0
        total_success = True
        
        for test_type, result in results.items():
            status = "PASSED" if result['success'] else "FAILED"
            duration = result.get('duration', 0)
            total_duration += duration
            
            if not result['success']:
                total_success = False
            
            print(f"{test_type:20}: {status:6} ({duration:.2f}s)")
        
        print("-" * 60)
        overall_status = "PASSED" if total_success else "FAILED"
        print(f"{'OVERALL':20}: {overall_status:6} ({total_duration:.2f}s)")
        
        if not total_success:
            print("\nSome tests failed. Check the output above for details.")
            return False
        else:
            print("\nAll tests passed successfully!")
            return True


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(
        description="Test runner for ProjectBudgetinator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--unit", action="store_true",
        help="Run only unit tests"
    )
    parser.add_argument(
        "--integration", action="store_true", 
        help="Run only integration tests"
    )
    parser.add_argument(
        "--performance", action="store_true",
        help="Run only performance tests"
    )
    parser.add_argument(
        "--coverage", action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--html", action="store_true",
        help="Generate HTML coverage report"
    )
    parser.add_argument(
        "--benchmark", action="store_true",
        help="Run benchmark tests"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--fast", action="store_true",
        help="Skip slow tests"
    )
    parser.add_argument(
        "--lint", action="store_true",
        help="Run code linting"
    )
    parser.add_argument(
        "--specific", type=str,
        help="Run specific test file or function"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Check dependencies
    if not runner.check_dependencies():
        sys.exit(1)
    
    results = {}
    success = True
    
    try:
        # Run linting if requested
        if args.lint:
            lint_success = runner.lint_code()
            results['linting'] = {
                'success': lint_success,
                'duration': 0
            }
            success = success and lint_success
        
        # Run specific test if requested
        if args.specific:
            specific_success = runner.run_specific_test(args.specific, args.verbose)
            results['specific'] = {
                'success': specific_success,
                'duration': 0
            }
            success = success and specific_success
        
        # Run individual test categories
        elif args.unit:
            unit_success = runner.run_unit_tests(args.verbose, args.coverage)
            results['unit_tests'] = {
                'success': unit_success,
                'duration': 0
            }
            success = success and unit_success
        
        elif args.integration:
            integration_success = runner.run_integration_tests(args.verbose, args.coverage)
            results['integration_tests'] = {
                'success': integration_success,
                'duration': 0
            }
            success = success and integration_success
        
        elif args.performance or args.benchmark:
            perf_success = runner.run_performance_tests(args.verbose)
            results['performance_tests'] = {
                'success': perf_success,
                'duration': 0
            }
            success = success and perf_success
        
        # Generate coverage report only
        elif args.coverage:
            coverage_success = runner.generate_coverage_report(args.html)
            results['coverage'] = {
                'success': coverage_success,
                'duration': 0
            }
            success = success and coverage_success
        
        # Run all tests
        else:
            all_results = runner.run_all_tests(args.verbose, args.coverage, args.fast)
            results.update(all_results)
            
            # Also run performance tests separately if not fast mode
            if not args.fast:
                perf_success = runner.run_performance_tests(args.verbose)
                results['performance_tests'] = {
                    'success': perf_success,
                    'duration': 0
                }
                success = success and perf_success
    
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during test execution: {e}")
        sys.exit(1)
    
    # Print summary
    if results:
        overall_success = runner.print_summary(results)
        sys.exit(0 if overall_success else 1)
    else:
        print("No tests were run")
        sys.exit(1)


if __name__ == "__main__":
    main()
