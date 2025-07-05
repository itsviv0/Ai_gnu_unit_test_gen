import re

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
