import re
import os

def clean_llm_cpp_output(response: str) -> str:
    """
    Extract C++ code block from markdown-like LLM response.
    Strips explanations and markdown formatting.
    """
    
    code_match = re.search(r"```cpp\n(.*?)```", response, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()
    
    code_match = re.search(r"```c\n(.*?)```", response, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()

    code_match = re.search(r"```cc\n(.*?)```", response, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()

    # if no backticks, assume entire response is code
    return response.strip()



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