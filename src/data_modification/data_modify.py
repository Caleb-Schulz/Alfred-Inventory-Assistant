# data_modify.py
# Making a tool that would allow the agent to add any data to any column
import pandas as pd
from langchain.tools import tool

@tool("add_data_to_column", return_direct=True)
def add_data_to_column(inventory_json: str, column_name: str, data, row_index: int = None) -> dict:
    """
    Add data to a specific column in the DataFrame.
    Args:
        inventory_json(str): The input DataFrame as a JSON string.
        column_name(str): The name of the column to which data should be added.
        data: The data to be added to the column. This can be a single value.
        row_index(int): The row index to update.
    Returns:
        dict: The updated inventory data as JSON.
    """
    df = pd.read_json(inventory_json, orient="records")

    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")

    if row_index is None:
        raise ValueError("A row_index must be provided.")

    if row_index < 0 or row_index >= len(df):
        raise ValueError("Row index is out of range.")

    df.at[row_index, column_name] = data

    return {
        "result": df.to_json(orient="records"),
        "unit": "inventory_update",
        "detail": {
            "updated_column": column_name,
            "updated_value": data,
            "row_index": row_index
        }
    }