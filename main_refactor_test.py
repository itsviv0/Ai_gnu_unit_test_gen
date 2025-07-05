import sys
import os
from llm_client import refactor_main_code, generate_tests_with_yaml
from utils.utils import clean_llm_cpp_output
import yaml

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"Saved: {path}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python main_refactor_test.py <path_to_cpp_file> <path_to_yaml>")
        sys.exit(1)

    cpp_file = sys.argv[1]
    yaml_file = sys.argv[2]

    if not os.path.isfile(cpp_file):
        print(f"Error: {cpp_file} does not exist.")
        sys.exit(1)
    if not os.path.isfile(yaml_file):
        print(f"Error: {yaml_file} does not exist.")
        sys.exit(1)

    cpp_code = read_file(cpp_file)
    yaml_str = read_file(yaml_file)

    print("Calling LLM to generate tests...")
    test_code_raw = generate_tests_with_yaml(cpp_code, yaml_str)
    test_code = clean_llm_cpp_output(test_code_raw)

    # Write test file in 'tests/' subdirectory
    file_base = os.path.splitext(os.path.basename(cpp_file))[0]
    test_path = os.path.join("tests", f"test_{file_base}.cpp")
    write_file(test_path, test_code)

if __name__ == "__main__":
    main()