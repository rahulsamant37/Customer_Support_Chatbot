#!/usr/bin/env python3
"""
Test runner script for the Customer Support Chatbot project.
Provides different test execution modes and reporting options.
"""

import argparse
import subprocess
import sys
import os

def run_tests(test_type="all", verbose=False, coverage=False, output_format="terminal"):
    """
    Run tests with specified parameters.
    
    Args:
        test_type (str): Type of tests to run ('unit', 'integration', 'api', 'all')
        verbose (bool): Enable verbose output
        coverage (bool): Enable coverage reporting
        output_format (str): Output format ('terminal', 'junit', 'html')
    """
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test type filter
    if test_type != "all":
        cmd.extend(["-m", test_type])
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add coverage
    if coverage:
        cmd.extend([
            "--cov=.",
            "--cov-report=term-missing"
        ])
        
        if output_format == "html":
            cmd.append("--cov-report=html:htmlcov")
        elif output_format == "xml":
            cmd.append("--cov-report=xml")
    
    # Add output format
    if output_format == "junit":
        cmd.extend(["--junit-xml=test-results.xml"])
    
    # Add test directory
    cmd.append("tests/")
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Please install pytest:")
        print("pip install pytest pytest-cov")
        return 1

def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Test runner for Customer Support Chatbot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                          # Run all tests
  python run_tests.py --type unit              # Run only unit tests
  python run_tests.py --type integration -v   # Run integration tests verbosely
  python run_tests.py --coverage --format html # Run with HTML coverage report
  python run_tests.py --type api --format junit # Run API tests with JUnit output
        """
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=["unit", "integration", "api", "slow", "all"],
        default="all",
        help="Type of tests to run (default: all)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Enable coverage reporting"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["terminal", "junit", "html", "xml"],
        default="terminal",
        help="Output format (default: terminal)"
    )
    
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install test dependencies before running"
    )
    
    args = parser.parse_args()
    
    # Install dependencies if requested
    if args.install_deps:
        print("Installing test dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "httpx>=0.24.0",  # For FastAPI testing
            "pytest-asyncio>=0.21.0"
        ], check=True)
        print("Dependencies installed successfully.")
    
    # Check if we're in the right directory
    if not os.path.exists("tests"):
        print("Error: 'tests' directory not found.")
        print("Please run this script from the project root directory.")
        return 1
    
    # Run the tests
    return_code = run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=args.coverage,
        output_format=args.format
    )
    
    # Print summary
    if return_code == 0:
        print("\n✅ All tests passed!")
        if args.coverage and args.format == "html":
            print("📊 Coverage report generated in 'htmlcov/index.html'")
    else:
        print(f"\n❌ Tests failed with exit code {return_code}")
    
    return return_code

if __name__ == "__main__":
    sys.exit(main())
