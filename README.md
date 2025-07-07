# Ai_gnu_unit_test_gen
This tool automatically generates, refines, and integrates C++ unit tests using a GitHub-hosted LLM (xai/grok-3) with support for YAML strict rules, project-wide batching, and GNU test coverage tools like gcov and lcov.

## ✨ Features
- ✅ Automatically generates Google Test–based unit tests for .cpp, .cc, .c files
- ✅ Follows configurable YAML-based strict test generation rules
- ✅ Refactors main files before testing (non-breaking)
- ✅ Refines generated tests to remove duplicates, add missing includes, and improve formatting
- ✅ Integrates cleanly with GNU coverage tools (gcov / lcov)
- ✅ Batch-processing for entire C++ projects
- ✅ LLM-powered via xai/grok-3 from GitHub AI (PAT required)

## Usage

1. Export GitHub PAT

    ```bash
        export GITHUB_TOKEN=your_pat_here
    ```

2. Install dependencies

    ```bash
    pip install azure-ai-inference pyyaml
    sudo apt install g++ gcov lcov
    ```

3. Run the tests generator

    ```bash
        python main_batch_test_generator.py /path/to/your/project strict_test_rules.yaml
    ```

4. You will recieve the following output:
    ```
    you_c_project/
    ├── refactored/         # (might not be generated if Grok finds your code good enough) refactored source files
    ├── tests/              # generated and refined Google Test files
    │   └── test_main.cpp
    │   └── test_xyz.cpp
    .
    .
    .
    .
    .
    /other source project files
    ```

## Compile with GCov Flags

1. Navigate to the generated project and compile:

    ```bash
    cd /full/path/to/my_sample_project
    ```

2. Complie

    ```bash
    g++ -fprofile-arcs -ftest-coverage -O0 -std=c++17 \
    your_code.cpp tests/test_your_code.cpp \
    -lgtest -lgtest_main -pthread -o test_app --coverage
    ```

3. Run the tests

    ```bash
    ./test_app
    ```

4. Generate HTML report:

    ```bash
    lcov --directory . --capture --output-file coverage.info
    genhtml coverage.info --output-directory coverage_report
    xdg-open coverage_report/index.html
    ```