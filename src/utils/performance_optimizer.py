"""
Performance Optimization Engine for ProjectBudgetinator.

This module provides comprehensive performance optimization capabilities including:
- Intelligent caching strategies
- Performance profiling and benchmarking
- Automatic optimization recommendations
- Excel processing optimization
- Memory and CPU usage optimization
"""

import time
import threading
import logging
import statistics
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from functools import wraps
import weakref

from utils.cache_manager import AdvancedCacheManager
from utils.performance_monitor import get_performance_monitor, CacheMetric, PerformanceBenchmark

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Result of a performance optimization."""
    operation_name: str
    original_duration: float
    optimized_duration: float
    improvement_percent: float
    optimization_type: str
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceProfile:
    """Performance profile for a function or operation."""
    function_name: str
    call_count: int
    total_duration: float
    avg_duration: float
    min_duration: float
    max_duration: float
    memory_usage: float
    cache_hit_rate: float
    optimization_potential: float
    bottleneck_score: float


class PerformanceOptimizer:
    """
    Advanced performance optimization engine.
    
    Features:
    - Automatic performance profiling
    - Intelligent caching recommendations
    - Excel processing optimization
    - Memory usage optimization
    - Performance regression detection
    """
    
    def __init__(self, cache_manager: AdvancedCacheManager):
        """
        Initialize performance optimizer.
        
        Args:
            cache_manager: Advanced cache manager instance
        """
        self.cache_manager = cache_manager
        self.performance_monitor = get_performance_monitor()
        
        # Optimization tracking
        self.optimization_results: List[OptimizationResult] = []
        self.performance_profiles: Dict[str, PerformanceProfile] = {}
        self.optimization_strategies: Dict[str, Callable] = {}
        
        # Performance baselines
        self.baselines: Dict[str, float] = {}
        self.regression_threshold = 0.15  # 15% performance degradation threshold
        
        # Optimization configuration
        self.auto_optimize = True
        self.optimization_interval = 300  # 5 minutes
        self.min_samples_for_optimization = 10
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Register built-in optimization strategies
        self._register_optimization_strategies()
        
        # Start background optimization
        self._start_optimization_thread()
    
    def _register_optimization_strategies(self):
        """Register built-in optimization strategies."""
        self.optimization_strategies.update({
            'excel_caching': self._optimize_excel_caching,
            'memory_management': self._optimize_memory_management,
            'function_caching': self._optimize_function_caching,
            'batch_processing': self._optimize_batch_processing,
            'lazy_loading': self._optimize_lazy_loading
        })
    
    def _start_optimization_thread(self):
        """Start background optimization thread."""
        def optimization_worker():
            while self.auto_optimize:
                try:
                    time.sleep(self.optimization_interval)
                    self._run_automatic_optimization()
                except Exception as e:
                    logger.error(f"Optimization worker error: {e}")
        
        optimization_thread = threading.Thread(
            target=optimization_worker,
            daemon=True,
            name="PerformanceOptimizer"
        )
        optimization_thread.start()
    
    def profile_function(self, func: Callable, *args, **kwargs) -> PerformanceProfile:
        """
        Profile a function's performance.
        
        Args:
            func: Function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            PerformanceProfile: Performance profile data
        """
        function_name = func.__name__
        
        # Get existing stats from performance monitor
        stats = self.performance_monitor.collector.get_function_stats(function_name)
        
        if not stats:
            # Run function once to get initial stats
            start_time = time.perf_counter()
            try:
                func(*args, **kwargs)
                duration = time.perf_counter() - start_time
                
                profile = PerformanceProfile(
                    function_name=function_name,
                    call_count=1,
                    total_duration=duration,
                    avg_duration=duration,
                    min_duration=duration,
                    max_duration=duration,
                    memory_usage=0.0,
                    cache_hit_rate=0.0,
                    optimization_potential=self._calculate_optimization_potential(function_name, duration),
                    bottleneck_score=self._calculate_bottleneck_score(function_name, duration)
                )
            except Exception as e:
                logger.error(f"Error profiling function {function_name}: {e}")
                raise
        else:
            # Use existing stats
            profile = PerformanceProfile(
                function_name=function_name,
                call_count=stats['count'],
                total_duration=stats['total_duration'],
                avg_duration=stats['avg_duration'],
                min_duration=stats['min_duration'],
                max_duration=stats['max_duration'],
                memory_usage=stats.get('avg_memory_delta', 0.0),
                cache_hit_rate=stats.get('cache_hit_rate', 0.0),
                optimization_potential=self._calculate_optimization_potential(function_name, stats['avg_duration']),
                bottleneck_score=self._calculate_bottleneck_score(function_name, stats['avg_duration'])
            )
        
        with self._lock:
            self.performance_profiles[function_name] = profile
        
        return profile
    
    def optimize_function(self, func: Callable, strategy: str = 'auto') -> OptimizationResult:
        """
        Optimize a function using specified strategy.
        
        Args:
            func: Function to optimize
            strategy: Optimization strategy ('auto', 'caching', 'memory', etc.)
            
        Returns:
            OptimizationResult: Optimization results
        """
        function_name = func.__name__
        
        # Profile current performance
        original_profile = self.profile_function(func)
        original_duration = original_profile.avg_duration
        
        # Determine optimization strategy
        if strategy == 'auto':
            strategy = self._select_optimization_strategy(original_profile)
        
        # Apply optimization
        optimization_func = self.optimization_strategies.get(strategy)
        if not optimization_func:
            raise ValueError(f"Unknown optimization strategy: {strategy}")
        
        optimized_func, recommendations = optimization_func(func, original_profile)
        
        # Measure optimized performance
        optimized_profile = self.profile_function(optimized_func)
        optimized_duration = optimized_profile.avg_duration
        
        # Calculate improvement
        improvement_percent = ((original_duration - optimized_duration) / original_duration) * 100
        
        result = OptimizationResult(
            operation_name=function_name,
            original_duration=original_duration,
            optimized_duration=optimized_duration,
            improvement_percent=improvement_percent,
            optimization_type=strategy,
            recommendations=recommendations
        )
        
        with self._lock:
            self.optimization_results.append(result)
        
        # Record benchmark
        benchmark = PerformanceBenchmark(
            operation_name=function_name,
            baseline_duration=original_duration,
            current_duration=optimized_duration,
            improvement_percent=improvement_percent,
            sample_size=original_profile.call_count,
            timestamp=datetime.now()
        )
        self.performance_monitor.collector.add_benchmark(benchmark)
        
        logger.info(f"Optimized {function_name}: {improvement_percent:.1f}% improvement using {strategy}")
        
        return result
    
    def _calculate_optimization_potential(self, function_name: str, avg_duration: float) -> float:
        """Calculate optimization potential score (0-100)."""
        # Factors that indicate optimization potential
        potential_score = 0.0
        
        # Duration-based potential
        if avg_duration > 1.0:  # > 1 second
            potential_score += 40
        elif avg_duration > 0.1:  # > 100ms
            potential_score += 20
        
        # Cache hit rate potential
        cache_stats = self.cache_manager.get_cache_stats()
        if cache_stats.get('hit_rate', 0) < 50:  # Low cache hit rate
            potential_score += 30
        
        # Memory usage potential
        stats = self.performance_monitor.collector.get_function_stats(function_name)
        if stats and stats.get('avg_memory_delta', 0) > 10 * 1024 * 1024:  # > 10MB
            potential_score += 20
        
        # Call frequency potential
        if stats and stats.get('count', 0) > 100:  # Frequently called
            potential_score += 10
        
        return min(potential_score, 100.0)
    
    def _calculate_bottleneck_score(self, function_name: str, avg_duration: float) -> float:
        """Calculate bottleneck score (0-100)."""
        # Get all function stats to compare
        all_stats = self.performance_monitor.collector.get_function_stats()
        
        if not all_stats:
            return 0.0
        
        # Calculate relative duration
        all_durations = [stats['avg_duration'] for stats in all_stats.values()]
        if not all_durations:
            return 0.0
        
        max_duration = max(all_durations)
        if max_duration == 0:
            return 0.0
        
        # Score based on relative duration
        relative_duration = avg_duration / max_duration
        bottleneck_score = relative_duration * 100
        
        # Boost score for frequently called slow functions
        stats = all_stats.get(function_name, {})
        call_count = stats.get('count', 0)
        if call_count > 50:
            bottleneck_score *= 1.5
        
        return min(bottleneck_score, 100.0)
    
    def _select_optimization_strategy(self, profile: PerformanceProfile) -> str:
        """Select the best optimization strategy for a function."""
        # High memory usage -> memory optimization
        if profile.memory_usage > 50 * 1024 * 1024:  # > 50MB
            return 'memory_management'
        
        # Low cache hit rate -> caching optimization
        if profile.cache_hit_rate < 30:
            return 'function_caching'
        
        # High call count with moderate duration -> batch processing
        if profile.call_count > 100 and profile.avg_duration > 0.1:
            return 'batch_processing'
        
        # Excel-related functions -> Excel caching
        if 'excel' in profile.function_name.lower() or 'workbook' in profile.function_name.lower():
            return 'excel_caching'
        
        # Default to function caching
        return 'function_caching'
    
    def _optimize_excel_caching(self, func: Callable, profile: PerformanceProfile) -> Tuple[Callable, List[str]]:
        """Optimize Excel operations with intelligent caching."""
        @wraps(func)
        def cached_excel_func(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"excel_{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            start_time = time.perf_counter()
            cached_result = self.cache_manager.get(cache_key)
            
            if cached_result is not None:
                # Cache hit
                duration = time.perf_counter() - start_time
                cache_metric = CacheMetric(
                    operation_type='get',
                    cache_key=cache_key,
                    hit=True,
                    duration=duration,
                    data_size=len(str(cached_result)),
                    timestamp=datetime.now(),
                    cache_level='memory'
                )
                self.performance_monitor.collector.add_cache_metric(cache_metric)
                return cached_result
            
            # Cache miss - execute function
            result = func(*args, **kwargs)
            
            # Cache result with appropriate TTL
            ttl = 600 if 'read' in func.__name__.lower() else 300  # 10 min for reads, 5 min for others
            self.cache_manager.set(cache_key, result, ttl)
            
            # Record cache miss
            duration = time.perf_counter() - start_time
            cache_metric = CacheMetric(
                operation_type='set',
                cache_key=cache_key,
                hit=False,
                duration=duration,
                data_size=len(str(result)),
                timestamp=datetime.now(),
                cache_level='memory'
            )
            self.performance_monitor.collector.add_cache_metric(cache_metric)
            
            return result
        
        recommendations = [
            "Implemented intelligent Excel caching with TTL",
            "Cache TTL optimized based on operation type",
            "Added cache hit/miss metrics tracking",
            "Consider warming cache for frequently accessed files"
        ]
        
        return cached_excel_func, recommendations
    
    def _optimize_memory_management(self, func: Callable, profile: PerformanceProfile) -> Tuple[Callable, List[str]]:
        """Optimize memory usage for functions."""
        @wraps(func)
        def memory_optimized_func(*args, **kwargs):
            import gc
            
            # Force garbage collection before execution
            gc.collect()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Force cleanup after execution
                gc.collect()
        
        recommendations = [
            "Added automatic garbage collection before/after execution",
            "Consider using generators for large data processing",
            "Implement streaming for large file operations",
            "Use context managers for resource management"
        ]
        
        return memory_optimized_func, recommendations
    
    def _optimize_function_caching(self, func: Callable, profile: PerformanceProfile) -> Tuple[Callable, List[str]]:
        """Add intelligent caching to functions."""
        from functools import lru_cache
        
        # Determine cache size based on call frequency
        cache_size = min(128, max(32, profile.call_count // 10))
        
        cached_func = lru_cache(maxsize=cache_size)(func)
        
        recommendations = [
            f"Added LRU cache with size {cache_size}",
            "Cache size optimized based on call frequency",
            "Consider using TTL cache for time-sensitive data",
            "Monitor cache hit rate for further optimization"
        ]
        
        return cached_func, recommendations
    
    def _optimize_batch_processing(self, func: Callable, profile: PerformanceProfile) -> Tuple[Callable, List[str]]:
        """Optimize for batch processing."""
        @wraps(func)
        def batch_optimized_func(*args, **kwargs):
            # If processing multiple items, batch them
            if args and isinstance(args[0], (list, tuple)) and len(args[0]) > 10:
                items = args[0]
                batch_size = 50  # Process in batches of 50
                results = []
                
                for i in range(0, len(items), batch_size):
                    batch = items[i:i + batch_size]
                    batch_result = func(batch, *args[1:], **kwargs)
                    results.extend(batch_result if isinstance(batch_result, (list, tuple)) else [batch_result])
                
                return results
            else:
                return func(*args, **kwargs)
        
        recommendations = [
            "Implemented batch processing for large datasets",
            "Optimized batch size for memory efficiency",
            "Consider parallel processing for CPU-intensive tasks",
            "Use streaming for very large datasets"
        ]
        
        return batch_optimized_func, recommendations
    
    def _optimize_lazy_loading(self, func: Callable, profile: PerformanceProfile) -> Tuple[Callable, List[str]]:
        """Implement lazy loading optimization."""
        @wraps(func)
        def lazy_loaded_func(*args, **kwargs):
            # Create a lazy loader that only executes when accessed
            class LazyResult:
                def __init__(self, func, args, kwargs):
                    self._func = func
                    self._args = args
                    self._kwargs = kwargs
                    self._result = None
                    self._loaded = False
                
                def __getattr__(self, name):
                    if not self._loaded:
                        self._result = self._func(*self._args, **self._kwargs)
                        self._loaded = True
                    return getattr(self._result, name)
                
                def __call__(self, *args, **kwargs):
                    if not self._loaded:
                        self._result = self._func(*self._args, **self._kwargs)
                        self._loaded = True
                    return self._result
            
            return LazyResult(func, args, kwargs)
        
        recommendations = [
            "Implemented lazy loading to defer execution",
            "Data loaded only when actually accessed",
            "Reduces initial memory footprint",
            "Consider for expensive initialization operations"
        ]
        
        return lazy_loaded_func, recommendations
    
    def _run_automatic_optimization(self):
        """Run automatic optimization on detected bottlenecks."""
        try:
            # Get performance statistics
            function_stats = self.performance_monitor.collector.get_function_stats()
            
            # Identify optimization candidates
            candidates = []
            for func_name, stats in function_stats.items():
                if (stats['count'] >= self.min_samples_for_optimization and
                    stats['avg_duration'] > 0.1):  # > 100ms average
                    
                    optimization_potential = self._calculate_optimization_potential(func_name, stats['avg_duration'])
                    if optimization_potential > 50:  # High potential
                        candidates.append((func_name, optimization_potential))
            
            # Sort by optimization potential
            candidates.sort(key=lambda x: x[1], reverse=True)
            
            # Log optimization opportunities
            if candidates:
                logger.info(f"Identified {len(candidates)} optimization candidates")
                for func_name, potential in candidates[:5]:  # Top 5
                    logger.info(f"  {func_name}: {potential:.1f}% optimization potential")
            
        except Exception as e:
            logger.error(f"Error in automatic optimization: {e}")
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report."""
        with self._lock:
            return {
                'optimization_results': [
                    {
                        'operation_name': result.operation_name,
                        'improvement_percent': result.improvement_percent,
                        'optimization_type': result.optimization_type,
                        'timestamp': result.timestamp.isoformat()
                    }
                    for result in self.optimization_results
                ],
                'performance_profiles': {
                    name: {
                        'call_count': profile.call_count,
                        'avg_duration': profile.avg_duration,
                        'optimization_potential': profile.optimization_potential,
                        'bottleneck_score': profile.bottleneck_score
                    }
                    for name, profile in self.performance_profiles.items()
                },
                'cache_stats': self.cache_manager.get_cache_stats(),
                'total_optimizations': len(self.optimization_results),
                'avg_improvement': statistics.mean([r.improvement_percent for r in self.optimization_results]) if self.optimization_results else 0
            }
    
    def enable_auto_optimization(self):
        """Enable automatic optimization."""
        self.auto_optimize = True
        logger.info("Automatic optimization enabled")
    
    def disable_auto_optimization(self):
        """Disable automatic optimization."""
        self.auto_optimize = False
        logger.info("Automatic optimization disabled")


# Global performance optimizer instance
_optimizer = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """Get global performance optimizer instance."""
    global _optimizer
    if _optimizer is None:
        from utils.cache_manager import cache_manager
        _optimizer = PerformanceOptimizer(cache_manager)
    return _optimizer


def optimize_performance(strategy: str = 'auto'):
    """Decorator for automatic performance optimization."""
    def decorator(func: Callable) -> Callable:
        optimizer = get_performance_optimizer()
        optimized_func, _ = optimizer.optimize_function(func, strategy)
        return optimized_func
    return decorator


if __name__ == "__main__":
    # Example usage
    optimizer = get_performance_optimizer()
    
    @optimize_performance('excel_caching')
    def example_excel_function(file_path: str):
        # Simulate Excel processing
        time.sleep(0.1)
        return f"Processed {file_path}"
    
    # Test optimization
    result = example_excel_function("test.xlsx")
    print(f"Result: {result}")
    
    # Get optimization report
    report = optimizer.get_optimization_report()
    print(f"Optimization report: {report}")