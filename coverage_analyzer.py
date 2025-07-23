"""
Coverage analysis and reporting utilities
"""

import subprocess
import os
import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CoverageResult:
    """Coverage analysis result"""

    file_path: str
    lines_total: int
    lines_covered: int
    coverage_percent: float
    uncovered_lines: List[int]


class CoverageAnalyzer:
    """Analyze code coverage using gcov and lcov"""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.coverage_dir = os.path.join(project_root, "coverage")
        os.makedirs(self.coverage_dir, exist_ok=True)

    def compile_with_coverage(
        self,
        source_files: List[str],
        test_files: List[str],
        output_binary: str = "test_runner",
    ) -> Tuple[bool, str]:
        """Compile source and test files with coverage flags"""
        try:
            compile_cmd = [
                "g++",
                "-fprofile-arcs",
                "-ftest-coverage",
                "-O0",
                "-std=c++17",
                *source_files,
                *test_files,
                "-lgtest",
                "-lgtest_main",
                "-pthread",
                "-o",
                os.path.join(self.coverage_dir, output_binary),
                "--coverage",
            ]

            result = subprocess.run(
                compile_cmd, capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode == 0:
                return True, "Compilation successful"
            else:
                return False, f"Compilation failed: {result.stderr}"

        except Exception as e:
            return False, f"Compilation error: {str(e)}"

    def run_tests(self, binary_name: str = "test_runner") -> Tuple[bool, str]:
        """Run the test binary"""
        try:
            binary_path = os.path.join(self.coverage_dir, binary_name)
            if not os.path.exists(binary_path):
                return False, f"Test binary {binary_path} not found"

            result = subprocess.run(
                [binary_path], capture_output=True, text=True, cwd=self.coverage_dir
            )

            return result.returncode == 0, (
                result.stdout if result.returncode == 0 else result.stderr
            )

        except Exception as e:
            return False, f"Test execution error: {str(e)}"

    def generate_coverage_report(self, format_type: str = "html") -> Tuple[bool, str]:
        """Generate coverage report using lcov"""
        try:
            # Capture coverage data
            lcov_cmd = [
                "lcov",
                "--directory",
                ".",
                "--capture",
                "--output-file",
                "coverage.info",
            ]
            result = subprocess.run(
                lcov_cmd, capture_output=True, text=True, cwd=self.coverage_dir
            )

            if result.returncode != 0:
                return False, f"lcov capture failed: {result.stderr}"

            if format_type == "html":
                # Generate HTML report
                genhtml_cmd = [
                    "genhtml",
                    "coverage.info",
                    "--output-directory",
                    "html_report",
                ]
                result = subprocess.run(
                    genhtml_cmd, capture_output=True, text=True, cwd=self.coverage_dir
                )

                if result.returncode == 0:
                    report_path = os.path.join(
                        self.coverage_dir, "html_report", "index.html"
                    )
                    return True, f"HTML report generated: {report_path}"
                else:
                    return False, f"genhtml failed: {result.stderr}"

            elif format_type == "json":
                # Convert to JSON using lcov --summary
                return self._generate_json_report()

            else:
                return False, f"Unsupported format: {format_type}"

        except Exception as e:
            return False, f"Coverage report generation error: {str(e)}"

    def _generate_json_report(self) -> Tuple[bool, str]:
        """Generate JSON coverage report"""
        try:
            # Get summary from lcov
            summary_cmd = ["lcov", "--summary", "coverage.info"]
            result = subprocess.run(
                summary_cmd, capture_output=True, text=True, cwd=self.coverage_dir
            )

            if result.returncode != 0:
                return False, f"lcov summary failed: {result.stderr}"

            # Parse lcov summary output
            coverage_data = self._parse_lcov_summary(result.stdout)

            # Save to JSON
            json_path = os.path.join(self.coverage_dir, "coverage_report.json")
            with open(json_path, "w") as f:
                json.dump(coverage_data, f, indent=2)

            return True, f"JSON report generated: {json_path}"

        except Exception as e:
            return False, f"JSON report generation error: {str(e)}"

    def _parse_lcov_summary(self, summary_output: str) -> Dict:
        """Parse lcov summary output into structured data"""
        lines = summary_output.split("\n")
        coverage_data = {"overall": {}, "files": []}

        for line in lines:
            if "lines......:" in line:
                # Parse overall line coverage
                match = re.search(r"(\d+\.\d+)%.*\((\d+) of (\d+)", line)
                if match:
                    coverage_data["overall"]["line_coverage"] = float(match.group(1))
                    coverage_data["overall"]["lines_covered"] = int(match.group(2))
                    coverage_data["overall"]["lines_total"] = int(match.group(3))

            elif "functions..:" in line:
                # Parse function coverage
                match = re.search(r"(\d+\.\d+)%.*\((\d+) of (\d+)", line)
                if match:
                    coverage_data["overall"]["function_coverage"] = float(
                        match.group(1)
                    )
                    coverage_data["overall"]["functions_covered"] = int(match.group(2))
                    coverage_data["overall"]["functions_total"] = int(match.group(3))

        return coverage_data

    def get_coverage_for_file(self, file_path: str) -> Optional[CoverageResult]:
        """Get detailed coverage information for a specific file"""
        try:
            # Use gcov to get file-specific coverage
            gcov_cmd = ["gcov", file_path]
            result = subprocess.run(
                gcov_cmd, capture_output=True, text=True, cwd=self.coverage_dir
            )

            if result.returncode != 0:
                return None

            # Parse gcov output
            gcov_file = file_path + ".gcov"
            if os.path.exists(os.path.join(self.coverage_dir, gcov_file)):
                return self._parse_gcov_file(
                    os.path.join(self.coverage_dir, gcov_file), file_path
                )

            return None

        except Exception:
            return None

    def _parse_gcov_file(self, gcov_path: str, original_file: str) -> CoverageResult:
        """Parse .gcov file to extract coverage information"""
        lines_total = 0
        lines_covered = 0
        uncovered_lines = []

        with open(gcov_path, "r") as f:
            for line_num, line in enumerate(f, 1):
                if line.strip().startswith("-:") or line.strip().startswith("#####:"):
                    continue

                parts = line.split(":", 2)
                if len(parts) >= 3:
                    execution_count = parts[0].strip()
                    source_line_num = parts[1].strip()

                    if source_line_num.isdigit():
                        lines_total += 1
                        if execution_count == "#####":
                            uncovered_lines.append(int(source_line_num))
                        elif execution_count.isdigit() and int(execution_count) > 0:
                            lines_covered += 1

        coverage_percent = (lines_covered / lines_total * 100) if lines_total > 0 else 0

        return CoverageResult(
            file_path=original_file,
            lines_total=lines_total,
            lines_covered=lines_covered,
            coverage_percent=coverage_percent,
            uncovered_lines=uncovered_lines,
        )

    def cleanup_coverage_files(self):
        """Clean up generated coverage files"""
        try:
            # Remove .gcda and .gcno files
            for root, dirs, files in os.walk(self.project_root):
                for file in files:
                    if file.endswith((".gcda", ".gcno", ".gcov")):
                        os.remove(os.path.join(root, file))
        except Exception as e:
            print(f"Warning: Could not clean up coverage files: {e}")

    def open_html_report(self):
        """Open HTML coverage report in browser"""
        html_report = os.path.join(self.coverage_dir, "html_report", "index.html")
        if os.path.exists(html_report):
            try:
                subprocess.run(["xdg-open", html_report], check=False)
                return True
            except:
                print(f"Please open {html_report} in your browser")
                return False
        return False
