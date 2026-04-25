# data_modify.py
# Making a tool that would allow the agent to add any data to any column
import re
import json
import pandas as pd
import streamlit as st
from io import StringIO
from langchain.tools import tool

@tool("add_data_to_column")
def add_data_to_column(instruction: str) -> dict:
    """
    Add data to a specific column in the DataFrame.
    Args:
        instruction(str): A request like 'set row 0 supplier to FreshCo'
    Returns:
        dict: The updated inventory data as JSON.
    """

    inventory_json = st.session_state.get("inventory_json", "[]")

    try:
        json.loads(inventory_json)
    except Exception:
        raise ValueError("Inventory data is missing or invalid.")

    df = pd.read_json(StringIO(inventory_json), orient="records")

    match = re.search(r"row\s+(\d+)\s+([a-zA-Z_]+)\s+to\s+(.+)", instruction.strip(), re.IGNORECASE)

    if not match:
        raise ValueError("Instruction format should look like: 'set row 0 supplier to FreshCo'")

    row_index = int(match.group(1))
    column_name = match.group(2).strip()
    new_value = match.group(3).strip()
    new_value = new_value.strip('"').strip("'")
    new_value = new_value.rstrip("]}").strip()

    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")

    if row_index < 0 or row_index >= len(df):
        raise ValueError("Row index is out of range.")

    df.at[row_index, column_name] = new_value

    return {
        "result": df.to_json(orient="records"),
        "unit": "inventory_update",
        "detail": {
            "updated_column": column_name,
            "updated_value": new_value,
            "row_index": row_index
        }
    }