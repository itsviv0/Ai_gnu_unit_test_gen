# AI GNU Unit Test Generator - Advanced Edition

This tool automatically generates, refines, and integrates C++ unit tests using AI (GitHub's xai/grok-3) with advanced features including validation, coverage analysis, comprehensive logging, and intelligent retry mechanisms.

## ✨ Enhanced Features

### Core Capabilities

- ✅ **AI-Powered Test Generation** - Uses GitHub's xai/grok-3 for intelligent test creation
- ✅ **Google Test Integration** - Full Google Test framework support with best practices
- ✅ **Smart Code Refactoring** - Non-breaking refactoring before test generation
- ✅ **YAML-Based Configuration** - Flexible, customizable rule-based generation
- ✅ **Batch Processing** - Handle entire C++ projects automatically

### Advanced Features

- 🔥 **Syntax Validation** - Automatic C++ syntax checking with compiler integration
- 🔥 **Intelligent Retry Logic** - Auto-retry failed operations with different approaches
- 🔥 **Coverage Analysis** - Integrated gcov/lcov coverage reporting with HTML output
- 🔥 **Enhanced Logging** - Comprehensive progress tracking and detailed reporting
- 🔥 **Configuration Management** - Advanced YAML configuration system
- 🔥 **Function Analysis** - Smart extraction and targeting of functions for testing
- 🔥 **Error Recovery** - Robust error handling and recovery mechanisms

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/itsviv0/Ai_gnu_unit_test_gen.git
cd Ai_gnu_unit_test_gen

# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt install g++ gcov lcov build-essential

# Set up GitHub token
export GITHUB_TOKEN=your_github_pat_here
```

### 2. Create Configuration

```bash
# Generate default configuration
python advanced_test_generator.py . config.yaml --create-config
```

### 3. Run Demo

```bash
# Run comprehensive demo
python demo.py
```

### 4. Generate Tests for Your Project

```bash
# Basic usage
python advanced_test_generator.py /path/to/your/cpp/project config.yaml

# With debug logging
python advanced_test_generator.py /path/to/your/cpp/project config.yaml --log-level DEBUG

# Dry run (analyze without generating)
python advanced_test_generator.py /path/to/your/cpp/project config.yaml --dry-run
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
