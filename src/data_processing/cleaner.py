import pandas as pd

# maps messy column names to the clean names so that the app will use
COLUMN_MAP = {
    "item name": "item_name",
    "stock": "current_stock",
    "min stock": "min_stock",
    "daily demand": "daily_demand",
    "lead time": "lead_days",
    "supplier": "supplier",
    "category": "category",
}

# maps messy column names to the clean names that the app will use
def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    cleaned_columns = {}

    for col in df.columns:
        normalized = col.strip().lower()
        cleaned_columns[col] = COLUMN_MAP.get(normalized, normalized.replace(" ", "_"))

    df = df.rename(columns=cleaned_columns)
    return df

# fills some missing values and flags rows that originally had missing data
def clean_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    df["needs_review"] = df.isna().any(axis=1)

    if "category" in df.columns:
        df["category"] = df["category"].fillna("uncategorized")

    if "supplier" in df.columns:
        df["supplier"] = df["supplier"].fillna("unknown")

    return df