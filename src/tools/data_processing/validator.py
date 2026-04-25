# validator.py
import pandas as pd
from src.tools.data_processing.schema import REQUIRED_COLUMNS, NUMERIC_COLUMNS

# checks to see if all required columns are present
def validate_required_columns(df: pd.DataFrame) -> None:
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

# checks for valid values in the numeric inventory columns
def validate_numeric_columns(df: pd.DataFrame) -> None:
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

# flags the rows with negative values in the numeric columns
def flag_negative_values(df: pd.DataFrame) -> pd.DataFrame:
    if "needs_review" not in df.columns:
        df["needs_review"] = False

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df.loc[df[col] < 0, "needs_review"] = True

    return df