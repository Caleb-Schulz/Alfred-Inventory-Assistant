import pandas as pd

COLUMN_MAP = {
    "item name": "item_name",
    "stock": "current_stock",
    "min stock": "min_stock",
    "daily demand": "daily_demand",
    "lead time": "lead_days",
    "supplier": "supplier",
    "category": "category",
}

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    cleaned_columns = {}

    for col in df.columns:
        normalized = col.strip().lower()
        cleaned_columns[col] = COLUMN_MAP.get(normalized, normalized.replace(" ", "_"))

    df = df.rename(columns=cleaned_columns)
    return df