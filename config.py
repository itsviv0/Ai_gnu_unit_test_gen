"""
Configuration management for the test generator
"""

import yaml
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class TestGenConfig:
    """Configuration class for test generation"""

    # LLM Settings
    llm_model: str = "xai/grok-3"
    llm_temperature: float = 0.7
    llm_top_p: float = 0.95
    llm_max_retries: int = 3

    # Test Generation
    test_framework: str = "gtest"
    target_coverage: float = 80.0
    include_edge_cases: bool = True
    include_performance_tests: bool = False
    max_tests_per_function: int = 5

    # File Handling
    excluded_dirs: List[str] = field(
        default_factory=lambda: ["tests", "refactored", ".git", "build"]
    )
    supported_extensions: List[str] = field(
        default_factory=lambda: [".cpp", ".cc", ".c"]
    )
    output_test_dir: str = "tests"
    output_refactored_dir: str = "refactored"

    # Validation
    validate_syntax: bool = True
    validate_compilation: bool = True
    auto_fix_issues: bool = True

    # Coverage Settings
    use_coverage: bool = True
    coverage_format: str = "html"  # html, xml, json
    coverage_threshold: float = 75.0

    @classmethod
    def load_from_file(cls, config_path: str) -> "TestGenConfig":
        """Load configuration from YAML file"""
        if not os.path.exists(config_path):
            print(f"Config file {config_path} not found, using defaults")
            return cls()

        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        return cls(**config_data)

    def save_to_file(self, config_path: str):
        """Save configuration to YAML file"""
        config_dict = {
            "llm_model": self.llm_model,
            "llm_temperature": self.llm_temperature,
            "llm_top_p": self.llm_top_p,
            "llm_max_retries": self.llm_max_retries,
            "test_framework": self.test_framework,
            "target_coverage": self.target_coverage,
            "include_edge_cases": self.include_edge_cases,
            "include_performance_tests": self.include_performance_tests,
            "max_tests_per_function": self.max_tests_per_function,
            "excluded_dirs": self.excluded_dirs,
            "supported_extensions": self.supported_extensions,
            "output_test_dir": self.output_test_dir,
            "output_refactored_dir": self.output_refactored_dir,
            "validate_syntax": self.validate_syntax,
            "validate_compilation": self.validate_compilation,
            "auto_fix_issues": self.auto_fix_issues,
            "use_coverage": self.use_coverage,
            "coverage_format": self.coverage_format,
            "coverage_threshold": self.coverage_threshold,
        }

        with open(config_path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False)


def create_default_config():
    """Create a default configuration file"""
    config = TestGenConfig()
    config.save_to_file("config.yaml")
    print("Created default config.yaml file")
