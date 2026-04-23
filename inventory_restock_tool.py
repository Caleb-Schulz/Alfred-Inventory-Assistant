from langchain.tools import tool
import pandas as pd


@tool
def inventory_restock_tool(inventory_json: str, sort_by: str = None) -> dict:
    """
    Determines inventory restock urgency using deterministic rules.

    Compute:
    - SAFE / LOW / URGENT labels
    - reorder quantities
    - optional sorting

    Args:
        inventory_json: inventory dataframe converted to JSON string
        sort_by: optional column to sort results

    Returns:
        dict containing updated inventory + summary
    """

    df = pd.read_json(inventory_json, orient="records")

    required_cols = ["item_name", "current_stock", "min_stock"]

    if not all(col in df.columns for col in required_cols):
        raise ValueError(
            f"Missing required columns: {required_cols}"
        )
