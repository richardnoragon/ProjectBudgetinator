"""
Application Metrics and Performance Monitoring System

This module provides comprehensive performance monitoring capabilities for
ProjectBudgetinator, including timing decorators, memory usage tracking,
and file operation statistics.
"""

import time
import psutil
import functools
import logging
import threading
import json
import gc
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, deque
from contextlib import contextmanager
from weakref import WeakSet


@dataclass
class PerformanceMetric:
    """Data class for storing performance metrics"""
    function_name: str
    duration: float
    memory_start: int
    memory_end: int
    memory_delta: int
    timestamp: datetime
    thread_id: int
    process_id: int
    args_count: int
    kwargs_count: int
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class SystemMetrics:
    """Data class for system-wide metrics"""
    cpu_percent: float
    memory_percent: float
    memory_available: int
    disk_usage_percent: float
    active_threads: int
    timestamp: datetime


@dataclass
class FileOperationMetric:
    """Data class for file operation metrics"""
    operation_type: str  # read, write, open, close
    file_path: str
    file_size: int
    duration: float
    success: bool
    timestamp: datetime
    error_message: Optional[str] = None


class MetricsCollector:
    """Centralized metrics collection and storage"""
    
    def __init__(self, max_metrics: int = 10000):
        """
        Initialize metrics collector.
        
        Args:
            max_metrics: Maximum number of metrics to keep in memory
        """
        self.max_metrics = max_metrics
        self.performance_metrics: deque = deque(maxlen=max_metrics)
        self.system_metrics: deque = deque(maxlen=max_metrics)
        self.file_metrics: deque = deque(maxlen=max_metrics)
        
        # Statistics
        self.function_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'total_duration': 0.0,
            'avg_duration': 0.0,
            'min_duration': float('inf'),
            'max_duration': 0.0,
            'total_memory_delta': 0,
            'avg_memory_delta': 0.0,
            'error_count': 0,
            'success_rate': 100.0
        })
        
        self.file_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'total_duration': 0.0,
            'avg_duration': 0.0,
            'total_size': 0,
            'error_count': 0,
            'success_rate': 100.0
        })
        
        self._lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def add_performance_metric(self, metric: PerformanceMetric):
        """Add a performance metric"""
        with self._lock:
            self.performance_metrics.append(metric)
            self._update_function_stats(metric)
    
    def add_system_metric(self, metric: SystemMetrics):
        """Add a system metric"""
        with self._lock:
            self.system_metrics.append(metric)
    
    def add_file_metric(self, metric: FileOperationMetric):
        """Add a file operation metric"""
        with self._lock:
            self.file_metrics.append(metric)
            self._update_file_stats(metric)
    
    def _update_function_stats(self, metric: PerformanceMetric):
        """Update function statistics"""
        stats = self.function_stats[metric.function_name]
        stats['count'] += 1
        stats['total_duration'] += metric.duration
        stats['avg_duration'] = stats['total_duration'] / stats['count']
        stats['min_duration'] = min(stats['min_duration'], metric.duration)
        stats['max_duration'] = max(stats['max_duration'], metric.duration)
        stats['total_memory_delta'] += metric.memory_delta
        stats['avg_memory_delta'] = stats['total_memory_delta'] / stats['count']
        
        if not metric.success:
            stats['error_count'] += 1
        
        stats['success_rate'] = ((stats['count'] - stats['error_count']) / stats['count']) * 100
    
    def _update_file_stats(self, metric: FileOperationMetric):
        """Update file operation statistics"""
        stats = self.file_stats[metric.operation_type]
        stats['count'] += 1
        stats['total_duration'] += metric.duration
        stats['avg_duration'] = stats['total_duration'] / stats['count']
        stats['total_size'] += metric.file_size
        
        if not metric.success:
            stats['error_count'] += 1
        
        stats['success_rate'] = ((stats['count'] - stats['error_count']) / stats['count']) * 100
    
    def get_function_stats(self, function_name: Optional[str] = None) -> Dict[str, Any]:
        """Get function performance statistics"""
        with self._lock:
            if function_name:
                return dict(self.function_stats.get(function_name, {}))
            return {name: dict(stats) for name, stats in self.function_stats.items()}
    
    def get_file_stats(self, operation_type: Optional[str] = None) -> Dict[str, Any]:
        """Get file operation statistics"""
        with self._lock:
            if operation_type:
                return dict(self.file_stats.get(operation_type, {}))
            return {op: dict(stats) for op, stats in self.file_stats.items()}
    
    def get_recent_metrics(self, count: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        """Get recent metrics"""
        with self._lock:
            return {
                'performance': [
                    {
                        'function_name': m.function_name,
                        'duration': m.duration,
                        'memory_delta': m.memory_delta,
                        'timestamp': m.timestamp.isoformat(),
                        'success': m.success
                    }
                    for m in list(self.performance_metrics)[-count:]
                ],
                'system': [
                    {
                        'cpu_percent': m.cpu_percent,
                        'memory_percent': m.memory_percent,
                        'timestamp': m.timestamp.isoformat()
                    }
                    for m in list(self.system_metrics)[-count:]
                ],
                'file': [
                    {
                        'operation_type': m.operation_type,
                        'file_size': m.file_size,
                        'duration': m.duration,
                        'timestamp': m.timestamp.isoformat(),
                        'success': m.success
                    }
                    for m in list(self.file_metrics)[-count:]
                ]
            }
    
    def export_metrics(self, file_path: str):
        """Export metrics to JSON file"""
        try:
            with self._lock:
                data = {
                    'export_timestamp': datetime.now().isoformat(),
                    'function_stats': dict(self.function_stats),
                    'file_stats': dict(self.file_stats),
                    'recent_metrics': self.get_recent_metrics(1000)
                }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.info(f"Metrics exported to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export metrics: {e}")
    
    def clear_metrics(self):
        """Clear all collected metrics"""
        with self._lock:
            self.performance_metrics.clear()
            self.system_metrics.clear()
            self.file_metrics.clear()
            self.function_stats.clear()
            self.file_stats.clear()
            self.logger.info("All metrics cleared")


class PerformanceMonitor:
    """Main performance monitoring class with advanced features"""
    
    _instance: Optional['PerformanceMonitor'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.collector = MetricsCollector()
        self.process = psutil.Process()
        self.logger = logging.getLogger(__name__)
        self._monitoring_active = True
        self._system_monitor_thread = None
        self._monitored_functions: WeakSet = WeakSet()
        
        # Start system monitoring
        self._start_system_monitoring()
        self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'PerformanceMonitor':
        """Get singleton instance"""
        return cls()
    
    def _start_system_monitoring(self):
        """Start background system monitoring"""
        def monitor_system():
            while self._monitoring_active:
                try:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    metric = SystemMetrics(
                        cpu_percent=cpu_percent,
                        memory_percent=memory.percent,
                        memory_available=memory.available,
                        disk_usage_percent=disk.percent,
                        active_threads=threading.active_count(),
                        timestamp=datetime.now()
                    )
                    
                    self.collector.add_system_metric(metric)
                    
                except Exception as e:
                    self.logger.error(f"System monitoring error: {e}")
                
                time.sleep(30)  # Monitor every 30 seconds
        
        self._system_monitor_thread = threading.Thread(
            target=monitor_system, 
            daemon=True, 
            name="SystemMonitor"
        )
        self._system_monitor_thread.start()
    
    def monitor_performance(self, 
                          include_memory: bool = True,
                          include_args: bool = False,
                          log_level: str = 'INFO') -> Callable:
        """
        Decorator for monitoring function performance.
        
        Args:
            include_memory: Whether to monitor memory usage
            include_args: Whether to include argument count in metrics
            log_level: Logging level for performance messages
            
        Returns:
            Decorated function
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Skip monitoring if disabled
                if not self._monitoring_active:
                    return func(*args, **kwargs)
                
                start_time = time.perf_counter()
                start_memory = 0
                
                if include_memory:
                    try:
                        start_memory = self.process.memory_info().rss
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        start_memory = 0
                
                success = True
                error_message = None
                result = None
                
                try:
                    result = func(*args, **kwargs)
                    return result
                    
                except Exception as e:
                    success = False
                    error_message = str(e)
                    raise
                    
                finally:
                    end_time = time.perf_counter()
                    end_memory = start_memory
                    
                    if include_memory:
                        try:
                            end_memory = self.process.memory_info().rss
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            end_memory = start_memory
                    
                    duration = end_time - start_time
                    memory_delta = end_memory - start_memory
                    
                    # Create performance metric
                    metric = PerformanceMetric(
                        function_name=func.__name__,
                        duration=duration,
                        memory_start=start_memory,
                        memory_end=end_memory,
                        memory_delta=memory_delta,
                        timestamp=datetime.now(),
                        thread_id=threading.get_ident(),
                        process_id=self.process.pid,
                        args_count=len(args) if include_args else 0,
                        kwargs_count=len(kwargs) if include_args else 0,
                        success=success,
                        error_message=error_message
                    )
                    
                    self.collector.add_performance_metric(metric)
                    
                    # Log performance information
                    memory_mb = memory_delta / 1024 / 1024
                    log_message = (
                        f"{func.__name__}: {duration:.3f}s"
                        f"{f', Memory: {memory_mb:+.2f}MB' if include_memory else ''}"
                        f"{f', Status: {'SUCCESS' if success else 'ERROR'}' if not success else ''}"
                    )
                    
                    log_func = getattr(self.logger, log_level.lower(), self.logger.info)
                    log_func(log_message)
                    
                    # Track monitored functions
                    self._monitored_functions.add(func)
            
            return wrapper
        return decorator
    
    @contextmanager
    def monitor_file_operation(self, 
                             operation_type: str, 
                             file_path: str):
        """
        Context manager for monitoring file operations.
        
        Args:
            operation_type: Type of operation (read, write, open, close)
            file_path: Path to the file being operated on
        """
        start_time = time.perf_counter()
        file_size = 0
        success = True
        error_message = None
        
        try:
            # Get file size if it exists
            if Path(file_path).exists():
                file_size = Path(file_path).stat().st_size
        except Exception:
            pass
        
        try:
            yield
            
        except Exception as e:
            success = False
            error_message = str(e)
            raise
            
        finally:
            duration = time.perf_counter() - start_time
            
            # Update file size after operation if it's a write
            if operation_type in ['write', 'create'] and success:
                try:
                    if Path(file_path).exists():
                        file_size = Path(file_path).stat().st_size
                except Exception:
                    pass
            
            metric = FileOperationMetric(
                operation_type=operation_type,
                file_path=file_path,
                file_size=file_size,
                duration=duration,
                success=success,
                timestamp=datetime.now(),
                error_message=error_message
            )
            
            self.collector.add_file_metric(metric)
            
            # Log file operation
            size_mb = file_size / 1024 / 1024
            self.logger.info(
                f"File {operation_type}: {Path(file_path).name} "
                f"({size_mb:.2f}MB) in {duration:.3f}s"
            )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        function_stats = self.collector.get_function_stats()
        file_stats = self.collector.get_file_stats()
        recent_metrics = self.collector.get_recent_metrics(100)
        
        # Calculate overall statistics
        total_functions = len(function_stats)
        total_calls = sum(stats['count'] for stats in function_stats.values())
        avg_success_rate = (
            sum(stats['success_rate'] for stats in function_stats.values()) / total_functions
            if total_functions > 0 else 100.0
        )
        
        # Memory statistics
        total_memory_delta = sum(stats['total_memory_delta'] for stats in function_stats.values())
        
        # File operation statistics
        total_file_ops = sum(stats['count'] for stats in file_stats.values())
        total_file_size = sum(stats['total_size'] for stats in file_stats.values())
        
        return {
            'summary': {
                'total_monitored_functions': total_functions,
                'total_function_calls': total_calls,
                'average_success_rate': avg_success_rate,
                'total_memory_delta_mb': total_memory_delta / 1024 / 1024,
                'total_file_operations': total_file_ops,
                'total_file_size_mb': total_file_size / 1024 / 1024,
                'monitoring_active': self._monitoring_active
            },
            'function_stats': function_stats,
            'file_stats': file_stats,
            'recent_metrics': recent_metrics
        }
    
    def get_slowest_functions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the slowest functions by average duration"""
        function_stats = self.collector.get_function_stats()
        
        sorted_functions = sorted(
            function_stats.items(),
            key=lambda x: x[1]['avg_duration'],
            reverse=True
        )
        
        return [
            {
                'function_name': name,
                'avg_duration': stats['avg_duration'],
                'max_duration': stats['max_duration'],
                'call_count': stats['count'],
                'success_rate': stats['success_rate']
            }
            for name, stats in sorted_functions[:limit]
        ]
    
    def get_memory_heavy_functions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get functions with highest memory usage"""
        function_stats = self.collector.get_function_stats()
        
        sorted_functions = sorted(
            function_stats.items(),
            key=lambda x: abs(x[1]['avg_memory_delta']),
            reverse=True
        )
        
        return [
            {
                'function_name': name,
                'avg_memory_delta_mb': stats['avg_memory_delta'] / 1024 / 1024,
                'total_memory_delta_mb': stats['total_memory_delta'] / 1024 / 1024,
                'call_count': stats['count']
            }
            for name, stats in sorted_functions[:limit]
        ]
    
    def enable_monitoring(self):
        """Enable performance monitoring"""
        self._monitoring_active = True
        self.logger.info("Performance monitoring enabled")
    
    def disable_monitoring(self):
        """Disable performance monitoring"""
        self._monitoring_active = False
        self.logger.info("Performance monitoring disabled")
    
    def reset_metrics(self):
        """Reset all collected metrics"""
        self.collector.clear_metrics()
        # Force garbage collection
        gc.collect()
    
    def export_report(self, file_path: str):
        """Export comprehensive performance report"""
        try:
            report = {
                'report_timestamp': datetime.now().isoformat(),
                'system_info': {
                    'cpu_count': psutil.cpu_count(),
                    'memory_total': psutil.virtual_memory().total,
                    'python_version': f"{psutil.Process().name()}",
                    'process_id': self.process.pid
                },
                'performance_summary': self.get_performance_summary(),
                'slowest_functions': self.get_slowest_functions(),
                'memory_heavy_functions': self.get_memory_heavy_functions()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"Performance report exported to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export performance report: {e}")
    
    def shutdown(self):
        """Shutdown monitoring system"""
        self._monitoring_active = False
        if self._system_monitor_thread and self._system_monitor_thread.is_alive():
            self._system_monitor_thread.join(timeout=5)
        self.logger.info("Performance monitoring shutdown complete")


# Global monitor instance
_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor


# Convenience decorators
def monitor_performance(include_memory: bool = True, 
                       include_args: bool = False,
                       log_level: str = 'INFO'):
    """Convenience decorator for performance monitoring"""
    return get_performance_monitor().monitor_performance(
        include_memory=include_memory,
        include_args=include_args,
        log_level=log_level
    )


def monitor_file_operation(operation_type: str, file_path: str):
    """Convenience context manager for file operation monitoring"""
    return get_performance_monitor().monitor_file_operation(operation_type, file_path)


# Performance analysis utilities
class PerformanceAnalyzer:
    """Utilities for analyzing performance data"""
    
    @staticmethod
    def detect_performance_issues(monitor: PerformanceMonitor) -> Dict[str, List[str]]:
        """Detect potential performance issues"""
        issues = {
            'slow_functions': [],
            'memory_leaks': [],
            'frequent_errors': [],
            'large_files': []
        }
        
        function_stats = monitor.collector.get_function_stats()
        file_stats = monitor.collector.get_file_stats()
        
        # Detect slow functions (>1 second average)
        for name, stats in function_stats.items():
            if stats['avg_duration'] > 1.0:
                issues['slow_functions'].append(
                    f"{name}: {stats['avg_duration']:.2f}s average"
                )
        
        # Detect potential memory leaks (consistent positive memory delta)
        for name, stats in function_stats.items():
            if stats['avg_memory_delta'] > 10 * 1024 * 1024:  # 10MB
                issues['memory_leaks'].append(
                    f"{name}: {stats['avg_memory_delta'] / 1024 / 1024:.2f}MB average increase"
                )
        
        # Detect functions with high error rates
        for name, stats in function_stats.items():
            if stats['success_rate'] < 95.0 and stats['count'] > 5:
                issues['frequent_errors'].append(
                    f"{name}: {stats['success_rate']:.1f}% success rate"
                )
        
        # Detect large file operations
        for op_type, stats in file_stats.items():
            if stats['total_size'] > 100 * 1024 * 1024:  # 100MB
                issues['large_files'].append(
                    f"{op_type}: {stats['total_size'] / 1024 / 1024:.2f}MB total"
                )
        
        return issues
    
    @staticmethod
    def generate_optimization_suggestions(monitor: PerformanceMonitor) -> List[str]:
        """Generate optimization suggestions based on metrics"""
        suggestions = []
        issues = PerformanceAnalyzer.detect_performance_issues(monitor)
        
        if issues['slow_functions']:
            suggestions.append(
                "Consider optimizing slow functions or adding async processing"
            )
        
        if issues['memory_leaks']:
            suggestions.append(
                "Investigate potential memory leaks in high-memory functions"
            )
        
        if issues['frequent_errors']:
            suggestions.append(
                "Improve error handling for functions with high failure rates"
            )
        
        if issues['large_files']:
            suggestions.append(
                "Consider streaming or chunked processing for large files"
            )
        
        function_stats = monitor.collector.get_function_stats()
        total_calls = sum(stats['count'] for stats in function_stats.values())
        
        if total_calls > 10000:
            suggestions.append(
                "High function call volume detected - consider caching frequently called functions"
            )
        
        return suggestions


def create_performance_report(output_file: str = None) -> str:
    """Create a comprehensive performance report"""
    monitor = get_performance_monitor()
    
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"performance_report_{timestamp}.json"
    
    monitor.export_report(output_file)
    return output_file


if __name__ == "__main__":
    # Example usage and testing
    monitor = get_performance_monitor()
    
    @monitor_performance()
    def example_function():
        time.sleep(0.1)
        return "test"
    
    # Test the monitoring
    for i in range(5):
        example_function()
    
    # Generate report
    report_file = create_performance_report()
    print(f"Performance report created: {report_file}")
    
    # Show summary
    summary = monitor.get_performance_summary()
    print(f"Total function calls: {summary['summary']['total_function_calls']}")
    print(f"Average success rate: {summary['summary']['average_success_rate']:.1f}%")
