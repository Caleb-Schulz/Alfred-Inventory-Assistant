# parser.py
import pandas as pd
from src.data_processing.cleaner import standardize_column_names, clean_missing_values, normalize_text_fields, remove_duplicates
from src.data_processing.validator import validate_required_columns, validate_numeric_columns, flag_negative_values
from src.data_processing.exporter import export_clean_inventory_csv

# Reads the inventory csv file and returns it as a dataframe and summary
def read_inventory_csv(file_path: str):
    df = pd.read_csv(file_path)
    original_row_count = len(df)
    df = standardize_column_names(df)
    validate_required_columns(df)
    df = clean_missing_values(df)
    df = normalize_text_fields(df)
    before_dedup = len(df)
    df = remove_duplicates(df)
    duplicates_removed = before_dedup - len(df)
    validate_numeric_columns(df)
    df = flag_negative_values(df)
    summary = {
        "original_rows": original_row_count,
        "cleaned_rows": len(df),
        "duplicates_removed": duplicates_removed,
        "rows_needing_review": int(df["needs_review"].sum()) if "needs_review" in df.columns else 0,
    }

    return df, summary

# tests the parser with a sample csv
# if __name__ == "__main__":
    # df, summary = read_inventory_csv("data/sample_inventory_messy.csv")
    # print(df)
    # print("\nSummary:")
    # print(summary)

# I Caleb commented the summary out because it is redundant info