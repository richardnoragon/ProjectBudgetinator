"""
Simple test to verify test infrastructure works.
"""

import pytest


def test_simple_addition():
    """Test that basic math works."""
    assert 1 + 1 == 2


def test_string_operations():
    """Test basic string operations."""
    text = "Hello World"
    assert "Hello" in text
    assert text.upper() == "HELLO WORLD"


class TestBasicFunctionality:
    """Test class for basic functionality."""
    
    def test_list_operations(self):
        """Test basic list operations."""
        items = [1, 2, 3]
        items.append(4)
        assert len(items) == 4
        assert 4 in items
    
    def test_dict_operations(self):
        """Test basic dictionary operations."""
        data = {"name": "Test", "value": 42}
        assert data["name"] == "Test"
        assert data.get("missing", "default") == "default"
    
    @pytest.mark.parametrize("input_value,expected", [
        (1, 2),
        (2, 4),
        (3, 6),
        (4, 8)
    ])
    def test_double_value(self, input_value, expected):
        """Test parameterized doubling function."""
        result = input_value * 2
        assert result == expected


@pytest.mark.performance
def test_performance_placeholder():
    """Placeholder for performance test."""
    # This would be a benchmark test
    result = sum(range(1000))
    assert result == 499500


@pytest.mark.integration
def test_integration_placeholder():
    """Placeholder for integration test."""
    # This would test integration between components
    assert True
