"""
Performance Monitoring GUI Components

This module provides GUI components for displaying performance metrics
and system monitoring information within the ProjectBudgetinator application.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

from utils.performance_monitor import get_performance_monitor, PerformanceAnalyzer


class PerformanceMonitorDialog:
    """Dialog for displaying performance monitoring information"""
    
    def __init__(self, parent):
        """
        Initialize performance monitor dialog.
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        self.monitor = get_performance_monitor()
        self.dialog = None
        self.update_thread = None
        self.running = False
        
        # Data for charts
        self.time_data = []
        self.cpu_data = []
        self.memory_data = []
        self.function_data = {}
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the performance monitor dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Performance Monitor")
        self.dialog.geometry("1000x700")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Overview tab
        self.create_overview_tab(notebook)
        
        # Function performance tab
        self.create_function_tab(notebook)
        
        # System metrics tab
        self.create_system_tab(notebook)
        
        # File operations tab
        self.create_file_tab(notebook)
        
        # Analysis tab
        self.create_analysis_tab(notebook)
        
        # Control buttons
        self.create_control_buttons()
        
        # Start auto-refresh
        self.start_auto_refresh()
        
        # Handle dialog close
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_overview_tab(self, notebook):
        """Create overview tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Overview")
        
        # Summary statistics
        summary_frame = ttk.LabelFrame(frame, text="Summary Statistics")
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create summary labels
        self.summary_labels = {}
        summary_info = [
            ("Total Function Calls", "total_calls"),
            ("Average Success Rate", "success_rate"),
            ("Total Memory Delta", "memory_delta"),
            ("File Operations", "file_ops"),
            ("Monitoring Status", "status")
        ]
        
        for i, (label, key) in enumerate(summary_info):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(summary_frame, text=f"{label}:").grid(
                row=row, column=col, sticky=tk.W, padx=5, pady=2
            )
            
            self.summary_labels[key] = ttk.Label(summary_frame, text="Loading...")
            self.summary_labels[key].grid(
                row=row, column=col+1, sticky=tk.W, padx=20, pady=2
            )
        
        # Recent activity
        activity_frame = ttk.LabelFrame(frame, text="Recent Activity")
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Activity treeview
        columns = ("Time", "Function", "Duration", "Memory", "Status")
        self.activity_tree = ttk.Treeview(activity_frame, columns=columns, show="headings")
        
        for col in columns:
            self.activity_tree.heading(col, text=col)
            self.activity_tree.column(col, width=120)
        
        # Scrollbars for activity tree
        activity_scroll_y = ttk.Scrollbar(activity_frame, orient=tk.VERTICAL, command=self.activity_tree.yview)
        activity_scroll_x = ttk.Scrollbar(activity_frame, orient=tk.HORIZONTAL, command=self.activity_tree.xview)
        self.activity_tree.configure(yscrollcommand=activity_scroll_y.set, xscrollcommand=activity_scroll_x.set)
        
        self.activity_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        activity_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        activity_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_function_tab(self, notebook):
        """Create function performance tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Function Performance")
        
        # Function statistics
        function_frame = ttk.LabelFrame(frame, text="Function Statistics")
        function_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Function treeview
        columns = ("Function", "Calls", "Avg Duration", "Max Duration", "Avg Memory", "Success Rate")
        self.function_tree = ttk.Treeview(function_frame, columns=columns, show="headings")
        
        for col in columns:
            self.function_tree.heading(col, text=col)
            self.function_tree.column(col, width=100)
        
        # Scrollbars
        func_scroll_y = ttk.Scrollbar(function_frame, orient=tk.VERTICAL, command=self.function_tree.yview)
        func_scroll_x = ttk.Scrollbar(function_frame, orient=tk.HORIZONTAL, command=self.function_tree.xview)
        self.function_tree.configure(yscrollcommand=func_scroll_y.set, xscrollcommand=func_scroll_x.set)
        
        self.function_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        func_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        func_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Function details
        details_frame = ttk.LabelFrame(frame, text="Function Details")
        details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.function_details = tk.Text(details_frame, height=6, wrap=tk.WORD)
        details_scroll = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.function_details.yview)
        self.function_details.configure(yscrollcommand=details_scroll.set)
        
        self.function_details.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.function_tree.bind("<<TreeviewSelect>>", self.on_function_select)
    
    def create_system_tab(self, notebook):
        """Create system metrics tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="System Metrics")
        
        # System info
        info_frame = ttk.LabelFrame(frame, text="System Information")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.system_labels = {}
        system_info = [
            ("CPU Usage", "cpu"),
            ("Memory Usage", "memory"),
            ("Active Threads", "threads"),
            ("Process ID", "pid")
        ]
        
        for i, (label, key) in enumerate(system_info):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(info_frame, text=f"{label}:").grid(
                row=row, column=col, sticky=tk.W, padx=5, pady=2
            )
            
            self.system_labels[key] = ttk.Label(info_frame, text="Loading...")
            self.system_labels[key].grid(
                row=row, column=col+1, sticky=tk.W, padx=20, pady=2
            )
        
        # System metrics chart
        chart_frame = ttk.LabelFrame(frame, text="System Metrics Chart")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)
        
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_file_tab(self, notebook):
        """Create file operations tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="File Operations")
        
        # File statistics
        file_frame = ttk.LabelFrame(frame, text="File Operation Statistics")
        file_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # File treeview
        columns = ("Operation", "Count", "Avg Duration", "Total Size", "Success Rate")
        self.file_tree = ttk.Treeview(file_frame, columns=columns, show="headings")
        
        for col in columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=120)
        
        # Scrollbars
        file_scroll_y = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=file_scroll_y.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Recent file operations
        recent_frame = ttk.LabelFrame(frame, text="Recent File Operations")
        recent_frame.pack(fill=tk.X, padx=5, pady=5, ipady=5)
        
        self.recent_files = tk.Text(recent_frame, height=8, wrap=tk.WORD)
        recent_scroll = ttk.Scrollbar(recent_frame, orient=tk.VERTICAL, command=self.recent_files.yview)
        self.recent_files.configure(yscrollcommand=recent_scroll.set)
        
        self.recent_files.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        recent_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_analysis_tab(self, notebook):
        """Create performance analysis tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Analysis")
        
        # Performance issues
        issues_frame = ttk.LabelFrame(frame, text="Detected Performance Issues")
        issues_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.issues_tree = ttk.Treeview(issues_frame, columns=("Type", "Description"), show="headings")
        self.issues_tree.heading("Type", text="Issue Type")
        self.issues_tree.heading("Description", text="Description")
        self.issues_tree.column("Type", width=150)
        self.issues_tree.column("Description", width=400)
        
        issues_scroll = ttk.Scrollbar(issues_frame, orient=tk.VERTICAL, command=self.issues_tree.yview)
        self.issues_tree.configure(yscrollcommand=issues_scroll.set)
        
        self.issues_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        issues_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Optimization suggestions
        suggestions_frame = ttk.LabelFrame(frame, text="Optimization Suggestions")
        suggestions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.suggestions_text = tk.Text(suggestions_frame, height=8, wrap=tk.WORD)
        suggestions_scroll = ttk.Scrollbar(suggestions_frame, orient=tk.VERTICAL, command=self.suggestions_text.yview)
        self.suggestions_text.configure(yscrollcommand=suggestions_scroll.set)
        
        self.suggestions_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        suggestions_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_control_buttons(self):
        """Create control buttons"""
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Control buttons
        ttk.Button(button_frame, text="Refresh", command=self.refresh_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Report", command=self.export_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset Metrics", command=self.reset_metrics).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Display", command=self.clear_display).pack(side=tk.LEFT, padx=5)
        
        # Monitoring controls
        self.monitoring_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            button_frame, 
            text="Enable Monitoring", 
            variable=self.monitoring_var,
            command=self.toggle_monitoring
        ).pack(side=tk.LEFT, padx=20)
        
        # Auto-refresh control
        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            button_frame,
            text="Auto Refresh",
            variable=self.auto_refresh_var
        ).pack(side=tk.LEFT, padx=5)
        
        # Close button
        ttk.Button(button_frame, text="Close", command=self.on_close).pack(side=tk.RIGHT, padx=5)
    
    def start_auto_refresh(self):
        """Start auto-refresh thread"""
        self.running = True
        self.update_thread = threading.Thread(target=self.auto_refresh_loop, daemon=True)
        self.update_thread.start()
    
    def auto_refresh_loop(self):
        """Auto-refresh loop"""
        while self.running:
            if self.auto_refresh_var.get():
                try:
                    self.dialog.after(0, self.refresh_data)
                except tk.TclError:
                    # Dialog was closed
                    break
            threading.Event().wait(2)  # Refresh every 2 seconds
    
    def refresh_data(self):
        """Refresh all performance data"""
        try:
            self.update_summary()
            self.update_activity()
            self.update_function_stats()
            self.update_system_metrics()
            self.update_file_stats()
            self.update_analysis()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh data: {e}")
    
    def update_summary(self):
        """Update summary statistics"""
        summary = self.monitor.get_performance_summary()
        
        self.summary_labels["total_calls"].config(
            text=str(summary['summary']['total_function_calls'])
        )
        self.summary_labels["success_rate"].config(
            text=f"{summary['summary']['average_success_rate']:.1f}%"
        )
        self.summary_labels["memory_delta"].config(
            text=f"{summary['summary']['total_memory_delta_mb']:.1f} MB"
        )
        self.summary_labels["file_ops"].config(
            text=str(summary['summary']['total_file_operations'])
        )
        self.summary_labels["status"].config(
            text="Active" if summary['summary']['monitoring_active'] else "Inactive"
        )
    
    def update_activity(self):
        """Update recent activity"""
        # Clear existing items
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        # Get recent metrics
        recent_metrics = self.monitor.collector.get_recent_metrics(50)
        
        # Add performance metrics
        for metric in recent_metrics['performance'][-20:]:  # Last 20 items
            time_str = datetime.fromisoformat(metric['timestamp']).strftime("%H:%M:%S")
            duration_str = f"{metric['duration']:.3f}s"
            memory_str = f"{metric['memory_delta'] / 1024 / 1024:+.1f}MB"
            status_str = "OK" if metric['success'] else "ERROR"
            
            self.activity_tree.insert("", tk.END, values=(
                time_str,
                metric['function_name'],
                duration_str,
                memory_str,
                status_str
            ))
    
    def update_function_stats(self):
        """Update function statistics"""
        # Clear existing items
        for item in self.function_tree.get_children():
            self.function_tree.delete(item)
        
        # Get function stats
        function_stats = self.monitor.collector.get_function_stats()
        
        # Sort by total duration
        sorted_functions = sorted(
            function_stats.items(),
            key=lambda x: x[1]['total_duration'],
            reverse=True
        )
        
        for name, stats in sorted_functions:
            self.function_tree.insert("", tk.END, values=(
                name,
                stats['count'],
                f"{stats['avg_duration']:.3f}s",
                f"{stats['max_duration']:.3f}s",
                f"{stats['avg_memory_delta'] / 1024 / 1024:+.1f}MB",
                f"{stats['success_rate']:.1f}%"
            ))
    
    def update_system_metrics(self):
        """Update system metrics and chart"""
        import psutil
        
        # Update current system info
        self.system_labels["cpu"].config(text=f"{psutil.cpu_percent():.1f}%")
        
        memory = psutil.virtual_memory()
        self.system_labels["memory"].config(text=f"{memory.percent:.1f}%")
        self.system_labels["threads"].config(text=str(threading.active_count()))
        self.system_labels["pid"].config(text=str(psutil.Process().pid))
        
        # Update charts
        recent_metrics = self.monitor.collector.get_recent_metrics(100)
        system_metrics = recent_metrics['system']
        
        if system_metrics:
            # Prepare data for charts
            times = [datetime.fromisoformat(m['timestamp']) for m in system_metrics[-30:]]
            cpu_values = [m['cpu_percent'] for m in system_metrics[-30:]]
            memory_values = [m['memory_percent'] for m in system_metrics[-30:]]
            
            # Clear and update charts
            self.ax1.clear()
            self.ax2.clear()
            
            self.ax1.plot(times, cpu_values, 'b-', label='CPU %')
            self.ax1.set_ylabel('CPU %')
            self.ax1.set_title('System Performance')
            self.ax1.legend()
            self.ax1.grid(True)
            
            self.ax2.plot(times, memory_values, 'r-', label='Memory %')
            self.ax2.set_ylabel('Memory %')
            self.ax2.set_xlabel('Time')
            self.ax2.legend()
            self.ax2.grid(True)
            
            # Format x-axis
            self.fig.autofmt_xdate()
            self.canvas.draw()
    
    def update_file_stats(self):
        """Update file operation statistics"""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Get file stats
        file_stats = self.monitor.collector.get_file_stats()
        
        for op_type, stats in file_stats.items():
            self.file_tree.insert("", tk.END, values=(
                op_type,
                stats['count'],
                f"{stats['avg_duration']:.3f}s",
                f"{stats['total_size'] / 1024 / 1024:.1f}MB",
                f"{stats['success_rate']:.1f}%"
            ))
        
        # Update recent file operations
        self.recent_files.delete(1.0, tk.END)
        recent_metrics = self.monitor.collector.get_recent_metrics(20)
        
        for metric in recent_metrics['file'][-10:]:
            time_str = datetime.fromisoformat(metric['timestamp']).strftime("%H:%M:%S")
            size_str = f"{metric['file_size'] / 1024 / 1024:.1f}MB"
            status_str = "OK" if metric['success'] else "ERROR"
            
            self.recent_files.insert(tk.END,
                f"{time_str} - {metric['operation_type']} ({size_str}) - {status_str}\n"
            )
    
    def update_analysis(self):
        """Update performance analysis"""
        # Clear existing items
        for item in self.issues_tree.get_children():
            self.issues_tree.delete(item)
        
        # Detect issues
        issues = PerformanceAnalyzer.detect_performance_issues(self.monitor)
        
        for issue_type, issue_list in issues.items():
            for issue in issue_list:
                self.issues_tree.insert("", tk.END, values=(
                    issue_type.replace('_', ' ').title(),
                    issue
                ))
        
        # Update suggestions
        suggestions = PerformanceAnalyzer.generate_optimization_suggestions(self.monitor)
        
        self.suggestions_text.delete(1.0, tk.END)
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                self.suggestions_text.insert(tk.END, f"{i}. {suggestion}\n\n")
        else:
            self.suggestions_text.insert(tk.END, "No optimization suggestions at this time.")
    
    def on_function_select(self, event):
        """Handle function selection"""
        selection = self.function_tree.selection()
        if selection:
            item = self.function_tree.item(selection[0])
            function_name = item['values'][0]
            
            # Get detailed stats for selected function
            function_stats = self.monitor.collector.get_function_stats(function_name)
            
            self.function_details.delete(1.0, tk.END)
            if function_stats:
                details = f"""Function: {function_name}
Total Calls: {function_stats['count']}
Total Duration: {function_stats['total_duration']:.3f}s
Average Duration: {function_stats['avg_duration']:.3f}s
Min Duration: {function_stats['min_duration']:.3f}s
Max Duration: {function_stats['max_duration']:.3f}s
Total Memory Delta: {function_stats['total_memory_delta'] / 1024 / 1024:.1f}MB
Average Memory Delta: {function_stats['avg_memory_delta'] / 1024 / 1024:.1f}MB
Error Count: {function_stats['error_count']}
Success Rate: {function_stats['success_rate']:.1f}%"""
                
                self.function_details.insert(tk.END, details)
    
    def toggle_monitoring(self):
        """Toggle performance monitoring"""
        if self.monitoring_var.get():
            self.monitor.enable_monitoring()
        else:
            self.monitor.disable_monitoring()
    
    def export_report(self):
        """Export performance report"""
        file_path = filedialog.asksaveasfilename(
            title="Export Performance Report",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.monitor.export_report(file_path)
                messagebox.showinfo("Success", f"Performance report exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report:\n{e}")
    
    def reset_metrics(self):
        """Reset all metrics"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all performance metrics?"):
            self.monitor.reset_metrics()
            self.refresh_data()
            messagebox.showinfo("Success", "Performance metrics have been reset.")
    
    def clear_display(self):
        """Clear all display elements"""
        # Clear treeviews
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        for item in self.function_tree.get_children():
            self.function_tree.delete(item)
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        for item in self.issues_tree.get_children():
            self.issues_tree.delete(item)
        
        # Clear text widgets
        self.function_details.delete(1.0, tk.END)
        self.recent_files.delete(1.0, tk.END)
        self.suggestions_text.delete(1.0, tk.END)
        
        # Clear charts
        self.ax1.clear()
        self.ax2.clear()
        self.canvas.draw()
    
    def on_close(self):
        """Handle dialog close"""
        self.running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)
        self.dialog.destroy()


class PerformanceIndicator:
    """Small performance indicator widget"""
    
    def __init__(self, parent):
        """
        Initialize performance indicator.
        
        Args:
            parent: Parent widget
        """
        self.parent = parent
        self.monitor = get_performance_monitor()
        
        # Create indicator frame
        self.frame = ttk.Frame(parent)
        
        # CPU indicator
        self.cpu_label = ttk.Label(self.frame, text="CPU: --")
        self.cpu_label.pack(side=tk.LEFT, padx=5)
        
        # Memory indicator
        self.memory_label = ttk.Label(self.frame, text="MEM: --")
        self.memory_label.pack(side=tk.LEFT, padx=5)
        
        # Function calls indicator
        self.calls_label = ttk.Label(self.frame, text="Calls: 0")
        self.calls_label.pack(side=tk.LEFT, padx=5)
        
        # Status indicator
        self.status_label = ttk.Label(self.frame, text="●", foreground="green")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Start updating
        self.update_indicators()
    
    def update_indicators(self):
        """Update performance indicators"""
        try:
            import psutil
            
            # Update CPU and memory
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            self.cpu_label.config(text=f"CPU: {cpu_percent:.0f}%")
            self.memory_label.config(text=f"MEM: {memory_percent:.0f}%")
            
            # Update function calls
            summary = self.monitor.get_performance_summary()
            total_calls = summary['summary']['total_function_calls']
            self.calls_label.config(text=f"Calls: {total_calls}")
            
            # Update status
            monitoring_active = summary['summary']['monitoring_active']
            if monitoring_active:
                self.status_label.config(text="●", foreground="green")
            else:
                self.status_label.config(text="●", foreground="red")
                
        except Exception:
            self.status_label.config(text="●", foreground="gray")
        
        # Schedule next update
        self.parent.after(5000, self.update_indicators)  # Update every 5 seconds
    
    def get_widget(self):
        """Get the indicator widget"""
        return self.frame


def show_performance_monitor(parent):
    """Show performance monitoring dialog"""
    try:
        dialog = PerformanceMonitorDialog(parent)
        return dialog
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open performance monitor:\n{e}")
        return None
