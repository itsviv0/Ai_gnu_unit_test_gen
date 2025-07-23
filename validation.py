"""
Validation utilities for C++ code and test generation
"""

import subprocess
import os
import tempfile
import re


def validate_cpp_syntax(code: str, file_type: str = "cpp") -> tuple[bool, str]:
    """
    Validate C++ code syntax using g++ compiler
    Returns (is_valid, error_message)
    """
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=f".{file_type}", delete=False
        ) as f:
            f.write(code)
            temp_file = f.name

        # Try to compile without linking
        result = subprocess.run(
            ["g++", "-fsyntax-only", "-std=c++17", temp_file],
            capture_output=True,
            text=True,
        )

        os.unlink(temp_file)

        if result.returncode == 0:
            return True, ""
        else:
            return False, result.stderr

    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_test_code(test_code: str) -> tuple[bool, list[str]]:
    """
    Validate that test code contains proper Google Test structure
    Returns (is_valid, list_of_issues)
    """
    issues = []

    # Check for required includes
    if "#include <gtest/gtest.h>" not in test_code:
        issues.append("Missing required #include <gtest/gtest.h>")

    # Check for at least one test case
    if not re.search(r"TEST\s*\(", test_code):
        issues.append("No TEST cases found")

    # Check for main function (if not using gtest_main)
    has_main = "int main" in test_code
    has_gtest_main = "gtest_main" in test_code

    if not has_main and not has_gtest_main:
        issues.append("No main function found and not using gtest_main")

    return len(issues) == 0, issues


def extract_functions_from_cpp(code: str) -> list[dict]:
    """
    Extract function signatures from C++ code for better test targeting
    Returns list of {'name': str, 'signature': str, 'return_type': str}
    """
    functions = []

    # Simple regex to find function definitions (not perfect but helpful)
    function_pattern = r"(\w+(?:\s*\*)?)\s+(\w+)\s*\([^)]*\)\s*\{"

    matches = re.finditer(function_pattern, code)
    for match in matches:
        return_type = match.group(1).strip()
        func_name = match.group(2).strip()

        # Skip main function and common keywords
        if func_name not in ["main", "if", "for", "while", "switch"]:
            functions.append(
                {
                    "name": func_name,
                    "return_type": return_type,
                    "signature": match.group(0).replace("{", "").strip(),
                }
            )

    return functions
