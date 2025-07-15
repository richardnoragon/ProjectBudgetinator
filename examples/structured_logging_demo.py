#!/usr/bin/env python3
"""
Demonstration of the structured logging system implemented for ProjectBudgetinator.

This script shows how to use the structured logging features including:
- Operation context tracking
- User context
- Correlation IDs
- Structured log formats
- JSON and traditional formatting
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from logger import (
    setup_logging, 
    get_structured_logger, 
    LogContext, 
    set_user_context,
    set_operation_context,
    clear_operation_context
)
import time


def demo_basic_structured_logging():
    """Demonstrate basic structured logging features."""
    print("=== Basic Structured Logging Demo ===")
    
    # Get a structured logger
    logger = get_structured_logger("demo.basic")
    
    # Simple logging with automatic context
    logger.info("This is a basic info message")
    logger.warning("This is a warning with extra context", 
                   component="demo_module", action="testing")
    logger.error("This is an error message", 
                error_code="DEMO_001", retry_count=3)


def demo_operation_context():
    """Demonstrate operation context tracking."""
    print("\n=== Operation Context Demo ===")
    
    logger = get_structured_logger("demo.operations")
    
    # Manual operation context
    op_id = set_operation_context("user_login")
    logger.info("User attempting login", username="demo_user")
    time.sleep(0.1)  # Simulate some processing
    logger.info("Login successful", login_duration_ms=100)
    clear_operation_context()
    
    # Using context manager (recommended)
    with LogContext("data_processing", user_id="user123"):
        logger.info("Starting data processing job")
        logger.debug("Processing batch 1", batch_size=100)
        logger.debug("Processing batch 2", batch_size=150)
        logger.info("Data processing completed", total_records=250)


def demo_user_context():
    """Demonstrate user context tracking."""
    print("\n=== User Context Demo ===")
    
    logger = get_structured_logger("demo.user_operations")
    
    # Set user context for the thread
    set_user_context("admin_user")
    
    with LogContext("file_upload"):
        logger.info("File upload started", filename="budget.xlsx", file_size=1024)
        logger.warning("File validation warning", 
                      warning="Missing header row", severity="low")
        logger.info("File upload completed", upload_duration_ms=500)


def demo_error_tracking():
    """Demonstrate error tracking with context."""
    print("\n=== Error Tracking Demo ===")
    
    logger = get_structured_logger("demo.error_handling")
    
    with LogContext("partner_creation", user_id="user456"):
        try:
            logger.info("Creating new partner", partner_id="P5", partner_name="Demo Partner")
            
            # Simulate an error
            raise ValueError("Invalid partner configuration")
            
        except ValueError as e:
            logger.exception("Partner creation failed", 
                           partner_id="P5", error_type="configuration_error")


def demo_performance_tracking():
    """Demonstrate performance tracking with structured logging."""
    print("\n=== Performance Tracking Demo ===")
    
    logger = get_structured_logger("demo.performance")
    
    with LogContext("excel_processing"):
        start_time = time.time()
        
        logger.info("Excel processing started", operation="bulk_import")
        
        # Simulate processing steps
        for i in range(3):
            step_start = time.time()
            time.sleep(0.1)  # Simulate work
            step_duration = (time.time() - step_start) * 1000
            
            logger.debug("Processing step completed", 
                        step_number=i+1, 
                        duration_ms=round(step_duration, 2))
        
        total_duration = (time.time() - start_time) * 1000
        logger.info("Excel processing completed", 
                   total_duration_ms=round(total_duration, 2),
                   steps_processed=3)


def demo_business_context():
    """Demonstrate business-specific context tracking."""
    print("\n=== Business Context Demo ===")
    
    logger = get_structured_logger("demo.business")
    
    with LogContext("workpackage_update", user_id="project_manager"):
        logger.info("Workpackage update initiated", 
                   workpackage_id="WP3", 
                   project_id="PROJ001")
        
        logger.debug("Validating workpackage data", 
                    start_month=6, end_month=12, lead_partner="P2")
        
        logger.info("Workpackage updated successfully", 
                   changes_made=["end_month", "budget"], 
                   previous_end_month=10, 
                   new_end_month=12)


def view_log_files():
    """Show how to view the generated log files."""
    print("\n=== Log Files Location ===")
    
    from pathlib import Path
    log_dir = Path.home() / "ProjectBudgetinator" / "Log Files"
    
    print(f"Log files are stored in: {log_dir}")
    
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        if log_files:
            print(f"Found {len(log_files)} log files:")
            for log_file in sorted(log_files):
                print(f"  - {log_file.name}")
        else:
            print("No log files found yet.")
    else:
        print("Log directory does not exist yet.")


def main():
    """Run all structured logging demonstrations."""
    print("ProjectBudgetinator Structured Logging Demonstration")
    print("=" * 60)
    
    # Initialize the logging system
    setup_logging()
    print("Structured logging system initialized")
    
    # Run demonstrations
    demo_basic_structured_logging()
    demo_operation_context()
    demo_user_context()
    demo_error_tracking()
    demo_performance_tracking()
    demo_business_context()
    view_log_files()
    
    print("\n" + "=" * 60)
    print("Demo completed! Check the log files to see structured output.")
    print("\nKey benefits of structured logging:")
    print("- Correlation IDs for tracking operations across modules")
    print("- User context for auditing and debugging")
    print("- JSON format for log aggregation and analysis")
    print("- Traditional format for console readability")
    print("- Automatic context propagation")
    print("- Performance and business metrics tracking")


if __name__ == "__main__":
    main()
