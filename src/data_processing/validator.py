import pandas as pd

# checks to see if all required columns are present
def validate_required_columns(df: pd.DataFrame) -> None:
    required_columns = [
        "item_name",
        "current_stock",
        "min_stock",
        "daily_demand",
        "lead_days",
        "supplier",
        "category"
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

# checks for valid values in the numeric inventory columns
def validate_numeric_columns(df: pd.DataFrame) -> None:
    numeric_columns = ["current_stock", "min_stock", "daily_demand", "lead_days"]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

# flags the rows with negative values in the numeric columns
def flag_negative_values(df: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = ["current_stock", "min_stock", "daily_demand", "lead_days"]

    if "needs_review" not in df.columns:
        df["needs_review"] = False

    for col in numeric_columns:
        if col in df.columns:
            df.loc[df[col] < 0, "needs_review"] = True

    return df