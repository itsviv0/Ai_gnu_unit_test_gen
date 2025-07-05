import sys
import os
from llm_client import refactor_main_code, generate_tests_for_main
from utils.utils import clean_llm_cpp_output

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)
    print(f"Saved file: {path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python main_refactor_test.py <path_to_main_cpp>")
        sys.exit(1)

    main_path = sys.argv[1]
    if not os.path.isfile(main_path):
        print(f"Error: File {main_path} does not exist.")
        sys.exit(1)

    original_code = read_file(main_path)

    print("Calling LLM to refactor main...")
    refactored_code = refactor_main_code(original_code)

    # Save refactored main only if changed
    if refactored_code.strip() != original_code.strip():
        refactored_path = os.path.splitext(main_path)[0] + "_refactored.cpp"
        write_file(refactored_path, refactored_code)
    else:
        print("No refactoring needed.")
        refactored_path = main_path

    print("Calling LLM to generate tests...")
    test_code_raw = generate_tests_for_main(refactored_code)
    test_code = clean_llm_cpp_output(test_code_raw)
    test_file_path = os.path.join(os.path.dirname(main_path), "test_main.cpp")
    write_file(test_file_path, test_code)

if __name__ == "__main__":
    main()