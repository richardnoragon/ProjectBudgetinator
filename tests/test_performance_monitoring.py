#!/usr/bin/env python3
"""
Simple test for performance monitoring system
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.performance_monitor import get_performance_monitor, monitor_performance
import time

@monitor_performance()
def test_function():
    """Test function to verify monitoring works"""
    time.sleep(0.1)
    return 'Success'

def main():
    print('🧪 Testing performance monitoring system...')
    
    # Initialize monitor
    monitor = get_performance_monitor()
    print(f'✅ Monitor initialized: {monitor is not None}')
    
    # Run test function
    print('🔄 Running monitored test function...')
    result = test_function()
    print(f'✅ Test function result: {result}')
    
    # Get summary
    summary = monitor.get_performance_summary()
    total_calls = summary['summary']['total_function_calls']
    print(f'📊 Function calls tracked: {total_calls}')
    
    if total_calls > 0:
        print('🎉 Performance monitoring system is working correctly!')
        
        # Show function stats
        function_stats = monitor.collector.get_function_stats()
        for func_name, stats in function_stats.items():
            print(f'   • {func_name}: {stats["count"]} calls, {stats["avg_duration"]:.3f}s avg')
    else:
        print('❌ No function calls were tracked - there may be an issue')
    
    return True

if __name__ == '__main__':
    main()
