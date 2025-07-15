#!/usr/bin/env python3
"""
Static Analysis Runner for ProjectBudgetinator

This script runs all configured static analysis tools:
- MyPy for type checking
- Pylint for code quality
- Flake8 for style and basic errors  
- Bandit for security scanning
- Black for code formatting (check mode)
- isort for import sorting (check mode)
"""

import subprocess
import sys
import os
import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import time


class AnalysisResult:
    """Container for analysis results."""
    
    def __init__(self, tool: str, exit_code: int, output: str, duration: float):
        self.tool = tool
        self.exit_code = exit_code
        self.output = output
        self.duration = duration
        self.passed = exit_code == 0


class StaticAnalyzer:
    """Main static analysis runner."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_path = project_root / "src"
        self.tests_path = project_root / "tests"
        self.results: List[AnalysisResult] = []
        
    def run_command(self, cmd: List[str], tool_name: str) -> AnalysisResult:
        """Run a command and capture results."""
        print(f"\n{'='*60}")
        print(f"Running {tool_name}...")
        print(f"Command: {' '.join(cmd)}")
        print(f"{'='*60}")
        
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            duration = time.time() - start_time
            
            print(f"\n{tool_name} output:")
            print("-" * 40)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            return AnalysisResult(
                tool=tool_name,
                exit_code=result.returncode,
                output=result.stdout + result.stderr,
                duration=duration
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"{tool_name} timed out after 5 minutes!")
            return AnalysisResult(
                tool=tool_name,
                exit_code=124,  # Timeout exit code
                output=f"{tool_name} execution timed out",
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            print(f"Error running {tool_name}: {e}")
            return AnalysisResult(
                tool=tool_name,
                exit_code=1,
                output=str(e),
                duration=duration
            )
    
    def run_mypy(self) -> AnalysisResult:
        """Run MyPy type checking."""
        cmd = ["python", "-m", "mypy", "src/", "--config-file", "mypy.ini"]
        return self.run_command(cmd, "MyPy")
    
    def run_pylint(self) -> AnalysisResult:
        """Run Pylint code quality analysis."""
        cmd = ["python", "-m", "pylint", "src/", "--rcfile", ".pylintrc"]
        return self.run_command(cmd, "Pylint")
    
    def run_flake8(self) -> AnalysisResult:
        """Run Flake8 style checking."""
        cmd = ["python", "-m", "flake8", "src/", "--config", ".flake8"]
        return self.run_command(cmd, "Flake8")
    
    def run_bandit(self) -> AnalysisResult:
        """Run Bandit security scanning."""
        cmd = ["python", "-m", "bandit", "-r", "src/", "-c", ".bandit", "-f", "txt"]
        return self.run_command(cmd, "Bandit")
    
    def run_black_check(self) -> AnalysisResult:
        """Run Black code formatting check."""
        cmd = ["python", "-m", "black", "--check", "--diff", "src/"]
        return self.run_command(cmd, "Black (check)")
    
    def run_isort_check(self) -> AnalysisResult:
        """Run isort import sorting check."""
        cmd = ["python", "-m", "isort", "--check-only", "--diff", "src/"]
        return self.run_command(cmd, "isort (check)")
    
    def run_all_tools(self, selected_tools: Optional[List[str]] = None) -> List[AnalysisResult]:
        """Run all or selected static analysis tools."""
        available_tools = {
            "mypy": self.run_mypy,
            "pylint": self.run_pylint,
            "flake8": self.run_flake8,
            "bandit": self.run_bandit,
            "black": self.run_black_check,
            "isort": self.run_isort_check,
        }
        
        if selected_tools:
            tools_to_run = {k: v for k, v in available_tools.items() if k in selected_tools}
        else:
            tools_to_run = available_tools
        
        print(f"Running static analysis on: {self.project_root}")
        print(f"Tools: {', '.join(tools_to_run.keys())}")
        
        for tool_name, tool_func in tools_to_run.items():
            result = tool_func()
            self.results.append(result)
        
        return self.results
    
    def generate_summary(self) -> str:
        """Generate a summary of all results."""
        summary = []
        summary.append("\n" + "="*80)
        summary.append("STATIC ANALYSIS SUMMARY")
        summary.append("="*80)
        
        total_duration = sum(r.duration for r in self.results)
        passed_count = sum(1 for r in self.results if r.passed)
        failed_count = len(self.results) - passed_count
        
        summary.append(f"Total tools run: {len(self.results)}")
        summary.append(f"Passed: {passed_count}")
        summary.append(f"Failed: {failed_count}")
        summary.append(f"Total time: {total_duration:.2f} seconds")
        summary.append("")
        
        for result in self.results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            summary.append(f"{result.tool:15} | {status:8} | {result.duration:6.2f}s | Exit: {result.exit_code}")
        
        summary.append("")
        
        if failed_count > 0:
            summary.append("FAILED TOOLS:")
            summary.append("-" * 40)
            for result in self.results:
                if not result.passed:
                    summary.append(f"\n{result.tool}:")
                    summary.append(f"Exit code: {result.exit_code}")
                    if result.output:
                        # Truncate output if too long
                        output = result.output[:1000] + "..." if len(result.output) > 1000 else result.output
                        summary.append(f"Output: {output}")
        
        summary.append("\n" + "="*80)
        
        return "\n".join(summary)
    
    def save_results_json(self, output_file: Path):
        """Save results to JSON file."""
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "project_root": str(self.project_root),
            "summary": {
                "total_tools": len(self.results),
                "passed": sum(1 for r in self.results if r.passed),
                "failed": sum(1 for r in self.results if not r.passed),
                "total_duration": sum(r.duration for r in self.results)
            },
            "results": [
                {
                    "tool": r.tool,
                    "passed": r.passed,
                    "exit_code": r.exit_code,
                    "duration": r.duration,
                    "output": r.output
                }
                for r in self.results
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run static analysis tools")
    parser.add_argument(
        "--tools",
        nargs="+",
        choices=["mypy", "pylint", "flake8", "bandit", "black", "isort"],
        help="Specific tools to run (default: all)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default="build/static_analysis_results.json",
        help="Output file for JSON results"
    )
    parser.add_argument(
        "--no-summary",
        action="store_true",
        help="Skip printing summary"
    )
    
    args = parser.parse_args()
    
    # Find project root
    current_dir = Path.cwd()
    project_root = current_dir
    
    # Look for pyproject.toml or src/ directory to confirm project root
    if not (project_root / "pyproject.toml").exists() and not (project_root / "src").exists():
        print("Warning: Cannot find pyproject.toml or src/ directory. Using current directory as project root.")
    
    # Create output directory
    args.output.parent.mkdir(exist_ok=True)
    
    # Run analysis
    analyzer = StaticAnalyzer(project_root)
    results = analyzer.run_all_tools(args.tools)
    
    # Generate and display summary
    if not args.no_summary:
        summary = analyzer.generate_summary()
        print(summary)
    
    # Save results to JSON
    analyzer.save_results_json(args.output)
    
    # Exit with error code if any tool failed
    exit_code = 0 if all(r.passed for r in results) else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
