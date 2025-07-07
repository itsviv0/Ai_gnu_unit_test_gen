import os
import sys
from utils.utils import find_cpp_files
from llm_client import (
    refactor_main_code,
    generate_tests_with_yaml,
    refine_generated_tests,
)

def read_file(path):
    with open(path, "r") as f:
        return f.read()

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"Saved: {path}")

def generate_and_refine_tests(project_root, yaml_path):
    yaml_str = read_file(yaml_path)
    cpp_files = find_cpp_files(project_root)

    for cpp_file in cpp_files:
        file_base = os.path.splitext(os.path.basename(cpp_file))[0]
        print(f"\n🔧 Processing {cpp_file}...")

        original_code = read_file(cpp_file)
        refactored_code = refactor_main_code(original_code)

        # Save refactored file if different
        if refactored_code.strip() != original_code.strip():
            refactored_path = cpp_file.replace(project_root, os.path.join(project_root, "refactored"))
            write_file(refactored_path, refactored_code)
        else:
            refactored_code = original_code  # fallback to original if unchanged

        # Step 1: Generate test file
        test_code = generate_tests_with_yaml(refactored_code, yaml_str)
        test_file_path = os.path.join(project_root, "tests", f"test_{file_base}.cpp")
        write_file(test_file_path, test_code)

        # Step 2: Refine the generated test file
        print(f"🎯 Refining tests for {file_base}.cpp")
        refined_code = refine_generated_tests(test_code, yaml_str)
        write_file(test_file_path, refined_code)

def main():
    if len(sys.argv) != 3:
        print("Usage: python main_batch_test_generator.py <project_root> <yaml_rules_path>")
        sys.exit(1)

    project_root = sys.argv[1]
    yaml_path = sys.argv[2]

    if not os.path.isdir(project_root):
        print(f"Error: {project_root} is not a directory.")
        sys.exit(1)
    if not os.path.isfile(yaml_path):
        print(f"Error: {yaml_path} does not exist.")
        sys.exit(1)

    generate_and_refine_tests(project_root, yaml_path)

if __name__ == "__main__":
    main()
