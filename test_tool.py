# test_tool.py
import pytest
from tool import inventory_stock_flagger

def test_happy_path():
    csv_data = "item_name,current_stock,min_stock\nWidgetA,10,20\nWidgetB,50,"
    
    result = inventory_stock_flagger(csv_data)
    
    assert result["result"] == "Issues Found"
    assert "Empty cells: 1" in result["detail"]
    assert "Low stock: 1" in result["detail"]
    assert "visual_report" in result

def test_edge_case():
    csv_data = "item_name,current_stock,min_stock\nWidgetC,10,10\nWidgetD,NA,5"
    
    result = inventory_stock_flagger(csv_data)
    
    assert result["result"] == "Success"
    assert "Empty cells: 0" in result["detail"]
    assert "Low stock: 0" in result["detail"]

def test_invalid_input_raises():
    csv_data = "item_name,current_stock\nWidgetA,10"
    
    with pytest.raises(ValueError, match="CSV must contain columns"):
        inventory_stock_flagger(csv_data)