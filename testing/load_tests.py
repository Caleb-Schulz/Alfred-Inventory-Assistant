import pandas as pd
from src.tools.inventory_restock_tool import inventory_restock_tool

def test_load_multiple_requests():
    df = pd.DataFrame({
        "item_name": ["Milk"],
        "current_stock": [5],
        "min_stock": [10]
    })

    json_data = df.to_json(orient="records")

    for _ in range(100):
        result = inventory_restock_tool(json_data)
        assert result["unit"] == "inventory_status"