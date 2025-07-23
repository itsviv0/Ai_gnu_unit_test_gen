#!/usr/bin/env python3
"""
Demo script to showcase advanced test generator features
"""
import os
import sys
import subprocess
from pathlib import Path


def run_demo():
    """Run a comprehensive demo of the test generator"""
    print("🎭 AI GNU Unit Test Generator - Advanced Demo")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("advanced_test_generator.py").exists():
        print("❌ Please run this demo from the project root directory")
        return 1

    # Step 1: Create default config if it doesn't exist
    if not Path("config.yaml").exists():
        print("📋 Creating default configuration...")
        result = subprocess.run(
            [
                sys.executable,
                "advanced_test_generator.py",
                ".",
                "config.yaml",
                "--create-config",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✅ Configuration created")
        else:
            print("❌ Failed to create configuration")
            return 1

    # Step 2: Dry run analysis
    print("\n🔍 Analyzing sample project structure...")
    result = subprocess.run(
        [
            sys.executable,
            "advanced_test_generator.py",
            "sample_project",
            "config.yaml",
            "--dry-run",
        ],
        capture_output=True,
        text=True,
    )
    print(result.stdout)

    # Step 3: Generate tests for sample project
    print("\n🚀 Generating tests for sample project...")
    result = subprocess.run(
        [
            sys.executable,
            "advanced_test_generator.py",
            "sample_project",
            "config.yaml",
            "--log-level",
            "INFO",
        ]
    )

    if result.returncode == 0:
        print("\n✅ Test generation completed successfully!")

        # Show generated files
        test_dir = Path("sample_project/tests")
        if test_dir.exists():
            print(f"\n📁 Generated test files in {test_dir}:")
            for test_file in test_dir.glob("*.cpp"):
                print(f"  - {test_file.name}")

        refactored_dir = Path("sample_project/refactored")
        if refactored_dir.exists():
            print(f"\n♻️  Refactored files in {refactored_dir}:")
            for ref_file in refactored_dir.glob("*"):
                print(f"  - {ref_file.name}")

        # Show coverage report if generated
        coverage_dir = Path("sample_project/coverage")
        if coverage_dir.exists():
            html_report = coverage_dir / "html_report" / "index.html"
            if html_report.exists():
                print(f"\n📊 Coverage report available at: {html_report}")
                print("   Open this file in your browser to view detailed coverage")

        print("\n🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("  1. Review generated tests in sample_project/tests/")
        print("  2. Compile and run tests with coverage")
        print("  3. Customize config.yaml for your projects")
        print("  4. Run on your own C++ projects!")

    else:
        print("❌ Test generation failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(run_demo())
