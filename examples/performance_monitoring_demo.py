"""
Performance Monitoring Usage Examples

This module demonstrates how to use the performance monitoring system
in ProjectBudgetinator for various scenarios.
"""

import time
import random
from pathlib import Path
from typing import List
from utils.performance_monitor import (
    monitor_performance, 
    monitor_file_operation, 
    get_performance_monitor,
    create_performance_report,
    PerformanceAnalyzer
)


class ExcelOperationExamples:
    """Examples of Excel operations with performance monitoring"""
    
    @monitor_performance(include_memory=True, log_level='INFO')
    def load_large_excel_file(self, file_path: str) -> bool:
        """
        Example of loading a large Excel file with performance monitoring.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Success status
        """
        try:
            # Simulate file loading operation
            with monitor_file_operation('read', file_path):
                # Simulate time-consuming operation
                time.sleep(random.uniform(0.5, 2.0))
                
                # Simulate memory allocation
                large_data = list(range(100000))
                
                # Process data
                processed_data = [x * 2 for x in large_data]
                
                return len(processed_data) > 0
                
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    @monitor_performance(include_memory=True, log_level='INFO')
    def save_excel_file(self, file_path: str, data: List[List]) -> bool:
        """
        Example of saving Excel file with performance monitoring.
        
        Args:
            file_path: Path to save file
            data: Data to save
            
        Returns:
            Success status
        """
        try:
            with monitor_file_operation('write', file_path):
                # Simulate data processing
                time.sleep(random.uniform(0.2, 1.0))
                
                # Simulate file write
                time.sleep(random.uniform(0.1, 0.5))
                
                return True
                
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
    
    @monitor_performance(include_memory=True, log_level='INFO')
    def process_partner_data(self, partner_count: int) -> dict:
        """
        Example of processing partner data with performance monitoring.
        
        Args:
            partner_count: Number of partners to process
            
        Returns:
            Processing results
        """
        results = {
            'processed': 0,
            'errors': 0,
            'total_time': 0
        }
        
        start_time = time.time()
        
        for i in range(partner_count):
            try:
                # Simulate partner data processing
                time.sleep(random.uniform(0.01, 0.05))
                
                # Simulate some data manipulation
                partner_data = {
                    'id': i,
                    'name': f'Partner {i}',
                    'data': list(range(random.randint(10, 100)))
                }
                
                results['processed'] += 1
                
            except Exception:
                results['errors'] += 1
        
        results['total_time'] = time.time() - start_time
        return results
    
    @monitor_performance(include_memory=True, log_level='INFO')
    def validate_workbook_structure(self, file_path: str) -> dict:
        """
        Example of workbook validation with performance monitoring.
        
        Args:
            file_path: Path to workbook
            
        Returns:
            Validation results
        """
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'sheets_checked': 0
        }
        
        try:
            # Simulate validation process
            sheet_names = ['Sheet1', 'Partners', 'WorkPackages', 'Summary']
            
            for sheet_name in sheet_names:
                # Simulate sheet validation
                time.sleep(random.uniform(0.1, 0.3))
                
                # Random validation results
                if random.random() < 0.1:  # 10% chance of error
                    validation_results['errors'].append(f"Error in {sheet_name}")
                    validation_results['valid'] = False
                
                if random.random() < 0.2:  # 20% chance of warning
                    validation_results['warnings'].append(f"Warning in {sheet_name}")
                
                validation_results['sheets_checked'] += 1
            
            return validation_results
            
        except Exception as e:
            validation_results['valid'] = False
            validation_results['errors'].append(str(e))
            return validation_results


def demonstrate_performance_monitoring():
    """Demonstrate various aspects of performance monitoring"""
    
    print("🚀 Performance Monitoring Demonstration")
    print("=" * 50)
    
    # Get the performance monitor instance
    monitor = get_performance_monitor()
    
    # Create examples instance
    examples = ExcelOperationExamples()
    
    print("\n📊 Running Excel Operations...")
    
    # Simulate various operations
    operations = [
        ("Loading large file", lambda: examples.load_large_excel_file("large_file.xlsx")),
        ("Saving data", lambda: examples.save_excel_file("output.xlsx", [[1, 2, 3]])),
        ("Processing partners", lambda: examples.process_partner_data(50)),
        ("Validating workbook", lambda: examples.validate_workbook_structure("test.xlsx"))
    ]
    
    for operation_name, operation in operations:
        print(f"  • {operation_name}...")
        result = operation()
        print(f"    Result: {result}")
    
    print("\n📈 Performance Summary:")
    
    # Get performance summary
    summary = monitor.get_performance_summary()
    
    print(f"  • Total function calls: {summary['summary']['total_function_calls']}")
    print(f"  • Average success rate: {summary['summary']['average_success_rate']:.1f}%")
    print(f"  • Total memory delta: {summary['summary']['total_memory_delta_mb']:.2f} MB")
    print(f"  • File operations: {summary['summary']['total_file_operations']}")
    
    print("\n🐌 Slowest Functions:")
    slowest = monitor.get_slowest_functions(5)
    for func_info in slowest:
        print(f"  • {func_info['function_name']}: {func_info['avg_duration']:.3f}s avg")
    
    print("\n🧠 Memory Heavy Functions:")
    memory_heavy = monitor.get_memory_heavy_functions(5)
    for func_info in memory_heavy:
        print(f"  • {func_info['function_name']}: {func_info['avg_memory_delta_mb']:+.2f}MB avg")
    
    print("\n🔍 Performance Analysis:")
    issues = PerformanceAnalyzer.detect_performance_issues(monitor)
    
    for issue_type, issue_list in issues.items():
        if issue_list:
            print(f"  • {issue_type.replace('_', ' ').title()}:")
            for issue in issue_list:
                print(f"    - {issue}")
    
    print("\n💡 Optimization Suggestions:")
    suggestions = PerformanceAnalyzer.generate_optimization_suggestions(monitor)
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    # Export detailed report
    print("\n📄 Exporting Performance Report...")
    report_file = create_performance_report()
    print(f"  Report saved to: {report_file}")
    
    print("\n✅ Demonstration complete!")
    return report_file


def simulate_performance_load():
    """Simulate various performance scenarios for testing"""
    
    print("\n🔄 Simulating Performance Load...")
    
    examples = ExcelOperationExamples()
    
    # Simulate different types of operations
    scenarios = [
        ("Light load", 5, 0.1),
        ("Medium load", 15, 0.5),
        ("Heavy load", 30, 1.0)
    ]
    
    for scenario_name, operations, delay in scenarios:
        print(f"  Running {scenario_name}...")
        
        for i in range(operations):
            # Mix different operation types
            if i % 3 == 0:
                examples.load_large_excel_file(f"file_{i}.xlsx")
            elif i % 3 == 1:
                examples.process_partner_data(random.randint(10, 50))
            else:
                examples.validate_workbook_structure(f"workbook_{i}.xlsx")
            
            time.sleep(delay)
    
    print("  Load simulation complete!")


def monitor_custom_function_example():
    """Example of monitoring a custom function"""
    
    @monitor_performance(include_memory=True, include_args=True, log_level='DEBUG')
    def custom_data_processing(data_size: int, processing_type: str) -> dict:
        """Custom function with performance monitoring"""
        
        # Simulate different processing types
        if processing_type == "fast":
            time.sleep(random.uniform(0.1, 0.3))
        elif processing_type == "medium":
            time.sleep(random.uniform(0.5, 1.0))
        else:  # slow
            time.sleep(random.uniform(1.0, 2.0))
        
        # Simulate memory usage based on data size
        data = list(range(data_size))
        processed = [x ** 2 for x in data]
        
        return {
            'input_size': data_size,
            'output_size': len(processed),
            'processing_type': processing_type
        }
    
    print("\n🔧 Custom Function Monitoring Example:")
    
    # Test different scenarios
    test_cases = [
        (1000, "fast"),
        (5000, "medium"),
        (10000, "slow"),
        (2000, "fast"),
        (8000, "medium")
    ]
    
    for data_size, proc_type in test_cases:
        result = custom_data_processing(data_size, proc_type)
        print(f"  Processed {result['input_size']} items ({proc_type}) -> {result['output_size']} results")


if __name__ == "__main__":
    # Run the demonstration
    report_file = demonstrate_performance_monitoring()
    
    # Run additional examples
    simulate_performance_load()
    monitor_custom_function_example()
    
    print(f"\n📊 Complete performance report available in: {report_file}")
    print("\n🎯 You can now:")
    print("  • Open the GUI performance monitor")
    print("  • Review the exported JSON report")
    print("  • Analyze function performance metrics")
    print("  • Implement optimization suggestions")
