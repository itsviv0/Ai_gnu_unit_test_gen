"""
Enhanced logging and progress tracking
"""

import logging
import sys
from datetime import datetime
from typing import Optional
import json
import os


class TestGenLogger:
    """Enhanced logger for test generation with progress tracking"""

    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        self.start_time = datetime.now()
        self.stats = {
            "files_processed": 0,
            "tests_generated": 0,
            "refactored_files": 0,
            "errors": 0,
            "warnings": 0,
        }

        # Setup logging
        log_format = "%(asctime)s - %(levelname)s - %(message)s"

        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            handlers=[logging.StreamHandler(sys.stdout)],
        )

        self.logger = logging.getLogger("TestGenerator")

        # Add file handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(log_format))
            self.logger.addHandler(file_handler)

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message"""
        self.stats["warnings"] += 1
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.stats["errors"] += 1
        self.logger.error(message)

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

    def log_file_processing(self, file_path: str, action: str = "processing"):
        """Log file processing with emoji"""
        if action == "processing":
            self.info(f"🔧 Processing {os.path.basename(file_path)}...")
            self.stats["files_processed"] += 1
        elif action == "refactored":
            self.info(f"♻️  Refactored {os.path.basename(file_path)}")
            self.stats["refactored_files"] += 1
        elif action == "tested":
            self.info(f"✅ Generated tests for {os.path.basename(file_path)}")
            self.stats["tests_generated"] += 1
        elif action == "skipped":
            self.warning(f"⏭️  Skipped {os.path.basename(file_path)}")

    def log_validation(self, file_path: str, is_valid: bool, message: str = ""):
        """Log validation results"""
        if is_valid:
            self.info(f"✅ Validation passed for {os.path.basename(file_path)}")
        else:
            self.error(
                f"❌ Validation failed for {os.path.basename(file_path)}: {message}"
            )

    def log_coverage(self, coverage_percent: float, threshold: float):
        """Log coverage results"""
        if coverage_percent >= threshold:
            self.info(
                f"📊 Coverage: {coverage_percent:.1f}% (✅ Above {threshold}% threshold)"
            )
        else:
            self.warning(
                f"📊 Coverage: {coverage_percent:.1f}% (⚠️  Below {threshold}% threshold)"
            )

    def print_summary(self):
        """Print final summary"""
        duration = datetime.now() - self.start_time

        print("\n" + "=" * 60)
        print("🎯 TEST GENERATION SUMMARY")
        print("=" * 60)
        print(f"⏱️  Duration: {duration}")
        print(f"📁 Files processed: {self.stats['files_processed']}")
        print(f"🧪 Tests generated: {self.stats['tests_generated']}")
        print(f"♻️  Files refactored: {self.stats['refactored_files']}")
        print(f"⚠️  Warnings: {self.stats['warnings']}")
        print(f"❌ Errors: {self.stats['errors']}")

        if self.stats["errors"] == 0:
            print("🎉 All operations completed successfully!")
        else:
            print("⚠️  Some operations had errors. Check logs for details.")
        print("=" * 60)

    def save_report(self, output_path: str):
        """Save detailed report to JSON"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "statistics": self.stats,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
        }

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        self.info(f"📄 Report saved to {output_path}")


# Progress bar utility
def show_progress(current: int, total: int, description: str = "Progress"):
    """Show simple progress bar"""
    if total == 0:
        return

    progress = current / total
    bar_length = 40
    filled_length = int(bar_length * progress)

    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    percent = progress * 100

    print(
        f"\r{description}: |{bar}| {percent:.1f}% ({current}/{total})",
        end="",
        flush=True,
    )

    if current == total:
        print()  # New line when complete
