"""
Progress Indicators Demonstration Script

This script demonstrates the new progress indicator system implemented
for ProjectBudgetinator operations including:
- File operations with progress feedback
- Partner creation with progress tracking
- Cancellation support
- Time estimation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gui.progress_dialog import (
    ProgressDialog, ProgressContext, ThreadedProgressOperation,
    show_progress_for_operation, create_progress_dialog
)
from logger import get_structured_logger, LogContext


logger = get_structured_logger("examples.progress_demo")


class ProgressDemoWindow:
    """Main window for progress indicator demonstrations."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Progress Indicators Demo - ProjectBudgetinator")
        self.root.geometry("600x500")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the demonstration UI."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="ProjectBudgetinator Progress Indicators Demo",
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_text = (
            "This demo shows the new progress indicators implemented for "
            "long-running operations in ProjectBudgetinator. Each demo "
            "simulates different types of operations with realistic progress feedback."
        )
        desc_label = ttk.Label(main_frame, text=desc_text, wraplength=550)
        desc_label.pack(pady=(0, 20))
        
        # Demo buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 20))
        
        # File operations demo
        ttk.Button(
            buttons_frame,
            text="1. File Loading Demo",
            command=self.demo_file_loading,
            width=25
        ).pack(pady=5, fill=tk.X)
        
        ttk.Button(
            buttons_frame,
            text="2. File Saving Demo",
            command=self.demo_file_saving,
            width=25
        ).pack(pady=5, fill=tk.X)
        
        ttk.Button(
            buttons_frame,
            text="3. Partner Creation Demo",
            command=self.demo_partner_creation,
            width=25
        ).pack(pady=5, fill=tk.X)
        
        ttk.Button(
            buttons_frame,
            text="4. Batch Operations Demo",
            command=self.demo_batch_operations,
            width=25
        ).pack(pady=5, fill=tk.X)
        
        ttk.Button(
            buttons_frame,
            text="5. Cancellable Operation Demo",
            command=self.demo_cancellable_operation,
            width=25
        ).pack(pady=5, fill=tk.X)
        
        ttk.Button(
            buttons_frame,
            text="6. Context Manager Demo",
            command=self.demo_context_manager,
            width=25
        ).pack(pady=5, fill=tk.X)
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Demo Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(results_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Clear and close buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Clear Results",
            command=self.clear_results
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Close",
            command=self.root.quit
        ).pack(side=tk.RIGHT)
    
    def log_result(self, message):
        """Add a message to the results area."""
        self.results_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\\n")
        self.results_text.see(tk.END)
        self.root.update()
    
    def clear_results(self):
        """Clear the results area."""
        self.results_text.delete(1.0, tk.END)
    
    def demo_file_loading(self):
        """Demonstrate file loading with progress."""
        self.log_result("Starting File Loading Demo...")
        
        def file_loading_operation(progress):
            with LogContext("demo_file_loading"):
                # Simulate file loading steps
                steps = [
                    ("Opening file dialog...", 10),
                    ("Reading file metadata...", 25),
                    ("Loading Excel workbook...", 40),
                    ("Analyzing worksheets...", 60),
                    ("Validating data structure...", 80),
                    ("Finalizing load...", 100)
                ]
                
                for step_name, progress_value in steps:
                    if progress.is_cancelled():
                        return False
                    
                    progress.update_status(step_name)
                    progress.update_progress(progress_value, 100)
                    
                    # Simulate work time
                    time.sleep(0.8)
                
                logger.info("File loading demo completed")
                return "demo_file.xlsx"
        
        def completion_callback(result):
            if result:
                self.log_result(f"File loading completed: {result}")
            else:
                self.log_result("File loading was cancelled or failed")
        
        show_progress_for_operation(
            self.root,
            file_loading_operation,
            title="Loading Excel File...",
            can_cancel=True,
            show_eta=True,
            completion_callback=completion_callback
        )
    
    def demo_file_saving(self):
        """Demonstrate file saving with progress."""
        self.log_result("Starting File Saving Demo...")
        
        def file_saving_operation(progress):
            with LogContext("demo_file_saving"):
                steps = [
                    ("Preparing data for save...", 15),
                    ("Validating Excel structure...", 30),
                    ("Writing worksheet data...", 50),
                    ("Applying formatting...", 70),
                    ("Finalizing file...", 90),
                    ("Save completed!", 100)
                ]
                
                for step_name, progress_value in steps:
                    if progress.is_cancelled():
                        return False
                    
                    progress.update_status(step_name)
                    progress.update_progress(progress_value, 100)
                    time.sleep(0.6)
                
                logger.info("File saving demo completed")
                return True
        
        def completion_callback(result):
            if result:
                self.log_result("File saving completed successfully")
            else:
                self.log_result("File saving was cancelled or failed")
        
        show_progress_for_operation(
            self.root,
            file_saving_operation,
            title="Saving Excel File...",
            can_cancel=True,
            show_eta=True,
            completion_callback=completion_callback
        )
    
    def demo_partner_creation(self):
        """Demonstrate partner creation with progress."""
        self.log_result("Starting Partner Creation Demo...")
        
        def partner_creation_operation(progress):
            with LogContext("demo_partner_creation", partner_id="P5"):
                steps = [
                    ("Validating partner data...", 15),
                    ("Creating worksheet...", 30),
                    ("Setting up dimensions...", 45),
                    ("Adding partner information...", 60),
                    ("Adding work package data...", 80),
                    ("Applying formatting...", 95),
                    ("Partner creation complete!", 100)
                ]
                
                for step_name, progress_value in steps:
                    if progress.is_cancelled():
                        return False
                    
                    progress.update_status(step_name)
                    progress.update_progress(progress_value, 100)
                    time.sleep(0.7)
                
                logger.info("Partner creation demo completed")
                return "Partner P5 - DEMO"
        
        def completion_callback(result):
            if result:
                self.log_result(f"Partner creation completed: {result}")
            else:
                self.log_result("Partner creation was cancelled or failed")
        
        show_progress_for_operation(
            self.root,
            partner_creation_operation,
            title="Creating Partner P5 - DEMO...",
            can_cancel=True,
            show_eta=True,
            completion_callback=completion_callback
        )
    
    def demo_batch_operations(self):
        """Demonstrate batch operations with progress."""
        self.log_result("Starting Batch Operations Demo...")
        
        def batch_operation(progress):
            with LogContext("demo_batch_operations"):
                total_items = 8
                items = [f"Item {i+1}" for i in range(total_items)]
                
                for i, item in enumerate(items):
                    if progress.is_cancelled():
                        return False
                    
                    progress.update_status(f"Processing {item}...")
                    progress_value = int(((i + 1) / total_items) * 100)
                    progress.update_progress(progress_value, 100)
                    
                    # Simulate processing time
                    time.sleep(0.5)
                
                logger.info("Batch operations demo completed")
                return total_items
        
        def completion_callback(result):
            if result:
                self.log_result(f"Batch processing completed: {result} items processed")
            else:
                self.log_result("Batch processing was cancelled or failed")
        
        show_progress_for_operation(
            self.root,
            batch_operation,
            title="Processing Multiple Items...",
            can_cancel=True,
            show_eta=True,
            completion_callback=completion_callback
        )
    
    def demo_cancellable_operation(self):
        """Demonstrate a long operation that can be cancelled."""
        self.log_result("Starting Cancellable Operation Demo (try cancelling it!)...")
        
        def long_operation(progress):
            with LogContext("demo_long_operation"):
                for i in range(200):  # Very long operation
                    if progress.is_cancelled():
                        logger.info("Operation cancelled by user")
                        return False
                    
                    progress.update_status(f"Processing step {i+1} of 200...")
                    progress.update_progress(i + 1, 200)
                    time.sleep(0.1)  # Simulate work
                
                logger.info("Long operation completed")
                return True
        
        def completion_callback(result):
            if result:
                self.log_result("Long operation completed successfully")
            else:
                self.log_result("Long operation was cancelled")
        
        show_progress_for_operation(
            self.root,
            long_operation,
            title="Long Running Operation (Cancellable)...",
            can_cancel=True,
            show_eta=True,
            completion_callback=completion_callback
        )
    
    def demo_context_manager(self):
        """Demonstrate using the progress context manager."""
        self.log_result("Starting Context Manager Demo...")
        
        def run_with_context():
            try:
                with ProgressContext(self.root, "Context Manager Demo", True, True) as progress:
                    with LogContext("demo_context_manager"):
                        for i in range(5):
                            if progress.is_cancelled():
                                self.log_result("Context manager operation cancelled")
                                return
                            
                            progress.update_status(f"Context step {i+1}...")
                            progress.update_progress((i + 1) * 20, 100)
                            time.sleep(1)
                        
                        logger.info("Context manager demo completed")
                        self.log_result("Context manager operation completed successfully")
            except Exception as e:
                self.log_result(f"Context manager operation failed: {e}")
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=run_with_context, daemon=True)
        thread.start()
    
    def run(self):
        """Run the demonstration window."""
        self.log_result("Progress Indicators Demo initialized")
        self.log_result("Click any button above to test progress indicators")
        self.root.mainloop()


def main():
    """Main function to run the progress demo."""
    print("ProjectBudgetinator Progress Indicators Demonstration")
    print("=" * 60)
    
    # Initialize logging
    with LogContext("progress_demo_session"):
        logger.info("Starting progress indicators demonstration")
        
        try:
            demo = ProgressDemoWindow()
            demo.run()
        except Exception as e:
            logger.exception("Demo failed to start")
            print(f"Error: {e}")
        finally:
            logger.info("Progress indicators demonstration ended")


if __name__ == "__main__":
    main()
