from src.data_processing.parser import read_inventory_csv
from src.tools.inventory_restock_tool import inventory_restock_tool


def test_full_pipeline():
    df, _ = read_inventory_csv("data/sample_inventory_messy.csv")

    json_data = df.to_json(orient="records")

    result = inventory_restock_tool(json_data)

    assert result["unit"] == "inventory_status"
    assert "urgent" in result["detail"]
    assert "low" in result["detail"]

    # to run all test
    # pytest