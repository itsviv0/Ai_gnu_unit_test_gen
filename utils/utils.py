import re
import os


def clean_llm_cpp_output(response: str) -> str:
    """
    Extract C++ code block from markdown-like LLM response.
    Strips explanations and markdown formatting.
    """
    if not response:
        return ""

    # Try to find code blocks with different language specifiers
    patterns = [
        r"```cpp\n(.*?)```",
        r"```c\+\+\n(.*?)```",
        r"```c\n(.*?)```",
        r"```cc\n(.*?)```",
        r"```h\n(.*?)```",
        r"```\n(.*?)```",  # Generic code block
        r"```(.*?)```",  # Code block without language
    ]

    for pattern in patterns:
        code_match = re.search(pattern, response, re.DOTALL)
        if code_match:
            extracted_code = code_match.group(1).strip()
            # Basic validation that this looks like C++ code
            if any(
                keyword in extracted_code
                for keyword in [
                    "#include",
                    "int ",
                    "void ",
                    "class ",
                    "struct ",
                    "TEST(",
                ]
            ):
                return extracted_code

    # If no code blocks found, check if the entire response looks like C++ code
    response_stripped = response.strip()
    if any(
        keyword in response_stripped
        for keyword in ["#include", "int main", "void ", "class ", "struct ", "TEST("]
    ):
        return response_stripped

    # Fallback: return the response as-is but warn
    print(
        "Warning: Could not extract clean C++ code from LLM response, using full response"
    )
    return response_stripped


def find_cpp_files(root_dir, exclude_dirs=None):
    valid_exts = (".cpp", ".cc", ".c")
    exclude_dirs = set(exclude_dirs or ["tests", "refactored"])
    cpp_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for file in filenames:
            if file.endswith(valid_exts):
                full_path = os.path.join(dirpath, file)
                cpp_files.append(full_path)

    return cpp_files
