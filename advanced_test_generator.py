#!/usr/bin/env python3
"""
Advanced AI-powered C++ Unit Test Generator
Enhanced version with validation, coverage, and comprehensive reporting
"""
import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional

# Import our modules
from utils.utils import find_cpp_files
from llm_client import (
    refactor_main_code,
    generate_tests_with_yaml,
    refine_generated_tests,
)
from config import TestGenConfig, create_default_config
from logger import TestGenLogger, show_progress
from validation import (
    validate_cpp_syntax,
    validate_test_code,
    extract_functions_from_cpp,
)
from coverage_analyzer import CoverageAnalyzer


class AdvancedTestGenerator:
    """Advanced test generator with enhanced features"""

    def __init__(self, project_root: str, config_path: str, log_level: str = "INFO"):
        self.project_root = Path(project_root).resolve()
        self.config = TestGenConfig.load_from_file(config_path)
        self.logger = TestGenLogger(
            log_level, f"{self.project_root}/test_generation.log"
        )
        self.coverage_analyzer = CoverageAnalyzer(str(self.project_root))

        # Create output directories
        self.test_dir = self.project_root / self.config.output_test_dir
        self.refactored_dir = self.project_root / self.config.output_refactored_dir
        self.test_dir.mkdir(exist_ok=True)

        self.logger.info(
            f"🚀 Starting advanced test generation for {self.project_root}"
        )
        self.logger.info(f"📋 Configuration loaded from {config_path}")

    def read_file(self, path: Path) -> str:
        """Read file content safely"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Failed to read {path}: {e}")
            return ""

    def write_file(self, path: Path, content: str) -> bool:
        """Write file content safely"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self.logger.debug(f"✅ Saved: {path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write {path}: {e}")
            return False

    def analyze_cpp_file(self, file_path: Path) -> dict:
        """Analyze C++ file to extract functions and metadata"""
        code = self.read_file(file_path)
        functions = extract_functions_from_cpp(code)

        return {
            "path": file_path,
            "functions": functions,
            "lines": len(code.splitlines()),
            "size_bytes": len(code.encode("utf-8")),
        }

    def refactor_code_with_validation(
        self, original_code: str, file_path: Path
    ) -> tuple[str, bool]:
        """Refactor code with validation"""
        if not self.config.validate_syntax:
            refactored = refactor_main_code(original_code)
            return refactored, True

        # Try refactoring with retries
        for attempt in range(self.config.llm_max_retries):
            self.logger.debug(f"Refactoring attempt {attempt + 1} for {file_path.name}")

            refactored = refactor_main_code(original_code)

            # Validate syntax
            is_valid, error_msg = validate_cpp_syntax(refactored)

            if is_valid:
                self.logger.log_validation(str(file_path), True)
                return refactored, True
            else:
                self.logger.log_validation(str(file_path), False, error_msg)
                if attempt == self.config.llm_max_retries - 1:
                    self.logger.warning(
                        f"Refactoring failed after {self.config.llm_max_retries} attempts, using original"
                    )
                    return original_code, False

        return original_code, False

    def generate_tests_with_validation(
        self, code: str, file_path: Path
    ) -> tuple[str, bool]:
        """Generate tests with validation and retries"""
        yaml_content = self.read_file(Path("strict_test_rules.yaml"))

        for attempt in range(self.config.llm_max_retries):
            self.logger.debug(
                f"Test generation attempt {attempt + 1} for {file_path.name}"
            )

            # Generate tests
            test_code = generate_tests_with_yaml(code, yaml_content)

            if not test_code.strip():
                self.logger.error(f"Empty test code generated for {file_path.name}")
                continue

            # Validate test structure
            is_valid, issues = validate_test_code(test_code)

            if is_valid and self.config.validate_syntax:
                # Also validate C++ syntax
                syntax_valid, syntax_error = validate_cpp_syntax(test_code)
                if syntax_valid:
                    return test_code, True
                else:
                    self.logger.warning(
                        f"Test syntax validation failed: {syntax_error}"
                    )
            elif is_valid:
                return test_code, True
            else:
                self.logger.warning(f"Test validation issues: {', '.join(issues)}")

        self.logger.error(
            f"Failed to generate valid tests for {file_path.name} after {self.config.llm_max_retries} attempts"
        )
        return "", False

    def refine_tests_with_validation(
        self, test_code: str, file_path: Path
    ) -> tuple[str, bool]:
        """Refine tests with validation"""
        yaml_content = self.read_file(Path("strict_test_rules.yaml"))

        for attempt in range(self.config.llm_max_retries):
            self.logger.debug(
                f"Test refinement attempt {attempt + 1} for {file_path.name}"
            )

            refined_code = refine_generated_tests(test_code, yaml_content)

            # Validate refined tests
            is_valid, issues = validate_test_code(refined_code)

            if is_valid:
                if self.config.validate_syntax:
                    syntax_valid, _ = validate_cpp_syntax(refined_code)
                    if syntax_valid:
                        return refined_code, True
                else:
                    return refined_code, True
            else:
                self.logger.warning(
                    f"Refined test validation issues: {', '.join(issues)}"
                )

        self.logger.warning(
            f"Test refinement failed, using original generated tests for {file_path.name}"
        )
        return test_code, False

    def process_file(self, cpp_file: Path) -> bool:
        """Process a single C++ file"""
        self.logger.log_file_processing(str(cpp_file), "processing")

        # Analyze file
        file_analysis = self.analyze_cpp_file(cpp_file)
        self.logger.debug(
            f"Found {len(file_analysis['functions'])} functions in {cpp_file.name}"
        )

        # Read original code
        original_code = self.read_file(cpp_file)
        if not original_code.strip():
            self.logger.error(f"Empty or unreadable file: {cpp_file}")
            return False

        # Refactor if enabled
        refactored_code = original_code
        if (
            self.config.test_framework == "gtest"
        ):  # Assuming refactor is enabled for gtest
            refactored_code, refactor_success = self.refactor_code_with_validation(
                original_code, cpp_file
            )

            # Save refactored file if different and successful
            if refactor_success and refactored_code.strip() != original_code.strip():
                refactored_path = self.refactored_dir / cpp_file.relative_to(
                    self.project_root
                )
                if self.write_file(refactored_path, refactored_code):
                    self.logger.log_file_processing(str(cpp_file), "refactored")

        # Generate tests
        test_code, test_success = self.generate_tests_with_validation(
            refactored_code, cpp_file
        )
        if not test_success:
            return False

        # Save initial test file
        test_file_name = f"test_{cpp_file.stem}.cpp"
        test_file_path = self.test_dir / test_file_name

        if not self.write_file(test_file_path, test_code):
            return False

        # Refine tests
        refined_code, refine_success = self.refine_tests_with_validation(
            test_code, cpp_file
        )

        # Save refined tests
        if self.write_file(test_file_path, refined_code):
            self.logger.log_file_processing(str(cpp_file), "tested")
            return True

        return False

    def run_coverage_analysis(self) -> Optional[dict]:
        """Run complete coverage analysis"""
        if not self.config.use_coverage:
            self.logger.info("Coverage analysis disabled in config")
            return None

        self.logger.info("📊 Starting coverage analysis...")

        # Find source and test files
        source_files = find_cpp_files(
            str(self.project_root), exclude_dirs=self.config.excluded_dirs
        )
        test_files = list(self.test_dir.glob("test_*.cpp"))

        if not test_files:
            self.logger.warning("No test files found for coverage analysis")
            return None

        # Compile with coverage
        self.logger.info("🔨 Compiling with coverage flags...")
        compile_success, compile_msg = self.coverage_analyzer.compile_with_coverage(
            [str(f) for f in source_files], [str(f) for f in test_files]
        )

        if not compile_success:
            self.logger.error(f"Coverage compilation failed: {compile_msg}")
            return None

        # Run tests
        self.logger.info("🧪 Running tests for coverage...")
        test_success, test_output = self.coverage_analyzer.run_tests()

        if not test_success:
            self.logger.error(f"Test execution failed: {test_output}")
            return None

        self.logger.info("Test execution successful")

        # Generate coverage report
        self.logger.info(
            f"📈 Generating {self.config.coverage_format} coverage report..."
        )
        report_success, report_msg = self.coverage_analyzer.generate_coverage_report(
            self.config.coverage_format
        )

        if report_success:
            self.logger.info(f"Coverage report generated: {report_msg}")

            # Open HTML report if requested
            if self.config.coverage_format == "html":
                self.coverage_analyzer.open_html_report()

            return {"success": True, "message": report_msg}
        else:
            self.logger.error(f"Coverage report generation failed: {report_msg}")
            return {"success": False, "message": report_msg}

    def generate_all_tests(self) -> bool:
        """Main method to generate all tests"""
        # Find all C++ files
        cpp_files = [
            Path(f)
            for f in find_cpp_files(str(self.project_root), self.config.excluded_dirs)
        ]

        if not cpp_files:
            self.logger.error("No C++ files found in the project")
            return False

        self.logger.info(f"📁 Found {len(cpp_files)} C++ files to process")

        # Process each file
        success_count = 0
        for i, cpp_file in enumerate(cpp_files):
            show_progress(i, len(cpp_files), "Processing files")

            if self.process_file(cpp_file):
                success_count += 1
            else:
                self.logger.log_file_processing(str(cpp_file), "skipped")

        show_progress(len(cpp_files), len(cpp_files), "Processing files")

        self.logger.info(
            f"✅ Successfully processed {success_count}/{len(cpp_files)} files"
        )

        # Run coverage analysis if enabled
        coverage_result = self.run_coverage_analysis()

        # Generate final report
        self.logger.print_summary()
        self.logger.save_report(str(self.project_root / "test_generation_report.json"))

        return success_count > 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Advanced AI-powered C++ Unit Test Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("project_root", help="Path to the C++ project root directory")
    parser.add_argument("config_path", help="Path to the configuration YAML file")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )
    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Create a default configuration file and exit",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze project without generating tests",
    )

    args = parser.parse_args()

    if args.create_config:
        create_default_config()
        print("✅ Default configuration created as 'config.yaml'")
        print("Edit this file to customize test generation settings.")
        return 0

    # Validate inputs
    if not os.path.isdir(args.project_root):
        print(f"❌ Error: {args.project_root} is not a directory.")
        return 1

    if not os.path.isfile(args.config_path):
        print(f"❌ Error: {args.config_path} does not exist.")
        print("💡 Use --create-config to generate a default configuration file.")
        return 1

    try:
        # Initialize and run generator
        generator = AdvancedTestGenerator(
            args.project_root, args.config_path, args.log_level
        )

        if args.dry_run:
            print("🔍 Dry run mode - analyzing project structure...")
            cpp_files = find_cpp_files(args.project_root)
            print(f"📁 Found {len(cpp_files)} C++ files:")
            for f in cpp_files:
                print(f"  - {f}")
            return 0

        success = generator.generate_all_tests()
        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
