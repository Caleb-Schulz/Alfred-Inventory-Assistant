# inventory_restock_tool.py
from langchain.tools import tool
import pandas as pd
import streamlit as st
import json
from io import StringIO


@tool
def inventory_restock_tool(inventory_json: str = "", sort_by: str = None) -> dict:
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

    # fallback to session state if tool input is missing or bad
    if not inventory_json or not str(inventory_json).strip():
        inventory_json = st.session_state.get("inventory_json", "[]")

    try:
        json.loads(inventory_json)
    except Exception:
        inventory_json = st.session_state.get("inventory_json", "[]")

    # df = pd.read_json(StringIO(inventory_json), orient="records")
    data = json.loads(inventory_json)
    if isinstance(data, dict):
        data = [data]
    df = pd.DataFrame(data)

    required_cols = ["item_name", "current_stock", "min_stock"]

    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"Missing required columns: {required_cols}")

    df["current_stock"] = pd.to_numeric(df["current_stock"], errors="coerce")
    df["min_stock"] = pd.to_numeric(df["min_stock"], errors="coerce")

    status_list = []
    reorder_list = []

    for _, row in df.iterrows():
        stock = row["current_stock"]
        minimum = row["min_stock"]

        if pd.isnull(stock) or pd.isnull(minimum):
            status = "UNKNOWN"
            reorder = 0

        elif minimum <= 0:
            status = "UNKNOWN"
            reorder = 0

        else:
            ratio = stock / minimum

            if stock <= 0.0:
                status = "URGENT"
            elif ratio < 1.0:
                status = "URGENT"
            elif ratio < 1.5:
                status = "LOW"
            else:
                status = "SAFE"

            reorder = max(minimum - stock, 0)

        status_list.append(status)
        reorder_list.append(reorder)

    df["status"] = status_list
    df["reorder_qty"] = reorder_list

    if sort_by and sort_by in df.columns:
        df = df.sort_values(by=sort_by)

    summary = {
        "urgent": int((df["status"] == "URGENT").sum()),
        "low": int((df["status"] == "LOW").sum()),
        "safe": int((df["status"] == "SAFE").sum()),
        "unknown": int((df["status"] == "UNKNOWN").sum())
    }

    return {
        "result": df.to_json(orient="records"),
        "unit": "inventory_status",
        "detail": summary
    }