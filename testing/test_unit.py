import pytest
import pandas as pd
from src.tools.inventory_restock_tool import inventory_restock_tool

def test_basic_restock_logic():
    df = pd.DataFrame({
        "item_name": ["Milk", "Eggs", "Rice"],
        "current_stock": [5, 20, 50],
        "min_stock": [10, 20, 25]
    })

    json_data = df.to_json(orient="records")

    result = inventory_restock_tool.invoke(json_data)

    assert result["unit"] == "inventory_status"
    assert result["detail"]["urgent"] >= 1
    assert result["detail"]["safe"] >= 1

def test_unknown_values():
    df = pd.DataFrame({
        "item_name": ["Tomato"],
        "current_stock": [None],
        "min_stock": [20]
    })

    json_data = df.to_json(orient="records")

    result = inventory_restock_tool.invoke(json_data)

    assert result["detail"]["unknown"] == 1

def test_invalid_input():
    df = pd.DataFrame({
        "item_name": ["Milk"],
        "wrong_column": [10]
    })

    json_data = df.to_json(orient="records")

    with pytest.raises(ValueError):
        inventory_restock_tool.invoke(json_data)

# to run all test
# pytest